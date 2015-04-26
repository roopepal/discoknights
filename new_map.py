from square import Square
from constants import *
from coordinates import Coordinates
from common import *
from map_object import MapObject
from object_type import ObjectType
from new_character import Character
from turn_controller import TurnController
from ui import Button
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
		# update range
		self.in_range = self.turn_controller.current_character.get_movement_range()
		self.view.update_range = MOVEMENT
		# update action buttons
		self.view.update_action_buttons()
		# update character info
		self.view.update_char_info = True
		
	
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
		
		# calculate the pixel width and height of the map to be drawed
		self.width = (self.map.width + self.map.height) * TILE_W / 2 
		self.height = (self.map.width + self.map.height) * TILE_H / 2 + 8	# 8 is the 'thickness' of a square
		
		# set draw offset to center the map horizontally on the surface
		self.draw_offset_x = self.width / 2 - TILE_W / 2
		
		# initialize map base and range surfaces
		self.squares_image = pygame.Surface( (self.width, self.height), pygame.SRCALPHA )
		self.range_image = pygame.Surface( (self.width, self.height), pygame.SRCALPHA )
		self.rect = self.squares_image.get_rect()
		
		# center the map image in the game window
		self.center_in_window()
		
		# draw squares
		self.draw_squares()
		
		# init range update state
		self.update_range = False
		
		# load range indicators
		self.load_indicators()
		
		# load bottom menu
		self.load_bottom_menu_bg()
		self.end_turn_btn = Button(self, END_TURN_PATH, END_TURN_HOVER_PATH, END_TURN_PUSH_PATH, "End Turn", L_FONT, WHITE)
		self.end_turn_btn.set_rect((self.screen.get_width() - self.end_turn_btn.rect.width - 7, self.screen.get_height() - self.end_turn_btn.rect.height - 7))
		
		# load character info backgrounds
		self.char_info_bg = pygame.image.load(CHAR_INFO_BG_PATH).convert_alpha()
		self.char_info_turn = pygame.image.load(CHAR_INFO_TURN_PATH).convert_alpha()
		self.char_info_dead = pygame.image.load(CHAR_INFO_DEAD_PATH).convert_alpha()
		
		# init character info update state
		### name differs from the method to reveal the method outside also
		self.update_char_info = False
		
		
	def center_in_window(self):
		# center the map view's rectangle in the window
		self.rect.center = self.screen.get_rect().center
	
	
	def load_indicators(self):
		# load range indicator image
		self.move_range_ind = pygame.image.load(MOVE_RANGE_IND_PATH).convert_alpha()
		self.attack_range_ind = pygame.image.load(ATTACK_RANGE_IND_PATH).convert_alpha()
		self.heal_range_ind = pygame.image.load(HEAL_RANGE_IND_PATH).convert_alpha()
	
	
	def load_bottom_menu_bg(self):
		# load a narrow background image for the bottom bar
		bottom_bar_piece = pygame.image.load(BOTTOM_BAR_PATH).convert()
		
		# prepare a surface the width of the screen and the height of the piece
		bottom_bar = pygame.Surface( (self.screen.get_width(), bottom_bar_piece.get_height()) )
		
		# fill the bar with the pieces
		for i in range( int(self.screen.get_width() / bottom_bar_piece.get_width()) ):
			bottom_bar.blit(bottom_bar_piece, (bottom_bar_piece.get_width() * i, 0))
			
		# load action menu background
		action_menu_bg = pygame.image.load(ACTION_MENU_PATH).convert_alpha()
		
		# create surface for combining action menu and bar
		self.bottom_menu_bg = pygame.Surface( (self.screen.get_width(), action_menu_bg.get_height() + 7), pygame.SRCALPHA )
		
		# blit bar at bottom
		self.bottom_menu_bg.blit(bottom_bar, bottom_bar.get_rect( bottom=self.bottom_menu_bg.get_rect().bottom ))

		# blit action menu background at bottom left with a small margin
		self.bottom_menu_bg.blit(action_menu_bg, action_menu_bg.get_rect( bottomleft=(7, self.bottom_menu_bg.get_rect().bottom - 7 )))

	
	def update_action_buttons(self):
		# separate buttons and texts for button handling
		self.action_buttons = []
		self.action_texts = []
		
		# get actions for the character in turn
		for action in self.map.turn_controller.current_character.actions:
			# init button
			button = Button(self, ACTION_BTN_PATH, ACTION_BTN_HOVER_PATH, ACTION_BTN_PUSH_PATH, "Use", S_FONT, WHITE)
			self.action_buttons.append(button)
			# set position
			button.set_rect((17, self.screen.get_height() - 94 + 26 * self.action_buttons.index(button)))
		
			# get text
			text = action.name + " (" + str(action.strength) + ")"
			text = S_FONT.render(text, False, BLACK)
			# set position
			text_pos = text.get_rect()
			text_pos.move_ip(65, self.screen.get_height() - 84 + self.action_buttons.index(button) * 26)
			# add to list
			self.action_texts.append((text, text_pos))
	
	
	def update_character_info(self):
		# prepare surface to draw on
		self.character_info_image = pygame.Surface((self.screen.get_width(), self.char_info_bg.get_height() + 7))
		
		# count player and AI characters
		plr_count = 0
		ai_count = 0
		
		# get info for all characters
		for character in self.map.characters:
			# copy clean background
			if character.dead:
				background = self.char_info_dead.copy()
			elif character == self.map.turn_controller.current_character:
				background = self.char_info_turn.copy()
			else:
				background = self.char_info_bg.copy()
			
			# blit head image on background, clip only head
			head_image = character.view.stand_images["right"]
			head_image.set_clip(pygame.Rect(0,0, 20,20))
			background.blit(head_image, (5,5), (8,5,24,24))

			# get health text
			text_line_1 = str(character.health) + "/"
			text_line_2 = str(character.max_health)

			# render text lines on background in correct position
			t1 = S_FONT.render(text_line_1, 1, BLACK)
			t2 = S_FONT.render(text_line_2, 1, BLACK)
			t1_pos = t1.get_rect()
			t1_pos.move_ip(0,36)
			t1_pos.centerx = background.get_rect().centerx
			background.blit(t1, t1_pos)
			t2_pos = t2.get_rect()
			t2_pos.move_ip(0,46)
			t2_pos.centerx = background.get_rect().centerx
			background.blit(t2, t2_pos)

			# blit in the correct position depending on if character is AI or not
			if character.ai:
				self.character_info_image.blit(background, (self.screen.get_width() - (ai_count+1) * 34 - 5, 7))
				ai_count += 1
			else:
				self.character_info_image.blit(background, (7 + plr_count* 34, 7))
				plr_count += 1
				
		# reset update state
		self.update_char_info = False
			
	
	def draw_squares(self):
		for x in range(self.map.width):
			for y in range(self.map.height):
				square = self.map.get_square_at( Coordinates(x,y) )
				
				# convert map coordinates to screen coordinates
				screen_x, screen_y = map_to_screen(x,y)
				
				# blit the square
				self.squares_image.blit( square.type.image, (screen_x + self.draw_offset_x, screen_y) )
				
	
	def draw_range(self, indicator):
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
		# update range if it has changed
		if self.update_range == MOVEMENT:
			self.draw_range(self.move_range_ind)
		elif self.update_range == ATTACK:
			self.draw_range(self.attack_range_ind)
		elif self.update_range == HEAL:
			self.draw_range(self.heal_range_ind)
		
		# update character info if it has changed
		if self.update_char_info == True:
			self.update_character_info()
		
		# update buttons
		self.end_turn_btn.update()
		for btn in self.action_buttons:
			btn.update()
	
	
	def draw(self):
		# blit map and range
		self.screen.blit(self.squares_image, self.rect)
		self.screen.blit(self.range_image, self.rect)
		
		# blit character info
		self.screen.blit(self.character_info_image, (0,0))
		
		# bottom menu background
		self.screen.blit(self.bottom_menu_bg, self.bottom_menu_bg.get_rect(bottomleft=self.screen.get_rect().bottomleft))
		# end turn button
		self.end_turn_btn.draw()
		# action buttons
		for btn in self.action_buttons:
			btn.draw()
		# action texts, first index surface, second index position
		for text in self.action_texts:
			self.screen.blit(text[0], text[1])
