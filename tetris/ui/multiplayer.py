import socket
from ipaddress import IPv4Address

import pygame

from tetris.ui import layout

from tetris.settings import load_port, load_name, save_name
from tetris.ui.render import draw_centered_text
from tetris.network.client import Client
from tetris.network.server import Server
from tetris.network.protocol import clean_name, MAX_NAME, MAX_PLAYERS

MUTED = (155, 155, 170)


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
    values = {'name': load_name(), 'ip': ''}
    limits = {'name': MAX_NAME, 'ip': 15}
    focus = 'name' if hosting or not values['name'] else 'ip'
    selected = False
    status = ''
    lobby = None  # nomes dos jogadores na sala, depois de entrar
    you = None

    def leave():
        nonlocal lobby
        lobby = None
        client = resources.pop('client', None)
        if client:
            client.close()
        server = resources.pop('server', None)
        if server:
            server.close()

    def connect():
        nonlocal status
        if resources.get('client'):
            return
        name = clean_name(values['name'])
        if not name:
            status = 'Informe seu nome.'
            return
        try:
            address = '127.0.0.1' if hosting else str(IPv4Address(values['ip']))
        except ValueError:
            status = 'Informe um IPv4 válido, como 192.168.1.10.'
            return
        try:
            save_name(name)
        except OSError:
            pass
        try:
            if hosting:
                resources['server'] = Server(port)
            resources['client'] = Client(address, port, name)
            status = 'Conectando…'
        except OSError:
            status = 'Não foi possível hospedar. Verifique a porta configurada.'

    def draw_field(key, label, field):
        active = focus == key
        draw_centered_text(win, label, field.move(0, round(-50 * factor)), 26)
        pygame.draw.rect(win, (22, 22, 30), field, border_radius=6)
        pygame.draw.rect(win, MUTED if active else (65, 65, 80), field, 1, border_radius=6)
        text = font.render(values[key], True, (240, 240, 245))
        rect = text.get_rect(center=field.center)
        if active and selected:
            pygame.draw.rect(win, (65, 65, 95), rect.inflate(6, 4))
        win.blit(text, rect)
        if active and not selected and pygame.time.get_ticks() % 1000 < 500:
            pygame.draw.line(win, (240, 240, 245), rect.topright, rect.bottomright)

    while True:
        clock.tick(60)
        connection = resources.get('client')
        if connection:
            for message in connection.poll():
                kind = message.get('type')
                if kind == 'lobby' and isinstance(message.get('players'), list):
                    lobby, you = [str(name) for name in message['players']], message.get('you')
                    status = ''
                elif kind == 'start':
                    return main(win, connection, message['seed'], message.get('names'),
                                message.get('player', 0))
                elif kind in ('error', 'disconnected'):
                    status = message.get('message', 'Conexão encerrada. Tente novamente.')
                    leave()
                    break
        factor = layout.scale(win)
        font = layout.font(max(1, round(28 * factor)))
        fields = {'name': layout.rect(win, 240, 262, 320, 56)}
        if not hosting:
            fields['ip'] = layout.rect(win, 240, 392, 320, 56)
        back = layout.rect(win, 280, 705, 240, 56)
        start = layout.rect(win, 280, 633, 240, 56)
        can_start = hosting and lobby is not None and len(lobby) >= 2
        mouse = pygame.mouse.get_pos()
        win.fill((0, 0, 0))
        if lobby is None:
            draw_centered_text(win, 'Criar partida' if hosting else 'Entrar na partida',
                               layout.rect(win, 20, 100, 760, 80), 48)
            draw_field('name', 'Seu nome', fields['name'])
            if not hosting:
                draw_field('ip', 'IP do computador que vai hospedar', fields['ip'])
            draw_centered_text(win, f'Porta: {port} (definida em Configurações)',
                               layout.rect(win, 20, 493, 760, 35), 24)
            draw_centered_text(win, status, layout.rect(win, 20, 560, 760, 40), 24)
            draw_button(win, start, 'Criar sala' if hosting else 'Conectar',
                        start.collidepoint(mouse), enabled=not connection)
            draw_button(win, back, 'Voltar', back.collidepoint(mouse))
        else:
            draw_centered_text(win, 'Sala', layout.rect(win, 20, 70, 760, 80), 48)
            if hosting:
                # Mais de uma interface pode estar ativa (Wi-Fi, cabo ou VPN).
                text = ' / '.join(addresses) if addresses else 'IP local não encontrado'
                draw_centered_text(win, f'Passe seu IP aos outros jogadores: {text}',
                                   layout.rect(win, 20, 160, 760, 35), 24)
                draw_centered_text(win, f'Porta: {port}', layout.rect(win, 20, 197, 760, 30), 22, MUTED)
            panel = layout.rect(win, 220, 245, 360, 55 + 28 * MAX_PLAYERS)
            pygame.draw.rect(win, (22, 22, 30), panel, border_radius=12)
            draw_centered_text(win, f'Jogadores ({len(lobby)}/{MAX_PLAYERS})',
                               layout.rect(win, 220, 255, 360, 35), 24, MUTED)
            for index, name in enumerate(lobby):
                mine = index == you
                draw_centered_text(win, f'{name} (você)' if mine else name,
                                   layout.rect(win, 240, 293 + 28 * index, 320, 28), 22,
                                   (255, 215, 90) if mine else (240, 240, 245))
            if not hosting:
                status = 'Aguardando o host iniciar a partida…'
            elif not can_start:
                status = 'Aguardando outros jogadores…'
            else:
                status = 'Inicie quando todos estiverem na sala.'
            draw_centered_text(win, status, layout.rect(win, 20, 590, 760, 35), 24)
            if hosting:
                draw_button(win, start, 'Iniciar partida', start.collidepoint(mouse), enabled=can_start)
            draw_button(win, back, 'Sair da sala', back.collidepoint(mouse))
        pygame.display.update()

        def confirm():
            if lobby is None:
                connect()
            elif can_start:
                resources['server'].start_game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    return True
                if start.collidepoint(event.pos):
                    confirm()
                focus = next((key for key, field in fields.items() if field.collidepoint(event.pos)), None)
                selected = focus is not None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
                if event.key == pygame.K_RETURN:
                    confirm()
                elif event.key == pygame.K_TAB and not hosting:
                    focus, selected = ('ip' if focus == 'name' else 'name'), True
                elif focus and not connection:
                    value = values[focus]
                    typed = event.unicode
                    allowed = (typed.isprintable() if focus == 'name'
                               else all(c in '0123456789.' for c in typed))
                    if event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
                        selected = True
                    elif event.key == pygame.K_BACKSPACE:
                        values[focus] = '' if selected else value[:-1]
                        selected = False
                    elif typed and allowed:
                        candidate = typed if selected else value + typed
                        if len(candidate) <= limits[focus]:
                            values[focus] = candidate
                            selected = False
