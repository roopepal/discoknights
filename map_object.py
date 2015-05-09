import pygame, os
from constants import GRAPHICS_DIR
from coordinates import map_to_screen

class MapObject(object):
	'''
	Defines a map object.
	'''
	
	def __init__(self, object_type):
		'''
		Creates a object on the map.
		'''
		self.type = object_type
		self.map = None
		self.coordinates = None


	def added_to_map(self, mp, coordinates):
		# Updates the object attributes when the object is added to a map.
		self.map = mp
		self.coordinates = coordinates

	
	def set_view(self):
		# initiate MapObjectView
		self.view = MapObjectView(self)
	

	def __str__(self):
		return self.type.name
		


class MapObjectView(object):
	
	def __init__(self, map_object):
		self.map_object = map_object
		self.image = pygame.image.load( os.path.join(GRAPHICS_DIR, self.map_object.type.sprite_path) )
		self.rect = self.image.get_rect()
		# set draw offsets
		self.draw_offset_x = self.map_object.type.offset_x
		self.draw_offset_y = self.map_object.type.offset_y
		
		self.set_screen_pos()
		
		
	def set_screen_pos(self):
		# get position on map
		map_pos = self.map_object.coordinates
		# convert to screen coordinates
		screen_x, screen_y = map_to_screen(map_pos.x, map_pos.y)
		# add horizontal draw offset to prevent negative x coordinates
		screen_x += self.map_object.map.view.draw_offset_x
		# add map offset on screen
		screen_x += self.map_object.map.view.rect.topleft[0]
		screen_y += self.map_object.map.view.rect.topleft[1]
		# set position on screen
		self.rect.x = screen_x + self.draw_offset_x
		self.rect.y = screen_y + self.draw_offset_y
		
		
	def draw(self):
		self.map_object.map.view.screen.blit(self.image, self.rect)
