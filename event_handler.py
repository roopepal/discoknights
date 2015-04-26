from action import Action
from common import *
from constants import *
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
			# change state with number keys, DEBUG
			if event.key == pygame.K_1:
				self.state.state_manager.go_to(self.state.state_manager.game)
			elif event.key == pygame.K_2:
				self.state.state_manager.go_to(self.state.state_manager.main_menu)
			elif event.key == pygame.K_3:
				self.state.state_manager.go_to(self.state.state_manager.options_menu)
			
			# handle key presses
			else:
				self.handle_key(event.key)
			
		# other events, e.g. mouse movement
		else:
			self.handle_event(event)



class IntroEventHandler(EventHandler):
	def __init__(self, state):
		EventHandler.__init__(self)
		
		# set program state
		self.state = state
	
	
	def skip(self):
		self.state.state_manager.go_to(self.state.state_manager.main_menu)
	
	def handle_click(self, mouse_pos):
		self.skip()
	
	def handle_key(self, key):
		self.skip()
		
	def handle_event(self, event):
		pass



class MenuEventHandler(EventHandler):
	def __init__(self, state, menu):
		EventHandler.__init__(self)
		
		# set program state
		self.state = state
		# set menu
		self.menu = menu
		
	
	def handle_key(self, key):
		pass
		
		
	def handle_click(self, mouse_pos):
		for option in self.menu.options:
			if option.rect.collidepoint(pygame.mouse.get_pos()):
				if option.function and not option.greyed:
					option.function()
				
	
	def handle_event(self, event):
		for option in self.menu.options:
			if option.rect.collidepoint(pygame.mouse.get_pos()):
				option.hovered = True
				break
			elif option.hovered:
				option.hovered = False



class GameEventHandler(EventHandler):
	def __init__(self, state, mp):
		EventHandler.__init__(self)
		
		# set program state
		self.state = state
		# set map
		self.map = mp
		# selected action
		self.selected_action = None
		
	
	def handle_event(self, event):
		pass
	
	
	def handle_key(self, key):
		if key == pygame.K_ESCAPE:
			# go to menu with ESC
			self.state.state_manager.go_to(self.state.state_manager.main_menu)
			# set Resume Game option not greyed out
			self.state.state_manager.main_menu.menu.options[0].greyed = False
	
	
	def handle_click(self, mouse_pos):
		# get current character
		character = self.map.turn_controller.current_character
		
		# if character is not walking
		if not character.walking:
			# init status
			click_handled = False
			
			# recognize end turn button
			if self.map.view.end_turn_btn.rect.collidepoint(mouse_pos):
				character.end_turn()
				# set state
				click_handled = True
		
			# recognize action buttons
			for button in self.map.view.action_buttons:
				if button.rect.collidepoint(mouse_pos):
					# get action
					action = character.actions[self.map.view.action_buttons.index(button)]
					self.selected_action = action
				
					# get action range
					self.map.in_range = action.get_action_range()
				
					# update range on map view based on action type
					if action.type == Action.DAMAGE or action.type == Action.STUN:
						self.map.view.update_range = ATTACK
					elif action.type == Action.HEAL:
						self.map.view.update_range = HEAL
				
					# update character turn state
					character.has_moved = True
				
					# set state
					click_handled = True
		
			# if button was not clicked, get square clicked
			if not click_handled:
				# account for map positioning on screen
				mouse_x = mouse_pos[0] - self.map.view.rect.left - self.map.view.width / 2
				mouse_y = mouse_pos[1] - self.map.view.rect.top

				# convert coordinates
				map_x, map_y = screen_to_map(mouse_x, mouse_y)
				coordinates = Coordinates(map_x, map_y)

				# if character has not moved, i.e. should move now
				if not character.has_moved:
					# get shortest path to clicked square
					self.map.in_range = character.get_movement_range()
					path = character.get_shortest_path(coordinates)
			
					# if path was found
					if path:
						character.walking, character.walk_path = True, path
						# clear range indicators on map
						self.map.in_range = []
						self.map.view.update_range = MOVEMENT
					else:
						print("Out of range.")
		
				# if action was selected
				elif self.selected_action:
					# get square clicked
					square = self.map.get_square_at(coordinates)
					# if square is in range
					if square.coordinates in self.map.in_range:
						# if there is a character in the square clicked
						if square.character:
							# use action
							self.selected_action.perform(coordinates)
							# reset action selected
							self.selected_action = None
							# end turn
							character.end_turn()
						else:
							# end turn
							character.end_turn()
							print("Missed!")
							
					
				