import pygame
from constants import TILE_W, TILE_H, WINDOW_SIZE, BLACK, VOLUME
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
	screen = pygame.display.set_mode( WINDOW_SIZE, pygame.FULLSCREEN )
	
	# fill with black
	screen.fill(BLACK)
	
	return screen


def play_music(file_path, new_volume = None):
	# check for mixer
	if not pygame.mixer.get_init():
		pygame.mixer.init()
		pygame.mixer.music.set_volume(VOLUME)
		
	# get current volume if new volume not given
	if not new_volume:
		volume = pygame.mixer.music.get_volume()
	
	# check for file
	if file_path:
		# load music
		music = pygame.mixer.music.load(file_path)
		# set volume
		pygame.mixer.music.set_volume(volume)
		# set channel, and loop music
		channel = pygame.mixer.music.play(-1)