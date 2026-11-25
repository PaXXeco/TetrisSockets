import unittest

from tetris.core.sequence import PieceSequence
from tetris.core.state import GameState


class HoldTests(unittest.TestCase):
    def setUp(self):
        self.state = GameState(PieceSequence(seed=42))

    def test_first_hold_stores_piece_and_takes_next_from_queue(self):
        state = self.state
        shape, next_piece = state.current_piece.shape, state.next_piece
        self.assertTrue(state.hold())
        self.assertIs(state.hold_piece.shape, shape)
        self.assertIs(state.current_piece, next_piece)
        self.assertEqual(len(state.next_pieces), 5)

    def test_hold_is_blocked_until_piece_locks_then_swaps(self):
        state = self.state
        first = state.current_piece.shape
        state.hold()
        second = state.current_piece.shape
        self.assertFalse(state.hold())
        self.assertIs(state.hold_piece.shape, first)

        state.hard_drop()
        self.assertFalse(state.hold())  # peça já travando
        state.update()
        third, queue = state.current_piece.shape, list(state.next_pieces)
        self.assertTrue(state.hold())
        self.assertIs(state.current_piece.shape, first)
        self.assertIs(state.hold_piece.shape, third)
        self.assertEqual(list(state.next_pieces), queue)
        self.assertIsNot(second, None)

    def test_held_piece_returns_to_spawn_position_and_rotation(self):
        state = self.state
        state.move(-2, 0)
        state.move(0, 3)
        state.rotate()
        state.hold()
        held = state.hold_piece
        self.assertEqual((held.x, held.y, held.rotation), (5, 0, 0))

    def test_swap_into_blocked_spawn_ends_the_game(self):
        state = self.state
        state.hold()
        state.hard_drop()
        state.update()
        state.locked_positions.update({(x, y): (100, 100, 100) for x in range(3, 8) for y in range(3)})
        state.hold()
        self.assertTrue(state.lost())


if __name__ == '__main__':
    unittest.main()
