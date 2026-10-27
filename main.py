import pygame

from tetris.config import s_width, s_height
from tetris.ui.game import main
from tetris.ui.menu import main_menu

pygame.font.init()

win = pygame.display.set_mode((s_width, s_height), pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption('TetrisSockets')
pygame.key.set_repeat(170, 50)

main_menu(win, main)
