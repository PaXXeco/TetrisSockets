import pygame

from tetris.ui.render import (draw_window, draw_next_shapes, draw_hold, draw_text_middle,
                              draw_opponents, draw_leaderboard)
from tetris.score import max_score, update_score
from tetris.core.state import GameState
from tetris.core.sequence import PieceSequence
from tetris.ui import layout
from tetris.config import s_width, s_height, play_width, top_left_x
from tetris.network.protocol import valid_board


# Largura da coluna dos adversários: mais larga quando há muitos tabuleiros.
def opponents_width(count):
    return 240 if count <= 4 else 360


def main(win, connection=None, seed=None, names=None, player=0):
    if not connection:
        return play(win)
    # Na partida em rede o canvas ganha uma coluna para os adversários;
    # a janela é alargada para o tabuleiro não encolher.
    size = win.get_size()
    layout.extra_width = opponents_width(len(names or []) - 1)
    wanted = round(size[1] * (s_width + layout.extra_width) / s_height)
    widened = size[0] < wanted
    if widened:
        pygame.display.set_mode((wanted, size[1]), pygame.RESIZABLE)
    try:
        return play(win, connection, seed, names or [], player)
    finally:
        layout.extra_width = 0
        if widened and pygame.display.get_surface():
            pygame.display.set_mode(size, pygame.RESIZABLE)


def play(win, connection=None, seed=None, names=(), player=0):
    last_score = max_score()
    state = GameState(PieceSequence(seed=seed))
    opponents = {index: {'name': name, 'score': 0, 'out': False,
                         'grid': [[(0, 0, 0)] * 10 for _ in range(20)]}
                 for index, name in enumerate(names) if index != player}
    my_name = names[player] if player < len(names) else ''
    network_time = 0
    finished = None
    ranking = []
    reported_loss = False

    def draw():
        draw_window(win, state.grid, state.score, last_score, state.level)
        draw_next_shapes(state.next_pieces, win)
        draw_hold(win, state.hold_piece, state.can_hold)
        if connection:
            layout.text(win, my_name, layout.rect(win, top_left_x, 150, play_width, 35), 26)
            draw_opponents(win, list(opponents.values()))

    run = True
    clock = pygame.time.Clock()
    fall_time = 0
    space_held = False

    while run:
        state.refresh_grid()
        # tick devolve o tempo real desde o último frame (ms)
        dt = clock.tick(60)
        if connection:
            for message in connection.poll():
                kind = message.get('type')
                opponent = opponents.get(message.get('player'))
                if kind == 'board' and opponent and valid_board(message):
                    opponent['grid'], opponent['score'] = message['grid'], message['score']
                elif kind == 'eliminated' and opponent:
                    opponent['out'] = True
                elif kind == 'garbage' and not reported_loss and finished is None:
                    state.add_garbage(message['holes'])
                elif kind == 'result' and finished is None:
                    finished = 'Você venceu!' if message['won'] else 'Você perdeu!'
                    ranking = [entry for entry in message.get('ranking', []) if isinstance(entry, dict)]
                elif kind in ('disconnected', 'error') and finished is None:
                    finished = 'Conexão encerrada'
        if finished is not None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    return True
            draw()
            draw_leaderboard(win, finished, ranking, player)
            pygame.display.update()
            continue
        if connection and state.lost() and not reported_loss:
            connection.send({'type': 'game_over', 'score': state.score})
            reported_loss = True
        fall_time += dt

        # a velocidade da queda acompanha o nível, que sobe com a pontuação
        if fall_time/1000 >= state.fall_speed and not reported_loss:
            fall_time = 0
            state.fall()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                space_held = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
            if event.type == pygame.KEYDOWN and not state.change_piece and not reported_loss:
                if event.key == pygame.K_LEFT:
                    state.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    state.move(1, 0)
                elif event.key == pygame.K_UP:
                    state.rotate()
                elif event.key == pygame.K_SPACE and not space_held:
                    space_held = True
                    state.hard_drop()
                    fall_time = 0
                elif event.key in (pygame.K_c, pygame.K_LSHIFT) and state.hold():
                    fall_time = 0

                if event.key == pygame.K_DOWN:
                    state.move(0, 1)

        cleared = state.update() if not reported_loss else 0
        if connection:
            if cleared >= 2:
                connection.send({'type': 'attack', 'lines': {2: 1, 3: 2, 4: 4}[cleared]})
            network_time += dt
            if network_time >= 100:
                network_time = 0
                connection.send({'type': 'board', 'grid': state.grid, 'score': state.score})

        draw()
        if reported_loss:
            # Com mais de dois jogadores, o eliminado assiste até sobrar um.
            draw_text_middle(win, 'Eliminado', 48, (255, 255, 255))
        pygame.display.update()

        if state.lost():
            if connection:
                if not reported_loss:
                    connection.send({'type': 'game_over', 'score': state.score})
                    reported_loss = True
                continue
            draw_text_middle(win, "Você perdeu!", 80, (255,255,255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(state.score)
    return True
