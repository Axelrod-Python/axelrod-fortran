from axelrod_fortran.player import Player
import axelrod as axl
from axelrod.action import Action

C, D = Action.C, Action.D


def test_versus_alternator():
    players = (Player('ktitfortatc_'), axl.Alternator())
    match = axl.Match(players, 5)
    expected = [(C, C), (C, D), (D, C), (C, D), (D, C)]
    assert match.play() == expected


def test_versus_cooperator():
    players = (Player('ktitfortatc_'), axl.Cooperator())
    match = axl.Match(players, 5)
    expected = [(C, C), (C, C), (C, C), (C, C), (C, C)]
    assert match.play() == expected


def test_versus_defector():
    players = (Player('ktitfortatc_'), axl.Defector())
    match = axl.Match(players, 5)
    expected = [(C, D), (D, D), (D, D), (D, D), (D, D)]
    assert match.play() == expected
