import pygame

from tetris.config import rows, columns, block_size, play_width, play_height, top_left_x, top_left_y

FONT_NAME = 'comicsans,liberationsans'
TEXT_COLOR = (240, 240, 245)


def draw_centered_text(surface, text, rect, size, color=TEXT_COLOR):
    font = pygame.font.SysFont(FONT_NAME, size)
    label = font.render(str(text), True, color)
    while label.get_width() > rect.width and size > 1:
        size -= 1
        font = pygame.font.SysFont(FONT_NAME, size)
        label = font.render(str(text), True, color)
    surface.blit(label, label.get_rect(center=rect.center))


def side_panel(surface, right, y, height):
    margin = 20
    x = top_left_x + play_width + margin if right else margin
    width = top_left_x - 2 * margin
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (22, 22, 30), rect, border_radius=12)
    return rect.inflate(-20, -20)


def draw_stat(surface, title, value, right, y):
    rect = side_panel(surface, right, y, 110)
    draw_centered_text(surface, title, pygame.Rect(rect.x, rect.y, rect.width, 30), 24)
    draw_centered_text(surface, value, pygame.Rect(rect.x, rect.y + 35, rect.width, 50), 36)

def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("comicsans,liberationsans", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width /2 - (label.get_width()/2), top_left_y + play_height/2 - label.get_height()/2))

# Desenha a grade 
def draw_grid(surface, row, col):
    sx = top_left_x
    sy = top_left_y
    for i in range(row+1):
        pygame.draw.line(surface, (128,128,128), (sx, sy+ i*block_size), (sx + play_width, sy + i * block_size))
    for j in range(col+1):
        pygame.draw.line(surface, (128,128,128), (sx + j * block_size, sy), (sx + j * block_size, sy + play_height))


def draw_next_shapes(shapes, surface):
    rect = side_panel(surface, True, top_left_y, play_height)
    draw_centered_text(surface, 'Próximas peças', pygame.Rect(rect.x, rect.y, rect.width, 35), 24)
    if not shapes:
        return
    slot_height = (rect.height - 45) // len(shapes)
    for index, shape in enumerate(shapes):
        preview = pygame.Rect(rect.x, rect.y + 45 + index * slot_height,
                              rect.width, slot_height)
        if index:
            pygame.draw.line(surface, (45, 45, 55), preview.topleft, preview.topright)
        draw_piece_preview(shape, surface, preview)


def draw_piece_preview(shape, surface, preview):
    cells = [(j, i) for i, line in enumerate(shape.shape[shape.rotation % len(shape.shape)])
             for j, cell in enumerate(line) if cell == '0']
    min_x = min(x for x, y in cells)
    min_y = min(y for x, y in cells)
    cell_size = min(24, preview.width // 4, (preview.height - 16) // 4)
    width = (max(x for x, y in cells) - min_x + 1) * cell_size
    height = (max(y for x, y in cells) - min_y + 1) * cell_size
    sx = preview.centerx - width // 2
    sy = preview.centery - height // 2
    for x, y in cells:
        cell = pygame.Rect(sx + (x - min_x) * cell_size,
                           sy + (y - min_y) * cell_size, cell_size, cell_size)
        pygame.draw.rect(surface, shape.color, cell)
        pygame.draw.rect(surface, (22, 22, 30), cell, 1)

def draw_window(surface, grid, score=0, last_score=0):
    surface.fill((0,0,0))

    draw_centered_text(surface, 'TetrisSockets',
                       pygame.Rect(20, 30, surface.get_width() - 40, 80), 54)
    draw_stat(surface, 'Recorde', last_score, False, top_left_y)
    draw_stat(surface, 'Pontuação', score, False, top_left_y + 130)

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j* block_size, top_left_y + i * block_size, block_size, block_size), 0)

    # draw grid and border
    draw_grid(surface, rows, columns)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x-5, top_left_y-5, play_width+10, play_height+10), 5)
    # pygame.display.update()
