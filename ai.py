from action import Action
import random

class Ai(object):	 
	def __init__(self, current_map):
		self.map = current_map
		self.character = None

	def get_target(self, get_team_member=False):
		'''Chooses the target enemy player based on distance and health left.
		Possible and reachable target characters are given ranks by distance
		to it and health left, and the one with the lowest average rank
		is chosen as the target.'''
		
		# find a target for the character in turn
		self.character = self.map.turn_controller.current_character
		
		# Get possible targets, do not include self and other characters in the same team.
		possible_targets = []

		for c in self.map.characters:
			if get_team_member:
				# get those in the same team and not self
				if (not c.dead) and (c.team == self.character.team) and (not c == self.character):
					possible_targets.append(c)
			
			else:
				# get those in the other team
				if (not c.dead) and (not c.team == self.character.team):
					possible_targets.append(c)		
				
		# Prepare for Lee algorithm for distance calculations. Give every square a distance
		# value. A large range ensures that all reachable squares on the map get covered.
		full_range = self.character.map.width * self.character.map.height - 1
		self.map.set_in_range(full_range, self.character.coordinates)
		
		# Rank possible targets by their distance and remaining health
		distances = {}
		healths = {}
		
		# save non-reachable to be removed from possible targets
		non_reachable = []
		
		for t in possible_targets:
			
			# path length
			# check that character is reachable
			reachable = False
						
			if not self.map.square_at(t.coordinates).range_count == 0:
				reachable = True
				
			if reachable:
				# get shortest path to the target
				path = self.map.get_shortest_path(self.character.coordinates, t.coordinates, ignore_range=True)
				
				if path:
					distances[t] = len(path)
			
				# remaining health
				healths[t] = t.health
							
			# if not reachable, remove from possible targets
			else:
				non_reachable.append(t)
		
		# remove non-reachable from possible targets
		for c in non_reachable:
			possible_targets.remove(c)
		
		# check that there are any reachable targets
		if len(distances) == 0:
			return False, False
		
		# Get characters in lists sorted by distance and health
		sorted_by_distance = sorted(distances, key=distances.__getitem__)
		sorted_by_health = sorted(healths, key=healths.__getitem__)
				
		# Calculate ranks, ties result in the same rank
		distance_ranks = {}
		health_ranks = {}
		
		# distance ranks
		previous = None
		rank = 0
		
		for char in sorted_by_distance:
			# if value larger than the previous, or there is no previous
			if not previous or distances[char] > previous:
				rank += 1
				previous = distances[char]
			# put to dict
			distance_ranks[char] = rank
		
		# health ranks
		previous = None
		rank = 0
		
		for char in sorted_by_health:
			# if value larger than the previous, or there is no previous
			if not previous or healths[char] > previous:
				rank += 1
				previous = healths[char]
			# put to dict
			health_ranks[char] = rank
		
		# Calculate averages of the ranks
		avg_ranks = {}
		
		for t in possible_targets:
			avg_ranks[t] = (distance_ranks[t] + health_ranks[t]) / 2


		#print("Distance ranks: " + str([(c.name, v) for c, v in distance_ranks.items()]))
		#print("Health ranks: " + str([(c.name, v) for c, v in health_ranks.items()]))
		#print("Average rankg: " + str([(c.name, v) for c, v in avg_ranks.items()]))
		

		# Choose target with the minimum average rank
		chosen_target = min(avg_ranks, key=avg_ranks.__getitem__)
		
		# Get path to the chosen target
		chosen_target_path = self.map.get_shortest_path(self.character.coordinates, chosen_target.coordinates, ignore_range=True)
				
		# Return character and the path to it
		return chosen_target, chosen_target_path


	def get_next_move(self):
		'''Returns the coordinates on the path to the target character up to the maximum movement range.'''
		self.character.target, steps = self.get_target()

		if steps and len(steps) > 0:
			self.map.set_in_range(self.character.range, self.character.coordinates)
		
			for i in range( len(steps) ):
				if steps[-1 - i] in self.map.in_range:
					return steps[0: -i]
		
		return False


	def choose_action(self, team_action=False):
		'''Returns an action and the target to perform it on.
		The action with the highest effect caused it selected. The effect
		calculation includes a random element to introduce some irrationality
		to the AI.'''
		
		# get target character
		if team_action:
			target = self.get_target(get_team_member=True)[0]
		else:
			target = self.get_target()[0]
		
		# get actions
		actions = self.character.actions
		
		# if the character has no actions
		if len(actions) == 0:
			return False, False
		
		# get the longest range action
		furthest_action = None
		
		## if team action is wanted
		if team_action:
			
			for action in actions:
						
				if action.type == Action.HEAL \
				  or (action.type == Action.BUFF and action.strength >= 1):
				
					if furthest_action == None or action.range > furthest_action.range:
						furthest_action = action
		
		## if an attack is wanted
		else:
			
			for action in actions:
						
				if action.type in [Action.DAMAGE, Action.STUN] \
				  or (action.type == Action.BUFF and action.strength < 1):
				
					if furthest_action == None or action.range > furthest_action.range:
						furthest_action = action
		
		# check that there was a wanted type of action
		if not furthest_action:
			return False, False
		
		# get coordinates within the longest range action, ignore characters and
		# non-walkable squares because the range is for an action
		self.map.set_in_range(furthest_action.range, self.character.coordinates, \
								ignore_characters=True, ignore_non_walkable=True)
		
		# get path and distance to target
		path_to_target = self.map.get_shortest_path(self.character.coordinates, target.coordinates)
		
		# check that target is in range, otherwise return no action and target
		if not path_to_target:
			return False, False
			
		# get path length
		distance_to_target = len(path_to_target)
		
		# Get the action with the highest damage and enough range.
		# A random term may affect the choice: a modifier drawn from 
		# the normal distribution is added to the damage when choosing,
		# so the AI is rational most of the time but not always. 

		highest_effect = None
		highest_effect_action = None
		
		# select team action if wanted
		if team_action:
			
			for action in actions:
				
				# only take team helping actions
				if action.type == Action.HEAL \
				  or (action.type == Action.BUFF and action.strength >= 1):
			
					# if action has enough range
					if action.range >= distance_to_target:
			
						if action.type == Action.HEAL:
							random_term = random.normalvariate(0, 7.75)
							effect = action.strength + random_term
				
						# a buff action equals 10 times its strength in the base case
						## e.g. a buff of 1.5 would get an effect value of 15
						elif action.type == Action.BUFF:
							random_term = random.normalvariate(0, 7.75)
							effect = 10 * action.strength + random_term
					
						# if damage is higher than for any action so far, select this action
						if highest_effect == None or effect > highest_effect:
							highest_effect = effect
							highest_effect_action = action
		
		# select attack action if wanted
		else:
		
			for action in actions:
			
				# only take attack actions
				if action.type in [Action.DAMAGE, Action.STUN] \
				  or (action.type == Action.BUFF and action.strength < 1):
			
					# if action has enough range
					if action.range >= distance_to_target:
			
						if action.type == Action.DAMAGE:
							random_term = random.normalvariate(0, 7.75)
							effect = action.strength + random_term
				
						# a stun action equals 20 effect in the base case
						elif action.type == Action.STUN:
							random_term = random.normalvariate(0, 7.75)
							effect = 20 + random_term
					
						# a negative buff action equals 15 effect in the base case 
						elif action.type == Action.BUFF and action.strength < 1:
							random_term = random.normalvariate(0, 7.75)
							effect = 10 / action.strength + random_term
					
						# if effect is higher than for any action so far, select this action
						if highest_effect == None or effect > highest_effect:
							highest_effect = effect
							highest_effect_action = action


		# Return the selected action and target.
		
		return highest_effect_action, target


	def get_action(self):
		'''Returns an action and the target to perform it on.
		   The AI attacks enemy players most of the time,
		   but may help team mates if there is a possibility.'''
		
		attack_action, attack_action_target = self.choose_action()
		
		team_action, team_action_target = self.choose_action(team_action=True)		
		
		# if both attacking and helping a teammate are possible
		if attack_action and team_action:
			is_aggressive = random.random()
			
			# the AI is aggressive 80% of the time
			if is_aggressive > 0.2:
				return attack_action, attack_action_target
			
			else:
				return team_action, team_action_target
		
		# if only attacking is possible
		elif attack_action:
			return attack_action, attack_action_target
		
		# if only helping a teammate is possible
		elif team_action:
			return team_action, team_action_target

		# if no action possible
		else:
			return False, False


	def make_move(self):
		'''Moves the current AI player towards its target. For command line use.'''
		
		target = self.get_next_move()
				
		if target:
			self.character.move_to_coordinates(target)
			print(str(self.character) + " moved to " + str(target))
		
		self.character.end_turn()