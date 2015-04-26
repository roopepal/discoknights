from action import Action
from constants import *
from new_map import Map
from object_type import ObjectType
from squaretype import SquareType
from new_character import Character
from coordinates import Coordinates
import direction

# can be used to get json representation of the config after reading
#import json
	


class ConfigReader(object):
	'''A config file reader that builds maps and characters based on configuration files.'''
	
	def __init__(self):
		
		# read config from files
		file = open(MAP_CONFIG, 'r')
		self.map_config = self.read_config(file)
		file.close()
		
		file = open(CHARACTER_CONFIG, 'r')
		self.character_config = self.read_config(file)
		file.close()
	
	
	def read_config(self, input):
		'''Read config files and build a nested dictionary.'''
		
		self.config = []
		self.current_line = ''
		self.line_count = 0
		self.block_index = -1
		
		def nl():
			self.current_line = input.readline().strip()
			self.line_count += 1

		self.lines_in_file = 0
		for line in input:
			self.lines_in_file += 1
		
		input.seek(0)
		
		nl()
		
		#header_parts = self.current_line.split()
		
		'''
		if header_parts[0] != "DISCO":
			# raise error
			print()
		if header_parts[1] != "KNIGHTS":
			# raise error
		if header_parts[2].strip().lower() != 'config':
			# raise error
		'''
					
		while self.line_count <= self.lines_in_file:
			
			# If line doesn't start with #, go to the next line
			if not self.current_line.startswith('#'): 
				nl()
			
			# If the line is empty or a comment, jump back to the beginning of the loop
			if self.current_line == '' or self.current_line.startswith("//"):
				continue
			
			# A block was found, add a new item to the dictionary
			self.config.append({'id' : self.current_line.strip("#")})
			self.block_index += 1
			nl()
			
			# While still in the same block and rows left in file
			while not self.current_line.startswith('#') and self.line_count <= self.lines_in_file:

				# Skip empty lines and comments
				if self.current_line == '' or self.current_line.startswith("//"):
					nl()

				elif ":" in self.current_line:
					line_parts = self.current_line.split(":")
					# If there's a beginning bracket after the colon, put the following into a list or a dict
					if line_parts[1].strip() == "{":

						# Save the key, it will be lost if a dict is created
						key = line_parts[0]
						nl()

						# If there is a colon, create a dict
						if ":" in self.current_line:
							self.config[self.block_index][key] = {}

							while not "}" in self.current_line:
								line_parts = self.current_line.split(":")

								# If there is multiple values, create a list of the values
								if "," in line_parts[1]:
									self.config[self.block_index][key][line_parts[0]] = [ value.strip() for value in line_parts[1].split(",") ]
								else:
									self.config[self.block_index][key][line_parts[0]] = line_parts[1].strip()
								nl()

						# If there is no colon, create a list
						else:
							self.config[self.block_index][key] = []

							while not "}" in self.current_line:
								self.config[self.block_index][key].append(self.current_line.split())
								nl()

						# Ending bracket was found, go to next line
						nl()
					
					# If there's no beginning bracket, just take the value and do not create another structure
					else:
						self.config[self.block_index][line_parts[0]] = line_parts[1].strip()
						nl()

		#print("The following config was created:")
		#print(json.dumps(self.config, indent=2))

		return self.config

	
	def build_map_base(self, state, map_config, map_index):
		'''Build a map without characters.'''
		
		# Initialize Map object
		mp = Map(state)
		
		# Build map
		for item in map_config:
						
			# Square types
			if item["id"].lower() == "squaretype":
				print("Building squaretype '{:}'...".format(item["name"]))
				mp.add_squaretype(
					SquareType(
						item["name"],
						item["short"],
						(item["walkable"].lower() in ["true"]),
						item["sprite"]
						)
					)

			# Object types
			elif item["id"].lower() == "object":
				print("Building object type '{:}'...".format(item["name"]))
				mp.add_object_type(
					ObjectType(
						item["name"],
						item["short"],
						item["sprite"],
						int(item["offset_x"]),
						int(item["offset_y"])
						)
					)
			
			# Map squares and objects in squares
			elif item["id"].lower() == "map" and int(item["index"]) == map_index:
				print("Building map...")
				mp.build_squares(
					int( item["height"] ), 
					int( item["width"] ), 
					item["squares"]
					)
		
		# return built map base	
		return mp


	def build_characters_on_map(self, character_config, mp):
		'''Builds characters on a map and returns the map back.'''
		
		# Characters and actions
		for item in character_config:
			if item["id"].lower() == "character":
				print("Building character '{:}'...".format(item["name"]))
				
				# check if there are walk sprites
				if 'walk_sprites' in item:
					walk_sprites = item["walk_sprites"]
				
				# if no walk sprites
				else:
					walk_sprites = None
				
				# create a new Character object
				new_character = Character(
									item["name"],
									int(item["max_health"]),
									int(item["move_range"]),
									item["is_ai"].lower() == "true",
									item["stand_sprites"],
									walk_sprites
									)
 
				# read coordinates to add character at
				coordinates = Coordinates(int(item["x"]), int(item["y"]))

				# if there is a square and it is empty, add character there
				if mp.contains_coordinates(coordinates) and mp.get_square_at(coordinates).type.walkable:
					mp.add_character(new_character, Coordinates(int(item["x"]), int(item["y"])), getattr(direction, item["facing"].upper()))

				# otherwise print reason for failure
				elif not mp.get_square_at(coordinates).type.walkable:
					print("Cannot add character to {:}, square type '{:}' not walkable.".format(coordinates, mp.get_square_at(coordinates).type.name))
				elif not mp.contains_coordinates(coordinates):
					print("Cannot add character to {:}, out of bounds.".format(coordinates))

				# Create actions for characters
				for item2 in character_config:
					if item2["id"].lower() == "action" and item2["character"] == new_character.name:

						# if more than 3 actions have been given
						if len(new_character.actions) > 3:
							print("Cannot have more than 3 actions.")

						# if at most 3 actions have been given
						else:
							print("Adding action {:} to character {:}...".format(item2["name"], item2["character"]))
							new_character.add_action(
									getattr(Action, item2["type"].upper()),
									int(item2["strength"]),
									int(item2["max_range"]),
									item2["name"]
									)
		
		return mp
		
		
	def get_map(self, state, map_index):
		'''Builds a full map with characters and objects.'''

		# build map base
		mp = self.build_map_base(state, self.map_config, map_index) 

		# build characters on the map base
		mp = self.build_characters_on_map(self.character_config, mp)

		# return built map
		return mp