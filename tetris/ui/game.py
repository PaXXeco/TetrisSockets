import pygame

from tetris.ui.render import draw_window, draw_next_shape, draw_text_middle
from tetris.score import max_score, update_score
from tetris.core.state import GameState

def main(win):
    last_score = max_score()
    state = GameState()

    run = True
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0

    while run:
        state.refresh_grid()
        # tick devolve o tempo real desde o último frame (ms)
        dt = clock.tick(60)
        fall_time += dt
        level_time += dt

        # a cada 5 segundos a peça cai um pouco mais rápido
        if level_time/1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005

        if fall_time/1000 >= fall_speed:
            fall_time = 0
            state.fall()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    state.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    state.move(1, 0)
                elif event.key == pygame.K_UP:
                    state.rotate()

                if event.key == pygame.K_DOWN:
                    state.move(0, 1)

        state.update()

        draw_window(win, state.grid, state.score, last_score)
        draw_next_shape(state.next_piece, win)
        pygame.display.update()

        if state.lost():
            draw_text_middle(win, "YOU LOST!", 80, (255,255,255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(state.score)
