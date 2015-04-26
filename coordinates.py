from direction import x_step, y_step, get_directions
from constants import TILE_W, TILE_H

class Coordinates(object):
	'''
	This class defines a simple coordinate pair: x, y.
	'''
	
	def __init__(self, x, y):
		self.x = x
		self.y = y
	
	def is_right_neighbor(self, coordinates):
		return (coordinates.x - self.x == 1 and coordinates.y == self.y)
	
	def is_left_neighbor(self, coordinates):
		return (coordinates.x - self.x == -1 and coordinates.y == self.y)
		
	def is_top_neighbor(self, coordinates):
		return (coordinates.x == self.x and coordinates.y - self.y == -1)
	
	def is_bottom_neighbor(self, coordinates):
		return (coordinates.x == self.x and coordinates.y - self.y == 1)
	
	def get_neighbor(self, direction):
		return Coordinates(self.x + x_step(direction), self.y + y_step(direction))
	
	def get_neighbors(self):
		return [ self.get_neighbor(direction) for direction in get_directions() ]
	
	def __eq__(self, obj):
		return self.x == obj.x and self.y == obj.y
	
	def __str__(self):
		return "({:}, {:})".format(self.x,self.y)
		

def map_to_screen(map_x, map_y):
	# convert map coordinates to isometric screen coordinates
	screen_x = (map_x - map_y) * (TILE_W / 2)
	screen_y = (map_x + map_y) * (TILE_H / 2)
	return screen_x, screen_y
	
	
def screen_to_map(screen_x, screen_y):
	# convert isometric screen coordinates to map coordinates
	# assuming origins are at the top
	screen_x /= 2
	map_x = (screen_y + screen_x)/(TILE_H)
	map_y = (screen_y - screen_x)/(TILE_H)
	if map_x < 0:
		map_x -= 1
	if map_y < 0:
		map_y -= 1
	return int(map_x), int(map_y)