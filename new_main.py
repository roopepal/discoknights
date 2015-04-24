from common import reset_screen
from config_reader import build
from constants import FPS
from event_handler import GameEventHandler
from new_map import Map, MapView
from state import GameState, MainMenuState
import pygame, sys


def main():
	
	pygame.init()
	clock = pygame.time.Clock()
	
	# Initialize screen and set display mode
	reset_screen()
	
	# Build the map from config files
	m = build()
	
	# Initialize game states
	game = GameState(m)
	main_menu = MainMenuState()
	
	# set current state
	state = main_menu
	
	while 1:
		
		clock.tick(FPS)
		
		state.handle_events()
		state.update()
		state.render()
		
		#print("fps: " + str(int(clock.get_fps())))
		pygame.display.update()
		
	pygame.quit()
	sys.exit()


if __name__ == "__main__": main()