import pygame
import options
from config_reader import ConfigReader
from constants import *
from coordinates import Coordinates

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

def build():
	# read config from files
	r = ConfigReader()
	f = open(MAP_CONFIG, 'r')
	map_config = r.read_config(f)
	f.close()
	f = open(CHARACTER_CONFIG, 'r')
	character_config = r.read_config(f)
	f.close()
	
	# build map and characters
	m = r.build_from_config(map_config, character_config)
	
	# return built map
	return m


def reset_screen():
	# check if display has been initialized
	if not pygame.display.get_init():
		pygame.init()
		
	# set screen
	#flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
	screen = pygame.display.set_mode( options.window_size )
	# fill with black
	screen.fill(BLACK)
	
	return screen

	
def game_loop(mp):
	# draw map and possible range indicators
	mp.view.draw()
	
	# draw characters and objects in proper order for correct depth
	for x in range(mp.width):
		for y in range(mp.height):
			square = mp.get_square_at(Coordinates(x,y))
			character = square.character
			map_object = square.object 
			if character:
				character.view.draw()
			if map_object:
				map_object.view.draw()
