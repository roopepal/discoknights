from coordinates import Coordinates
from menu import Menu, MenuOption
from event_handler import GameEventHandler, MenuEventHandler
import pygame

class State(object):
	def __init__(self, event_handler):
		self.event_handler = event_handler
	
	def handle_events(self):
		for event in pygame.event.get():
			self.event_handler.handle(event)
	
	def update(self):
		raise NotImplementedError
		
	def render(self):
		raise NotImplementedError
		
		
class GameState(State):
	def __init__(self, mp):
		# set map
		self.map = mp
		
		# init event handler
		State.__init__(self, GameEventHandler(self.map) )
		
		# start game
		self.map.start_game()
		
	def update(self):
		# update map and range indicators
		self.map.view.update()
		
		# update characters
		for character in self.map.characters:
			character.view.update()
		
	def render(self):
		# render map and range indicators
		self.map.view.draw()
		
		# render characters and objects
		for x in range(self.map.width):
			for y in range(self.map.height):
				square = self.map.get_square_at(Coordinates(x,y))
				character = square.character
				map_object = square.object 
				if character:
					character.view.draw()
				if map_object:
					map_object.view.draw()
		
		
class MainMenuState(State):
	def __init__(self):
		# init menu object
		self.menu = Menu()
		
		State.__init__(self, MenuEventHandler(self.menu))
		
		# add menu options
		self.menu.options.append( MenuOption(self.menu, "New Game") )
		self.menu.options.append( MenuOption(self.menu, "Options") )
		self.menu.options.append( MenuOption(self.menu, "Quit") )
		
		# set option positioning
		for option in self.menu.options:
			option.set_rect()

	def update(self):
		# update options
		for option in self.menu.options:
			option.update()
	
	def render(self):
		# render options
		for option in self.menu.options:
			option.draw()