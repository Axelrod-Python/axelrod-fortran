from axelrod_fortran.strategies import all_strategies
from axelrod_fortran.player import Player
from axelrod import Alternator, Cooperator, Defector, Match, Game
from axelrod.action import Action
from ctypes import c_int, c_float, POINTER

import itertools

C, D = Action.C, Action.D


def test_init():
    for strategy in all_strategies:
        player = Player(strategy)
        assert player.original_name == strategy
        assert player.original_function.argtypes == (
            POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int),
            POINTER(c_float))
        assert player.original_function.restype == c_int


def test_matches():
    for strategy in all_strategies:
        for opponent in (Alternator, Cooperator, Defector):
            players = (Player(strategy), opponent())
            match = Match(players, turns=200)
            assert all(
                action in (C, D) for interaction in match.play()
                for action in interaction)

def test_noisy_matches():
    for strategy in all_strategies:
        for opponent in (Alternator, Cooperator, Defector):
            players = (Player(strategy), opponent())
            match = Match(players, turns=200, noise=0.5)
            assert all(
                action in (C, D) for interaction in match.play()
                for action in interaction)

def test_probend_matches():
    for strategy in all_strategies:
        for opponent in (Alternator, Cooperator, Defector):
            players = (Player(strategy), opponent())
            match = Match(players, prob_end=0.5, noise=0.5)
            assert all(
                action in (C, D) for interaction in match.play()
                for action in interaction)

def test_matches_with_different_game():
    for strategy in all_strategies:
        for opponent in (Alternator, Cooperator, Defector):
            game = Game(r=4,s=0,p=2,t=6)
            players = (Player(strategy, game=game), opponent())
            match = Match(players, turns=200, game=game)
            assert all(
                action in (C, D) for interaction in match.play()
                for action in interaction)


def test_original_strategy():
    """
    Test original strategy against all possible first 5 moves of a Match
    """
    actions_to_scores = {(0, 0): (3, 3), (0, 1): (0, 5),
                         (1, 0): (5, 0), (1, 1): (1, 1)}
    for strategy in all_strategies:
        for opponent_sequence in itertools.product((0, 1), repeat=5):

            player = Player(strategy)

            # Initial set up for empty history
            my_score, their_score = 0, 0
            move_number = 1
            their_previous_action, my_action = 0, 0

            for action in opponent_sequence:
                my_action = player.original_strategy(
                    their_last_move=their_previous_action,
                    move_number=move_number,
                    my_score=my_score,
                    their_score=their_score,
                    noise=0,
                    my_last_move=my_action)

                assert my_action in [0, 1]

                scores = actions_to_scores[my_action, action]
                their_previous_action = action
                my_score += scores[0]
                their_score += scores[1]
