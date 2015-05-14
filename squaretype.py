from constants import *
import os
import pygame

class SquareType(object):
	'''
	This class defines the types of squares on the map.
	'''
	
	def __init__(self, name, short, walkable, sprite=None):
		'''Constructor'''
		
		self.name = name
		self.short = short
		self.walkable = walkable
		self.sprite = sprite
		if self.sprite:
			self.image = pygame.image.load( os.path.join(GRAPHICS_DIR, sprite) ).convert_alpha()
		self.offset_y = 0
	
	
	def __eq__(self, obj):
		'''Equality check based on square type name.'''
		
		return isinstance(obj, SquareType) and obj.get_name() == self.name
	
	
	def __str__(self):
		return self.name