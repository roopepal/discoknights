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
	
	# Main loop
	while 1:

		# Lock maximum FPS
		clock.tick(FPS)

		# Handle mouse and keyboard events
		state_mgr.current_state.handle_events()

		# Update elements
		state_mgr.current_state.update()

		# Draw elements
		state_mgr.current_state.draw()

		# Draw cursor
		state_mgr.current_state.draw_cursor()

		# Render screen
		pygame.display.update()


	pygame.quit()
	sys.exit()


if __name__ == "__main__": main()