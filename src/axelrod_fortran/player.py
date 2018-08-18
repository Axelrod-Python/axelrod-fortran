from collections import defaultdict
from ctypes import cdll, c_int, c_float, byref, POINTER
from ctypes.util import find_library
import os
import platform
import random
import re
import shutil
import subprocess
import tempfile
import uuid
import warnings

import axelrod as axl
from axelrod.interaction_utils import compute_final_score
from axelrod.action import Action
from .strategies import characteristics

C, D = Action.C, Action.D
actions = {0: C, 1: D}
original_actions = {C: 0, D: 1}


path_regex = r""".*?\s=>\s(.*?{}.*?)\\"""

self_interaction_message = """
You are playing a match with the same player against itself. However
axelrod_fortran players share memory. You can initialise another instance of an
Axelrod_fortran player with player.clone().
"""


class LibraryManager(object):
    """LibraryManager creates and loads copies of a shared library, which
    enables multiple copies of the same strategy to be run without the end user
    having to maintain many copies of the shared library.

    This works by making a copy of the shared library file and loading it into
    memory again. Loading the same file again will return a reference to the
    same memory addresses.

    Additionally, library manager tracks how many copies of the library have
    been loaded, and how many copies there are of each Player, so as to load
    only as many copies of the shared library as needed.
    """

    def __init__(self, shared_library_name, verbose=False):
        self.shared_library_name = shared_library_name
        self.verbose = verbose
        self.library_copies = []
        self.player_indices = defaultdict(set)
        self.player_next = defaultdict(set)
        # Generate a random prefix for tempfile generation
        self.prefix = str(uuid.uuid4())
        self.library_path = self.find_shared_library(shared_library_name)
        self.filenames = []

    def find_shared_library(self, shared_library_name):
        # Hack for Linux since find_library doesn't return the full path.
        if 'Linux' in platform.system():
            output = subprocess.check_output(["ldconfig", "-p"])
            for line in str(output).split(r"\n"):
                rhs = line.split(" => ")[-1]
                if shared_library_name in rhs:
                    return rhs
            raise ValueError("{} not found".format(shared_library_name))
        else:
            return find_library(
                shared_library_name.replace("lib", "").replace(".so", ""))

    def load_dll_copy(self):
        """Load a new copy of the shared library."""
        # Copy the library file to a new location so we can load the copy.
        temp_directory = tempfile.gettempdir()
        copy_number = len(self.library_copies)
        new_filename = os.path.join(
            temp_directory,
            "{}-{}-{}".format(
                self.prefix,
                str(copy_number),
                self.shared_library_name)
        )
        if self.verbose:
            print("Loading {}".format(new_filename))
        shutil.copy2(self.library_path, new_filename)
        self.filenames.append(new_filename)
        shared_library = cdll.LoadLibrary(new_filename)
        self.library_copies.append(shared_library)

    def next_player_index(self, name):
        """Determine the index of the next free shared library copy to
        allocate for the player. If none is available then load another copy."""
        # Is there a free index?
        if len(self.player_next[name]) > 0:
            return self.player_next[name].pop()
        # Do we need to load a new copy?
        player_count = len(self.player_indices[name])
        if player_count == len(self.library_copies):
            self.load_dll_copy()
            return player_count
        # Find the first unused index
        for i in range(len(self.library_copies)):
            if i not in self.player_indices[name]:
                return i
        raise ValueError("We shouldn't be here.")

    def load_library_for_player(self, name):
        """For a given player return a copy of the shared library for use
        in a Player class, along with an index for later releasing."""
        index = self.next_player_index(name)
        self.player_indices[name].add(index)
        if self.verbose:
            print("allocating {}".format(index))
        return index, self.library_copies[index]

    def release(self, name, index):
        """Release the copy of the library so that it can be re-allocated."""
        self.player_indices[name].remove(index)
        if self.verbose:
            print("releasing {}".format(index))
        self.player_next[name].add(index)

    def __del__(self):
        """Cleanup temp files on object deletion."""
        for filename in self.filenames:
            if os.path.exists(filename):
                os.remove(filename)


class Player(axl.Player):

    classifier = {"stochastic": True}
    library_manager = None

    def __init__(self, original_name,
                 shared_library_name='libstrategies.so'):
        """
        Parameters
        ----------
        original_name: str
            The name of the fortran function from the original axelrod
            tournament
        game: axelrod.Game
            A instance of an axelrod Game
        """
        super().__init__()
        if not Player.library_manager:
            Player.library_manager = LibraryManager(shared_library_name)
        self.index, self.shared_library = \
            self.library_manager.load_library_for_player(original_name)
        self.original_name = original_name
        self.original_function = self.original_name

        is_stochastic = characteristics[self.original_name]['stochastic']
        if is_stochastic is not None:
            self.classifier['stochastic'] = is_stochastic

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__original_function = None

    @property
    def original_name(self):
        return self.__original_name

    @original_name.setter
    def original_name(self, value):
        if value in characteristics:
            self.__original_name = value
        else:
            raise ValueError('{} is not a valid Fortran function'.format(value))

    @property
    def original_function(self):
        return self.__original_function

    @original_function.setter
    def original_function(self, value):
        self.__original_function = self.shared_library[(value + '_').lower()]
        self.__original_function.argtypes = (
            POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int),
            POINTER(c_float))
        self.__original_function.restype = c_int

    def original_strategy(
        self, their_last_move, move_number, my_score, their_score, random_value,
        my_last_move
    ):
        args = (
            c_int(their_last_move), c_int(move_number), c_int(my_score),
            c_int(their_score), c_float(random_value), c_int(my_last_move))
        return self.original_function(*[byref(arg) for arg in args])

    def strategy(self, opponent):
        if self is opponent:
            warnings.warn(message=self_interaction_message)

        if not self.history:
            their_last_move = 0
            scores = (0, 0)
            my_last_move = 0
        else:
            their_last_move = original_actions[opponent.history[-1]]
            scores = compute_final_score(zip(self.history, opponent.history),
                                         game=self.match_attributes["game"])
            my_last_move = original_actions[self.history[-1]]
        move_number = len(self.history) + 1
        if self.classifier["stochastic"]:
            random_value = random.random()
        else:
            random_value = 0
        original_action = self.original_strategy(
            their_last_move, move_number, scores[0], scores[1], random_value,
            my_last_move)
        return actions[original_action]

    def reset(self):
        # Release the library before rest, which regenerates the player.
        self.library_manager.release(self.original_name, self.index)
        super().reset()
        self.original_function = self.original_name

    def __del__(self):
        # Release the library before deletion.
        self.library_manager.release(self.original_name, self.index)

    def __repr__(self):
        return self.original_name
