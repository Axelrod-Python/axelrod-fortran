import random
import warnings

import axelrod as axl
from axelrod.interaction_utils import compute_final_score
from axelrod.action import Action
from ctypes import cdll, c_int, c_float, byref, POINTER
from .strategies import characteristics

C, D = Action.C, Action.D
actions = {0: C, 1: D}
original_actions = {C: 0, D: 1}


class Player(axl.Player):

    classifier = {"stochastic": True}

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
        self.shared_library_name = shared_library_name
        self.shared_library = cdll.LoadLibrary(shared_library_name)
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
        if type(opponent) is Player \
          and (opponent.original_name == self.original_name) \
          and (opponent.shared_library_name == self.shared_library_name):

            message = """
You are playing a match with two copies of the same player.
However the axelrod fortran players share memory.
You can initialise an instance of an Axelrod_fortran player with a
`shared_library_name`
variable that points to a copy of the shared library."""
            warnings.warn(message=message)

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
        super().reset()
        self.original_function = self.original_name
