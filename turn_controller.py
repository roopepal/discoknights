from ai import Ai
from constants import MOVEMENT

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
		self.characters.append(character)

		# If this was the first character added, reset the turn cycle.
		if len(self.characters) == 1:
			self.reset()


	def reset(self):
		if not len(self.characters) == 0:
			self.current_character = self.characters[0]
		else:
			print("No characters in turn controller.")


	def was_moved(self):
		self.current_has_moved = True


	def next(self):
		# get next character
		current_index = self.characters.index(self.current_character)
		if current_index < ( len(self.characters) - 1 ):
			self.current_character = self.characters[ current_index + 1 ]
		else:
			self.current_character = self.characters[0]
		
		# if character is stunned or dead, skip it
		if self.current_character.stunned > 0:
			# set message variable here also								#TODO!
			self.current_character.stunned -= 1
			self.next()
		elif self.current_character.dead:
			self.next()
		
		# if character is AI, handle movement
		elif self.current_character.ai:
			self.move_ai()
		
		# otherwise
		else:	 
			self.current_has_moved = False
			ret = "Move or choose an action."
	
			return ret
			
	def ai_use_action(self):
		action, target_coordinates = self.ai.get_action()
		
		# if got target, perform action
		if target_coordinates:
			action.perform(target_coordinates)
			
			# end turn
			self.current_character.end_turn()
		else:
			# end turn
			self.current_character.end_turn()
		
		
	def move_ai(self):
		# get movement path
		walk_path = self.ai.get_next_move()

		# if got target
		if walk_path:
			# set character to walk
			self.current_character.walking = True
			self.current_character.walk_path = walk_path

			# clear range indicators on map
			self.map.in_range = []
			self.map.view.update_range = MOVEMENT
			
		else:
			self.ai_use_action()
			
		