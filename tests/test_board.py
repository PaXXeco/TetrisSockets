import unittest

from tetris.core.board import clear_rows, create_grid
from tetris.config import columns


class ClearRowsTests(unittest.TestCase):
    def test_blocks_fall_by_number_of_cleared_rows_below(self):
        red = (255, 0, 0)
        blue = (0, 0, 255)
        for cleared in ((), (19,), (18, 19), (17, 19), (16, 17, 18, 19)):
            with self.subTest(cleared=cleared):
                locked = {(x, y): red for y in cleared for x in range(columns)}
                blocks = {(0, y): blue for y in (-1, 10, 16, 17, 18, 19)
                          if y not in cleared}
                locked.update(blocks)
                original = locked
                count = clear_rows(create_grid(locked), locked)
                expected = {(x, y + sum(row > y for row in cleared)): color
                            for (x, y), color in blocks.items()}
                self.assertEqual(count, len(cleared))
                self.assertEqual(locked, expected)
                self.assertIs(locked, original)


if __name__ == '__main__':
    unittest.main()
