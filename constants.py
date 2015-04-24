''' Useful constants '''

import pygame, os
if not pygame.display.get_init():
	pygame.init()

# Game
FPS = 60
HALF_SPEED_WALK = True

# Map
TILE_W = 64
TILE_H = 32
# Map range types
MOVEMENT = 1
ATTACK = 2
HEAL = 3

# Resource paths
MAP_CONFIG = "map_config"
CHARACTER_CONFIG = "character_config"
GRAPHICS_DIR = "graphics"
MOVE_RANGE_IND_PATH = os.path.join(GRAPHICS_DIR, "movement_range_indicator.gif")
ATTACK_RANGE_IND_PATH = os.path.join(GRAPHICS_DIR, "attack_range_indicator.gif")
HEAL_RANGE_IND_PATH = os.path.join(GRAPHICS_DIR, "heal_range_indicator.gif")
FONT_DIR = "fonts"
FONT_PATH = os.path.join(FONT_DIR, "coders_crux.ttf")

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)

MENU_OPTION_COLOR = WHITE
MENU_OPTION_HOVER_COLOR = (190,190,190)

# Fonts
S_FONT = pygame.font.Font(FONT_PATH, 14)
M_FONT = pygame.font.Font(FONT_PATH, 16)
L_FONT = pygame.font.Font(FONT_PATH, 24)
XL_FONT = pygame.font.Font(FONT_PATH, 40)