from itertools import islice
import unittest

from tetris.core.sequence import PieceSequence
from tetris.core.shapes import shapes
from tetris.core.state import GameState


class PieceSequenceTests(unittest.TestCase):
    def test_each_bag_contains_all_seven_types(self):
        pieces = list(islice(PieceSequence(seed=42), 140))
        for start in range(0, len(pieces), 7):
            self.assertEqual(sorted(pieces[start:start + 7]), list(range(7)))

    def test_readers_consume_same_sequence_at_different_speeds(self):
        sequence = PieceSequence(seed=42)
        fast = iter(sequence)
        expected = list(islice(fast, 30))
        slow = iter(sequence)
        self.assertEqual(list(islice(slow, 4)), expected[:4])
        expected.extend(islice(fast, 30))
        self.assertEqual(list(islice(slow, 56)), expected[4:])

    def test_seed_reproduces_sequence(self):
        first = list(islice(PieceSequence(seed=42), 70))
        second = list(islice(PieceSequence(seed=42), 70))
        self.assertEqual(first, second)

    def test_game_states_keep_independent_pieces_and_progress(self):
        sequence = PieceSequence(seed=42)
        fast = GameState(sequence)
        slow = GameState(sequence)
        self.assertEqual(fast.current_piece.shape, slow.current_piece.shape)
        self.assertEqual(fast.next_piece.shape, slow.next_piece.shape)
        self.assertIsNot(fast.current_piece, slow.current_piece)
        self.assertIsNot(fast.next_piece, slow.next_piece)
        fast.current_piece.x = 2
        fast.current_piece.rotation = 1
        self.assertEqual(slow.current_piece.x, 5)
        self.assertEqual(slow.current_piece.rotation, 0)

        def advance(state):
            # Tabuleiro vazio para verificar várias sacolas sem encerrar a partida.
            state.locked_positions.clear()
            state.refresh_grid()
            while not state.change_piece:
                state.fall()
            state.update()
            return state.current_piece.shape

        expected = [advance(fast) for _ in range(20)]
        self.assertEqual([advance(slow) for _ in range(20)], expected)

    def test_preview_queue_matches_pieces_played_and_refills(self):
        sequence = PieceSequence(seed=42)
        expected = list(islice(sequence, 30))
        state = GameState(sequence)
        for index in range(24):
            self.assertEqual(state.current_piece.shape, shapes[expected[index]])
            self.assertEqual([piece.shape for piece in state.next_pieces],
                             [shapes[kind] for kind in expected[index + 1:index + 6]])
            self.assertIs(state.next_piece, state.next_pieces[0])
            next_piece = state.next_piece
            state.locked_positions.clear()
            state.refresh_grid()
            while not state.change_piece:
                state.fall()
            state.update()
            self.assertIs(state.current_piece, next_piece)


if __name__ == '__main__':
    unittest.main()
