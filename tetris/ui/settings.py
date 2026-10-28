import pygame

from tetris.ui import layout

from tetris.settings import load_port, save_port
from tetris.ui.render import draw_centered_text


def settings_menu(win):
    # Import local evita dependência circular com o menu principal.
    from tetris.ui.menu import draw_button

    value = str(load_port())
    active = True
    selected = True
    message = ''
    message_color = (240, 240, 245)
    clock = pygame.time.Clock()

    def persist():
        nonlocal message, message_color
        try:
            save_port(int(value) if value else 0)
            message = 'Porta salva.'
            message_color = (120, 220, 160)
        except ValueError:
            message = 'Informe uma porta entre 1 e 65535.'
            message_color = (255, 140, 140)
        except OSError:
            message = 'Não foi possível salvar a configuração.'
            message_color = (255, 140, 140)

    while True:
        clock.tick(60)
        factor = layout.scale(win)
        font = layout.font(max(1, round(28 * factor)))
        field = layout.rect(win, 280, 382, 240, 56)
        save = layout.rect(win, 280, 482, 240, 56)
        back = layout.rect(win, 280, 554, 240, 56)
        win.fill((0, 0, 0))
        draw_centered_text(win, 'Configurações', layout.rect(win, 20, 100, 760, 80), 48)
        draw_centered_text(win, 'Porta de rede', field.move(0, round(-60 * factor)), 28)
        draw_centered_text(win, 'Usada para criar e entrar em partidas.',
                           layout.rect(win, 20, 282, 760, 30), 22)
        pygame.draw.rect(win, (22, 22, 30), field, border_radius=6)
        pygame.draw.rect(win, (155, 155, 170) if active else (65, 65, 80), field, 1, border_radius=6)
        text = font.render(value, True, (240, 240, 245))
        text_rect = text.get_rect(center=field.center)
        if active and selected:
            pygame.draw.rect(win, (65, 65, 95), text_rect.inflate(6, 4))
        win.blit(text, text_rect)
        if active and not selected and pygame.time.get_ticks() % 1000 < 500:
            pygame.draw.line(win, (240, 240, 245), text_rect.topright, text_rect.bottomright)
        draw_centered_text(win, message, layout.rect(win, 20, 448, 760, 30), 20, message_color)
        mouse = pygame.mouse.get_pos()
        draw_button(win, save, 'Salvar', save.collidepoint(mouse))
        draw_button(win, back, 'Voltar', back.collidepoint(mouse))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                active = field.collidepoint(event.pos)
                selected = active
                if back.collidepoint(event.pos):
                    return True
                if save.collidepoint(event.pos):
                    persist()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
                if event.key == pygame.K_RETURN:
                    persist()
                elif active:
                    if event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
                        selected = True
                    elif event.key == pygame.K_BACKSPACE:
                        value = '' if selected else value[:-1]
                        selected = False
                        message = ''
                    elif event.unicode and all(char in '0123456789' for char in event.unicode):
                        candidate = event.unicode if selected else value + event.unicode
                        if len(candidate) <= 5:
                            value = candidate
                            selected = False
                            message = ''
