from constants import *
import os
import pygame

class SquareType(object):
	'''
	This class defines the types of squares on the map.
	'''
	
	def __init__(self, name, short, walkable, sprite=None):
		'''
		Creates a new square type.
		
		@param self.name: (String) The name of the square type.
		@param self.short: (String) A one-letter short name for the square type.
		@param self.walkable: (Boolean) Whether a character walk into a square of this type.
		@param self.sprite: (String) A path to the sprite file.
		'''
		
		self.name = name
		self.short = short
		self.walkable = walkable
		self.sprite = sprite
		if self.sprite:
			self.image = pygame.image.load( os.path.join(GRAPHICS_DIR, sprite) ).convert_alpha()
		self.offset_y = 0
	
	
	def __eq__(self, obj):
		return isinstance(obj, SquareType) and obj.get_name() == self.name
	
	
	def __str__(self):
		return self.name