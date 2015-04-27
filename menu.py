from constants import *

class Menu(object):
	
	def __init__(self, state):
		# set state
		self.state = state
		
		# set screen
		self.screen = self.state.screen
		
		# menu options
		self.options = []


class MenuOption(object):
	
	def __init__(self, menu, text, function=None, greyed=False, func_parameter=None):
		# set parent menu
		self.menu = menu
		
		# set text and helper for updating it
		self.text = text
		self.update_text = True
		
		# set function
		self.function = function
		# set parameter
		self.func_parameter = func_parameter
		print("Got parameter: " + str(func_parameter))
		
		# prepare images
		self.set_images()
		
		# set option state helpers
		self.hovered = False
		self.greyed = greyed
		
		# update image
		self.update()


	def set_images(self):
		# prepare normal and hover image
		self.normal_image = XL_FONT.render(self.text, 0, MENU_OPTION_COLOR)
		self.hover_image = XL_FONT.render(self.text, 0, MENU_OPTION_HOVER_COLOR)
		self.greyed_image = XL_FONT.render(self.text, 0, MENU_OPTION_GREYED_COLOR)
		
		
	def set_rect(self):
		# get image rect
		self.rect = self.image.get_rect()
		
		# find screen vertical center
		ver_center = WINDOW_SIZE[1] / 2
		
		# position vertically according to number of options in the menu
		self.rect.top = ver_center - len(self.menu.options) / 2 * 64 + self.menu.options.index(self) * 64
		
		# center horizontally
		self.rect.centerx = self.menu.screen.get_rect().centerx

	
	def update(self):
		# update images if needed
		if self.update_text:
			self.set_images()
			
		# set image according to state
		if self.hovered and not self.greyed:
			self.image = self.hover_image
		elif not self.greyed:
			self.image = self.normal_image
		else:
			self.image = self.greyed_image
			
	
	def draw(self):
		self.menu.screen.blit(self.image, self.rect)
		
		

class MenuOptionPicture(MenuOption):
	pass