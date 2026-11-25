import time
import unittest

from tetris.network.client import Client
from tetris.network.server import Server
from tetris.network.protocol import Decoder, encode, MAX_PLAYERS
from tetris.core.state import GameState
from tetris.core.sequence import PieceSequence


def receive(client, kind, where=lambda message: True):
    # Guarda o que ainda não foi consumido: poll() pode trazer várias mensagens.
    backlog = client.__dict__.setdefault('backlog', [])
    deadline = time.monotonic() + 4
    while time.monotonic() < deadline:
        backlog.extend(client.poll())
        for message in backlog:
            if message['type'] == kind and where(message):
                backlog.remove(message)
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


class RoomTestCase(unittest.TestCase):
    names = ['Ana', 'Bia']

    def setUp(self):
        self.server = Server(0, host='127.0.0.1')
        self.clients = []
        for count, name in enumerate(self.names, 1):
            self.clients.append(Client('127.0.0.1', self.server.port, name))
            # Espera cada um aparecer na sala para a ordem dos jogadores ser a da lista.
            self.lobby = receive(self.clients[-1], 'lobby', lambda m: len(m['players']) == count)

    def start(self):
        self.server.start_game()
        return [receive(client, 'start') for client in self.clients]

    def tearDown(self):
        for client in self.clients:
            client.close()
        self.server.close()


class NetworkTests(RoomTestCase):
    def test_seed_names_attacks_board_and_result(self):
        starts = self.start()
        self.assertEqual(starts[0]['seed'], starts[1]['seed'])
        self.assertEqual([start['player'] for start in starts], [0, 1])
        self.assertEqual(starts[1]['names'], ['Ana', 'Bia'])
        first = GameState(PieceSequence(starts[0]['seed']))
        second = GameState(PieceSequence(starts[1]['seed']))
        self.assertEqual(first.current_piece.shape, second.current_piece.shape)
        for count in (1, 2, 4):
            self.clients[0].send({'type': 'attack', 'lines': count})
            holes = receive(self.clients[1], 'garbage')['holes']
            self.assertEqual(len(holes), count)
            self.assertTrue(all(0 <= hole < 10 for hole in holes))
        self.clients[0].send({'type': 'board', 'grid': first.grid, 'score': 20})
        board = receive(self.clients[1], 'board')
        self.assertEqual((board['player'], board['score']), (0, 20))
        self.clients[1].send({'type': 'board', 'grid': second.grid, 'score': 50})
        receive(self.clients[0], 'board')
        self.clients[0].send({'type': 'game_over', 'score': 30})
        ranking = [{'player': 1, 'name': 'Bia', 'score': 50}, {'player': 0, 'name': 'Ana', 'score': 30}]
        for client, won in zip(self.clients, (False, True)):
            result = receive(client, 'result')
            self.assertEqual(result['won'], won)
            self.assertEqual(result['ranking'], ranking)

    def test_port_can_be_hosted_again_right_after_a_match(self):
        self.start()
        self.clients[0].send({'type': 'game_over', 'score': 0})
        receive(self.clients[1], 'result')
        self.server.close()
        Server(self.server.port, host='127.0.0.1').close()

    def test_player_who_disconnects_loses(self):
        self.start()
        self.clients[0].close()
        result = receive(self.clients[1], 'result')
        self.assertTrue(result['won'])
        self.assertEqual([entry['name'] for entry in result['ranking']], ['Bia', 'Ana'])

    def test_invalid_attack_removes_sender(self):
        self.start()
        self.clients[0].send({'type': 'attack', 'lines': 100})
        self.assertTrue(receive(self.clients[1], 'result')['won'])
        receive(self.clients[0], 'disconnected')


class LobbyTests(RoomTestCase):
    names = ['Ana', 'ana', 'Bia']

    def test_lobby_lists_players_with_unique_names(self):
        self.assertEqual(self.lobby, {'type': 'lobby', 'players': ['Ana', 'ana (2)', 'Bia'], 'you': 2})

    def test_leaving_updates_lobby_and_start_needs_two_players(self):
        self.clients[2].close()
        self.clients[1].close()
        receive(self.clients[0], 'lobby', lambda m: m['players'] == ['Ana'])
        self.server.start_game()
        time.sleep(0.4)
        self.assertFalse(any(m['type'] == 'start' for m in self.clients[0].poll()))
        late = Client('127.0.0.1', self.server.port, 'Caio')
        self.clients.append(late)
        receive(late, 'lobby')
        self.server.start_game()
        self.assertEqual(receive(late, 'start')['names'], ['Ana', 'Caio'])

    def test_full_room_refuses_new_player(self):
        for number in range(len(self.clients), MAX_PLAYERS):
            self.clients.append(Client('127.0.0.1', self.server.port, f'J{number}'))
        receive(self.clients[0], 'lobby', lambda m: len(m['players']) == MAX_PLAYERS)
        extra = Client('127.0.0.1', self.server.port, 'G')
        self.clients.append(extra)
        self.assertEqual(receive(extra, 'error')['message'], 'A sala está cheia.')

    def test_three_players_are_ranked_by_elimination(self):
        self.start()
        self.clients[1].send({'type': 'game_over', 'score': 10})
        for client in (self.clients[0], self.clients[2]):
            self.assertEqual(receive(client, 'eliminated')['player'], 1)
        # O eliminado não ataca nem é alvo: o lixo só vai para quem ainda joga.
        self.clients[1].send({'type': 'attack', 'lines': 4})
        for _ in range(5):
            self.clients[0].send({'type': 'attack', 'lines': 1})
            receive(self.clients[2], 'garbage')
        self.clients[2].send({'type': 'game_over', 'score': 40})
        result = receive(self.clients[1], 'result')
        self.assertFalse(result['won'])
        self.assertEqual([entry['name'] for entry in result['ranking']], ['Ana', 'Bia', 'ana (2)'])
        self.assertTrue(receive(self.clients[0], 'result')['won'])
        self.assertFalse(any(m['type'] == 'garbage' for m in self.clients[1].poll() + self.clients[0].poll()))


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
