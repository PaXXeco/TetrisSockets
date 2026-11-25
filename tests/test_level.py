import unittest

from tetris.core.sequence import PieceSequence
from tetris.core.state import GameState
from tetris.config import rows, columns


class LevelTests(unittest.TestCase):
    def test_level_rises_every_100_points_and_speeds_up_to_a_limit(self):
        state = GameState(PieceSequence(seed=42))
        self.assertEqual((state.level, state.fall_speed), (1, 0.27))
        speeds = []
        for score, level in ((90, 1), (100, 2), (250, 3), (1100, 12), (5000, 51)):
            state.score = score
            self.assertEqual(state.level, level)
            speeds.append(state.fall_speed)
        self.assertEqual(speeds[0], 0.27)
        self.assertEqual(speeds, sorted(speeds, reverse=True))
        self.assertEqual(speeds[-2:], [0.05, 0.05])

    def test_clearing_lines_raises_the_level(self):
        state = GameState(PieceSequence(seed=42))
        state.score = 90
        # Uma linha quase cheia: o que faltar é completado pela peça que travar.
        state.locked_positions.update({(x, rows - 1): (100, 100, 100) for x in range(columns)})
        state.refresh_grid()
        state.hard_drop()
        state.update()
        self.assertEqual((state.score, state.level), (100, 2))


if __name__ == '__main__':
    unittest.main()
