import pygame
import options
from constants import *
from coordinates import Coordinates


def map_to_screen(map_x, map_y):
	# convert map coordinates to isometric screen coordinates
	screen_x = (map_x - map_y) * (TILE_W / 2)
	screen_y = (map_x + map_y) * (TILE_H / 2)
	return screen_x, screen_y
	
	
def screen_to_map(screen_x, screen_y):
	# convert isometric screen coordinates to map coordinates
	# assuming origins are at the top
	screen_x /= 2
	map_x = (screen_y + screen_x)/(TILE_H)
	map_y = (screen_y - screen_x)/(TILE_H)
	if map_x < 0:
		map_x -= 1
	if map_y < 0:
		map_y -= 1
	return int(map_x), int(map_y)


def reset_screen():
	# check if display has been initialized
	if not pygame.display.get_init():
		pygame.init()
		
	# set screen
	screen = pygame.display.set_mode( options.window_size )
	
	# fill with black
	screen.fill(BLACK)
	
	return screen
