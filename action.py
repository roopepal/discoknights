from queue import Queue

class Action(object):
	
	# Action types
	DAMAGE = 1
	HEAL = 2
	STUN = 3
	
	def __init__(self, character, action_type, strength, action_range, name):
		self.type = action_type
		self.strength = strength
		self.range = action_range
		self.name = name
		self.character = character


	def perform(self, target_coordinates):
		# Turn towards target
		self.character.turn_towards(target_coordinates)
		# Get character at target square
		target_character = self.character.map.square_at(target_coordinates).character
		# If no character at the target coordinates
		if not target_character:
			print("Missed!")
			return "Missed!"
		else:
			if self.type == Action.DAMAGE:
				target_character.damage(self.strength)
			elif self.type == Action.HEAL:
				target_character.heal(self.strength)
			elif self.type == Action.STUN:
				target_character.stun(self.strength)
			
			# update effect text
			self.character.map.view.trigger_effect_text = (self, target_coordinates)
			
			return "Used '" + self.name + "' on " + self.character.map.square_at(target_coordinates).character.name


	def __str__(self):
		return self.name