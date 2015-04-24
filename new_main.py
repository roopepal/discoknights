from common import *
from config_reader import ConfigReader
from new_map import Map
import pygame, sys



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

#@do_cprofile




def main():			
	
	pygame.init()
	clock = pygame.time.Clock()
	fps = 60
	
	# initialize
	reset_screen()
	
	# build from config, return map
	mp = build()
	
	done = False
	while not done:
		
		clock.tick(fps)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True
		
		
		game_loop(m)
		
		
		
		print("fps: " + str(int(clock.get_fps())))
		pygame.display.update()
		
	pygame.quit()
	sys.exit()
	
if __name__ == "__main__": main()