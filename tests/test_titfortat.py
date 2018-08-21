from axelrod_fortran import Player
import axelrod as axl
from axelrod.action import Action

C, D = Action.C, Action.D


def test_versus_alternator():
    players = (Player('ktitfortatc'), axl.Alternator())
    match = axl.Match(players, 5)
    expected = [(C, C), (C, D), (D, C), (C, D), (D, C)]
    assert match.play() == expected


def test_versus_cooperator():
    players = (Player('ktitfortatc'), axl.Cooperator())
    match = axl.Match(players, 5)
    expected = [(C, C), (C, C), (C, C), (C, C), (C, C)]
    assert match.play() == expected


def test_versus_defector():
    players = (Player('ktitfortatc'), axl.Defector())
    match = axl.Match(players, 5)
    expected = [(C, D), (D, D), (D, D), (D, D), (D, D)]
    assert match.play() == expected


def test_versus_itself():
    players = (Player('ktitfortatc'), Player('ktitfortatc'))
    match = axl.Match(players, 5)
    expected = [(C, C), (C, C), (C, C), (C, C), (C, C)]
    assert match.play() == expected
