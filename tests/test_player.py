from axelrod_fortran.strategies import all_strategies
from axelrod_fortran.player import Player
from axelrod import Alternator, Cooperator, Defector, Match
from axelrod.action import Action
from ctypes import c_int, c_float, POINTER

from hypothesis import given
from hypothesis.strategies import integers

C, D = Action.C, Action.D


def test_init():
    for strategy in all_strategies:
        player = Player(strategy)
        assert player.original_name == strategy
        assert player.original_function.argtypes == (
            POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int),
            POINTER(c_float))
        assert player.original_function.restype == c_int


@given(
    their_last_move=integers(min_value=0, max_value=1),
    move_number=integers(min_value=1, max_value=200),
    my_score=integers(min_value=0, max_value=200),
    their_score=integers(min_value=0, max_value=200),
    my_last_move=integers(min_value=0, max_value=1))
def test_original_strategy(
    their_last_move, move_number, my_score, their_score, my_last_move
):
    for strategy in all_strategies:
        player = Player(strategy)
        action = player.original_strategy(
            their_last_move, move_number, my_score, their_score, 0,
            my_last_move)
        assert action in (0, 1), print(f'{strategy} returned {action}')


def test_matches():
    for strategy in all_strategies:
        for opponent in (Alternator, Cooperator, Defector):
            players = (Player(strategy), opponent())
            match = Match(players, 50)
            assert all(
                action in (C, D) for interaction in match.play()
                for action in interaction)
