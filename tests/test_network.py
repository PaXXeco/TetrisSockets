import time
import unittest

from tetris.network.client import Client
from tetris.network.server import Server
from tetris.network.protocol import Decoder, encode
from tetris.core.state import GameState
from tetris.core.sequence import PieceSequence


def receive(client, kind):
    deadline = time.monotonic() + 4
    while time.monotonic() < deadline:
        for message in client.poll():
            if message['type'] == kind:
                return message
        time.sleep(0.01)
    raise AssertionError(f'Mensagem não recebida: {kind}')


class ProtocolTests(unittest.TestCase):
    def test_fragmented_and_combined_messages(self):
        decoder = Decoder()
        data = encode({'type': 'attack', 'lines': 2}) + encode({'type': 'game_over'})
        self.assertEqual(decoder.feed(data[:5]), [])
        self.assertEqual(decoder.feed(data[5:]),
                         [{'type': 'attack', 'lines': 2}, {'type': 'game_over'}])

    def test_rejects_oversized_message(self):
        with self.assertRaises(ValueError):
            Decoder().feed(b'x' * 32769)


class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.server = Server(0, host='127.0.0.1')
        self.clients = [Client('127.0.0.1', self.server.port) for _ in range(2)]
        self.starts = [receive(client, 'start') for client in self.clients]

    def tearDown(self):
        for client in self.clients:
            client.close()
        self.server.close()

    def test_seed_attacks_board_and_result(self):
        self.assertEqual(self.starts[0]['seed'], self.starts[1]['seed'])
        first = GameState(PieceSequence(self.starts[0]['seed']))
        second = GameState(PieceSequence(self.starts[1]['seed']))
        self.assertEqual(first.current_piece.shape, second.current_piece.shape)
        for count in (1, 2, 4):
            self.clients[0].send({'type': 'attack', 'lines': count})
            holes = receive(self.clients[1], 'garbage')['holes']
            self.assertEqual(len(holes), count)
            self.assertTrue(all(0 <= hole < 10 for hole in holes))
        self.clients[0].send({'type': 'board', 'grid': first.grid, 'score': 20})
        self.assertEqual(receive(self.clients[1], 'board')['score'], 20)
        self.clients[0].send({'type': 'game_over'})
        self.assertFalse(receive(self.clients[0], 'result')['won'])
        self.assertTrue(receive(self.clients[1], 'result')['won'])

    def test_disconnect_is_reported(self):
        self.clients[0].close()
        self.assertEqual(receive(self.clients[1], 'disconnected')['type'], 'disconnected')

    def test_invalid_attack_ends_connection(self):
        self.clients[0].send({'type': 'attack', 'lines': 100})
        receive(self.clients[1], 'disconnected')


class GarbageTests(unittest.TestCase):
    def test_garbage_pushes_blocks_up_and_has_one_hole(self):
        state = GameState()
        state.locked_positions[(0, 10)] = (255, 0, 0)
        state.add_garbage([3, 7])
        self.assertEqual(state.locked_positions[(0, 8)], (255, 0, 0))
        for row, hole in ((18, 3), (19, 7)):
            self.assertNotIn((hole, row), state.locked_positions)
            self.assertEqual(sum((x, row) in state.locked_positions for x in range(10)), 9)

    def test_garbage_overflow_loses_game(self):
        state = GameState()
        state.locked_positions[(0, 0)] = (255, 0, 0)
        state.add_garbage([5])
        self.assertTrue(state.lost())


if __name__ == '__main__':
    unittest.main()
