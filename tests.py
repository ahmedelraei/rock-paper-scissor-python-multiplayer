import unittest
from game import Game


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game(1)

    def test_initial_state(self):
        self.assertFalse(self.game.p1_moved)
        self.assertFalse(self.game.p2_moved)
        self.assertEqual(self.game.id, 1)
        self.assertFalse(self.game.ready)
        self.assertEqual([None, None], self.game.moves)
        self.assertEqual([0, 0], self.game.wins)
        self.assertEqual(0, self.game.ties)
        self.assertEqual(0, self.game.rounds)

    def test_move(self):
        self.game.play(0, "rock")
        self.assertEqual(self.game.get_player_move(0), "rock")

    def test_reset_moves(self):
        self.game.play(0, "rock")
        self.game.play(1, "paper")
        self.game.reset_moves()
        self.assertEqual([None, None], self.game.moves)

    def test_rock_paper(self):
        self.game.play(0, "rock")
        self.game.play(1, "paper")
        self.assertEqual(1, self.game.winner())

    def test_paper_rock(self):
        self.game.play(0, "paper")
        self.game.play(1, "rock")
        self.assertEqual(0, self.game.winner())

    def test_rock_scissors(self):
        self.game.play(0, "rock")
        self.game.play(1, "scissors")
        self.assertEqual(0, self.game.winner())

    def test_scissors_rock(self):
        self.game.play(0, "scissors")
        self.game.play(1, "rock")
        self.assertEqual(1, self.game.winner())

    def test_paper_scissors(self):
        self.game.play(0, "paper")
        self.game.play(1, "scissors")
        self.assertEqual(1, self.game.winner())

    def test_scissors_paper(self):
        self.game.play(0, "scissors")
        self.game.play(1, "paper")
        self.assertEqual(0, self.game.winner())

    def test_tie(self):
        self.game.play(0, "scissors")
        self.game.play(1, "scissors")
        self.assertEqual(-1, self.game.winner())
        self.game.reset_moves()
