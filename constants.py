''' Useful constants '''

import os

# Map
TILE_W = 64
TILE_H = 32

# Resource paths
MAP_CONFIG = "map_config"
CHARACTER_CONFIG = "character_config"

GRAPHICS_DIR = "graphics"
MOVE_RANGE_IND_PATH = os.path.join(GRAPHICS_DIR, "movement_range_indicator.gif")
ATTACK_RANGE_IND_PATH = os.path.join(GRAPHICS_DIR, "attack_range_indicator.gif")
HEAL_RANGE_IND_PATH = os.path.join(GRAPHICS_DIR, "heal_range_indicator.gif")

# Colors

BLACK = (0,0,0)