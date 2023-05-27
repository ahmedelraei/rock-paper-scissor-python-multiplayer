import asyncio
import signal
import unittest
from unittest.mock import patch, MagicMock
from game import Game
from communication import Event, Communication
from server import Server


class TestHandleClient(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()

    def test_get_player(self):
        server = Server("127.0.0.1", 3333)
        server.add_to_waiting(self.client, 1)
        self.assertEqual({}, server.waiting)
