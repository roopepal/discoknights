import pygame
import options
from constants import *

def map_to_screen(map_x, map_y):
	screen_x = (map_x - map_y) * (TILE_W / 2)
	screen_y = (map_x + map_y) * (TILE_H / 2)
	return screen_x, screen_y
	
def screen_to_map(screen_x, screen_y, offset_x=0, offset_y=0):
	x -= ( offset_x + tile_w / 2 )
	y -= offset_y
	x = x / 2
	map_x = (y + x)/(tile_h)
	map_y = (y - x)/(tile_h)
	if map_x < 0:
		map_x -= 1
	if map_y < 0:
		map_y -= 1	  
	return int(map_x), int(map_y)
	

	
	#map.x = (screen.x / TILE_WIDTH_HALF + screen.y / TILE_HEIGHT_HALF) /2;
	#map.y = (screen.y / TILE_HEIGHT_HALF -(screen.x / TILE_WIDTH_HALF)) /2;


def load_sprites(map):
	# For each squaretype
	for squaretype in m.squaretypes:
		sprites[m.squaretypes[squaretype].sprite] = pygame.image.load(m.squaretypes[squaretype].sprite).convert_alpha()
	
	# For each object type
	for object_type in m.object_types:
		sprites[m.object_types[object_type].sprite] = pygame.image.load(m.object_types[object_type].sprite).convert_alpha()







def reset_screen():
	# check if display has been initialized
	if not pygame.display.get_init():
		pygame.init()
		
	# set screen
	screen = pygame.display.set_mode( options.window_size, pygame.DOUBLEBUFdiscoknights )
	# fill with black
	screen.fill( (0,0,0) )
	
	return screen