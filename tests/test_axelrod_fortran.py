from axelrod_fortran.player import Player
import axelrod as axl
from axelrod.action import Action

C, D = Action.C, Action.D


def test_titfortat():
    players = (Player('ktitfortatc_'), axl.Alternator())
    match = axl.Match(players, 5)
    expected = [(C, C), (C, D), (D, C), (C, D), (D, C)]
    assert match.play() == expected
