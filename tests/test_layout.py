import os
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame

from tetris.core.state import GameState
from tetris.ui import layout
from tetris.ui.menu import main_menu
from tetris.ui.multiplayer import multiplayer_menu
from tetris.ui.settings import settings_menu
from tetris.ui.render import draw_window, draw_next_shapes
from tetris.ui.game import main


class ResizeTests(unittest.TestCase):
    def test_network_game_renders_and_sends_board_after_hard_drop(self):
        pygame.font.init()
        win = pygame.display.set_mode((800, 825))
        connection = Mock()
        connection.poll.return_value = [{'type': 'board', 'score': 10,
                                         'grid': [[[0, 0, 0] for _ in range(10)] for _ in range(20)]},
                                        {'type': 'garbage', 'holes': [3]}]
        clock = Mock()
        clock.tick.return_value = 100
        try:
            with patch('pygame.time.Clock', return_value=clock), patch('pygame.event.get', side_effect=[
                    [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)],
                    [pygame.event.Event(pygame.QUIT)]]):
                self.assertFalse(main(win, connection, seed=42))
            sent = [call.args[0] for call in connection.send.call_args_list]
            self.assertEqual(sent[0]['type'], 'board')
            self.assertTrue(any(cell != (0, 0, 0) for row in sent[0]['grid'] for cell in row))
        finally:
            pygame.display.quit()

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
