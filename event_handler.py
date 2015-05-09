from action import Action
from constants import *
from coordinates import Coordinates, map_to_screen, screen_to_map
import pygame, sys

class EventHandler(object):
	def __init__(self, state):
		
		# set program state
		self.state = state
			
	def handle(self, event):
		# get mouse position
		mouse_pos = pygame.mouse.get_pos()
		
		# update cursor position
		self.state.state_mgr.cursor_pos = (mouse_pos)
		
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		
		# mouse clicks	
		elif event.type == pygame.MOUSEBUTTONUP:
			self.handle_click(mouse_pos)
			
		# key presses
		elif event.type == pygame.KEYDOWN:
			self.handle_key(event.key)
		
		else:
			self.handle_event(event)



class IntroEventHandler(EventHandler):
	def __init__(self, state):
		EventHandler.__init__(self, state)
	
	def skip(self):
		self.state.state_mgr.go_to(self.state.state_mgr.main_menu)
	
	def handle_click(self, mouse_pos):
		self.skip()
	
	def handle_key(self, key):
		self.skip()
		
	def handle_event(self, event):
		pass



class MenuEventHandler(EventHandler):
	def __init__(self, state):
		EventHandler.__init__(self, state)


	def handle_key(self, key):
		pass
		
		
	def handle_click(self, mouse_pos):
		for option in self.state.menu.options:

			# if option was clicked
			if option.rect.collidepoint(pygame.mouse.get_pos()):

				# if option is available and there is a function for it
				if option.function and not option.greyed:

					# if there is a function parameter
					if not option.func_parameter == None :
						option.function(option.func_parameter)

					# else if no parameter
					else:
						option.function()
				
	
	def handle_event(self, event):
		for option in self.state.menu.options:
			
			# if mouse is over the option
			if option.rect.collidepoint(pygame.mouse.get_pos()):
				option.hovered = True
				break

			elif option.hovered:
				option.hovered = False



class GameEventHandler(EventHandler):
	
	def __init__(self, state):
		
		EventHandler.__init__(self, state)
		
		# selected action
		self.selected_action = None
		
	
	def handle_event(self, event):
				
		# handle AI movement and actions
		## movement
		if event.type == AI_MOVE_EVENT:
			# make move
			self.state.map.turn_controller.ai_move()
			
			# zero timer
			pygame.time.set_timer(AI_MOVE_EVENT, 0)
		
		## actions	
		elif event.type == AI_ACTION_EVENT:
			# make move
			self.state.map.turn_controller.ai_use_action()
			
			# zero timer
			pygame.time.set_timer(AI_ACTION_EVENT, 0)
	
	
	def handle_key(self, key):
		if key == pygame.K_ESCAPE:

			# go to menu with ESC
			self.state.state_mgr.go_to(self.state.state_mgr.main_menu)

			# set Resume Game option not greyed out
			self.state.state_mgr.main_menu.menu.options[0].greyed = False
	
	
	def handle_click(self, mouse_pos):
		# get current character
		character = self.state.map.turn_controller.current_character
		
		# if character is not walking and it is not AI's turn
		if not character.walking and not character.ai:
			# init status
			click_handled = False
			
			# recognize end turn button
			if self.state.map.view.end_turn_btn.rect.collidepoint(mouse_pos):
				character.end_turn()

				# set event handling state
				click_handled = True
		
			# recognize action buttons
			for button in self.state.map.view.action_buttons:
				if button.rect.collidepoint(mouse_pos):

					# get action
					action = character.actions[self.state.map.view.action_buttons.index(button)]
					self.selected_action = action
				
					# get action range
					self.state.map.set_in_range(action.range, character.coordinates, \
										  ignore_characters=True, ignore_non_walkable=True)
				
					# update range on map view based on action type
					if action.type == Action.DAMAGE or action.type == Action.STUN:
						self.state.map.view.update_range = ATTACK_RANGE
					elif action.type == Action.HEAL:
						self.state.map.view.update_range = HEAL_RANGE
					elif action.type == Action.BUFF:
						if action.strength >= 1:
							self.state.map.view.update_range = HEAL_RANGE
						elif action.strength < 1:
							self.state.map.view.update_range = ATTACK_RANGE
				
					# update character turn state
					character.has_moved = True
				
					# set state
					click_handled = True

			# if button was not clicked, get square clicked
			if not click_handled:

				# account for map positioning on screen
				mouse_x = mouse_pos[0] - self.state.map.view.rect.left - self.state.map.view.draw_offset_x - TILE_W / 2
				mouse_y = mouse_pos[1] - self.state.map.view.rect.top

				# convert coordinates
				map_x, map_y = screen_to_map(mouse_x, mouse_y)
				
				coordinates = Coordinates(map_x, map_y)
				
				# if character has not moved, i.e. should move now
				if not character.has_moved:

					# get shortest path to clicked square
					self.state.map.set_in_range(character.range, character.coordinates)
					path = self.state.map.get_shortest_path(character.coordinates, coordinates)
			
					# if path was found
					if path:
						character.walking, character.walk_path = True, path

						# clear range indicators on map
						self.state.map.in_range = []
						self.state.map.view.update_range = MOVEMENT_RANGE
					else:
						print("Out of range.")
		
				# if action is waiting for target
				elif self.selected_action:

					# get square clicked
					square = self.state.map.square_at(coordinates)

					# if square is in range
					if coordinates in self.state.map.in_range:

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