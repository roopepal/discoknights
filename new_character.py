from direction import *
from action import Action
from constants import *
from coordinates import map_to_screen, screen_to_map
from queue import Queue
import pygame, os


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
		self.ai = is_ai
		
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
		print(self.name, self.stunned)

		
	def heal(self, amount):
		# Increases the character's health points by the given amount, up to max health.
		self.health += amount
		if self.health > self.max_health:
			self.health = self.max_health
	
	
	def add_action(self, action_type, strength, action_range, description):
		# Adds an action that the character can perform.
		self.actions.append( Action(self, action_type, strength, action_range, description) )
		
		
	def use_action(self, index, target_coordinates):
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
		# Changes the direction the character is facing.
		self.facing = direction


	def has_turn(self):
		# Returns True if it is this character's turn.
		return self.map.turn_controller.current_character == self
	
	
	def end_turn(self):
		# Reset move status
		self.has_moved = False
		
		# Give turn to next character
		self.map.turn_controller.next()
		
		# Update range to next character
		self.map.in_range = self.map.turn_controller.current_character.get_movement_range()
		self.map.view.update_range = MOVEMENT
		
		# Update character info and actions
		self.map.view.update_char_info = True
		self.map.view.update_action_buttons()
				
	
	def get_movement_range(self, move_range=None):
		'''
		Returns a list of the coordinates that are within the movement
		range from the character. For movement, a square has to be
		walkable and empty.
		
		Also sets the range_counts for squares to be used with the
		get_shortest_path() method.
		
		Allows for an optional custom range.
		
		Based on the BFS algorithm.
		'''
		if not move_range:
			move_range = self.range
		
		in_range = []
		squares_in_map = self.map.squares
		start = self.coordinates
		queue = Queue()

		# reset the status of all squares
		for row in squares_in_map:
			for square in row:
				# visited flag
				square.visited = False
				# steps from start
				square.range_count = 0
		
		# put the start coordinates into the queue
		queue.put(start)
		self.map.get_square_at(start).visited = True

		while not queue.empty():
			# get next coordinates from queue
			current = queue.get()
			# get neighboring coordinates
			neighbors = current.get_neighbors()
			for n in neighbors:
				# get neighbor square at coordinates n
				square = self.map.get_square_at(n)
				# if there is a square at n
				if square:
					# if the square is walkable and empty
					if square.visited == False and square.type.walkable and square.is_empty():
						# set range count from start to be one more than for the current square
						square.range_count = self.map.get_square_at(current).range_count + 1
						# if square is still within range, put in queue
						if square.range_count <= move_range:
							square.visited = True
							queue.put(n)
							# if not already in the list that will be returned, add
							if not square.coordinates in in_range:
								in_range.append(square.coordinates)
									
		# return the list of coordinates
		
		return in_range

			
	def get_shortest_path(self, coordinates, for_ai = False):
		'''
		Gets the shortest path from the character to the given
		coordinates. Returns a list of coordinates.
		
		Assumes that the method get_movement_range() has been run
		before this, so that the range_counts in squares are correct.

		Based on the Lee algorithm.
		'''
		in_range = self.map.in_range
		start = self.coordinates
		end = coordinates
		path = []
		
		# last step is known, it is the target coordinates
		path.append(end)
		
		# if the target is not in range, there is no path there
		if not end in in_range:
			print("Not in range.")
			return False
		
		# trace back from the end
		current_range_count = self.map.get_square_at(end).range_count 
		
		while True:
			
			neighbors = end.get_neighbors()
			
			for n in neighbors:
				# if n is the start point, the full path has been found
				if n == start:
					# reverse path because we started from the end
					path.reverse()
					return path

				square = self.map.get_square_at(n)
				# if square has a smaller range count from the starting point, and is walkable and empty
				if square.range_count < current_range_count and square.type.walkable:
					if for_ai:
						# add to the shortest path
						path.append(n)
						# go on to finding the next step
						end = n
						current_range_count = self.map.get_square_at(end).range_count
						break
					elif square.is_empty():
						# add to the shortest path
						path.append(n)
						# go on to finding the next step
						end = n
						current_range_count = self.map.get_square_at(end).range_count
						break
						
	
	def move_forward(self):
		'''
		Moves one step to the direction the character is facing.
		'''
		target_coordinates = self.coordinates.get_neighbor(self.facing)
		target_square = self.map.get_square_at(target_coordinates)
		
		if target_square.type.walkable and target_square.is_empty():
			self.map.get_square_at(self.coordinates).character = None
			self.coordinates = target_coordinates
			self.map.get_square_at(target_coordinates).character = self
			return True
		else:
			return False
		
		
	def move_to_direction(self, direction):
		'''
		Moves one step to the given direction.
		'''
		self.turn_to_direction(direction)
		return self.move_forward()	  
		
		
	def move_to_coordinates(self, target):
		'''
		Moves the character to the given target coordinates, if the coordinates are within the move range of the character.
		'''
		if not self.has_turn():
			print("It's not {:}'s turn.".format(self.name))			# Debugging print
			return False
		elif self.stunned:
			print("{:} is stunned".format(self.name))
		ret = False
		
		squares_within_range = self.within_range(self.range)
		
		if self.map.get_square_at(target) in squares_within_range:
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
		
		elif not self.map.get_square_at(target) in squares_within_range:
			print("Out of range.")														# Debugging print
		
		else:
			return ret
				
	def __str__(self):
		return self.name



class CharacterView(object):
	
	def __init__(self, character):
		self.character = character
		
		# create dicts for images
		self.stand_images = {}
		self.walk_images = {}
		
		# position character in the center of the isometric tile
		self.draw_offset_x = 13
		self.draw_offset_y = -30
		
		# load sprite images
		# there is one standing sprite for each direction
		for sprite_path in self.character.stand_sprite_paths:
			image = pygame.image.load( os.path.join(GRAPHICS_DIR, self.character.stand_sprite_paths[sprite_path] ) )
			self.stand_images[sprite_path] = image
		
		# check if walking sprites exist
		if self.character.walk_sprite_paths:			
			# create lists for walking sprites
			for direction in get_directions():
				self.walk_images[direction[1]] = []
			
			# there are multiple sprites for each walking direction
			for direction in self.character.walk_sprite_paths:
				for sprite_path in self.character.walk_sprite_paths[direction]:
					image = pygame.image.load( os.path.join(GRAPHICS_DIR, sprite_path ) )
					self.walk_images[direction].append(image)
		
		# set current image
		self.image = self.stand_images[ self.character.facing[1] ]
		self.rect = image.get_rect()
		
		# set position the first time
		self.set_screen_pos()
		
		# initialize animation frame index
		self.anim_frame = 0
		# initialize animation frame count for half speed updating
		self.frame_count = 0
	
	
	def set_screen_pos(self):
		# get position on map
		map_pos = self.character.coordinates
		# convert to screen coordinates
		screen_x, screen_y = map_to_screen(map_pos.x, map_pos.y)
		# add horizontal draw offset to prevent negative x coordinates
		screen_x += self.character.map.view.draw_offset_x
		# add map offset on screen
		screen_x += self.character.map.view.rect.topleft[0]
		screen_y += self.character.map.view.rect.topleft[1]
		# set position on screen
		self.rect.x = screen_x + self.draw_offset_x
		self.rect.y = screen_y + self.draw_offset_y
	
	
	def get_next_walk_frame(self):
		# get number of sprites
		anim_len = len(self.walk_images[self.character.facing[1]])

		# increment frame count
		self.frame_count += 1
		
		# check if half speed, full speed may be too fast
		if HALF_SPEED_WALK:
			if self.frame_count % 2 == 0:
				self.anim_frame += 1
		else:
			self.anim_frame += 1
		
		# reset if over number of frames
		if self.anim_frame > anim_len - 1:
			self.anim_frame = 0
		
		# return the next image
		return self.walk_images[self.character.facing[1]][self.anim_frame]
		
	
	def update(self):
		if self.character.walking:
			# set turn status to moved
			self.character.has_moved = True
			
			# get current step
			step = self.character.walk_path[0]
			
			# set facing direction
			if self.character.coordinates.is_top_neighbor(step):
				self.character.facing = UP
			elif self.character.coordinates.is_right_neighbor(step):
				self.character.facing = RIGHT
			elif self.character.coordinates.is_bottom_neighbor(step):
				self.character.facing = DOWN
			elif self.character.coordinates.is_left_neighbor(step):
				self.character.facing = LEFT
			
			# set image
			if self.walk_images:
				self.image = self.get_next_walk_frame()
			else:
				self.image = self.stand_images[self.character.facing[1]]
			
			# move image to facing direction
			self.rect.move_ip(self.character.facing[2][0], self.character.facing[2][1])
			
			# get target screen coordinates
			target_x, target_y = map_to_screen(step.x, step.y)
			target_x += self.character.map.view.rect.topleft[0] + self.character.map.view.draw_offset_x + self.character.view.draw_offset_x
			target_y += self.character.map.view.rect.topleft[1] + self.character.view.draw_offset_y
			
			# if reached step target, go to next step
			if self.rect.topleft == (target_x, target_y):
				
				# move in background logic
				self.character.move_forward()
				
				# remove walked step
				self.character.walk_path.remove(step)
				
				if len(self.character.walk_path) == 0:
					# stop walking
					self.character.walking = False
					
					# set standing sprite
					self.image = self.stand_images[self.character.facing[1]]
					
					# get AI action
					if self.character.ai:
						self.character.map.turn_controller.ai_use_action()
						
			
	def draw(self):
		self.character.map.view.screen.blit(self.image, self.rect)

