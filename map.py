from square import Square
from constants import *
from coordinates import Coordinates, map_to_screen
from map_object import MapObject
from map_view import MapView
from object_type import ObjectType
from queue import Queue
from character import Character
from turn_controller import TurnController
import pygame, os


class Map(object):
	'''
	Defines the map object that contains the game world.
	'''
	
	def __init__(self, state):
		'''Constructor'''
		
		# set program state
		self.state = state
		
		self.characters = []
		self.objects = []
		self.squaretypes = {}
		self.object_types = {}
		self.turn_controller = TurnController(self)

		# list of coordinates in range for character movement and actions
		self.in_range = None


	def build_squares(self, height, width, squares_input, team1_start, team2_start, init_view=True):
		'''Builds the map based on the given input.'''
		
		# set dimensions
		self.height = height
		self.width = width
		
		# set starting positions for characters
		self.team1_start = team1_start
		self.team2_start = team2_start

		# prepare empty slots for squares
		self.squares = height * [None]
		for y in range(height):
			self.squares[y] = width * [None]
		
		# fill slots with squares
		for y in range(height):
			for x in range(width):
				
				# separate square type and possible object
				input_parts = squares_input[y][x].split(".")
				
				# only allow one object in square, print error but do not crash program
				if len(input_parts) > 2:
					print("There cannot be more than one object in a square. Only the first object added.")
				
				# if square type is defined, insert square				 
				if input_parts[0] in self.squaretypes.keys():
					self.squares[y][x] = Square( Coordinates(x,y), self.squaretypes[input_parts[0]] )
		
				# if there is an object to add, insert object
				if len(input_parts) > 1:
					self.add_object( Coordinates(x,y), MapObject(self.object_types[input_parts[1]]) )
		
		if init_view:
			# initialize MapView
			self.view = MapView(self)
			
			# initialize MapObjectViews
			for o in self.objects:
				o.set_view()
			
	
	def start_game(self):
		'''Starts the game and gives the turn to the first character.'''
		
		# update range
		character = self.turn_controller.current_character
		self.set_in_range(character.range, character.coordinates)
		self.view.update_range = MOVEMENT_RANGE
		
		# update action buttons
		self.view.update_action_buttons()
		
		# update character info
		self.view.update_char_info = True
		
		# show "PLAY!" message
		self.view.trigger_event_text("PLAY!", font=XXL_FONT)
		
		# if AI character is first in turn
		if character.ai:
			pygame.time.set_timer(AI_MOVE_EVENT, AI_DELAY)
		
	
	def square_at(self, coordinates):
		'''Returns the square at the given coordinates.'''
		
		if self.contains_coordinates(coordinates):
			square = self.squares[coordinates.y][coordinates.x]
			if square:
				return square
			else:
				return False
		else:
			return False
	
	
	def add_squaretype(self, squaretype):
		'''Adds the square type if it does not exist yet.'''
		
		if not squaretype.short in self.squaretypes:
			self.squaretypes[squaretype.short] = squaretype
		 
			
	def add_object_type(self, object_type):
		'''Adds the object type if it does not exist yet.'''
		
		if not object_type.short in self.object_types:
			self.object_types[object_type.short] = object_type
	 
	  
	def add_character(self, character, coordinates, facing, init_view=True):
		'''Adds the given character on the map, and updates the turn controller's
		and the character's attributes.'''
		
		if self.square_at(coordinates).is_empty():
			# add to the map
			self.characters.append(character)
			self.square_at(coordinates).character = character
			
			# add to the turn controller
			self.turn_controller.add_character(character)
			
			# update the character's attributes
			character.added_to_map(self,coordinates,facing, init_view=init_view)
			
		else:
			print("Square wasn't empty. Cannot add character.")
	
	
	def add_object(self, coordinates, map_object):
		'''Adds the given object on the map, and updates the object's attributes.'''
		
		if self.square_at(coordinates).is_empty():
			# add to the map
			self.objects.append(map_object)
			self.square_at(coordinates).object = map_object
			
			# update the character's attributes
			map_object.added_to_map(self, coordinates)
		else:
			print("Square wasn't empty. Cannot add object.")
	
	
	def contains_coordinates(self, coordinates):
		'''Returns True or False based on if the map contains the given coordinates.'''
		
		return 0 <= coordinates.x < self.width and 0 <= coordinates.y < self.height
	

	def set_in_range(self, max_range, start, ignore_characters=False, ignore_non_walkable=False):
		'''
		Sets the list of the coordinates that are within the given
		range from the given start coordinates.
		
		Also sets the range_counts for squares to be used with the
		get_shortest_path() method of the Character class.
		
		Based on the BFS algorithm.
		'''
		
		in_range = []
		queue = Queue()

		# reset the status of all squares
		for row in self.squares:
			for square in row:
				# visited flag
				square.visited = False
				# steps from start
				square.range_count = 0
		
		# put the start coordinates into the queue
		queue.put(start)
		self.square_at(start).visited = True

		while not queue.empty():
			# get next coordinates from queue
			current = queue.get()
			# get neighboring coordinates
			neighbors = current.get_neighbors()
			for n in neighbors:
				# get neighbor square at coordinates n
				square = self.square_at(n)
				# if there is a square at n
				if square:
					# if the square has not been visited
					if square.visited == False:
						# set range count from start to be one more than for the current square
						square.range_count = self.square_at(current).range_count + 1
						# if square is still within range, put in queue
						if square.range_count <= max_range:
							square.visited = True
							# check for conditions given
							if (ignore_characters and square.type.walkable and not square.object) \
							  or (ignore_non_walkable and square.is_empty()) \
							  or (square.type.walkable and square.is_empty()):
								# put suitable coordinates in queue
								queue.put(n)
								# if not already in the list that will be returned, add
								if not n in in_range:
									in_range.append(n)

	
		# return the list of coordinates
		self.in_range = in_range


	def get_shortest_path(self, start, end, ignore_range=False):
		'''
		Gets the shortest path from the character to the given
		coordinates. Returns a list of coordinates. If target
		coodrinates are not in range, returns False, unless
		ignore_range flag is set True.

		Assumes that the method get_movement_range() has been run
		before this, so that the range_counts in squares are correct.

		Based on the Lee algorithm.
		'''

		path = []

		# last step is known, it is the target coordinates
		path.append(end)
		
		# if the target is not in range, there is no path there
		if not ignore_range and not end in self.in_range:
			return False
		
		# trace back from the end point
		current_range_count = self.square_at(end).range_count 
		
		while True:

			neighbors = end.get_neighbors()

			for n in neighbors:
				# if n is the start point, the path is complete
				if n == start:
					# reverse path because we started from the end
					path.reverse()
					return path

				square = self.square_at(n)

				# if square is reachable, has a smaller range count from 
				# the starting point, and is walkable and empty
				if square and not square.range_count == 0 and square.range_count < current_range_count \
				  and square.type.walkable and square.is_empty():
					# add to the shortest path
					path.append(n)
					# go on to finding the next step
					end = n
					current_range_count = self.square_at(end).range_count
					break


	def get_simple_map(self):
		'''Returns a simple text representation of the map as a string.'''
		
		simple_map = ""
		
		for y in range(self.height):
			for x in range(self.width):
				square = self.square_at( Coordinates(x,y) )
				# get the first letter of the character's name
				if square.character:
					simple_map = simple_map + square.character.name[0] + " "
				# get the first letter of the object's type
				elif square.object:
					simple_map = simple_map + str(square.object)[0] + " "
				# get the first letter of the square's type
				else:
					simple_map = simple_map + str(square.type)[0] + " "
			# new line
			simple_map = simple_map + "\n"
		
		return simple_map


	def get_range_count_map(self):
		'''Returns a text representation of the map range counts as a string.'''
		
		range_count_map = ""
		
		for y in range(self.height):
			for x in range(self.width):
				square = self.square_at( Coordinates(x,y) )
				range_count_map = range_count_map + str(square.range_count) + " "
				# balance spacing
				if square.range_count < 10:
					range_count_map = range_count_map + " "
			# new line
			range_count_map = range_count_map + "\n"
				
		return range_count_map