from axelrod_fortran.strategies import all_strategies
from axelrod_fortran.player import Player
from ctypes import c_int


def test_init():
    for strategy in all_strategies:
        player = Player(strategy)
        assert player.original_name == strategy
        assert player.original_function.restype == c_int


def test_strategy():
    for strategy in all_strategies:
        player = Player(strategy)


