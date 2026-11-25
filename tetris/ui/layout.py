from functools import lru_cache

import pygame

from tetris.config import s_width, s_height


# Largura somada ao canvas durante a partida em rede (coluna dos adversários).
extra_width = 0


def scale(surface):
    return min(surface.get_width() / (s_width + extra_width), surface.get_height() / s_height)


def rect(surface, x, y, width, height):
    factor = scale(surface)
    offset_x = (surface.get_width() - (s_width + extra_width) * factor) / 2
    offset_y = (surface.get_height() - s_height * factor) / 2
    return pygame.Rect(round(offset_x + x * factor), round(offset_y + y * factor),
                       max(1, round(width * factor)), max(1, round(height * factor)))


@lru_cache(maxsize=128)
def font(size, bold=False):
    return pygame.font.SysFont('comicsans,liberationsans', max(1, size), bold=bold)


def text(surface, value, bounds, size, color=(240, 240, 245), bold=False):
    size = max(1, round(size * scale(surface)))
    label = font(size, bold).render(str(value), True, color)
    while label.get_width() > bounds.width and size > 1:
        size -= 1
        label = font(size, bold).render(str(value), True, color)
    surface.blit(label, label.get_rect(center=bounds.center))
