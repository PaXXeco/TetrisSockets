import pygame

from tetris.ui import layout

from tetris.config import rows, columns, block_size, play_width, play_height, top_left_x, top_left_y, s_width

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


def draw_hold(surface, piece, available=True):
    rect = side_panel(surface, False, top_left_y + 390, 130)
    header = round(30 * layout.scale(surface))
    draw_centered_text(surface, 'Guardada', pygame.Rect(rect.x, rect.y, rect.width, header), 24)
    if piece is None:
        return
    preview = pygame.Rect(rect.x, rect.y + header, rect.width, rect.height - header)
    # Fica apagada enquanto a troca não estiver liberada.
    draw_piece_preview(piece, surface, preview, padding=0,
                       color=None if available else (90, 90, 100))


def draw_piece_preview(shape, surface, preview, padding=16, color=None):
    cells = [(j, i) for i, line in enumerate(shape.shape[shape.rotation % len(shape.shape)])
             for j, cell in enumerate(line) if cell == '0']
    min_x = min(x for x, y in cells)
    min_y = min(y for x, y in cells)
    cell_size = max(1, min(round(24 * layout.scale(surface)), preview.width // 4, (preview.height - round(padding * layout.scale(surface))) // 4))
    width = (max(x for x, y in cells) - min_x + 1) * cell_size
    height = (max(y for x, y in cells) - min_y + 1) * cell_size
    sx = preview.centerx - width // 2
    sy = preview.centery - height // 2
    for x, y in cells:
        cell = pygame.Rect(sx + (x - min_x) * cell_size,
                           sy + (y - min_y) * cell_size, cell_size, cell_size)
        pygame.draw.rect(surface, color or shape.color, cell)
        pygame.draw.rect(surface, (22, 22, 30), cell, 1)

# Adversários na coluna extra, em uma grade que usa o maior tabuleiro que couber.
def draw_opponents(surface, opponents):
    if not opponents:
        return
    area_width, label = layout.extra_width - 20, 30
    best = None
    for cols in range(1, len(opponents) + 1):
        lines = -(-len(opponents) // cols)
        cell_w, cell_h = area_width / cols, play_height / lines
        height = min(cell_h - label - 10, (cell_w - 10) * 2)
        if best is None or height > best[0]:
            best = (height, cols, cell_w, cell_h)
    height, cols, cell_w, cell_h = best
    for index, opponent in enumerate(opponents):
        x = s_width + (index % cols) * cell_w
        y = top_left_y + (index // cols) * cell_h
        color = (120, 120, 135) if opponent['out'] else TEXT_COLOR
        layout.text(surface, f"{opponent['name']}: {opponent['score']}",
                    layout.rect(surface, x, y, cell_w - 6, label), 22, color)
        bounds = layout.rect(surface, x + (cell_w - height / 2) / 2, y + label, height / 2, height)
        pygame.draw.rect(surface, (0, 0, 0), bounds)
        for row_index, row in enumerate(opponent['grid']):
            for col_index, cell in enumerate(row):
                if tuple(cell) == (0, 0, 0):
                    continue
                left = bounds.x + col_index * bounds.width // columns
                top = bounds.y + row_index * bounds.height // rows
                block = pygame.Rect(left, top,
                                    bounds.x + (col_index + 1) * bounds.width // columns - left,
                                    bounds.y + (row_index + 1) * bounds.height // rows - top)
                pygame.draw.rect(surface, (70, 70, 80) if opponent['out'] else cell, block)
        # Mesma grade do tabuleiro principal, mais discreta quando as células são pequenas.
        line = (128, 128, 128) if bounds.width >= 14 * columns else (70, 70, 80)
        for row_index in range(1, rows):
            line_y = bounds.y + row_index * bounds.height // rows
            pygame.draw.line(surface, line, (bounds.x, line_y), (bounds.right - 1, line_y))
        for col_index in range(1, columns):
            line_x = bounds.x + col_index * bounds.width // columns
            pygame.draw.line(surface, line, (line_x, bounds.y), (line_x, bounds.bottom - 1))
        pygame.draw.rect(surface, (155, 155, 170), bounds, 1)
        if opponent['out']:
            layout.text(surface, 'Eliminado', bounds, 20, TEXT_COLOR)


# Placar do fim da partida em rede: ranking é a lista do servidor, do 1º ao último.
def draw_leaderboard(surface, title, ranking, me):
    width = 440
    x = (s_width + layout.extra_width - width) / 2
    step = 46 if len(ranking) <= 6 else 38
    height = 150 + step * len(ranking) + (40 if ranking else 0)
    y = top_left_y + (play_height - height) / 2
    panel = layout.rect(surface, x, y, width, height)
    pygame.draw.rect(surface, (22, 22, 30), panel, border_radius=12)
    pygame.draw.rect(surface, (155, 155, 170), panel, 1, border_radius=12)
    layout.text(surface, title, layout.rect(surface, x + 20, y + 20, width - 40, 60), 44, bold=True)
    if ranking:
        layout.text(surface, 'Classificação', layout.rect(surface, x, y + 85, width, 30), 22, (155, 155, 170))
    for place, entry in enumerate(ranking):
        row_y = y + 125 + step * place
        mine = entry.get('player') == me
        color = (255, 215, 90) if mine else TEXT_COLOR
        if mine:
            pygame.draw.rect(surface, (38, 38, 48), layout.rect(surface, x + 20, row_y, width - 40, step - 6),
                             border_radius=6)
        layout.text(surface, f'{place + 1}º', layout.rect(surface, x + 30, row_y, 50, step - 6), 26, color)
        layout.text(surface, entry.get('name', '?'), layout.rect(surface, x + 90, row_y, 220, step - 6), 26, color)
        layout.text(surface, entry.get('score', 0), layout.rect(surface, x + 320, row_y, 90, step - 6), 26, color)
    layout.text(surface, 'Enter para voltar ao menu',
                layout.rect(surface, x, y + height - 45, width, 30), 20, (155, 155, 170))


def draw_window(surface, grid, score=0, last_score=0, level=1):
    surface.fill((0,0,0))

    draw_centered_text(surface, 'TetrisSockets',
                       layout.rect(surface, 20, 30, s_width + layout.extra_width - 40, 80), 54)
    draw_stat(surface, 'Recorde', last_score, False, top_left_y)
    draw_stat(surface, 'Pontuação', score, False, top_left_y + 130)
    draw_stat(surface, 'Nível', level, False, top_left_y + 260)

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], layout.rect(surface, top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    # draw grid and border
    draw_grid(surface, rows, columns)
    pygame.draw.rect(surface, (255, 0, 0), layout.rect(surface, top_left_x-5, top_left_y-5, play_width+10, play_height+10), max(1, round(5 * layout.scale(surface))))
    # pygame.display.update()
