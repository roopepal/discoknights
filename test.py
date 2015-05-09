from action import Action
from character import Character
from config_reader import ConfigReader, ConfigFileError
from coordinates import Coordinates
from direction import *
from map import Map
from map_object import MapObject
from object_type import ObjectType
from squaretype import SquareType

import pygame

from io import StringIO
import unittest


class RangeAndPathfindingTest(unittest.TestCase):
	'''Tests the range and pathfinding algorithms.'''

	def setUp(self):
		'''Sets up a test map.'''

		# Create test map, with no state
		self.map = Map(None)

		# Add grass and water square types and a rock object type
		self.map.add_squaretype( SquareType("Grass", "g", True) )
		self.map.add_squaretype( SquareType("Water", "w", False) )
		self.map.add_object_type( ObjectType("rock", "r", "rock.gif", 0, 0) )

		# Build test map
		squares = [["g","g","g","w","g","g"],
				   ["g","g","g","g.r","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"]]

		self.map.build_squares(6, 6, squares, None, None, init_view=False)

		# add two test characters
		self.char_a = Character("A", 1, 100, 3, False, None)
		self.map.add_character(self.char_a, Coordinates(5,0), RIGHT, init_view=False)

		self.char_b = Character("B", 1, 100, 3, False, None)
		self.map.add_character(self.char_b, Coordinates(5,2), RIGHT, init_view=False)

	
	def test_range_finding(self):
		'''Tests the range finding algorithm Map.set_in_range()'''
		
		# Coordinates within 3 steps from (5,0)
		self.map.set_in_range(3, Coordinates(5,0), ignore_characters=False, ignore_non_walkable=False)
		
		# Should include 4 coordinates since water is not walkable and character B is in (5,2)
		self.assertEqual(4, len(self.map.in_range),\
							"There should be 4 coordinates in range.")

		# Coordinates within 3 steps from (5,0), ignoring non-walkable square types
		self.map.set_in_range(3, Coordinates(5,0), ignore_characters=False, ignore_non_walkable=True)
		
		# Should include 6 coordinates since character B is in (5,2) and there's a rock at (3,1)
		self.assertEqual(6, len(self.map.in_range),\
							"There should be 7 coordinates in range when ignoring non-walkable square types.")

		# Coordinates within 3 steps from (5,0), ignoring characters
		self.map.set_in_range(3, Coordinates(5,0), ignore_characters=True, ignore_non_walkable=False)
		
		# Should include 6 coordinates even though character B is in (5,2)
		self.assertEqual(6, len(self.map.in_range),\
							"There should be 6 coordinates in range when ignoring characters.")

		# Coordinates within 3 steps from (5,0), ignoring characters and non-walkable square types
		self.map.set_in_range(3, Coordinates(5,0), ignore_characters=True, ignore_non_walkable=True)
		
		# Should include 8 coordinates even since everything but objects are ignored
		self.assertEqual(8, len(self.map.in_range),\
							"There should be 9 coordinates in range when ignoring characters and non-walkable square types.")

		# Coordinates within 10 steps from (5,0) should cover all coordinates on the map, ignoring all except objects
		self.map.set_in_range(10, Coordinates(5,0), ignore_characters=True, ignore_non_walkable=True)
		
		# Should include 34 coordinates, all squares (6*6) minus the starting point and the rock 
		self.assertEqual(34, len(self.map.in_range),\
							"There should be 35 coordinates in range when ignoring characters and non-walkable square types.")

	
	def test_finding_shortest_path(self):
		'''Tests the pathfinding algorithm Character.get_shortest_path()'''

		# Find the shortest path for character A from (5,0) to (0,0) which is outside range
		self.map.set_in_range(self.char_a.range, self.char_a.coordinates)
		path = self.map.get_shortest_path(self.char_a.coordinates, Coordinates(0,0))

		self.assertFalse(path, "(0,0) should not be within 3 steps from (5,0).")

		# Find the shortest path for character A from (5,0) to (5,0) which should return False
		self.map.set_in_range(self.char_a.range, self.char_a.coordinates)
		path = self.map.get_shortest_path(self.char_a.coordinates, Coordinates(5,0))

		self.assertFalse(path, "There should not be a path if the character is already at the target coordinates.")

		# Find the shortest path for character A from (5,0) to (4,2) which is in range
		self.map.set_in_range(self.char_a.range, self.char_a.coordinates)
		path = self.map.get_shortest_path(self.char_a.coordinates, Coordinates(4,2))

		self.assertEqual(3, len(path), "The path from (5,0) to (4,2) should be 3 steps.")

		# Find the shortest path from character A at (5,0) to (2,0), ignoring character's own maximum movement range
		## 7 steps should be required to get to the target, set extra range to bring up errors if any
		self.map.set_in_range(10, self.char_a.coordinates)
		path = self.map.get_shortest_path(self.char_a.coordinates, Coordinates(2,0), ignore_range=True)

		self.assertEqual(7, len(path), "The path from (5,0) to (2,0) should be 3 steps.")



class MovementTest(unittest.TestCase):
	'''Tests character movement on map.'''

	def setUp(self):
		'''Sets up a test map.'''

		# Create test map, with no state
		self.map = Map(None)

		# Add grass and water square types
		self.map.add_squaretype( SquareType("Grass", "g", True) )
		self.map.add_squaretype( SquareType("Water", "w", False) )
		self.map.add_object_type( ObjectType("rock", "r", "rock.gif", 0, 0) )

		# Build test map
		squares = [["g","g","g","w","g","g"],
				   ["g","g","g","g.r","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"]]

		self.map.build_squares(6, 6, squares, None, None, init_view=False)

		# add two test characters
		self.char_a = Character("A", 1, 100, 2, False, None)
		self.map.add_character(self.char_a, Coordinates(1,1), RIGHT, init_view=False)

		self.char_b = Character("B", 1, 100, 2, False, None)
		self.map.add_character(self.char_b, Coordinates(3,3), RIGHT, init_view=False)


	def test_basic_one_step_movement(self):
		'''Tests basic movement.'''

		# move character A from (1,1) to (2,1)
		self.char_a.move_forward()
		
		self.assertEqual('(2, 1)', str(self.char_a.coordinates),\
							"Character A should be in (2,1) after one move forward.")

		# try to move character A from (2,1) to (3,1) which is a rock
		self.char_a.move_forward()
		
		self.assertEqual('(2, 1)', str(self.char_a.coordinates),\
							"Character A should not be able to move to a square with an object.")

		# turn right and move forward
		self.char_a.turn_to_direction(DOWN)
		self.char_a.move_forward()

		self.assertEqual('(2, 2)', str(self.char_a.coordinates),\
							"Character A should be in (2,2) after right turn and move forward.")

		# move left
		self.char_a.move_to_direction(LEFT)
		
		self.assertEqual('(1, 2)', str(self.char_a.coordinates),\
							"Character A should be in (1,2) after moving left.")

		# move up and try to go over map bounds
		self.char_a.move_to_direction(UP)
		self.char_a.move_to_direction(UP)
		self.char_a.move_to_direction(UP)
		
		# should be in (1,0) since cannot go outside map
		self.assertEqual('(1, 0)', str(self.char_a.coordinates),\
							"Character A should not be able to move outside the map.")

	def test_movement_range_with_pathfinding(self):
		'''Tests maximum character movement range.
		Uses the range and pathfinding algorithms
		Map.set_in_range() and Character.get_shortest_path().'''

		# Try to move character A from (1,1) to (4,1) which is out of range
		success = self.char_a.move_to_coordinates(Coordinates(4,1))

		self.assertFalse(success, "(4,1) should not be within range of character A.")

		# Character A should still be in (1,1)
		self.assertEqual('(1, 1)', str(self.char_a.coordinates),\
							"Character A should be in (1,1) after trying to move outside range.")

		#Try to move character A from (1,1) to (2,2) which is in range
		success = self.char_a.move_to_coordinates(Coordinates(2,2))

		self.assertTrue(success, "(2,2) should be within range of character A.")

		# Character A should be in (2,2)
		self.assertEqual('(2, 2)', str(self.char_a.coordinates),\
							"Character A should be in (2,2) after trying to move within range.")



class ConfigReaderTest(unittest.TestCase):
	'''Tests the config reader's error handling.'''
	
	def setUp(self):
		'''Initializes the config reader.'''
		self.reader = ConfigReader(auto_open=False)


	def test_unmatched_parentheses_check(self):
		'''Tests the ConfigReader.check_parentheses() method which should raise
		an error when the input file has unmatched parentheses, brackets, or braces.'''

		self.config_file = StringIO()
		
		# build a deliberately corrupted config file missing a closing brace
		self.config_file.write("DISCO KNIGHTS Config\n")
		self.config_file.write("#Map\n")
		self.config_file.write("squares: {")
		
		error = None

		try:
			self.reader.check_parentheses(self.config_file)
		except ConfigFileError as e:
			error = e

		self.assertNotEqual(None, error, "A ConfigFileError should have been raised.")


	def test_unrecognized_file_header(self):
		'''Tests the ConfigReader.read_config() method with an unrecognized
		file header on the first line.'''

		self.config_file = StringIO()
		
		# build a deliberately corrupted config file with the wrong header
		self.config_file.write("DISCO Config\n")
		self.config_file.write("#Map\n")
		self.config_file.write("index: 1")
		
		error = None

		try:
			self.reader.read_config(self.config_file)
		except ConfigFileError as e:
			error = e

		self.assertNotEqual(None, error, "A ConfigFileError should have been raised.")
		
		
		# Another wrong type of header
		
		self.config_file = StringIO()
		
		# build a deliberately corrupted config file with the wrong header
		self.config_file.write("DISCO K Config\n")
		self.config_file.write("#Map\n")
		self.config_file.write("index: 1")
		
		error = None

		try:
			self.reader.read_config(self.config_file)
		except ConfigFileError as e:
			error = e

		self.assertNotEqual(None, error, "A ConfigFileError should have been raised.")
		
	
	def test_unrecognized_content(self):
		'''Tests the ConfigReader.read_config() method with unrecognized content.'''
		
		self.config_file = StringIO()
		
		# build a deliberately corrupted config file with a missing colon
		self.config_file.write("DISCO KNIGHTS Config\n")
		self.config_file.write("#Map\n")
		self.config_file.write("index 1\n")
		self.config_file.write("width: 5\n")
		
		error = None

		try:
			self.reader.read_config(self.config_file)
		except ConfigFileError as e:
			error = e

		self.assertNotEqual(None, error, "A ConfigFileError should have been raised.")
		
		# Test another file with a content type that is correctly formatted but not used.
		# The config reader should read through correctly. Therefore, the config reader
		# should allow for adding features without errors.
		
		self.config_file = StringIO()
		
		# build a correctly formatted config file with a new feature "max_characters"
		self.config_file.write("DISCO KNIGHTS Config\n")
		self.config_file.write("#Map\n")
		self.config_file.write("index: 1\n")
		self.config_file.write("max_characters: 4\n")
		
		error = None

		try:
			self.reader.read_config(self.config_file)
		except ConfigFileError as e:
			error = e

		self.assertEqual(None, error, "A ConfigFileError should not have been raised.")



class TurnControllerTest(unittest.TestCase):
	
	def setUp(self):
		'''Sets up a test map.'''

		# Create test map, with no state
		self.map = Map(None)

		# Add grass and water square types and a rock object type
		self.map.add_squaretype( SquareType("Grass", "g", True) )
		self.map.add_squaretype( SquareType("Water", "w", False) )
		self.map.add_object_type( ObjectType("rock", "r", "rock.gif", 0, 0) )

		# Build test map
		squares = [["g","g","g","w","g","g"],
				   ["g","g","g","g.r","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"]]

		self.map.build_squares(6, 6, squares, None, None, init_view=False)

		# add two test characters
		self.char_a = Character("A", 1,  100, 3, False, None)
		self.map.add_character(self.char_a, Coordinates(5,0), RIGHT, init_view=False)

		self.char_b = Character("B", 1, 100, 3, False, None)
		self.map.add_character(self.char_b, Coordinates(5,2), RIGHT, init_view=False)
		
	
	def test_characters_added_on_map(self):
		'''Tests that characters are added to the turn controller when added on the map.'''
		
		# there should be two characters in the turn controller after the test setUp()
		self.assertEqual(2, len(self.map.turn_controller.characters), \
							"There should be 2 characters in the turn controller.")

		# add more characters, 1 player and 1 AI
		self.char_c = Character("B", 1, 100, 3, False, None)
		self.map.add_character(self.char_c, Coordinates(1,2), RIGHT, init_view=False)
		
		self.char_d = Character("B", 2, 100, 3, True, None)
		self.map.add_character(self.char_d, Coordinates(3,2), RIGHT, init_view=False)
		
		# there should be 4 characters now
		self.assertEqual(4, len(self.map.turn_controller.characters), \
							"There should be 4 characters in the turn controller.")

		# the current character should be the first one added
		self.assertEqual(self.char_a, self.map.turn_controller.current_character, \
							"It should be character A's turn.")
							
	
	def test_turn_controller_reset(self):
		'''Tests that the TurnController.reset() method correctly gives the first character.'''
		
		# manually set the turn to the second character
		self.map.turn_controller.current_character = self.char_b
		
		# it should be B's turn
		self.assertEqual(self.char_b, self.map.turn_controller.current_character, \
							"It should be character B's turn.")

		# reset the turn controller
		self.map.turn_controller.reset()
		
		# it should be A's turn after the reset
		self.assertEqual(self.char_a, self.map.turn_controller.current_character, \
							"It should be character A's turn after a reset.")



class AiTest(unittest.TestCase):
	'''Tests the AI methods that have no random element.'''
	
	def setUp(self):
		'''Sets up a test map.'''

		# Create test map, with no state
		self.map = Map(None)

		# Add grass and water square types and a rock object type
		self.map.add_squaretype( SquareType("Grass", "g", True) )
		self.map.add_squaretype( SquareType("Water", "w", False) )
		self.map.add_object_type( ObjectType("rock", "r", "rock.gif", 0, 0) )

		# Build test map
		squares = [["g","w","g","w","g","g"],
				   ["w","w","g","g.r","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"]]

		self.map.build_squares(6, 6, squares, None, None, init_view=False)

		# add three test characters, 2 player and 2 AI
		self.char_a = Character("A", 1, 100, 3, False, None)
		self.map.add_character(self.char_a, Coordinates(5,0), RIGHT, init_view=False)

		self.char_b = Character("B", 1, 100, 3, False, None)
		self.map.add_character(self.char_b, Coordinates(5,2), RIGHT, init_view=False)
		
		self.char_c = Character("C", 2, 100, 3, True, None)
		self.map.add_character(self.char_c, Coordinates(0,0), RIGHT, init_view=False)

		self.char_d = Character("D", 2, 100, 3, True, None)
		self.map.add_character(self.char_d, Coordinates(4,5), RIGHT, init_view=False)
		
		
	def test_target_acquiring(self):
		'''Tests that the correct enemy player is chosen as the target.'''
		
		# give turn to the AI character D
		self.map.turn_controller.current_character = self.char_d
		
		# D should get B as target, and the path length there should be 4
		chosen_enemy, chosen_enemy_path = self.map.turn_controller.ai.get_target()
		
		self.assertEqual(self.char_b, chosen_enemy, "D should get B as target.")
		self.assertEqual(4, len(chosen_enemy_path), "There should be 4 steps from D to B.")
		
		
		# C should not get any target as it is isolated
		self.map.turn_controller.current_character = self.char_c
		chosen_enemy, chosen_enemy_path = self.map.turn_controller.ai.get_target()
		
		self.assertFalse(chosen_enemy, "C should get no target, it is isolated.")
		self.assertFalse(chosen_enemy_path, "There should be no path as there is no target.")
		

	def test_next_move_acquiring(self):
		'''Tests that the path to move next is given correctly, taking into account
		the character's maximum movement range.'''
		
		# give turn to the AI character D
		self.map.turn_controller.current_character = self.char_d
		
		# C can move a maximum of 3 steps
		path = self.map.turn_controller.ai.get_next_move()



class ActionEffectTest(unittest.TestCase):
	'''Tests the effects of actions on characters.'''
	
	def setUp(self):
		'''Sets up a test map with one character.'''

		# Create test map, with no state
		self.map = Map(None)

		# Add grass square type
		self.map.add_squaretype( SquareType("Grass", "g", True) )

		# Build test map
		squares = [["g","g"],
				   ["g","g"]]

		self.map.build_squares(2, 2, squares, None, None, init_view=False)

		# add three test characters, 2 player and 2 AI
		self.char_a = Character("A", 1, 100, 3, False, None)
		self.map.add_character(self.char_a, Coordinates(0,0), RIGHT, init_view=False)
		
	
	def test_action_effects(self):
		'''Tests the effects of actions on target characters.'''
		
		self.char_a.damage(20)
		
		# character A should have 80 health left
		self.assertEqual(80, self.char_a.health, "Character A should have 80 health left.")

		
		self.char_a.heal(50)

		# character A should have 100 health after healing over the maximum health
		self.assertEqual(100, self.char_a.health, "Character A should have 80 health left.")
		
		
		self.char_a.stun(1)
		
		# character A should be stunned for 1 turn
		self.assertEqual(1, self.char_a.stunned, "Character A should be stunned for 1 turn.")
		
		
		self.char_a.damage(150)
		
		# character A should have 100 health after healing over the maximum health
		self.assertTrue(self.char_a.dead, "Character A should be dead after damage of 150.")




if __name__ == "__main__":
	
	# run all tests as one test suite
	unittest.main()