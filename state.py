import config_reader
from constants import *
from coordinates import Coordinates
from menu import Menu, MenuOption, MenuOptionMapImage
from event_handler import IntroEventHandler, GameEventHandler, MenuEventHandler
import pygame, sys



class StateManager(object):
	'''Manages the game state'''
	def __init__(self):
		
		# get default fullscreen setting
		self.fullscreen = FULLSCREEN
		
		# Initialize screen and set display mode
		self.reset_screen()
		
		# load cursor and hide system cursor
		pygame.mouse.set_visible(False)
		self.cursor = pygame.image.load(CURSOR_PATH).convert_alpha()
		self.cursor_pos = self.cursor.get_rect()
		
		# init config reader (reads config files)
		self.config_reader = config_reader.ConfigReader()
		
		# count maps available
		self.map_count = self.config_reader.count_available_maps()
		
		# init menu states
		self.intro_screen = IntroScreenState(self)
		self.main_menu = MainMenuState(self)
		self.choose_map_menu = ChooseMapMenuState(self)
		self.options_menu = OptionsMenuState(self)
		self.sound_menu = SoundMenuState(self)
		self.display_menu = DisplayMenuState(self)
		
		# init game state
		self.game = None
		
		# start game in menu
		self.current_state = self.intro_screen
		
	
	def go_to(self, state):
		# reset screen
		self.reset_screen()
		# change state
		self.current_state = state
		# change music when entering game
		if self.current_state == self.game and not self.game.running:
			self.game.running = True
			self.play_music(GAME_MUSIC_PATH)
			
	
	def reset_screen(self):
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
		
		
	def play_music(self, file_path, new_volume = None):
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
			# set channel, and loop music
			channel = pygame.mixer.music.play(-1)
		
		

class State(object):
	'''Super class for game states'''
	
	def __init__(self, state_mgr):
		# set state manager
		self.state_mgr = state_mgr
		
		# init screen
		self.screen = self.state_mgr.reset_screen()
	
	def handle_events(self):
		for event in pygame.event.get():
			self.event_handler.handle(event)
	
	def update(self):
		raise NotImplementedError
		
	def draw(self):
		raise NotImplementedError
		
	def draw_cursor(self):
		self.screen.blit(self.state_mgr.cursor, self.state_mgr.cursor_pos)



class IntroScreenState(State):
	'''Intro screen'''
	def __init__(self, state_mgr):
		State.__init__(self, state_mgr)
		
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
		if self.image == self.text_image_white:
			self.image = self.text_image_grey
		else:
			self.image = self.text_image_white
	
	
	def update(self):
		# change image every half second
		if pygame.time.get_ticks() > (self.timer + 500):
			self.toggle_image()
			self.timer = pygame.time.get_ticks()
		
	
	def draw(self):
		self.screen.blit(self.bg, (0,0))
		self.screen.blit(self.image, self.image.get_rect(center=self.screen.get_rect().center))
	
	

class GameState(State):
	'''Actual game'''

	def __init__(self, state_mgr, map_index):
		State.__init__(self, state_mgr)
		
		# build map with config reader
		self.map = self.state_mgr.config_reader.get_map(self, map_index)
		
		# init event handler
		self.event_handler = GameEventHandler(self, self.map)
		
		# start game
		self.map.start_game()
		
		# running state
		self.running = False
		
	
	def check_for_win(self):		
		plr_characters_alive = 0
		ai_characters_alive = 0
		
		# check all characters
		for c in self.map.characters:
			if not c.ai and not c.dead:
				plr_characters_alive += 1
			elif c.ai and not c.dead:
				ai_characters_alive += 1
		
		# recognize winner		
		if plr_characters_alive == 0:
			# AI won
			self.state_mgr.game_over = GameOverMenuState(self.state_mgr, 2)

		elif ai_characters_alive == 0:
			# player won
			self.state_mgr.game_over = GameOverMenuState(self.state_mgr, 1)

		if plr_characters_alive == 0 or ai_characters_alive == 0:
			self.state_mgr.go_to(self.state_mgr.game_over)
			self.running = False
			# disable "resume game" option
			self.state_mgr.main_menu.menu.options[0].greyed = True
	
	def update(self):
		# check for winner
		self.check_for_win()
				
		# update map and range indicators
		self.map.view.update()
		
		# update characters
		for character in self.map.characters:
			character.view.update()
			

	def draw(self):
		# fill screen
		self.screen.fill(BLACK)
		
		# draw map and range indicators
		self.map.view.draw()
		
		# draw characters and objects
		for x in range(self.map.width):
			for y in range(self.map.height):
				square = self.map.square_at(Coordinates(x,y))
				character = square.character
				map_object = square.object 
				if character and not character.dead:
					character.view.draw()
				if map_object:
					map_object.view.draw()
					
		# draw action effect test
		if self.map.view.effect_text:
			self.screen.blit(self.map.view.effect_text, self.map.view.effect_text_rect)
		
		# draw large event text
		if self.map.view.event_text:
			self.screen.blit(self.map.view.event_text, self.map.view.event_text_rect)


class MenuState(State):
	'''Parent class for menus'''
	def __init__(self, state_mgr):
		State.__init__(self, state_mgr)
		

		# init menu
		self.menu = Menu(self)

		# init event handler
		self.event_handler = MenuEventHandler(self, self.menu)
		
		# load background image
		self.bg = pygame.image.load(MENU_BACKGROUND_PATH).convert()
		
		
	def set_rects(self):
		# set option positioning
		for option in self.menu.options:
			option.set_rect()
			
		
	def go_to_main_menu(self):
		self.state_mgr.go_to(self.state_mgr.main_menu)
	
	def go_to_choose_map(self):
		self.state_mgr.go_to(self.state_mgr.choose_map_menu)
	
	def go_to_options(self):
		self.state_mgr.go_to(self.state_mgr.options_menu)
		
	def go_to_sound(self):
		self.state_mgr.go_to(self.state_mgr.sound_menu)
		
	def go_to_display(self):
		self.state_mgr.go_to(self.state_mgr.display_menu)
		
	def resume_game(self):
		self.state_mgr.go_to(self.state_mgr.game)
		
	def quit(self):
		pygame.quit()
		sys.exit()
		
	
	def update(self):
		# update options
		for option in self.menu.options:
			option.update()
	
	def draw(self):
		# clear background
		self.menu.screen.blit(self.bg, (0,0))
		# draw options
		for option in self.menu.options:
			option.draw()



class MainMenuState(MenuState):
	'''Main menu'''
	def __init__(self, state_mgr):
		# set name
		self.name = "Main Menu"
		
		# init parent class
		MenuState.__init__(self, state_mgr)
		
		# add menu options
		self.menu.options.append( MenuOption(self.menu, "Resume Game", self.resume_game, greyed=True) )
		self.menu.options.append( MenuOption(self.menu, "New Game", self.go_to_choose_map) )
		self.menu.options.append( MenuOption(self.menu, "Options", self.go_to_options) )
		self.menu.options.append( MenuOption(self.menu, "Quit", self.quit) )
		
		# set option positioning
		self.set_rects()
	

	
class OptionsMenuState(MenuState):
	'''Options menu'''
	def __init__(self, state_mgr):
		# set name
		self.name = "Options"
		
		# init parent class
		MenuState.__init__(self, state_mgr)
		
		# add menu options
		self.menu.options.append( MenuOption(self.menu, "Sound", self.go_to_sound) )
		self.menu.options.append( MenuOption(self.menu, "Window", self.go_to_display) )
		self.menu.options.append( MenuOption(self.menu, "Back to Main Menu", self.go_to_main_menu) )
		
		# set option positioning
		self.set_rects()
	
	def go_to_sound_menu(self):
		self.state_mgr.go_to(self.state_mgr.sound_menu)



class SoundMenuState(MenuState):
	'''Options menu'''
	def __init__(self, state_mgr):
		# set name
		self.name = "Options"
		
		# init parent class
		MenuState.__init__(self, state_mgr)
		
		# add menu options
		self.menu.options.append( MenuOption(self.menu, "Music: ON", self.toggle_music) )
		#self.menu.options.append( MenuOption(self.menu, "Effects: ON", self.toggle_effects) )
		self.menu.options.append( MenuOption(self.menu, "Back to Options", self.go_to_options) )
		
		# set sound toggles
		self.music_on = True
		self.effects_on = True
		
		# set option positioning
		self.set_rects()
		

	def toggle_music(self):
		if self.music_on:
			pygame.mixer.music.set_volume(0)
			self.music_on = False
			self.menu.options[0].text = "Music: OFF"
		else:
			pygame.mixer.music.set_volume(VOLUME)
			self.music_on = True
			self.menu.options[0].text = "Music: ON"


	def toggle_effects(self):
		if self.effects_on:
			self.effects_on = False
			self.menu.options[1].text = "Effects: OFF"
		else:
			self.effects_on = True
			self.menu.options[1].text = "Effects: ON"



class DisplayMenuState(MenuState):
	'''Options menu'''
	def __init__(self, state_mgr):
		# set name
		self.name = "Options"
		
		# init parent class
		MenuState.__init__(self, state_mgr)
		
		# add menu options
		self.menu.options.append( MenuOption(self.menu, "Fullscreen: OFF", self.toggle_fullscreen) )
		self.menu.options.append( MenuOption(self.menu, "Back to Options", self.go_to_options) )
		
		# set sound toggles
		self.music_on = True
		self.effects_on = True
		
		# set option positioning
		self.set_rects()
		

	def toggle_fullscreen(self):
		# toggle fullscreen setting
		if self.state_mgr.fullscreen:
			self.state_mgr.fullscreen = False
			self.menu.options[0].text = "Fullscreen: OFF"
		else:
			self.state_mgr.fullscreen = True
			self.menu.options[0].text = "Fullscreen: ON"
		# reset screen
		self.state_mgr.reset_screen()



class ChooseMapMenuState(MenuState):
		'''Options menu'''
		def __init__(self, state_mgr):
			# set name
			self.name = "Options"
		
			# init parent class
			MenuState.__init__(self, state_mgr)
		
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
			self.menu.options.append( MenuOption(self.menu, "Back to Main Menu", self.go_to_main_menu) )
			###### init position and move downwards
			self.menu.options[-1].set_rect()
			self.menu.options[-1].rect.top = self.screen.get_rect().centery + 100
			
	
		def start_game_with_map(self, map_index):
			self.state_mgr.game = GameState(self.state_mgr, map_index)
			self.state_mgr.go_to(self.state_mgr.game)
			
			

class GameOverMenuState(MenuState):
		'''Game over menu, shows the end result'''
		
		def __init__(self, state_mgr, winner):
			# set name
			self.name = "Options"
		
			# init parent class
			MenuState.__init__(self, state_mgr)
		
			# get game over banner image
			self.image = pygame.image.load(GAME_OVER_BANNER_PATH).convert_alpha()
			# get text based on who own
			if winner == 1:
				self.text = "You Won!"
			else:
				self.text = "You Lost!"
			self.text = XXL_FONT.render(self.text, True, BLACK)
			# blit text on image
			self.image.blit(self.text, self.text.get_rect(center=self.image.get_rect().center))
			
			# position image
			self.image_rect = self.image.get_rect()
			self.image_rect.centerx = self.screen.get_rect().centerx
			self.image_rect.top = self.screen.get_height() / 5
			
			# add back to main menu option
			self.menu.options.append( MenuOption(self.menu, "Go to Main Menu", self.go_to_main_menu) )
			# set menu option positioning below the banner
			self.menu.options[0].rect.centerx = self.screen.get_rect().centerx
			self.menu.options[0].rect.top = self.screen.get_height() - self.screen.get_height() / 5
			
			
		
		def draw(self):
			# clear background
			self.menu.screen.fill(BLACK)
			# draw banner
			self.screen.blit(self.image, self.image_rect)
			# draw options
			for option in self.menu.options:
				option.draw()