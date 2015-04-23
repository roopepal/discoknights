from new_character import Character, CharacterView
from common import *
from config_reader import ConfigReader
from coordinates import Coordinates
import direction
from new_map import Map, MapView
from object_type import ObjectType
import pygame, sys
from squaretype import SquareType
from options import *





import cProfile, pstats

def do_cprofile(func):
	def profiled_func(*args, **kwargs):
		profile = cProfile.Profile()
		try:
			profile.enable()
			result = func(*args, **kwargs)
			profile.disable()
			return result
		finally:
			ps = pstats.Stats(profile)
			ps.strip_dirs()
			ps.sort_stats('cumtime').print_stats()
	return profiled_func



@do_cprofile


def main():			
	
	pygame.init()
	clock = pygame.time.Clock()
	fps = 1000
	
	reset_screen()
	
	#read config from files
	r = ConfigReader()
	f = open('map_config', 'r')
	map_config = r.read_config(f)
	f.close()
	f = open('character_config', 'r')
	character_config = r.read_config(f)
	f.close()
	
	m = r.build_from_config(map_config, character_config)

	
	#milliseconds from last frame
	new_time, old_time = None, None	   
	
	done = False
	
	while not done:
		
		clock.tick(fps)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True
		
		# show fps and milliseconds
		if new_time:
			old_time = new_time
		new_time = pygame.time.get_ticks()
		if new_time and old_time:
			pygame.display.set_caption("fps: " + str(int(clock.get_fps())) + " ms: " + str(new_time-old_time))
		
		pygame.display.update()
		
	pygame.quit()
	sys.exit()
	
if __name__ == "__main__": main()