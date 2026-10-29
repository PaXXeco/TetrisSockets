import pygame

from tetris.ui import layout
from tetris.ui.settings import settings_menu
from tetris.ui.multiplayer import multiplayer_menu

FONT_NAME = 'comicsans,liberationsans'

button_width = 240
button_height = 56
button_color = (22, 22, 30)
button_hover_color = (38, 38, 48)


def draw_button(surface, rect, text, hover, enabled=True):
    hover = hover and enabled
    color = button_hover_color if hover else button_color
    pygame.draw.rect(surface, color, rect, border_radius=6)
    border_color = (155, 155, 170) if hover else (65, 65, 80)
    pygame.draw.rect(surface, border_color, rect, 1, border_radius=6)

    text_color = (240, 240, 245) if enabled else (120, 120, 135)
    layout.text(surface, text, rect, 28, text_color)


# start_game é a função que roda o jogo (recebe a janela)
def main_menu(win, start_game):
    clock = pygame.time.Clock()
    screen = 'home'

    run = True
    while run:
        clock.tick(60)
        win.fill((0, 0, 0))

        button = layout.rect(win, 280, 412, 240, 56)
        single_player = button.copy()
        settings_button = layout.rect(win, 280, 484, 240, 56)
        exit_button = layout.rect(win, 280, 556, 240, 56)
        multiplayer = settings_button.copy()
        back = layout.rect(win, 280, 586, 240, 56)
        layout.text(win, 'TetrisSockets', layout.rect(win, 20, 180, 760, 100), 80, bold=True)

        mouse = pygame.mouse.get_pos()
        if screen == 'modes':
            draw_button(win, single_player, 'Um jogador', single_player.collidepoint(mouse))
            draw_button(win, multiplayer, 'Multijogador', multiplayer.collidepoint(mouse))
            draw_button(win, back, 'Voltar', back.collidepoint(mouse))
        elif screen == 'multiplayer':
            draw_button(win, single_player, 'Criar partida', single_player.collidepoint(mouse))
            draw_button(win, multiplayer, 'Entrar na partida', multiplayer.collidepoint(mouse))
            draw_button(win, back, 'Voltar', back.collidepoint(mouse))
        else:
            draw_button(win, button, 'Jogar', button.collidepoint(mouse))
            draw_button(win, settings_button, 'Configurações', settings_button.collidepoint(mouse))
            draw_button(win, exit_button, 'Sair', exit_button.collidepoint(mouse))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                screen = 'modes' if screen == 'multiplayer' else 'home'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if screen == 'home' and button.collidepoint(event.pos):
                    screen = 'modes'
                elif screen == 'home' and settings_button.collidepoint(event.pos):
                    run = settings_menu(win)
                    break
                elif screen == 'home' and exit_button.collidepoint(event.pos):
                    run = False
                    break
                elif screen != 'home' and back.collidepoint(event.pos):
                    screen = 'modes' if screen == 'multiplayer' else 'home'
                elif screen == 'modes' and multiplayer.collidepoint(event.pos):
                    screen = 'multiplayer'
                elif screen == 'modes' and single_player.collidepoint(event.pos):
                    run = start_game(win)
                    break
                elif screen == 'multiplayer' and single_player.collidepoint(event.pos):
                    run = multiplayer_menu(win, hosting=True)
                    break
                elif screen == 'multiplayer' and multiplayer.collidepoint(event.pos):
                    run = multiplayer_menu(win)
                    break

    pygame.display.quit()
