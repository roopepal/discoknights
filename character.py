from action import Action
from character_view import CharacterView
from constants import MOVEMENT
from coordinates import screen_to_map
from direction import *
from queue import Queue


class Character(object):
	'''
	Defines a game character.
	'''
	
	def __init__(self, name, max_health, move_range, is_ai, stand_sprites, walk_sprites=None):
		'''Constructs a new game character.'''
		self.name = name
		self.coordinates = None
		self.facing = None
		self.map = None
		self.max_health = max_health
		self.health = max_health
		self.range = move_range
		self.actions = []
		self.stunned = 0
		
		# AI
		self.ai = is_ai
		self.target = None
		
		# sprite paths
		self.stand_sprite_paths = stand_sprites
		self.walk_sprite_paths = walk_sprites
		
		# initialize states
		self.dead = False
		self.has_moved = False
		self.walking = False
		self.walk_to = None
	
	
	def added_to_map(self, current_map, coordinates, facing):
		# Updates the character's attributes when the character is added to a map.
		self.map = current_map
		self.coordinates = coordinates
		self.facing = facing
		
		
	def set_view(self):
		# initiate CharacterView
		self.view = CharacterView(self)


	def damage(self, amount):
		# Decreases the character's health points by the given amount.
		self.health -= amount
		if self.health <= 0:
			self.dead = True
			self.health = 0

	
	def stun(self, turns):
		# Stuns the character for the given amount of turns.
		self.stunned += turns

		
	def heal(self, amount):
		# Increases the character's health points by the given amount, up to max health.
		self.health += amount
		if self.health > self.max_health:
			self.health = self.max_health
	
	
	def add_action(self, action_type, strength, action_range, description):
		# Adds an action that the character can perform.
		self.actions.append( Action(self, action_type, strength, action_range, description) )
		
		
	def use_action(self, index, target_coordinates):
		'''Uses the action at the given index. For command line use only.'''
		# Performs the given action at the given target coordinates.
		if not self.has_turn():
			print("It's not {:}'s turn.".format(self.name))
			return False
		elif self.stunned > 0:
			print("{:} is stunned.".format(self.name))
			return False
		else:
			self.actions[index-1].perform(target_coordinates)
			self.end_turn()
			return True
	
	
	def turn_to_direction(self, direction):
		# Changes the direction the character is facing to given direction.
		self.facing = direction

		
	def turn_towards(self, coordinates):
		# Changes the direction the character is facing towards given coordinates.
		if coordinates.x == self.coordinates.x and coordinates.y < self.coordinates.y:
			self.facing = UP
		elif coordinates.x == self.coordinates.x and coordinates.y > self.coordinates.y:
			self.facing = DOWN
		elif coordinates.x < self.coordinates.x and coordinates.y == self.coordinates.y:
			self.facing = LEFT
		elif coordinates.x > self.coordinates.x and coordinates.y == self.coordinates.y:
			self.facing = RIGHT


	def has_turn(self):
		# Returns True if it is this character's turn.
		return self.map.turn_controller.current_character == self
	
	
	def end_turn(self):
		# Reset move status
		self.has_moved = False

		# Give turn to next character
		self.map.turn_controller.next()

		# Update range to next character
		next_char = self.map.turn_controller.current_character
		self.map.set_in_range(next_char.range, next_char.coordinates)
		self.map.view.update_range = MOVEMENT
		
		# Update character info and actions
		self.map.view.update_char_info = True
		self.map.view.update_action_buttons()

			
	def get_shortest_path(self, coordinates, ignore_range=False):
		'''
		Gets the shortest path from the character to the given
		coordinates. Returns a list of coordinates.
		
		Assumes that the method get_movement_range() has been run
		before this, so that the range_counts in squares are correct.

		Based on the Lee algorithm.
		'''

		start = self.coordinates
		end = coordinates
		path = []
				
		# last step is known, it is the target coordinates
		path.append(end)
		
		# if the target is not in range, there is no path there
		if not ignore_range and not end in self.map.in_range:
			print("Not in range, cannot get path.")
			return False
		
		# trace back from the end
		current_range_count = self.map.square_at(end).range_count 
		
		while True:
						
			neighbors = end.get_neighbors()
			
			for n in neighbors:
				# if n is the start point, the full path has been found
				if n == start:
					# reverse path because we started from the end
					path.reverse()
					return path

				square = self.map.square_at(n)

				# if square is reachable, has a smaller range count from 
				# the starting point, and is walkable and empty
				if not square.range_count == 0 and square.range_count < current_range_count \
				  and square.type.walkable and square.is_empty():
					# add to the shortest path
					path.append(n)
					# go on to finding the next step
					end = n
					current_range_count = self.map.square_at(end).range_count
					break
						
	
	def move_forward(self):
		'''Moves one step to the direction the character is facing.'''
		
		target_coordinates = self.coordinates.get_neighbor(self.facing)
		target_square = self.map.square_at(target_coordinates)
		
		if target_square.type.walkable and target_square.is_empty():
			self.map.square_at(self.coordinates).character = None
			self.coordinates = target_coordinates
			self.map.square_at(target_coordinates).character = self
			return True
		else:
			return False
		
		
	def move_to_direction(self, direction):
		'''Moves one step to the given direction.'''
		
		self.turn_to_direction(direction)
		return self.move_forward()	  
		
		
	def move_to_coordinates(self, target):
		'''
		Moves the character to the given target coordinates,
		if the coordinates are within the move range of the character.
		For command line use only.
		'''
		
		if not self.has_turn():
			print("It's not {:}'s turn.".format(self.name))			# Debugging print
			return False
		elif self.stunned:
			print("{:} is stunned".format(self.name))
		ret = False
		
		squares_within_range = self.within_range(self.range)
		
		if self.map.square_at(target) in squares_within_range:
			shortest_path = self.get_shortest_path(target)
			for step in shortest_path:
								
				target_x = step.x
				target_y = step.y
				self_x = self.coordinates.x
				self_y = self.coordinates.y
				
				if ( target_x - self_x == 0 ) and ( target_y - self_y == -1 ):
					ret = self.move_to_direction(UP)
				if ( target_x - self_x == 1 ) and ( target_y - self_y == 0 ):
					ret = self.move_to_direction(RIGHT)
				if ( target_x - self_x == 0 ) and ( target_y - self_y == 1 ):
					ret = self.move_to_direction(DOWN)
				if ( target_x - self_x == -1 ) and ( target_y - self_y == 0 ):
					ret = self.move_to_direction(LEFT)
			
			self.has_moved = True
			return ret
		
		elif not self.map.square_at(target) in squares_within_range:
			print("Out of range.")														# Debugging print
		
		else:
			return ret
				
	def __str__(self):
		return self.name