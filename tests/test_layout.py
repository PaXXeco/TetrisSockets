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
from tetris.ui.render import draw_window, draw_next_shapes, draw_hold, draw_opponents, draw_leaderboard
from tetris.ui.game import main, opponents_width


class ResizeTests(unittest.TestCase):
    def test_network_game_renders_and_sends_board_after_hard_drop(self):
        pygame.font.init()
        win = pygame.display.set_mode((800, 825))
        connection = Mock()
        connection.poll.return_value = [{'type': 'board', 'score': 10, 'player': 1,
                                         'grid': [[[0, 0, 0] for _ in range(10)] for _ in range(20)]},
                                        {'type': 'eliminated', 'player': 2},
                                        {'type': 'garbage', 'holes': [3]}]
        clock = Mock()
        clock.tick.return_value = 100
        try:
            with patch('pygame.time.Clock', return_value=clock), patch('pygame.event.get', side_effect=[
                    [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)],
                    [pygame.event.Event(pygame.QUIT)]]):
                self.assertFalse(main(win, connection, 42, ['Ana', 'Bia', 'Caio'], 0))
            # A coluna extra dos adversários só existe durante a partida.
            self.assertEqual(layout.extra_width, 0)
            self.assertEqual(win.get_size(), (800, 825))
            sent = [call.args[0] for call in connection.send.call_args_list]
            self.assertEqual(sent[0]['type'], 'board')
            self.assertTrue(any(cell != (0, 0, 0) for row in sent[0]['grid'] for cell in row))
        finally:
            pygame.display.quit()

    def test_result_waits_for_key_and_shows_leaderboard(self):
        pygame.font.init()
        win = pygame.display.set_mode((800, 825))
        connection = Mock()
        ranking = [{'player': 1, 'name': 'Bia', 'score': 50}, {'player': 0, 'name': 'Ana', 'score': 30}]
        connection.poll.side_effect = [[{'type': 'result', 'won': False, 'ranking': ranking}], [], []]
        try:
            with patch('pygame.event.get', side_effect=[
                    [], [], [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)]]), \
                    patch('tetris.ui.game.draw_leaderboard') as leaderboard:
                self.assertTrue(main(win, connection, 42, ['Ana', 'Bia'], 0))
            self.assertEqual(leaderboard.call_args.args[1:], ('Você perdeu!', ranking, 0))
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
                    draw_hold(win, state.current_piece, False)
                    for count in range(1, 10):
                        layout.extra_width = opponents_width(count)
                        draw_opponents(win, [{'name': 'Bia', 'score': 10, 'out': count % 2,
                                              'grid': state.grid}] * count)
                    draw_leaderboard(win, 'Você venceu!', [{'player': 0, 'name': 'Ana', 'score': 5}], 0)
                    layout.extra_width = 0
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
