from axelrod_fortran.strategies import all_strategies
from axelrod_fortran.player import Player
from ctypes import c_int

from hypothesis import given
from hypothesis.strategies import integers


def test_init():
    for strategy in all_strategies:
        player = Player(strategy)
        assert player.original_name == strategy
        assert player.original_function.restype == c_int


@given(last_move=integers(min_value=0, max_value=1),
       score=integers(min_value=0, max_value=200))
def test_strategy(last_move, score):
    print(last_move, score)
    for strategy in all_strategies:
        player = Player(strategy)


