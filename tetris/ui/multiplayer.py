import socket
from ipaddress import IPv4Address

import pygame

from tetris.ui import layout

from tetris.settings import load_port
from tetris.ui.render import draw_centered_text
from tetris.network.client import Client
from tetris.network.server import Server


def local_addresses():
    try:
        addresses = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
        return sorted({item[4][0] for item in addresses
                       if not item[4][0].startswith('127.')})
    except OSError:
        return []


def multiplayer_menu(win, hosting=False):
    resources = {}
    try:
        return _room(win, hosting, resources)
    finally:
        if resources.get('client'):
            resources['client'].close()
        if resources.get('server'):
            resources['server'].close()


def _room(win, hosting, resources):
    from tetris.ui.menu import draw_button
    from tetris.ui.game import main

    clock = pygame.time.Clock()
    port = load_port()
    addresses = local_addresses() if hosting else []
    value = ''
    active = True
    selected = False
    status = ''

    def connect():
        nonlocal status
        if resources.get('client'):
            return
        try:
            if hosting:
                resources['server'] = Server(port)
                address = '127.0.0.1'
            else:
                address = str(IPv4Address(value))
            resources['client'] = Client(address, port)
            status = 'Conectando…'
        except ValueError:
            status = 'Informe um IPv4 válido, como 192.168.1.10.'
        except OSError:
            status = 'Não foi possível hospedar. Verifique a porta configurada.'

    while True:
        clock.tick(60)
        connection = resources.get('client')
        if connection:
            for message in connection.poll():
                if message.get('type') == 'waiting':
                    status = 'Aguardando o outro jogador…'
                elif message.get('type') == 'start':
                    return main(win, connection, message['seed'])
                elif message.get('type') in ('error', 'disconnected'):
                    status = message.get('message', 'Conexão encerrada. Tente novamente.')
                    connection.close()
                    resources.pop('client', None)
                    server = resources.pop('server', None)
                    if server:
                        server.close()
        factor = layout.scale(win)
        font = layout.font(max(1, round(28 * factor)))
        field = layout.rect(win, 240, 372, 320, 56)
        back = layout.rect(win, 280, 695, 240, 56)
        start = layout.rect(win, 280, 605, 240, 56)
        win.fill((0, 0, 0))
        draw_centered_text(win, 'Criar partida' if hosting else 'Entrar na partida',
                           layout.rect(win, 20, 100, 760, 80), 48)
        if hosting:
            draw_centered_text(win, 'Passe seu IP ao outro jogador na mesma rede:',
                               layout.rect(win, 20, 220, 760, 40), 26)
            # Mais de uma interface pode estar ativa (Wi-Fi, cabo ou VPN).
            text = ' / '.join(addresses) if addresses else 'IP local não encontrado'
            draw_centered_text(win, text, field, 32)
            draw_centered_text(win, 'Use o IP da rede compartilhada pelos dois computadores.',
                               layout.rect(win, 20, 438, 760, 35), 22)
        else:
            draw_centered_text(win, 'IP do computador que vai hospedar',
                               field.move(0, round(-65 * factor)), 26)
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
                           layout.rect(win, 20, 493, 760, 35), 24)
        draw_button(win, back, 'Voltar', back.collidepoint(pygame.mouse.get_pos()))
        draw_button(win, start, 'Hospedar' if hosting else 'Conectar',
                    start.collidepoint(pygame.mouse.get_pos()), enabled=not resources.get('client'))
        draw_centered_text(win, status, layout.rect(win, 20, 545, 760, 40), 24)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    return True
                if start.collidepoint(event.pos):
                    connect()
                active = field.collidepoint(event.pos)
                selected = active
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
                if event.key == pygame.K_RETURN:
                    connect()
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
