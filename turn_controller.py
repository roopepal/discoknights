from ai import Ai
from constants import MOVEMENT_RANGE, AI_DELAY, AI_MOVE_EVENT, AI_ACTION_EVENT
import pygame


class TurnController(object):
	
	def __init__(self, current_map):
		
		# set map
		self.map = current_map
		
		# set characters
		self.characters = []
		self.current_character = None
		
		# init turn status
		self.current_has_moved = False
		
		# init AI
		self.ai = Ai(self.map)
		

	def add_character(self, character):
		'''Adds a character to the turn controller.'''
		
		self.characters.append(character)

		# If this was the first character added, reset the turn cycle.
		if len(self.characters) == 1:
			self.reset()


	def reset(self):
		'''Resets the turn controller to the first character.'''
		
		if not len(self.characters) == 0:
			self.current_character = self.characters[0]
		else:
			print("No characters in turn controller.")


	def next(self):
		# update game state, including check for winner
		self.map.state.update()
		
		if self.map.state.running:
			# get next character
			current_index = self.characters.index(self.current_character)
			
			if current_index < ( len(self.characters) - 1 ):
				self.current_character = self.characters[ current_index + 1 ]
			else:
				self.current_character = self.characters[0]
			
			# if character is stunned or dead, skip it
			if self.current_character.stunned > 0:
				self.current_character.stunned -= 1
				self.next()
			elif self.current_character.dead:
				self.next()
	
			# if character is AI, initialize movement
			elif self.current_character.ai:
				
				# post ai movement event to the event queue
				pygame.time.set_timer(AI_MOVE_EVENT, AI_DELAY)
	
			# otherwise
			else:	 
				self.current_has_moved = False
				ret = self.map.view.trigger_event_text = "Move or choose an action"

		
	def ai_use_action(self):
		
		action = self.ai.get_action()

		# if got action, perform it
		if action:
			print(action.perform(self.current_character.target.coordinates))
			
			# end turn
			self.current_character.end_turn()
		else:
			# end turn
			self.current_character.end_turn()
		
		
	def ai_move(self):
		
		# get movement path
		walk_path = self.ai.get_next_move()

		# if got target
		if walk_path:
			# set character to walk
			self.current_character.walking = True
			self.current_character.walk_path = walk_path

			# clear range indicators on map
			self.map.in_range = []
			self.map.view.update_range = MOVEMENT_RANGE
			
		else:
			# post ai action event to the event queue
			pygame.time.set_timer(AI_ACTION_EVENT, AI_DELAY)