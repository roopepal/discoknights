from constants import MUSIC_DIR, RED, GREEN
import pygame, os

class Action(object):
	'''
	Defines an action that characters can use.
	'''
	
	# Action types
	DAMAGE = 1
	HEAL = 2
	STUN = 3
	BUFF = 4
	
	def __init__(self, character, action_type, strength, action_range, name, sound=None):
		'''Constructor'''
		
		self.type = action_type
		self.strength = strength
		self.range = action_range
		self.name = name
		self.character = character
		
		if sound:
			self.sound = pygame.mixer.Sound(os.path.join(MUSIC_DIR, sound))
		else:
			self.sound = None


	def perform(self, target_coordinates):
		'''Performs the action and triggers the effect text above the affected character.'''
		
		# Play action sound if sound effects are enabled and there is a sound
		if self.sound and self.character.map.state.state_mgr.sound_effects:
			self.sound.play()
		
		# Turn towards target
		self.character.turn_towards(target_coordinates)
		
		# Get character at target square
		target_character = self.character.map.square_at(target_coordinates).character
		
		# If no character at the target coordinates
		if not target_character:
			return "Missed!"
			
			# Reset buff multiplier
			self.character.buff_multiplier = 1
		
		else:
			if self.type == Action.DAMAGE:
				target_character.damage(self.strength * self.character.buff_multiplier)
				effect_text = "-" + str(int(self.strength * self.character.buff_multiplier))
				color = RED
				
			elif self.type == Action.HEAL:
				target_character.heal(self.strength * self.character.buff_multiplier)
				effect_text = "+" + str(int(self.strength * self.character.buff_multiplier))
				color = GREEN
				
			elif self.type == Action.STUN:
				target_character.stun(self.strength)
				effect_text = "STUN"
				color = RED
				
			elif self.type == Action.BUFF:
				target_character.buff(self.strength)
				if self.strength < 1:
					effect_text = "WEAKEN"
					color = RED
				else:
					effect_text = "BUFF"
					color = GREEN
			
			# trigger effect text
			self.character.map.view.trigger_effect_text(effect_text, color, target_coordinates)
			
			# Reset buff multiplier
			self.character.buff_multiplier = 1
			
			return "Used '" + self.name + "!"


	def __str__(self):
		return self.name