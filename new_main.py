from common import reset_screen
from constants import FPS
from state import StateManager
import pygame, sys


def main():
	
	# Initialize Pygame
	pygame.init()
	clock = pygame.time.Clock()
	
	# Initialize screen and set display mode
	reset_screen()
	
	# Initialize state manager
	state_mgr = StateManager()
	
	while 1:
		
		clock.tick(FPS)
		
		state_mgr.current_state.handle_events()
		state_mgr.current_state.update()
		state_mgr.current_state.draw()
		
		pygame.display.update()
		
	pygame.quit()
	sys.exit()


if __name__ == "__main__": main()