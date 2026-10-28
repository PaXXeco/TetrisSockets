import pygame

from tetris.ui import layout

from tetris.config import rows, columns, block_size, play_width, play_height, top_left_x, top_left_y

FONT_NAME = 'comicsans,liberationsans'
TEXT_COLOR = (240, 240, 245)


def draw_centered_text(surface, text, rect, size, color=TEXT_COLOR):
    layout.text(surface, text, rect, size, color)


def side_panel(surface, right, y, height):
    margin = 20
    x = top_left_x + play_width + margin if right else margin
    width = top_left_x - 2 * margin
    rect = layout.rect(surface, x, y, width, height)
    pygame.draw.rect(surface, (22, 22, 30), rect, border_radius=12)
    return rect.inflate(-round(20 * layout.scale(surface)), -round(20 * layout.scale(surface)))


def draw_stat(surface, title, value, right, y):
    rect = side_panel(surface, right, y, 110)
    draw_centered_text(surface, title, pygame.Rect(rect.x, rect.y, rect.width, round(30 * layout.scale(surface))), 24)
    draw_centered_text(surface, value, pygame.Rect(rect.x, rect.y + round(35 * layout.scale(surface)), rect.width, round(50 * layout.scale(surface))), 36)

def draw_text_middle(surface, text, size, color):
    layout.text(surface, text, layout.rect(surface, top_left_x, top_left_y, play_width, play_height), size, color, bold=True)

# Desenha a grade 
def draw_grid(surface, row, col):
    board = layout.rect(surface, top_left_x, top_left_y, play_width, play_height)
    sx, sy = board.topleft
    for i in range(row+1):
        pygame.draw.line(surface, (128,128,128), (sx, sy + round(i * board.height / row)), (board.right, sy + round(i * board.height / row)))
    for j in range(col+1):
        pygame.draw.line(surface, (128,128,128), (sx + round(j * board.width / col), sy), (sx + round(j * board.width / col), board.bottom))


def draw_next_shapes(shapes, surface):
    rect = side_panel(surface, True, top_left_y, play_height)
    draw_centered_text(surface, 'Próximas peças', pygame.Rect(rect.x, rect.y, rect.width, round(35 * layout.scale(surface))), 24)
    if not shapes:
        return
    header = round(45 * layout.scale(surface))
    slot_height = (rect.height - header) // len(shapes)
    for index, shape in enumerate(shapes):
        preview = pygame.Rect(rect.x, rect.y + header + index * slot_height,
                              rect.width, slot_height)
        if index:
            pygame.draw.line(surface, (45, 45, 55), preview.topleft, preview.topright)
        draw_piece_preview(shape, surface, preview)


def draw_piece_preview(shape, surface, preview):
    cells = [(j, i) for i, line in enumerate(shape.shape[shape.rotation % len(shape.shape)])
             for j, cell in enumerate(line) if cell == '0']
    min_x = min(x for x, y in cells)
    min_y = min(y for x, y in cells)
    cell_size = max(1, min(round(24 * layout.scale(surface)), preview.width // 4, (preview.height - round(16 * layout.scale(surface))) // 4))
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
                       layout.rect(surface, 20, 30, 760, 80), 54)
    draw_stat(surface, 'Recorde', last_score, False, top_left_y)
    draw_stat(surface, 'Pontuação', score, False, top_left_y + 130)

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], layout.rect(surface, top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    # draw grid and border
    draw_grid(surface, rows, columns)
    pygame.draw.rect(surface, (255, 0, 0), layout.rect(surface, top_left_x-5, top_left_y-5, play_width+10, play_height+10), max(1, round(5 * layout.scale(surface))))
    # pygame.display.update()
