from character import Character
from config_reader import ConfigReader, ConfigFileError
from coordinates import Coordinates
from direction import *
from map import Map
from squaretype import SquareType

from io import StringIO
import unittest


class RangeAndPathfindingTest(unittest.TestCase):
	'''Tests the range and pathfinding algorithms.'''

	def setUp(self):
		'''Sets up a test map.'''

		# Create test map, with no state
		self.map = Map(None)

		# Add grass and water square types
		self.map.add_squaretype( SquareType("Grass", "g", True) )
		self.map.add_squaretype( SquareType("Water", "w", False) )

		# Build test map
		squares = [["g","g","g","w","g","g"],
				   ["g","g","g","w","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"]]

		self.map.build_squares(6, 6, squares, init_view=False)

		# add two test characters
		self.char_a = Character("A", 100, 3, False, None)
		self.map.add_character(self.char_a, Coordinates(5,0), RIGHT, init_view=False)

		self.char_b = Character("B", 100, 3, False, None)
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
		
		# Should include 7 coordinates since character B is in (5,2)
		self.assertEqual(7, len(self.map.in_range),\
							"There should be 7 coordinates in range when ignoring non-walkable square types.")

		# Coordinates within 3 steps from (5,0), ignoring characters
		self.map.set_in_range(3, Coordinates(5,0), ignore_characters=True, ignore_non_walkable=False)
		
		# Should include 6 coordinates even though character B is in (5,2)
		self.assertEqual(6, len(self.map.in_range),\
							"There should be 6 coordinates in range when ignoring characters.")

		# Coordinates within 3 steps from (5,0), ignoring characters and non-walkable square types
		self.map.set_in_range(3, Coordinates(5,0), ignore_characters=True, ignore_non_walkable=True)
		
		# Should include 9 coordinates even though there is water and a character in way
		self.assertEqual(9, len(self.map.in_range),\
							"There should be 9 coordinates in range when ignoring characters and non-walkable square types.")

		# Coordinates within 10 steps from (5,0) should cover all coordinates on the map, ignoring all obstacles
		self.map.set_in_range(10, Coordinates(5,0), ignore_characters=True, ignore_non_walkable=True)
		
		# Should include 35 coordinates, all squares (6*6) minus the starting point 
		self.assertEqual(35, len(self.map.in_range),\
							"There should be 35 coordinates in range when ignoring characters and non-walkable square types.")

	
	def test_finding_shortest_path(self):
		'''Tests the pathfinding algorithm Character.get_shortest_path()'''

		# Find the shortest path for character A from (5,0) to (0,0) which is outside range
		self.map.set_in_range(self.char_a.range, self.char_a.coordinates)
		path = self.char_a.get_shortest_path(Coordinates(0,0))

		self.assertFalse(path, "(0,0) should not be within 3 steps from (5,0).")

		# Find the shortest path for character A from (5,0) to (5,0) which should return False
		self.map.set_in_range(self.char_a.range, self.char_a.coordinates)
		path = self.char_a.get_shortest_path(Coordinates(5,0))

		self.assertFalse(path, "There should not be a path if the character is already at the target coordinates.")

		# Find the shortest path for character A from (5,0) to (4,2) which is in range
		self.map.set_in_range(self.char_a.range, self.char_a.coordinates)
		path = self.char_a.get_shortest_path(Coordinates(4,2))

		self.assertEqual(3, len(path), "The path from (5,0) to (4,2) should be 3 steps.")

		# Find the shortest path from character A at (5,0) to (2,0), ignoring character's own maximum movement range
		## 7 steps should be required to get to the target, set extra range to bring up errors if any
		self.map.set_in_range(10, self.char_a.coordinates)
		path = self.char_a.get_shortest_path(Coordinates(2,0), ignore_range=True)

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

		# Build test map
		squares = [["g","g","g","w","g","g"],
				   ["g","g","g","w","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"],
				   ["g","g","g","g","g","g"]]

		self.map.build_squares(6, 6, squares, init_view=False)

		# add two test characters
		self.char_a = Character("A", 100, 2, False, None)
		self.map.add_character(self.char_a, Coordinates(1,1), RIGHT, init_view=False)

		self.char_b = Character("B", 100, 2, False, None)
		self.map.add_character(self.char_b, Coordinates(3,3), RIGHT, init_view=False)


	def test_basic_one_step_movement(self):
		'''Tests basic movement.'''

		# move character A from (1,1) to (2,1)
		self.char_a.move_forward()
		
		self.assertEqual('(2, 1)', str(self.char_a.coordinates),\
							"Character A should be in (2,1) after one move forward.")

		# try to move character A from (2,1) to (3,1) which is water
		self.char_a.move_forward()
		
		self.assertEqual('(2, 1)', str(self.char_a.coordinates),\
							"Character A should not be able to move over water.")

		# turn right and move forward
		self.char_a.turn_to_direction(DOWN)
		self.char_a.move_forward()

		self.assertEqual('(2, 2)', str(self.char_a.coordinates),\
							"Character A should be in (2,2) after right turn and move forward.")

		# move left
		self.char_a.move_to_direction(LEFT)
		
		self.assertEqual('(1, 2)', str(self.char_a.coordinates),\
							"Character A should be in (1,2) after moving left.")


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
		self.config_file.write("#Map {\n")
		self.config_file.write("squares: {")
		
		error = None

		try:
			self.reader.check_parentheses(self.config_file)
		except ConfigFileError as e:
			error = e

		self.assertNotEqual(None, error, "A ConfigFileError should have been raised.")



if __name__ == "__main__":
	unittest.main()