from action import Action
import random

class Ai(object):	 
	def __init__(self, current_map):
		self.map = current_map
		self.character = None


	def get_target(self):
		'''Returns the closest enemy character and the shortest path to it.'''
		self.character = self.map.turn_controller.current_character
		
		# Get possible targets, do not include self and other AI characters.
		possible_targets = []

		for c in self.map.characters:
			if not c.ai and not c.dead:
				possible_targets.append(c)

		# Prepare for Lee algorithm for distance calculations. Give every square a distance
		# value. A large range ensures that all reachable squares on the map get covered.
		full_range = self.character.map.width * self.character.map.height - 1
		self.map.set_in_range(full_range, self.character.coordinates)
				
		closest_enemy = None
		closest_enemy_path = None
		closest_enemy_path_len = None

		for t in possible_targets:
			# check that character is reachable
			reachable = False
			if not self.map.square_at(t.coordinates).range_count == 0:
				reachable = True

			if reachable:
				# get shortest path to the target
				path = self.character.get_shortest_path(t.coordinates, ignore_range=True)
				if path:
					path_len = len(path)
					
					print(t, path_len)
								
					if not closest_enemy_path_len or path_len < closest_enemy_path_len:
						closest_enemy = t
						closest_enemy_path = path
						closest_enemy_path_len = path_len

					if len(closest_enemy_path) == 1:
						closest_enemy_path = []
						
		print(str(self.character) + " got target: " + str(closest_enemy))
		
		return closest_enemy, closest_enemy_path
		

	def get_next_move(self):
		'''Returns the coordinates on the path to the target character that are furthest but still in movement range.'''
		self.character.target, steps = self.get_target()

		if steps and len(steps) > 0:
			self.map.set_in_range(self.character.range, self.character.coordinates)
		
			for i in range( len(steps) ):
				if steps[-1 - i] in self.map.in_range:
					return steps[0: -i]
		
		return False


	def get_action(self):
		'''Returns an action and the coordinates to perform it on.
		   The action with the highest possible damage caused is selected.'''
		
		# set helper variables
		target_in_range = False
		actions = self.character.actions
		chosen_action = None
		
		# get the longest range in the character's actions
		longest_range_action = None
		for action in actions:
			if longest_range_action == None or action.range > longest_range_action.range:
				longest_range_action = action
						
		# get coordinates within the longest range, ignore characters and
		# non-walkable squares because the range is for an action
		self.map.set_in_range(longest_range_action.range, self.character.coordinates,\
								ignore_characters=True, ignore_non_walkable=True)
				
		# check if target character is in action range
		for coordinates in self.map.in_range:
			square = self.map.square_at(coordinates)
			if square.character and square.character == self.character.target:
				target_in_range = True

		# if target is in range		
		if target_in_range:
			distance_to_target = len(self.character.get_shortest_path(self.character.target.coordinates))
			
			# Get the action with the highest damage and enough range.
			# A random term may affect the choice: a modifier drawn from 
			# the normal distribution is added to the damage when choosing,
			# so the AI is rational most of the time but not always. 
			# If a stun action is possible, choose action or stun randomly.
			highest_damage = None
			highest_damage_action = None
			
			for action in actions:
				if action.range >= distance_to_target:
					if action.type == Action.DAMAGE:
						random_term = random.normalvariate(0, 7.75)
						damage = action.strength + random_term
					#elif action.type == Action.STUN:
					#	 damage = 
						
					# if damage is higher than for any action so far
					if highest_damage == None or damage > highest_damage:
						highest_damage = damage
						highest_damage_action = action
					
			return highest_damage_action
		else:
			return False


	def make_move(self):
		'''Moves the current AI player towards its target. For the command line version, not used in the GUI version.'''
		
		target = self.get_next_move()
				
		if target:
			self.character.move_to_coordinates(target)
			print(str(self.character) + " moved to " + str(target))
		
		self.character.end_turn()