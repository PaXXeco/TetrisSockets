import pygame

from tetris.ui.render import draw_window, draw_next_shapes, draw_text_middle
from tetris.score import max_score, update_score
from tetris.core.state import GameState
from tetris.core.sequence import PieceSequence
from tetris.ui import layout
from tetris.network.protocol import valid_board


def draw_opponent(win, board, score):
    layout.text(win, f'Adversário: {score}', layout.rect(win, 20, 455, 210, 35), 24)
    bounds = layout.rect(win, 65, 500, 120, 240)
    for y, row in enumerate(board):
        for x, color in enumerate(row):
            cell = pygame.Rect(bounds.x + round(x * bounds.width / 10),
                               bounds.y + round(y * bounds.height / 20),
                               max(1, round(bounds.width / 10)), max(1, round(bounds.height / 20)))
            pygame.draw.rect(win, color, cell)
    pygame.draw.rect(win, (155, 155, 170), bounds, 1)

def main(win, connection=None, seed=None):
    last_score = max_score()
    state = GameState(PieceSequence(seed=seed))
    opponent_grid = [[(0, 0, 0)] * 10 for _ in range(20)]
    opponent_score = 0
    network_time = 0
    finished = None
    result_time = 0
    reported_loss = False

    run = True
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    space_held = False

    while run:
        state.refresh_grid()
        # tick devolve o tempo real desde o último frame (ms)
        dt = clock.tick(60)
        if connection:
            for message in connection.poll():
                kind = message.get('type')
                if kind == 'board' and valid_board(message):
                    opponent_grid, opponent_score = message['grid'], message['score']
                elif kind == 'garbage' and not reported_loss and finished is None:
                    state.add_garbage(message['holes'])
                elif kind == 'result' and finished is None:
                    finished = 'Você venceu!' if message['won'] else 'Você perdeu!'
                elif kind in ('disconnected', 'error') and finished is None:
                    finished = 'Conexão encerrada'
        if finished is not None:
            result_time += dt
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    return True
            draw_window(win, state.grid, state.score, last_score)
            draw_next_shapes(state.next_pieces, win)
            draw_opponent(win, opponent_grid, opponent_score)
            draw_text_middle(win, finished, 48, (255, 255, 255))
            pygame.display.update()
            if result_time >= 3000:
                return True
            continue
        if connection and state.lost() and not reported_loss:
            connection.send({'type': 'game_over'})
            reported_loss = True
        fall_time += dt
        level_time += dt

        # a cada 5 segundos a peça cai um pouco mais rápido
        if level_time/1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005

        if fall_time/1000 >= fall_speed and not reported_loss:
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

        draw_window(win, state.grid, state.score, last_score)
        draw_next_shapes(state.next_pieces, win)
        if connection:
            draw_opponent(win, opponent_grid, opponent_score)
        pygame.display.update()

        if state.lost():
            if connection:
                if not reported_loss:
                    connection.send({'type': 'game_over'})
                    reported_loss = True
                continue
            draw_text_middle(win, "Você perdeu!", 80, (255,255,255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(state.score)
    return True
