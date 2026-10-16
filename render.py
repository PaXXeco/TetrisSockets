import pygame

from config import rows, columns, block_size, play_width, play_height, top_left_x, top_left_y

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


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans,liberationsans', 30)
    label = font.render('Next Shape', 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy- 30))

def draw_window(surface, grid, score=0, last_score=0):
    surface.fill((0,0,0))

    # Desenha o nome do jogo
    font = pygame.font.SysFont('comicsans,liberationsans', 60)
    label = font.render('ABCDE', 1, (255,255,255))
    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    font = pygame.font.SysFont('comicsans,liberationsans', 60)
    label = font.render('Score: ' + str(score), 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100

    surface.blit(label, (sx + 20, sy + 160))
    # last score
    label = font.render('High Score: ' + last_score, 1, (255,255,255))

    sx = top_left_x - 200
    sy = top_left_y + 200

    surface.blit(label, (sx + 20, sy + 160))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j* block_size, top_left_y + i * block_size, block_size, block_size), 0)

    # draw grid and border
    draw_grid(surface, rows, columns)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x-5, top_left_y-5, play_width+10, play_height+10), 5)
    # pygame.display.update()
