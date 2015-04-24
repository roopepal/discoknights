from square import Square
from constants import *
from coordinates import Coordinates
from common import *
from map_object import MapObject
from object_type import ObjectType
from new_character import Character
from turn_controller import TurnController
import pygame, os


class Map(object):
	'''
	Defines the map object that contains the game world.
	'''
	
	def __init__(self):
		
		self.characters = []
		self.objects = []
		self.squaretypes = {}
		self.object_types = {}
		self.turn_controller = TurnController(self)
		# current range for character movement and actions
		self.in_range = None 
		
		
	def build_map(self, height, width, squares_input):
		self.height = height
		self.width = width
		# prepare empty slots for squares
		self.squares = height * [None]
		for y in range(height): 
			self.squares[y] = width * [None]
		# fill slots with squares
		for y in range(height):
			for x in range(width):
				# separate square type and possible object
				input_parts = squares_input[y][x].split(".")
				# if square type is defined, insert square				 
				if input_parts[0] in self.squaretypes.keys():
					self.squares[y][x] = Square( Coordinates(x,y), self.squaretypes[input_parts[0]] )
				# if there is an object to add, insert object
				if len(input_parts) > 1:
					self.add_object( Coordinates(x,y), MapObject(self.object_types[input_parts[1]]) )
		
		# initialize MapView
		self.view = MapView(self)
		# initialize MapObjectViews
		for o in self.objects:
			o.set_view()
			
	
	def start_game(self):
		self.in_range = self.turn_controller.current_character.get_movement_range()
		self.view.update_range = MOVEMENT
	
	
	def get_square_at(self, coordinates):
		if self.contains_coordinates(coordinates):
			square = self.squares[coordinates.y][coordinates.x]
			if square:
				return square
			else:
				print("There is not square at ({:}, {:})".format(coordinates.x, coordinates.y))
				return False
		else:
			print("Cannot get square from outside the map.")
			return False
	
	
	def add_squaretype(self, squaretype):
		if not squaretype.short in self.squaretypes:
			self.squaretypes[squaretype.short] = squaretype
		 
			
	def add_object_type(self, object_type):
		if not object_type.short in self.object_types:
			self.object_types[object_type.short] = object_type
	 
	  
	def add_character(self, character, coordinates, facing):
		if self.get_square_at(coordinates).is_empty():
			# add to the map
			self.characters.append(character)
			self.get_square_at(coordinates).character = character
			
			# add to the turn controller
			self.turn_controller.add_character(character)
			
			# update the character's attributes
			character.added_to_map(self,coordinates,facing)
			
			# initialize CharacterView
			character.set_view()
			
		else:
			print("Square wasn't empty. Cannot add character.")
	
	
	def add_object(self, coordinates, map_object):
		if self.get_square_at(coordinates).is_empty():
			# add to the map
			self.objects.append(map_object)
			self.get_square_at(coordinates).object = map_object
			
			# update the character's attributes
			map_object.added_to_map(self, coordinates)
		else:
			print("Square wasn't empty. Cannot add object.")
	
	
	def contains_coordinates(self, coordinates):
		# return True or False based on if the map contains the coordinates
		return 0 <= coordinates.x < self.width and 0 <= coordinates.y < self.height
	
	
	def get_simple_map(self):
		# returns a simple command-line representation of the map as a string.
		simple_map = ""
		for y in range(self.height):
			for x in range(self.width):
				square = self.get_square_at( Coordinates(x,y) )
				# get the first letter of the character's name
				if square.character:
					simple_map = simple_map + square.character.name[0] + " "
				# get the first letter of the object's type
				elif square.object:
					simple_map = simple_map + str(square.object)[0] + " "
				# get the first letter of the square's type
				else:
					simple_map = simple_map + str(square.type)[0] + " "
		return simple_map

 
class MapView(object):
	'''
	Defines a view for the Map object.
	'''
	
	def __init__(self, map_object):
		# set screen
		self.screen = reset_screen()
		
		# set map
		self.map = map_object
		
		# initialize range
		self.update_range = False
		
		# calculate the pixel width and height of the map to be rendered
		self.width = (self.map.width + self.map.height) * TILE_W / 2 
		self.height = (self.map.width + self.map.height) * TILE_H / 2 + 8	# 8 is the 'thickness' of a square
		
		# set draw offset to center the map horizontally on the surface
		self.draw_offset_x = self.width / 2 - TILE_W / 2
		
		# initialize map tile and range surfaces
		self.squares_image = pygame.Surface( (self.width, self.height), pygame.SRCALPHA )
		self.range_image = pygame.Surface( (self.width, self.height), pygame.SRCALPHA )
		self.rect = self.squares_image.get_rect()
		
		# render squares
		self.render_squares()
		
		# center the map image in the game window
		self.center_in_window()
		
		# load range indicators
		self.load_indicators()
		
		
	def center_in_window(self):
		# center the map view's rectangle in the window
		window_center = ( options.window_size[0] / 2, options.window_size[1] / 2 )
		self.rect.center = window_center
	
	
	def load_indicators(self):
		# load range indicator image
		self.move_range_ind = pygame.image.load(MOVE_RANGE_IND_PATH).convert_alpha()
		self.attack_range_ind = pygame.image.load(ATTACK_RANGE_IND_PATH).convert_alpha()
		self.heal_range_ind = pygame.image.load(HEAL_RANGE_IND_PATH).convert_alpha()
	
	
	def render_squares(self):
		for x in range(self.map.width):
			for y in range(self.map.height):
				square = self.map.get_square_at( Coordinates(x,y) )
				
				# convert map coordinates to screen coordinates
				screen_x, screen_y = map_to_screen(x,y)
				
				# blit the square
				self.squares_image.blit( square.type.image, (screen_x + self.draw_offset_x, screen_y) )
				
	
	def render_range(self, indicator):
		# clear range image
		self.range_image.fill(0)
		
		for coordinates in self.map.in_range:
			# convert map coordinates to screen coordinates 
			screen_x, screen_y = map_to_screen(coordinates.x, coordinates.y)
			
			# blit movement range indicator
			self.range_image.blit( indicator, (screen_x + self.draw_offset_x, screen_y) )
			
			# release range update
			self.update_range = False
	
	
	def move(self, delta_x, delta_y):
		self.rect.move_ip(delta_x, delta_y)
	
	
	def update(self):
		if self.update_range == MOVEMENT:
			self.render_range(self.move_range_ind)
		elif self.update_range == ATTACK:
			self.render_range(self.attack_range_ind)
		elif self.update_range == HEAL:
			self.render_range(self.heal_range_ind)
	
	
	def draw(self):
		self.screen.blit(self.squares_image, self.rect)
		self.screen.blit(self.range_image, self.rect)
