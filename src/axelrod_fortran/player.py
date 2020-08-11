from ctypes import byref, c_float, c_int, POINTER
import warnings

import axelrod as axl
from axelrod.interaction_utils import compute_final_score
from axelrod.action import Action

from .strategies import characteristics
from .shared_library_manager import MultiprocessManager, load_library

C, D = Action.C, Action.D
actions = {0: C, 1: D}
original_actions = {C: 0, D: 1}


self_interaction_message = """
You are playing a match with the same player against itself. However
axelrod_fortran players share memory. You can initialise another instance of an
Axelrod_fortran player with player.clone().
"""


# Initialize a module-wide manager for loading copies of the shared library.
manager = MultiprocessManager()
manager.start()
shared_library_manager = manager.SharedLibraryManager("libstrategies.so")


class Player(axl.Player):

    classifier = {"stochastic": True}

    def __init__(self, original_name):
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
        # The order of the next 4 lines is important. We must first check that
        # the player name is valid, then grab a copy of the shared library,
        # and then setup the actual strategy function.
        self.original_name = original_name
        self.index, self.shared_library_filename = \
            shared_library_manager.get_filename_for_player(self.original_name)
        self.shared_library = load_library(self.shared_library_filename)
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
    def original_name(self, key):
        if key in characteristics:
            self.__original_name = key
        else:
            raise ValueError('{} is not a valid Fortran function'.format(key))

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
            random_value = self._random.random()
        else:
            random_value = 0
        original_action = self.original_strategy(
            their_last_move, move_number, scores[0], scores[1], random_value,
            my_last_move)
        return actions[original_action]

    def _release_shared_library(self):
        # While this looks like we're checking that the shared library file
        # isn't deleted, the exception is actually thrown if the manager
        # thread closes before the player class is garbage collected, which
        # tends to happen at the end of a script.
        try:
            name = self.original_name
            index = self.index
        except AttributeError:
            # If the Player does finish __init__, because the name of a
            # non-existent strategy is supplied, a copy of the shared library
            # won't be loaded, nor will self.original_name or self.index
            # exist. In that case there's nothing to do.
            return
        try:
            shared_library_manager.release(name, index)
        except FileNotFoundError:
            pass

    def reset(self):
        # Release the shared library since the object is rebuilt on reset.
        self._release_shared_library()
        super().reset()
        self.original_function = self.original_name

    def __del__(self):
        # Release the library before deletion.
        self._release_shared_library()

    def __repr__(self):
        return self.original_name
