from common import *
import pygame, sys

class EventHandler(object):
	def __init__(self):
		pass
		# Set events that are read
		#pygame.event.set_allowed([
		#	pygame.QUIT,
		#	pygame.MOUSEBUTTONUP
		#])
	
	def handle(self, event):
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		
		# mouse clicks	
		elif event.type == pygame.MOUSEBUTTONUP:
			self.handle_click(pygame.mouse.get_pos())
			
		# key presses
		elif event.type == pygame.KEYDOWN:
			self.handle_key(event.key)
			
	
class MenuEventHandler(EventHandler):
	def __init__(self, menu):
		EventHandler.__init__(self)
		
		self.menu = menu
	
	
class GameEventHandler(EventHandler):
	def __init__(self, mp):
		EventHandler.__init__(self)
				
		# set map
		self.map = mp
		
	def handle_click(self, mouse_pos):
		# recognize menu
		if False:
			pass
		
		# else get square clicked
		else:

			# account for map positioning on screen
			mouse_x = mouse_pos[0] - self.map.view.rect.left - self.map.view.width / 2
			mouse_y = mouse_pos[1] - self.map.view.rect.top
			
			# convert coordinates
			map_x, map_y = screen_to_map(mouse_x, mouse_y)
			
			# get character with turn
			char = self.map.turn_controller.current_character
			
			# if the current character has not moved
			if not char.has_moved:
				
				# get shortest path to clicked square
				self.map.in_range = char.get_movement_range()
				path = char.get_shortest_path( Coordinates(map_x, map_y) )
				
				# if path was found
				if path:
					#[ print(str(s)) for s in path ]
					char.walking, char.walk_path = True, path
				else:
					print("Out of range.")
			