from action import Action
from constants import *
from map import Map
from object_type import ObjectType
from squaretype import SquareType
from character import Character
from coordinates import Coordinates
import direction

# can be used to get json representation of the config after reading
import json

class ConfigFileError(Exception):
	'''Defines an exception that the config reader throws in case of a corrupted file.'''
	
	def __init__(self, message):
		super(ConfigFileError, self).__init__(message)


class ConfigReader(object):
	'''A config file reader that builds maps and characters based on configuration files.'''
	
	def __init__(self, auto_open=True):
		
		if auto_open:
			# read config from files
			file = open(MAP_CONFIG, 'r')
			self.map_config = self.read_config(file)
			file.close()
			
			file = open(CHARACTER_CONFIG, 'r')
			self.character_config = self.read_config(file)
			file.close()
	
	
	def check_parentheses(self, input):
		'''Checks the given input for correct parentheses, brackets, and braces. Reports the line number for an error.'''
		
		stack = []
		line_nr = 0
		input.seek(0)
		
		for line in input:
			line_nr += 1
						
			# ignore comment lines
			if line.startswith("//"):
				continue
			
			# for each character in the line
			for char in line:
				# put openings in stack
				if char == '(' or char == '[' or char == '{':
					stack.append(char)
				
				# check closings from stack
				elif char == ')':
					if len(stack) == 0:
						raise ConfigFileError("Unmatched parentheses. Line {:}.".format(line_nr))
					elif stack[-1] == '(':
						stack.pop()
					else:
						raise ConfigFileError("Unmatched parentheses. Line {:}.".format(line_nr))
				
				elif char == ']':
					if len(stack) == 0:
						raise ConfigFileError("Unmatched brackets. Line {:}.".format(line_nr))
					elif stack[-1] == '[':
						stack.pop()
					else:
						raise ConfigFileError("Unmatched brackets. Line {:}".format(line_nr))
						
				elif char == '}':
					if len(stack) == 0:
						raise ConfigFileError("Unmatched braces. Line {:}.".format(line_nr))
					elif len(stack) == 0 or stack[-1] == '{':
						stack.pop()
					else:
						raise ConfigFileError("Unmatched braces. Line {:}".format(line_nr))
			
		# if stack is not empty, there are unclosed closures			
		if not len(stack) == 0:

			# inform what need to be closed
			unclosed = ""
			item_count = 0
			
			for item in stack:
				item_count += 1
				
				# add commas if needed
				if item_count > 1:
					unclosed += ", "
					
				unclosed += str(item)
			 
			raise ConfigFileError("Some closures not closed. Found unclosed '{:}'".format(unclosed))


	def read_config(self, input):
		'''Read config files and return the contents in a dictionary form.'''
		
		# Check input for matching parentheses, brackets, and braces.
		self.check_parentheses(input)
		
		# Return to beginning of file
		input.seek(0)
		
		self.config = []
		self.current_line = ''
		self.line_count = 0
		self.block_index = -1
		
		# Define 'next line' helper method
		def nl():
			'''Proceeds to the next line on the file.'''
			self.current_line = input.readline().strip()
			self.line_count += 1

		# Count lines
		self.lines_in_file = 0
		for line in input:
			self.lines_in_file += 1

		# Ensure that the reader is in the beginning of the file
		input.seek(0)
		
		# Read first line
		nl()
		
		# check header
		header_parts = self.current_line.split()
		
		if not len(header_parts) == 3:
			raise ConfigFileError("Unknown file type. Check file header.")
		
		if header_parts[0] != "DISCO":
			raise ConfigFileError("Unknown file type. Check file header.")
			
		if header_parts[1] != "KNIGHTS":
			raise ConfigFileError("Unknown file type. Check file header.")

		if header_parts[2].strip().lower() != 'config':
			raise ConfigFileError("Unknown file type. Check file header.")


		# go through the file line by line until no lines left
		while self.line_count <= self.lines_in_file:
			
			# If line doesn't start with #, go to the next line
			if not self.current_line.startswith('#'): 
				nl()
			
			# If the line is empty or a comment, jump back to the beginning of the loop to go to the next line
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
					# split the line where there is a colon
					line_parts = self.current_line.split(":")
					
					# If there's a beginning curly brace after the colon, put the following parts into a list or a dict
					if line_parts[1].strip() == "{":

						# Save the key, it will be lost if a dict is created
						key = line_parts[0]
						nl()

						# If there is a colon, create a dict
						if ":" in self.current_line:
							self.config[self.block_index][key] = {}

							# A closing curly brace on the line closes the dictionary
							while not "}" in self.current_line:
								
								# Separate keys and values 
								line_parts = self.current_line.split(":")

								# If there is multiple values separated with commas, create a list of the values
								if "," in line_parts[1]:
									self.config[self.block_index][key][line_parts[0]] = [ value.strip() for value in line_parts[1].split(",") ]
								
								# Otherwise just strip the value from extra spaces
								else:
									self.config[self.block_index][key][line_parts[0]] = line_parts[1].strip()
								
								# Go to the next line
								nl()

						# If there is no colon, create a list
						else:
							self.config[self.block_index][key] = []
							
							# A closing curly brace closes the list, keep going until there is one
							while not "}" in self.current_line:
								
								# Append the values separates by spaces to the list
								self.config[self.block_index][key].append(self.current_line.split())
								
								# Go to the next line
								nl()

						# Ending bracket was found, go to the next line
						nl()
					
					# If there's no beginning bracket, take the value and do not create another structure
					else:
						self.config[self.block_index][line_parts[0]] = line_parts[1].strip()
						
						# Go to the next line
						nl()


				# if there is content on the line but it cannot be recognized
				else:
					raise ConfigFileError("Cannot read config file. Unrecognized content on line {:}.".format(self.line_count))
				

		#print("The following config was created:")
		#print(json.dumps(self.config, indent=2))

		# Return the config dictionary built
		return self.config

	
	def build_map_base(self, state, map_config, map_index):
		'''Build a map without characters from the given config dictionary.'''

		# Check that map_config is a list
		if not isinstance(map_config, list):
			raise ConfigFileError("Wrong type of config input given.")

		# Initialize Map object
		mp = Map(state)
		
		# Build map
		for item in map_config:

			# Square types
			if item["id"].lower() == "squaretype":
				print("Building squaretype '{:}'...".format(item["name"]))
				
				# Try adding a square type based on the config file
				try:
					mp.add_squaretype(
					SquareType(
						item["name"],
						item["short"],
						(item["walkable"].lower() in ["true"]),
						item["sprite"]
						)
					)
				except pygame.error:
					raise ConfigFileError("There was a problem building the square type '{:}'. Could not find sprite '{:}'.".format(item["name"], item["sprite"]))
				except:
					raise ConfigFileError("There was a problem building the square type '{:}'. Make sure the map configuration file is properly formatted.".format(item["name"]))

			# Object types
			elif item["id"].lower() == "object":
				print("Building object type '{:}'...".format(item["name"]))
				
				# Try adding an object type based on the config file
				try:
					mp.add_object_type(
					ObjectType(
						item["name"],
						item["short"],
						item["sprite"],
						int(item["offset_x"]),
						int(item["offset_y"])
						)
					)
				except pygame.error:
					raise ConfigFileError("There was a problem building the object type '{:}'. Could not find sprite '{:}'.".format(item["name"], item["sprite"]))
				except:
					raise ConfigFileError("There was a problem building the object type '{:}'. Make sure the map configuration file is properly formatted.".format(item["name"]))
			
			# Build map squares and objects in squares
			elif item["id"].lower() == "map" and int(item["index"]) == map_index:
				print("Building map...")
				
				# Try building based on the config file
				try:
					mp.build_squares(
					int( item["height"] ), 
					int( item["width"] ),
					item["squares"],
					item["team1_start"],
					item["team2_start"]
					)
				except:
					raise ConfigFileError("There was a problem building map number {:}. Make sure the map configuration file is properly formatted.".format(item["index"])) 
					
		# return built map base
		return mp


	def build_characters_on_map(self, character_config, mp):
		'''Builds characters on a map and returns the map back.'''
		
		# counters for start positions
		team1_count = 0
		team2_count = 0
		
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
				
				# check that team number is 1 or 2
				if int(item["team"]) not in [1, 2]:
					raise ConfigFileError("A character can only be in team 1 or team 2. Make sure the map configuration file is properly formatted.")
				
				# Try creating a new Character object
				try:
					new_character = Character(
										item["name"],
										int(item["team"]),
										int(item["max_health"]),
										int(item["move_range"]),
										item["is_ai"].lower() == "true",
										item["stand_sprites"],
										walk_sprites
										)
				except:
					raise ConfigFileError("There was a problem building character '{:}'. Make sure the map configuration file is properly formatted.".format(item["name"]))				
				
				# try to get coordinates to add character at
				try:
					if new_character.team == 1:
						start_x = int(mp.team1_start[team1_count][0])
						start_y = int(mp.team1_start[team1_count][1])
						team1_count += 1
						
					if new_character.team == 2:
						start_x = int(mp.team2_start[team2_count][0])
						start_y = int(mp.team2_start[team2_count][1])
						team2_count += 1
						
					coordinates = Coordinates(start_x, start_y)
				
				# an index error means that there are not enough start positions for all characters,
				# desired behavior is to add as many as have been given start coordinates
				except IndexError:
					print("Not enough start coordinates, did not add character..")
				
				except:
					raise ConfigFileError("Invalid team {:} character start coordinates. Make sure the map configuration file is properly formatted.".format(new_character.team))

				# if there is a square and it is empty, add character there
				if mp.contains_coordinates(coordinates) and mp.square_at(coordinates).type.walkable:
					mp.add_character(new_character, coordinates, getattr(direction, item["facing"].upper()))

				elif not mp.contains_coordinates(coordinates):
					raise ConfigFileError("Cannot add character to {:}, out of map bounds.".format(coordinates))
				
				# otherwise print reason for failure, without crashing the whole program
				elif not mp.square_at(coordinates).type.walkable:
					raise ConfigFileError("Cannot add character to {:}, square type '{:}' not walkable.".format(coordinates, mp.square_at(coordinates).type.name))


				# Create actions for characters, loops over all items again to find all actions even if they come before the character
				for item2 in character_config:
					
					# If action was found and the character name matches the current character
					if item2["id"].lower() == "action" and item2["character"] == new_character.name:

						# if more than 3 actions have been given
						if len(new_character.actions) > 2:
							print("A character cannot have more than 3 actions.")

						# if at most 3 actions have been given
						else:
							print("Adding action {:} to character {:}...".format(item2["name"], item2["character"]))
							
							# read optional sound effect for action
							if "sound" in item2.keys():
								sound = item2["sound"]
							else:
								sound = None
							
							# use floating point numbers where there is a decimal
							if "." in item2["strength"]:
								strength = float(item2["strength"])
							else:
								strength = int(item2["strength"])
							
							# try adding the action
							try:
								new_character.add_action(
									getattr(Action, item2["type"].upper()),
									strength,
									int(item2["max_range"]),
									item2["name"],
									sound
									)
							except:
								raise ConfigFileError("Could not add action to character '{:}'. Make sure the character configuration file is properly formatted.".format(new_character.name))
		
		# Return the map back with the characters
		return mp
	
	
	def count_available_maps(self):
		'''Returns a count of available maps.'''
		
		count = 0
		
		for item in self.map_config:
			if item["id"].lower() == "map":
				count += 1
				
		# raise error if there are no maps at all
		if count == 0:
			raise ConfigFileError("No maps found in the config file!")
		
		return count
	
		
	def get_map(self, state, map_index):
		'''Builds a full map with characters and objects.'''

		# build map base
		mp = self.build_map_base(state, self.map_config, map_index) 

		# build characters on the map base
		mp = self.build_characters_on_map(self.character_config, mp)

		# return built map
		return mp