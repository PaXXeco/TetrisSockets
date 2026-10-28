import socket

import pygame

from tetris.settings import load_port
from tetris.ui.render import draw_centered_text


def local_addresses():
    try:
        addresses = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
        return sorted({item[4][0] for item in addresses
                       if not item[4][0].startswith('127.')})
    except OSError:
        return []


def multiplayer_menu(win, hosting=False):
    from tetris.ui.menu import draw_button, FONT_NAME

    width, height = win.get_size()
    field = pygame.Rect(width // 2 - 160, height // 2 - 40, 320, 56)
    back = pygame.Rect(width // 2 - 120, height - 130, 240, 56)
    font = pygame.font.SysFont(FONT_NAME, 28)
    clock = pygame.time.Clock()
    port = load_port()
    addresses = local_addresses() if hosting else []
    value = ''
    active = True
    selected = False

    while True:
        clock.tick(60)
        win.fill((0, 0, 0))
        draw_centered_text(win, 'Criar partida' if hosting else 'Entrar na partida',
                           pygame.Rect(20, 100, width - 40, 80), 48)
        if hosting:
            draw_centered_text(win, 'Passe seu IP ao outro jogador na mesma rede:',
                               pygame.Rect(20, 220, width - 40, 40), 26)
            # Mais de uma interface pode estar ativa (Wi-Fi, cabo ou VPN).
            text = ' / '.join(addresses) if addresses else 'IP local não encontrado'
            draw_centered_text(win, text, field, 32)
            draw_centered_text(win, 'Use o IP da rede compartilhada pelos dois computadores.',
                               pygame.Rect(20, field.bottom + 10, width - 40, 35), 22)
        else:
            draw_centered_text(win, 'IP do computador que vai hospedar',
                               field.move(0, -65), 26)
            pygame.draw.rect(win, (22, 22, 30), field, border_radius=6)
            pygame.draw.rect(win, (155, 155, 170) if active else (65, 65, 80),
                             field, 1, border_radius=6)
            label = font.render(value, True, (240, 240, 245))
            rect = label.get_rect(center=field.center)
            if active and selected:
                pygame.draw.rect(win, (65, 65, 95), rect.inflate(6, 4))
            win.blit(label, rect)
            if active and not selected and pygame.time.get_ticks() % 1000 < 500:
                pygame.draw.line(win, (240, 240, 245), rect.topright, rect.bottomright)

        draw_centered_text(win, f'Porta: {port} (definida em Configurações)',
                           pygame.Rect(20, field.bottom + 65, width - 40, 35), 24)
        draw_button(win, back, 'Voltar', back.collidepoint(pygame.mouse.get_pos()))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    return True
                active = field.collidepoint(event.pos)
                selected = active
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
                if not hosting and active:
                    if event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
                        selected = True
                    elif event.key == pygame.K_BACKSPACE:
                        value = '' if selected else value[:-1]
                        selected = False
                    elif event.unicode and all(c in '0123456789.' for c in event.unicode):
                        candidate = event.unicode if selected else value + event.unicode
                        if len(candidate) <= 15:
                            value = candidate
                            selected = False
