import pygame

FONT_NAME = 'comicsans,liberationsans'

button_width = 260
button_height = 80
button_color = (0, 150, 0)
button_hover_color = (0, 200, 0)


def draw_button(surface, rect, text, hover):
    color = button_hover_color if hover else button_color
    pygame.draw.rect(surface, color, rect, 0, border_radius=12)
    pygame.draw.rect(surface, (255, 255, 255), rect, 3, border_radius=12)

    font = pygame.font.SysFont(FONT_NAME, 40, bold=True)
    label = font.render(text, 1, (255, 255, 255))
    surface.blit(label, (rect.centerx - label.get_width() / 2, rect.centery - label.get_height() / 2))


# start_game é a função que roda o jogo (recebe a janela)
def main_menu(win, start_game):
    width, height = win.get_size()
    button = pygame.Rect((width - button_width) // 2, height // 2, button_width, button_height)
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(60)
        win.fill((0, 0, 0))

        # Desenha o nome do jogo
        font = pygame.font.SysFont(FONT_NAME, 80, bold=True)
        label = font.render('TetrisSockets', 1, (255, 255, 255))
        win.blit(label, (width / 2 - label.get_width() / 2, height / 2 - 200))

        draw_button(win, button, 'Jogar', button.collidepoint(pygame.mouse.get_pos()))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button.collidepoint(event.pos):
                    start_game(win)

    pygame.display.quit()
