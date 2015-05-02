''' Useful constants '''

import pygame, os
if not pygame.display.get_init():
	pygame.init()

# General
WINDOW_SIZE = (960, 576)
FULLSCREEN = False
FPS = 40
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

CURSOR_PATH =os.path.join(GRAPHICS_DIR, "cursor.gif")

INTRO_BACKGROUND_PATH = os.path.join(GRAPHICS_DIR, "intro_bg.gif")
MENU_BACKGROUND_PATH = os.path.join(GRAPHICS_DIR, "menu_bg.gif")

MOVE_RANGE_IND_PATH = os.path.join(GRAPHICS_DIR, "movement_range_indicator.gif")
ATTACK_RANGE_IND_PATH = os.path.join(GRAPHICS_DIR, "attack_range_indicator.gif")
HEAL_RANGE_IND_PATH = os.path.join(GRAPHICS_DIR, "heal_range_indicator.gif")

END_TURN_PATH = os.path.join(GRAPHICS_DIR, "end_turn_button.gif")
END_TURN_HOVER_PATH = os.path.join(GRAPHICS_DIR, "end_turn_button_hover.gif")
END_TURN_PUSH_PATH = os.path.join(GRAPHICS_DIR, "end_turn_button_push.gif")

ACTION_BTN_PATH = os.path.join(GRAPHICS_DIR, "action_button.gif")
ACTION_BTN_HOVER_PATH = os.path.join(GRAPHICS_DIR, "action_button_hover.gif")
ACTION_BTN_PUSH_PATH = os.path.join(GRAPHICS_DIR, "action_button_push.gif")

BOTTOM_BAR_PATH = os.path.join(GRAPHICS_DIR, "bottom_bar.gif")
ACTION_MENU_PATH = os.path.join(GRAPHICS_DIR, "actions_menu_long.gif")

CHAR_INFO_BG_PATH = os.path.join(GRAPHICS_DIR, "char_info.gif")
CHAR_INFO_TURN_PATH = os.path.join(GRAPHICS_DIR, "char_info_has_turn.gif")
CHAR_INFO_DEAD_PATH = os.path.join(GRAPHICS_DIR, "char_info_dead.gif")

GAME_OVER_BANNER_PATH = os.path.join(GRAPHICS_DIR, "game_over_banner.gif")

# Fonts
FONT_DIR = "fonts"
FONT_PATH = os.path.join(FONT_DIR, "coders_crux.ttf")
S_FONT = pygame.font.Font(FONT_PATH, 14)
M_FONT = pygame.font.Font(FONT_PATH, 16)
L_FONT = pygame.font.Font(FONT_PATH, 24)
XL_FONT = pygame.font.Font(FONT_PATH, 40)
XXL_FONT = pygame.font.Font(FONT_PATH, 90)

# Music
VOLUME = 0.2
MUSIC_DIR = "sounds"

INTRO_MUSIC_PATH = os.path.join(MUSIC_DIR, "struck_by_the_rain.ogg")
GAME_MUSIC_PATH = os.path.join(MUSIC_DIR, "yellow_copter_short.ogg")

VICTORY_MUSIC_PATH = os.path.join(MUSIC_DIR, "victory.ogg")
LOSE_MUSIC_PATH = os.path.join(MUSIC_DIR, "lost_game2.ogg")

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (10, 200, 10)
RED = (200, 10, 10)

MENU_OPTION_COLOR = (30,30,30)
MENU_OPTION_HOVER_COLOR = WHITE
MENU_OPTION_GREYED_COLOR = (190,190,190)

# Credits
CREDITS_PATH = "credits.txt"