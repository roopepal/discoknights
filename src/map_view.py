from action import Action
from constants import *
from coordinates import Coordinates, map_to_screen
from ui import Button


class MapView(object):
	'''
	Defines a graphical view for the Map.
	'''
	
	def __init__(self, map_object):
		'''Constructor'''
		
		# set map
		self.map = map_object
		
		# set screen
		self.screen = self.map.state.screen
		
		# calculate the pixel width and height of the map to be drawed
		self.width = (self.map.width + self.map.height) * TILE_W / 2 
		self.height = (self.map.width + self.map.height) * TILE_H / 2 + 8	# 8 is the 'thickness' of a square
				
		# set draw offset to center the map horizontally on the surface
		self.draw_offset_x = (self.map.height - 1) * TILE_W / 2 
		
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
		self.load_char_info_backgrounds()
		
		# init character info update state
		### name differs from the method to reveal the method outside also
		self.update_char_info = False
		
		# init action effect text
		self.effect_text = None
		
		# init large event text
		self.event_text = None
		
		
	def center_in_window(self):
		'''Center the map view's rectangle in the window.'''
		
		self.rect.center = self.screen.get_rect().center
	
	
	def load_char_info_backgrounds(self):
		'''Loads the resources for the character info items.'''
		
		self.char_info_bg = pygame.image.load(CHAR_INFO_BG_PATH).convert_alpha()
		self.char_info_turn = pygame.image.load(CHAR_INFO_TURN_PATH).convert_alpha()
		self.char_info_stunned = pygame.image.load(CHAR_INFO_STUNNED_PATH).convert_alpha()
		self.char_info_dead = pygame.image.load(CHAR_INFO_DEAD_PATH).convert_alpha()
	
	
	def load_indicators(self):
		'''Loads range indicator image resources.'''
		
		self.move_range_ind = pygame.image.load(MOVE_RANGE_IND_PATH).convert_alpha()
		self.attack_range_ind = pygame.image.load(ATTACK_RANGE_IND_PATH).convert_alpha()
		self.heal_range_ind = pygame.image.load(HEAL_RANGE_IND_PATH).convert_alpha()
	
	
	def load_bottom_menu_bg(self):
		'''Loads and combines the bottom menu background image resources.'''
		
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

	
	def draw_squares(self):
		'''Draws a Surface of the squares.'''
		
		for x in range(self.map.width):
			for y in range(self.map.height):
				square = self.map.square_at( Coordinates(x,y) )
				
				# convert map coordinates to screen coordinates
				screen_x, screen_y = map_to_screen(x,y)
				
				# blit the square
				self.squares_image.blit( square.type.image, (screen_x + self.draw_offset_x, screen_y) )
				
	
	def draw_range(self, indicator):
		'''Draws a surface of the range indicators.'''
		
		# clear range image
		self.range_image.fill(0)
		
		for coordinates in self.map.in_range:
			# convert map coordinates to screen coordinates 
			screen_x, screen_y = map_to_screen(coordinates.x, coordinates.y)
			
			# blit movement range indicator
			self.range_image.blit( indicator, (screen_x + self.draw_offset_x, screen_y) )
			
			# release range update
			self.update_range = False
	
	
	def update_action_buttons(self):
		'''Updates the action use buttons and texts to represent the current character.'''
		
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
			text = action.name + " (" + str(action.strength * action.character.buff_multiplier) + ")"
			text = S_FONT.render(text, False, BLACK)
			# set position
			text_pos = text.get_rect()
			text_pos.move_ip(65, self.screen.get_height() - 84 + self.action_buttons.index(button) * 26)
			# add to list
			self.action_texts.append((text, text_pos))
	
	
	def update_character_info(self):
		'''Updates the character info items to represent the current situation.'''
		
		# prepare surface to draw on
		self.character_info_image = pygame.Surface((self.screen.get_width(), self.char_info_bg.get_height() + 7), pygame.SRCALPHA)
		
		# count teams
		team1_count = 0
		team2_count = 0
		
		# get info for all characters
		for character in self.map.characters:
			# copy clean background
			if character.dead:
				background = self.char_info_dead.copy()
			elif character.stunned > 0:
				background = self.char_info_stunned.copy()	
			elif character == self.map.turn_controller.current_character:
				background = self.char_info_turn.copy()
			else:
				background = self.char_info_bg.copy()
			
			# blit head image on background, clip only head
			head_image = character.view.stand_images["right"]
			head_image.set_clip(pygame.Rect(0,0, 20,20))
			background.blit(head_image, (5,5), (8,5,24,24))

			# get health text
			text_line_1 = str(int(character.health)) + "/"
			text_line_2 = str(int(character.max_health))

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
			if character.team == 1:
				self.character_info_image.blit(background, (7 + team1_count* 34, 7))
				team1_count += 1
			else:
				self.character_info_image.blit(background, (self.screen.get_width() - (team2_count+1) * 34 - 5, 7))
				team2_count += 1
				
		# reset update state
		self.update_char_info = False

	
	def trigger_effect_text(self, text, color, coordinates):
		'''Triggers the effect text above the wanted coordinates.'''
		
		# draw text surface
		self.effect_text = L_FONT.render(text, False, color)
		
		# convert target coordinates to screen
		screen_x, screen_y = map_to_screen(coordinates.x, coordinates.y) 
		
		# set initial position, accounting for map position on screen
		self.effect_text_rect = self.effect_text.get_rect()
		
		## position horizontally in the middle of the square
		self.effect_text_rect.right = screen_x + self.rect.x + self.draw_offset_x + self.effect_text.get_width() / 2 + 32
		
		## position vertically above the square
		self.effect_text_rect.top = screen_y + self.rect.y - 40
		
		# reset position and fade count
		self.effect_count = 0
	
	
	def update_effect_text(self):
		'''Updates the effect text position. Floats it upwards and removes it.'''
		
		# if there is text, move it upwards
		if self.effect_text:
			
			# move upward
			self.effect_text_rect.move_ip(0,-1)

			# update count
			self.effect_count += 1
			# reset if count exceeded
			if self.effect_count > 20:
				self.effect_count = 0
				self.effect_text = None

	
	def trigger_event_text(self, text, font=XL_FONT):
		'''Triggers the large event text displayed over the map.'''
		
		# draw text surface
		self.event_text = font.render(text, False, WHITE)
		
		# set position in center above map
		self.event_text_rect = self.event_text.get_rect()
		self.event_text_rect.centerx = self.screen.get_rect().centerx
		self.event_text_rect.top = self.screen.get_height() / 6
		
		# set time triggered
		self.event_text_time = pygame.time.get_ticks()
		
	
	def update_event_text(self):
		'''Removes the large event text after 1.5 seconds.'''
		
		# if there is a text to show
		if self.event_text:
			
			# show for 1.5 seconds
			if pygame.time.get_ticks() > self.event_text_time + 1500:
				self.event_text = None
			
	
	def update(self):
		'''Updates the view parts.'''
		
		# update range if it has changed
		if self.update_range == MOVEMENT_RANGE:
			self.draw_range(self.move_range_ind)
		elif self.update_range == ATTACK_RANGE:
			self.draw_range(self.attack_range_ind)
		elif self.update_range == HEAL_RANGE:
			self.draw_range(self.heal_range_ind)
		
		# update characters
		for character in self.map.characters:
			character.view.update()
		
		# update character info if it has changed
		if self.update_char_info == True:
			self.update_character_info()
		
		# update action effect text
		self.update_effect_text()
		
		# update effect text
		self.update_event_text()
		
		# update buttons		
		self.end_turn_btn.update()
		
		for btn in self.action_buttons:
			btn.update()
	
	
	def draw(self):
		'''Draws the view parts to the screen.'''
		
		# blit map and range
		self.screen.blit(self.squares_image, self.rect)
		self.screen.blit(self.range_image, self.rect)
		
		# blit characters and objects
		for x in range(self.map.width):
			for y in range(self.map.height):
				square = self.map.square_at(Coordinates(x,y))
				character = square.character
				map_object = square.object 
				if character and not character.dead:
					character.view.draw()
				if map_object:
					map_object.view.draw()
		
		# blit character info
		self.screen.blit(self.character_info_image, (0,0))
		
		# bottom menu background
		self.screen.blit(self.bottom_menu_bg, self.bottom_menu_bg.get_rect(bottomleft=self.screen.get_rect().bottomleft))
		
		# end turn button
		self.end_turn_btn.draw()
		
		# action buttons
		for btn in self.action_buttons:
			btn.draw()
		
		# action texts, first index is surface, second index is position
		for text in self.action_texts:
			self.screen.blit(text[0], text[1])
			
		# draw possible action effect test
		if self.map.view.effect_text:
			self.screen.blit(self.map.view.effect_text, self.map.view.effect_text_rect)
		
		# draw possible large event text
		if self.map.view.event_text:
			self.screen.blit(self.map.view.event_text, self.map.view.event_text_rect)