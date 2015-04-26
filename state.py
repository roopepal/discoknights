import config_reader
from constants import *
from coordinates import Coordinates
from menu import Menu, MenuOption
from event_handler import IntroEventHandler, GameEventHandler, MenuEventHandler
import pygame, sys



class StateManager(object):
	'''Manages the game state'''
	def __init__(self):
		
		# get default fullscreen setting
		self.fullscreen = FULLSCREEN
		
		# init all states
		self.intro_screen = IntroScreenState(self)
		self.game = GameState(self, 1)
		self.main_menu = MainMenuState(self)
		self.choose_map_menu = ChooseMapMenuState(self)
		self.options_menu = OptionsMenuState(self)
		self.sound_menu = SoundMenuState(self)
		self.display_menu = DisplayMenuState(self)
		
		# start game in menu
		self.current_state = self.intro_screen
		
	
	def go_to(self, state):
		# reset screen
		self.reset_screen()
		# change state
		self.current_state = state
		# change music when entering game
		if self.current_state == self.game:
			self.play_music(GAME_MUSIC_PATH)
			
	
	def reset_screen(self):
		# check if display has been initialized
		if not pygame.display.get_init():
			pygame.init()	
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
		self.state_mgr = state_mgr
	
	def handle_events(self):
		for event in pygame.event.get():
			self.event_handler.handle(event)
	
	def update(self):
		raise NotImplementedError
		
	def draw(self):
		raise NotImplementedError



class IntroScreenState(State):
	'''Intro screen'''
	def __init__(self, state_mgr):
		State.__init__(self, state_mgr)
		
		# init event handler
		self.event_handler = IntroEventHandler(self)
		
		# set screen
		self.screen = self.state_mgr.reset_screen()
		
		# load images and set default
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
		self.screen.fill(BLACK)
		self.screen.blit(self.image, self.image.get_rect(center=self.screen.get_rect().center))
	
	

class GameState(State):
	'''Actual game'''
	def __init__(self, state_mgr, map_index):
		State.__init__(self, state_mgr)
		# init screen
		self.screen = self.state_mgr.reset_screen()
		
		# init config reader
		self.config_reader = config_reader.ConfigReader()
		
		# build map with config reader
		self.map = self.config_reader.get_map(self, map_index)
		
		# init event handler
		self.event_handler = GameEventHandler(self, self.map)
		
		# start game
		self.map.start_game()
		
		# running state
		self.running = True

		
		
	def update(self):
		# update map and range indicators
		self.map.view.update()
		
		# update characters
		for character in self.map.characters:
			character.view.update()
			


	def draw(self):
		# draw map and range indicators
		self.map.view.draw()
		
		# draw characters and objects
		for x in range(self.map.width):
			for y in range(self.map.height):
				square = self.map.get_square_at(Coordinates(x,y))
				character = square.character
				map_object = square.object 
				if character and not character.dead:
					character.view.draw()
				if map_object:
					map_object.view.draw()
		


class MenuState(State):
	'''Parent class for menus'''
	def __init__(self, state_mgr):
		State.__init__(self, state_mgr)
		
		# init screen
		self.screen = self.state_mgr.reset_screen()
		# init menu
		self.menu = Menu(self)
		# init event handler
		self.event_handler = MenuEventHandler(self, self.menu)
		
		
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
		self.menu.screen.fill(BLACK)
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
		self.menu.options.append( MenuOption(self.menu, "Effects: ON", self.toggle_effects) )
		self.menu.options.append( MenuOption(self.menu, "Back to Options", self.go_to_options) )
		
		# set sound toggles
		self.music_on = True
		self.effects_on = True
		
		# set option positioning
		self.set_rects()
		

	def toggle_music(self):
		if self.music_on:
			pygame.mixer.musiset_volume(0)
			self.music_on = False
			self.menu.options[0].text = "Music: OFF"
		else:
			pygame.mixer.musiset_volume(VOLUME)
			self.music_on = True
			self.menu.options[0].text = "Music: ON"


	def toggle_effects(self):
		if self.effects_on:
			self.effects_on = False
			self.menu.options[1].text = "Effects: OFF"
		else:
			pygame.mixer.musiunpause()
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
			
			self.menu.options.append( MenuOption(self.menu, "Back to Main Menu", self.go_to_main_menu) )
		
			# set option positioning
			self.set_rects()
	
		def go_to_sound_menu(self):
			self.state_mgr.go_to(self.state_mgr.sound_menu)