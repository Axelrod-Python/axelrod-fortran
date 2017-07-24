import axelrod.player as axl
from axelrod.interaction_utils import compute_final_score
from axelrod.action import Action

C, D = Action.C, Action.D


def original_strategy(
    their_last_move, move_number, my_score, their_score, noise, my_last_move
):
    # TODO
    # Convert the arguments to ctypes
    # call the fortran function
    # Convert the result to an Action and return it
    return C


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

    @property
    def original_name(self):
        return self.__original_name

    @original_name.setter
    def original_name(self, value):
        # TODO Validate the value against list of known fortran functions
        self.__original_name = value

    def strategy(self, opponent, noise=0):
        their_last_move = self.opponent.history[-1]
        move_number = len(self.history) + 1
        scores = compute_final_score(zip(self.history, self.opponent.history))
        my_last_move = self.history[-1]
        return original_strategy(
            their_last_move, move_number, scores[0], scores[1], noise,
            my_last_move)
