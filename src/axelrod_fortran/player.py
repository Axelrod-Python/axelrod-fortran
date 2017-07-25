import axelrod.player as axl
from axelrod.interaction_utils import compute_final_score
from axelrod.action import Action
from ctypes import cdll, c_int, c_float, byref, POINTER

C, D = Action.C, Action.D
strategies = cdll.LoadLibrary('libstrategies.so')
actions = {0: C, 1: D}
original_actions = {C: 0, D: 1}


class Player(axl.Player):

    def __init__(self, original_name):
        """
        Parameters
        ----------
        original_name: str
            The name of the fortran function from the original axelrod
            tournament
        """
        super().__init__()
        self.original_name = original_name
        self.original_function = strategies[self.original_name]
        self.original_function.argtypes = (
            POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int),
            POINTER(c_float))
        self.original_function.restype = c_int

    @property
    def original_name(self):
        return self.__original_name

    @original_name.setter
    def original_name(self, value):
        # TODO Validate the value against list of known fortran functions
        self.__original_name = value

    def original_strategy(
        self, their_last_move, move_number, my_score, their_score, noise,
        my_last_move
    ):
        args = (
            c_int(their_last_move), c_int(move_number), c_int(my_score),
            c_int(their_score), c_float(noise), c_int(my_last_move))
        action = self.original_function(*[byref(arg) for arg in args])
        return actions[action]

    def strategy(self, opponent, noise=0):
        if not self.history:
            their_last_move = 0
            scores = (0, 0)
            my_last_move = 0
        else:
            their_last_move = original_actions[opponent.history[-1]]
            scores = compute_final_score(zip(self.history, opponent.history))
            my_last_move = original_actions[self.history[-1]]
        move_number = len(self.history) + 1
        return self.original_strategy(
            their_last_move, move_number, scores[0], scores[1], noise,
            my_last_move)
