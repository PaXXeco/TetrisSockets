import os
import unittest
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame

from tetris.core.state import GameState
from tetris.ui import layout
from tetris.ui.menu import main_menu
from tetris.ui.multiplayer import multiplayer_menu
from tetris.ui.settings import settings_menu
from tetris.ui.render import draw_window, draw_next_shapes


class ResizeTests(unittest.TestCase):
    def test_layout_and_screens_follow_window_size(self):
        pygame.font.init()
        state = GameState()
        try:
            for size in ((800, 825), (1600, 1650), (1920, 1080), (480, 600)):
                with self.subTest(size=size):
                    win = pygame.display.set_mode(size, pygame.RESIZABLE)
                    bounds = layout.rect(win, 0, 0, 800, 825)
                    self.assertTrue(win.get_rect().contains(bounds))
                    self.assertAlmostEqual(bounds.width / bounds.height, 800 / 825, places=2)
                    draw_window(win, state.grid)
                    draw_next_shapes(state.next_pieces, win)
                    # Each screen draws at the new resolution before handling Quit.
                    with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.QUIT)]):
                        self.assertFalse(settings_menu(win))
                        self.assertFalse(multiplayer_menu(win))
                        with patch('tetris.ui.multiplayer.local_addresses', return_value=['192.168.1.10']):
                            self.assertFalse(multiplayer_menu(win, hosting=True))
                        main_menu(win, lambda surface: None)
        finally:
            pygame.display.quit()


if __name__ == '__main__':
    unittest.main()
