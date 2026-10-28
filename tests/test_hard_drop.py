import unittest

from tetris.core.board import valid_space
from tetris.core.piece import convert_shape_format
from tetris.core.sequence import PieceSequence
from tetris.core.state import GameState
from tetris.config import rows, columns


class HardDropTests(unittest.TestCase):
    def test_drop_stops_at_floor_or_stack_and_locks_on_update(self):
        for obstacle in (False, True):
            with self.subTest(obstacle=obstacle):
                state = GameState(PieceSequence(seed=42))
                if obstacle:
                    state.locked_positions.update(
                        {(x, rows - 5): (100, 100, 100) for x in range(columns)})
                piece = state.current_piece
                next_piece = state.next_piece
                state.hard_drop()
                self.assertTrue(state.change_piece)
                self.assertTrue(valid_space(piece, state.grid))
                piece.y += 1
                self.assertFalse(valid_space(piece, state.grid))
                piece.y -= 1
                positions = convert_shape_format(piece)
                state.update()
                self.assertIs(state.current_piece, next_piece)
                self.assertFalse(state.change_piece)
                # A linha completa usada como obstáculo é removida no update.
                shift = 1 if obstacle else 0
                for x, y in positions:
                    self.assertEqual(state.locked_positions[(x, y + shift)], piece.color)


if __name__ == '__main__':
    unittest.main()
