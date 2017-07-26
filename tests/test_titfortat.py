import unittest

from axelrod_fortran.player import Player
import axelrod as axl
from axelrod.action import Action

C, D = Action.C, Action.D


class TestAll(unittest.TestCase):
    def test_versus_alternator(self):
        players = (Player('ktitfortatc'), axl.Alternator())
        match = axl.Match(players, 5)
        expected = [(C, C), (C, D), (D, C), (C, D), (D, C)]
        self.assertEqual(match.play(), expected)

    def test_versus_cooperator(self):
        players = (Player('ktitfortatc'), axl.Cooperator())
        match = axl.Match(players, 5)
        expected = [(C, C), (C, C), (C, C), (C, C), (C, C)]
        self.assertEqual(match.play(), expected)

    def test_versus_defector(self):
        players = (Player('ktitfortatc'), axl.Defector())
        match = axl.Match(players, 5)
        expected = [(C, D), (D, D), (D, D), (D, D), (D, D)]
        self.assertEqual(match.play(), expected)
