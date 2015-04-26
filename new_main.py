from constants import FPS, VOLUME
from state import StateManager
import pygame, sys



def main():
	
	# Initialize Pygame
	pygame.init()
	clock = pygame.time.Clock()
	pygame.mixer.music.set_volume(VOLUME)
	
	# Initialize state manager
	state_mgr = StateManager()
	# Initialize screen and set display mode
	state_mgr.reset_screen()
	
	while 1:
		
		clock.tick(FPS)
		
		state_mgr.current_state.handle_events()
		state_mgr.current_state.update()
		state_mgr.current_state.draw()
		
		pygame.display.update()
		
	pygame.quit()
	sys.exit()


if __name__ == "__main__": main()