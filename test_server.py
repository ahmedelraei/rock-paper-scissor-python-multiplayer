import unittest
from unittest.mock import Mock
from server import Server
from game import Game
from communication import Event


class TestHandleClient(unittest.TestCase):
    def setUp(self):
        self.server = Server("127.0.0.1", 3333)
        self.client = Mock()

    def test_get_player(self):
        self.client.conn.return_value = "Player 1"
        self.server.add_to_waiting(self.client.conn(), 1)
        self.client.conn.assert_called_once()
        self.assertEqual({1: "Player 1"}, self.server.waiting)

    def test_connecting_6_players(self):
        for i in range(6):
            self.server.add_to_waiting(self.client.conn(), i)
        self.client.conn.assert_called()
        self.assertEqual(6, len(self.server.waiting))

    def test_connecting_more_than_6_players(self):
        for i in range(6):
            self.server.add_to_waiting(self.client.conn(), i)
        self.client.conn.assert_called()
        self.assertEqual(6, len(self.server.waiting))
        self.assertIsNone(self.server.add_to_waiting(self.client.conn(), 7))

    def test_lobby(self):
        for i in range(6):
            self.server.add_to_waiting(self.client.conn(), i)
        self.assertEqual([0, 1, 2, 3, 4], self.server.lobby(5))

    def test_invite(self):
        for i in range(6):
            self.server.add_to_waiting(self.client.conn(), i)
        event = self.server.invite(5, 4)
        self.assertEqual(Event.EventType.INVITE, event.type)
        self.assertEqual("5", event.message)

    def test_accept(self):
        for i in range(6):
            self.server.add_to_waiting(self.client.conn(), i)
        self.server.invite(5, 4)
        self.assertIsInstance(self.server.accept_invitation(5, 4), Game)

    def test_accept_non_existing_game(self):
        for i in range(6):
            self.server.add_to_waiting(self.client.conn(), i)
        self.server.invite(5, 4)
        self.assertIsNone(self.server.accept_invitation(6, 4))

    def test_accept_non_existing_player(self):
        for i in range(6):
            self.server.add_to_waiting(self.client.conn(), i)
        self.server.invite(5, 4)
        self.assertIsNone(self.server.accept_invitation(5, 7))

    def test_accept_non_existing_game_and_player(self):
        for i in range(6):
            self.server.add_to_waiting(self.client.conn(), i)
        self.server.invite(5, 4)
        self.assertIsNone(self.server.accept_invitation(6, 7))

    def test_decline(self):
        for i in range(6):
            self.server.add_to_waiting(self.client.conn(), i)
        self.server.invite(5, 4)
        self.assertIsInstance(self.server.decline_invitation(5, 4), Event)

    def test_decline_non_existing_game(self):
        for i in range(6):
            self.server.add_to_waiting(self.client.conn(), i)
        self.server.invite(5, 4)
        self.assertRaises(KeyError, lambda: self.server.decline_invitation(6, 4))

    def test_decline_non_existing_player(self):
        for i in range(6):
            self.server.add_to_waiting(self.client.conn(), i)
        self.server.invite(5, 4)
        self.assertRaises(KeyError, lambda: self.server.decline_invitation(5, 8))

    def test_decline_non_existing_game_and_player(self):
        for i in range(6):
            self.server.add_to_waiting(self.client.conn(), i)
        self.server.invite(5, 4)
        self.assertRaises(KeyError, lambda: self.server.decline_invitation(6, 8))

    def tearDown(self):
        self.server.close()
