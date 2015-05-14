from config_reader import ConfigReader
from constants import *
from menu import Menu, MenuOption, MenuOptionMapImage
from event_handler import IntroEventHandler, GameEventHandler, MenuEventHandler
import pygame, sys



class StateManager(object):
	'''
	Manages the program states.
	'''
	
	def __init__(self):
		'''Constructor'''
		
		# get default fullscreen setting
		self.fullscreen = FULLSCREEN
		
		# Initialize screen and set display mode
		self.reset_screen()
		
		# load cursor and hide system cursor
		pygame.mouse.set_visible(False)
		self.cursor = pygame.image.load(CURSOR_PATH).convert_alpha()
		self.cursor_pos = self.cursor.get_rect()
		
		# prepare music and sound effect toggles
		self.music = True
		self.sound_effects = True
		
		# init config reader (reads config files for map and characters)
		self.config_reader = ConfigReader()
		
		# count maps available
		self.map_count = self.config_reader.count_available_maps()
		
		# init states
		self.init_states()
		
		# start program at intro screen
		self.current_state = self.intro_screen
		
	
	def init_states(self):
		'''Initializes all states used in the program.'''
		
		# Intro screen
		self.intro_screen = IntroScreenState(self)
		
		# Game
		self.game = None
		
		# Menus
		self.main_menu = MenuState(self)
		self.options_menu = MenuState(self)
		self.sound_menu = MenuState(self)
		self.display_menu = MenuState(self)
		self.choose_map_menu = ChooseMapMenuState(self)
		
		# Credits
		self.credits = CreditsState(self)
		
		# Add menu options
		self.main_menu.add_option( "Resume Game", self.go_to_game, greyed=True )
		self.main_menu.add_option( "New Game", self.go_to, self.choose_map_menu )
		self.main_menu.add_option( "Options", self.go_to, self.options_menu )
		self.main_menu.add_option( "Credits", self.go_to, self.credits )
		self.main_menu.add_option( "Quit", self.quit )
				
		self.options_menu.add_option( "Sound", self.go_to, self.sound_menu )
		self.options_menu.add_option( "Display", self.go_to, self.display_menu )
		self.options_menu.add_option( "Back to Main Menu", self.go_to, self.main_menu )		
		
		self.sound_menu.add_option( "Music: ON", self.toggle_music )
		self.sound_menu.add_option( "Effects: ON", self.toggle_sound_effects )
		self.sound_menu.add_option( "Back to Options", self.go_to, self.options_menu )		
		
		self.display_menu.add_option( "Fullscreen: OFF", self.toggle_fullscreen )
		self.display_menu.add_option( "Back to Options", self.go_to, self.options_menu )
		
		# set option positioning for the menus
		for menu in [self.main_menu, self.options_menu, self.sound_menu, self.display_menu]:
			menu.set_rects()

	
	def go_to(self, state):
		'''Sets the current state to the given state.'''
		
		# reset screen
		self.reset_screen()
		
		# change state
		self.current_state = state
		
		# change music when entering game or menu
		if state == self.game and not self.game.running:
			self.game.running = True
			self.play_music(GAME_MUSIC_PATH)
			
		# if no music and entered main menu, play intro music
		elif not pygame.mixer.music.get_busy() and state == self.main_menu:
			self.play_music(INTRO_MUSIC_PATH)
			
		# if entered credits state, reset credits text positioning
		elif state == self.credits:
			self.credits.reset_position()
	
	
	def go_to_game(self):
		'''Sets the current state to the game state.'''
		
		# we need this in order to stay up-to-date on which game state object to reference, since 
		# python is "call-by-object", and the game state object we want to reference changes
		self.go_to(self.game)
	
	
	def quit(self):
		'''Exits the program safely.'''
		
		# quit program
		pygame.quit()
		sys.exit()
			
	
	def reset_screen(self):
		'''Returns a reset screen.'''
		
		# check if display has been initialized
		if not pygame.display.get_init():
			pygame.init()
		
		# set caption
		pygame.display.set_caption("Disco Knights")
		
		# set fullscreen flag
		flag = self.fullscreen * pygame.FULLSCREEN
		
		# set screen, get fullscreen setting from constants
		screen = pygame.display.set_mode( WINDOW_SIZE, flag )
		
		# fill with black
		screen.fill(BLACK)
		
		return screen
	
	
	def toggle_fullscreen(self):
		'''Toggles the fullscreen setting.'''
		
		# toggle fullscreen setting
		if self.fullscreen:
			self.fullscreen = False
			self.display_menu.menu.options[0].text = "Fullscreen: OFF"
		else:
			self.fullscreen = True
			self.display_menu.menu.options[0].text = "Fullscreen: ON"
		# reset screen
		self.reset_screen()
	
		
	def play_music(self, file_path, loop=-1, new_volume=None):
		'''Plays the music at the given path. Loops forever as default.'''
		
		# check for mixer
		if not pygame.mixer.get_init():
			pygame.mixer.init()
		
		# get current volume if new volume not given
		if not new_volume:
			volume = pygame.mixer.music.get_volume()
		# check for file
		if file_path:
			# load music
			music = pygame.mixer.music.load(file_path)
			# set volume
			pygame.mixer.music.set_volume(volume)
			# play music
			pygame.mixer.music.play(loop)

	
	def toggle_music(self):
		'''Toggles music volume to zero and back.'''
		
		if self.music:
			pygame.mixer.music.set_volume(0)
			self.music = False
			self.sound_menu.menu.options[0].text = "Music: OFF"
		else:
			pygame.mixer.music.set_volume(VOLUME)
			self.music = True
			self.sound_menu.menu.options[0].text = "Music: ON"


	def toggle_sound_effects(self):
		'''Toggles sound effects on and off.'''
		
		if self.sound_effects:
			self.sound_effects = False
			self.sound_menu.menu.options[1].text = "Effects: OFF"
		else:
			self.sound_effects = True
			self.sound_menu.menu.options[1].text = "Effects: ON"
	


class State(object):
	'''
	Super class for game states.
	'''
	
	def __init__(self, state_mgr):
		'''Constructor'''
		
		# set state manager
		self.state_mgr = state_mgr
		
		# init screen
		self.screen = self.state_mgr.reset_screen()
	
	
	def handle_events(self):
		'''Asks the event handler to handle events.'''
		
		for event in pygame.event.get():
			self.event_handler.handle(event)
	
	
	def update(self):
		raise NotImplementedError
	
		
	def draw(self):
		raise NotImplementedError
	
		
	def draw_cursor(self):
		self.screen.blit(self.state_mgr.cursor, self.state_mgr.cursor_pos)



class IntroScreenState(State):
	'''
	Intro screen state.
	'''
	
	def __init__(self, state_mgr):
		'''Constructor'''
		
		super(IntroScreenState, self).__init__(state_mgr)
		
		# init event handler
		self.event_handler = IntroEventHandler(self)
		
		# load background image
		self.bg = pygame.image.load(INTRO_BACKGROUND_PATH).convert()
		
		# load text surfaces and set default
		self.text_image_white = XL_FONT.render("< press any key >", 0, WHITE)
		self.text_image_grey = XL_FONT.render("< press any key >", 0, MENU_OPTION_COLOR)
		self.image = self.text_image_white
		
		# play music
		self.state_mgr.play_music(INTRO_MUSIC_PATH)
		
		# init timer
		self.timer = pygame.time.get_ticks()
	
	
	def toggle_image(self):
		'''Toggles the text surfaces of different color.'''
		
		if self.image == self.text_image_white:
			self.image = self.text_image_grey
		else:
			self.image = self.text_image_white
	
	
	def update(self):
		'''Changes text color every 0.5 seconds.'''
		
		# change image every half second
		if pygame.time.get_ticks() > (self.timer + 500):
			self.toggle_image()
			self.timer = pygame.time.get_ticks()
		
	
	def draw(self):
		'''Draws the background and the text.'''
		
		self.screen.blit(self.bg, (0,0))
		self.screen.blit(self.image, self.image.get_rect(center=self.screen.get_rect().center))
	
	

class GameState(State):
	'''
	Defines the game state.
	'''

	def __init__(self, state_mgr, map_index):
		'''Constructor'''
		
		super(GameState, self).__init__(state_mgr)
		
		# build map with config reader
		self.map = self.state_mgr.config_reader.get_map(self, map_index)
		
		# check if the teams are controlled by AI
		self.team1_ai = False
		self.team2_ai = False
		
		for c in self.map.characters:
			if c.ai:
				if c.team == 1:
					self.team1_ai = True
				elif c.team == 2:
					self.team2_ai = True
		
		# init event handler
		self.event_handler = GameEventHandler(self)
		
		# start game
		self.map.start_game()
		
		# running state
		self.running = False
		
	
	def check_for_win(self):
		'''Checks for and handles game ending and recognizes the winner.'''
			
		team1_alive = 0
		team2_alive = 0
		
		# check all characters
		for c in self.map.characters:
			if c.team == 1 and not c.dead:
				team1_alive += 1
			elif c.team == 2 and not c.dead:
				team2_alive += 1
		
		# init game over state
		if team1_alive == 0:
			# team 2 won
			self.state_mgr.game_over = GameOverMenuState(self.state_mgr, 2, self.team1_ai, self.team2_ai)

		elif team2_alive == 0:
			# team 1 won
			self.state_mgr.game_over = GameOverMenuState(self.state_mgr, 1, self.team1_ai, self.team2_ai)

		# go to game over state
		if team1_alive == 0 or team2_alive == 0:
			
			self.state_mgr.go_to(self.state_mgr.game_over)
			
			self.running = False
			
			# disable "resume game" option
			self.state_mgr.main_menu.menu.options[0].greyed = True
	
	
	def update(self):
		'''Updates the game state.'''
		
		# check for winner
		self.check_for_win()
				
		# update map and range indicators
		self.map.view.update()
			

	def draw(self):
		'''Draws the game to the screen.'''
		
		# fill screen
		self.screen.fill(GAME_BACKGROUND_COLOR)
		
		# draw map and range indicators
		self.map.view.draw()
		


class MenuState(State):
	'''Defines a menu state.'''
	
	def __init__(self, state_mgr):
		'''Constructor'''
		
		super(MenuState, self).__init__(state_mgr)

		# init menu
		self.menu = Menu(self)

		# init event handler
		self.event_handler = MenuEventHandler(self)
		
		# load background image
		self.bg = pygame.image.load(MENU_BACKGROUND_PATH).convert()
		
	
	def add_option(self, text, function, func_parameter=None, greyed=False):
		'''Creates and adds a new option to the menu.'''
		
		new_menu_option = MenuOption(self.menu, text, function, func_parameter, greyed)
		
		self.menu.options.append(new_menu_option)
	
	
	def set_rects(self):
		'''Sets option positioning.'''
		
		for option in self.menu.options:
			option.set_rect()
		
	
	def update(self):
		'''Updates options.'''
		
		for option in self.menu.options:
			option.update()
	
	
	def draw(self):
		'''Draws background and options to the screen.'''
		
		# clear background
		self.menu.screen.blit(self.bg, (0,0))
		# draw options
		for option in self.menu.options:
			option.draw()



class ChooseMapMenuState(MenuState):
		'''
		Map selection menu.
		'''
		
		def __init__(self, state_mgr):
			'''Constructor'''
		
			super(ChooseMapMenuState, self).__init__(state_mgr)
		
			# add menu options
			### maps
			for i in range(self.state_mgr.map_count):
				# concatenate map number to menu option text
				string = "Map " + str(i+1)
				# add menu option
				self.menu.options.append( MenuOptionMapImage(self.menu, string, self.start_game_with_map, func_parameter=(i+1)) )
				# set positioning
				self.menu.options[i].set_rect()

			### back to main menu option
			self.add_option( "Back to Main Menu", self.state_mgr.go_to, self.state_mgr.main_menu )
			
			###### init position and move downwards
			self.menu.options[-1].set_rect()
			self.menu.options[-1].rect.top = self.screen.get_rect().centery + 100
			
	
		def start_game_with_map(self, map_index):
			'''Moves to the game state with the given map.'''
			
			# update state manager game
			self.state_mgr.game = GameState(self.state_mgr, map_index)
			
			# go to game
			self.state_mgr.go_to_game()
			
			

class GameOverMenuState(MenuState):
		'''
		Game over menu, shows the end result.
		'''
		
		def __init__(self, state_mgr, winner, team1_ai, team2_ai):
			'''Constructor'''
		
			super(GameOverMenuState, self).__init__(state_mgr)
		
			# get game over banner image
			self.image = pygame.image.load(GAME_OVER_BANNER_PATH).convert_alpha()
									
			# set text and music based on who own and if game was played with AI
			if not team1_ai and team2_ai:
				if winner == 1:
					self.text = "You Won!"
					self.state_mgr.play_music(VICTORY_MUSIC_PATH, loop=0)
				else:
					self.text = "You Lost!"
					self.state_mgr.play_music(LOSE_MUSIC_PATH, loop=0)
			
			elif team1_ai and not team2_ai:
				if winner == 2:
					self.text = "You Won!"
					self.state_mgr.play_music(VICTORY_MUSIC_PATH, loop=0)
				else:
					self.text = "You Lost!"
					self.state_mgr.play_music(LOSE_MUSIC_PATH, loop=0)
					
			else:
				if winner == 1:
					self.text = "Plr 1 Won!"
					self.state_mgr.play_music(VICTORY_MUSIC_PATH, loop=0)
				else:
					self.text = "Plr 2 Won!"
					self.state_mgr.play_music(VICTORY_MUSIC_PATH, loop=0)
				
			# draw text
			self.text = XXL_FONT.render(self.text, True, BLACK)
			
			# blit text on image
			self.image.blit(self.text, self.text.get_rect(center=self.image.get_rect().center))
			
			# position image
			self.image_rect = self.image.get_rect()
			self.image_rect.centerx = self.screen.get_rect().centerx
			self.image_rect.top = self.screen.get_height() / 5
			
			# add back to main menu option
			self.add_option( "Back to Main Menu", self.state_mgr.go_to, self.state_mgr.main_menu )
			
			# set menu option positioning below the banner
			self.menu.options[0].rect.centerx = self.screen.get_rect().centerx
			self.menu.options[0].rect.top = self.screen.get_height() - self.screen.get_height() / 5


		def draw(self):
			'''Draws the game over state to the screen.'''
			
			# draw background
			self.screen.blit(self.bg, (0,0))
			# draw banner
			self.screen.blit(self.image, self.image_rect)
			# draw options
			for option in self.menu.options:
				option.draw()
				
				

class CreditsState(State):
	'''
	Scrolling credits.
	'''
	
	def __init__(self, state_mgr):
		'''Constructor'''
		
		super(CreditsState, self).__init__(state_mgr)
		
		# load background image
		self.bg = pygame.image.load(MENU_BACKGROUND_PATH).convert()
		
		# use the same event handler as the intro screen
		self.event_handler = self.state_mgr.intro_screen.event_handler
		
		# draw credits surface
		self.draw_credits()
	
	
	def get_credits(self):
		'''Reads credits from the credits file.'''
		
		# add lines to list
		credits = []
		line_count = 0

		file = open(CREDITS_PATH, 'r')

		for line in file:
			# remove new line characters
			line = line.rstrip("\r\n")
			# add to list
			credits.append(line)
			# increment line count
			line_count += 1

		file.close()
		
		# return text and line count
		return credits, line_count
	
	
	def draw_credits(self):
		'''Draws a surface with the credits text.'''
		
		# get text and line count
		self.text, self.line_count = self.get_credits()
		
		# create surface based on line count with line height 25px
		self.image = pygame.Surface((self.screen.get_width(), self.line_count * 25), pygame.SRCALPHA)
		
		# set initial position below screen
		self.rect = self.image.get_rect()
		self.rect.top = self.screen.get_height() + 50
		
		# draw text lines on surface
		line_count = 0
		
		for line in self.text:
			
			# lines ending with colon get a larger heading font
			if line.endswith(":"):
				text_image = XL_FONT.render(line, True, BLACK).convert_alpha()
			else:
				text_image = L_FONT.render(line, True, BLACK).convert_alpha()
				
			# position to center horizontally, and based on line count vertically
			text_rect = text_image.get_rect()
			text_rect.centerx = self.screen.get_rect().centerx
			text_rect.top = line_count * 25
			
			self.image.blit(text_image, text_rect)
			
			line_count += 1
			
	
	def reset_position(self):
		'''Sets the position below the screen'''
		self.rect.top = self.screen.get_height() + 50
	
	
	def update(self):
		'''Scrolls the credits up.'''
		
		self.rect.move_ip(0, -1)
		
		# warp back from bottom
		if self.rect.top < (- self.image.get_height()):
			self.reset_position()
		
	
	def draw(self):
		
		self.screen.blit(self.bg, (0,0))
		self.screen.blit(self.image, self.rect)
		