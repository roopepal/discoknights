from common import reset_screen
from constants import MENU_OPTION_COLOR, MENU_OPTION_HOVER_COLOR, XL_FONT
from options import window_size

class Menu(object):
	
	def __init__(self):
		# get screen
		self.screen = reset_screen()
		
		# menu options
		self.options = []


class MenuOption(object):
	
	def __init__(self, menu, text):
		# set parent menu
		self.menu = menu
		self.menu.options.append(self)
		
		# set text
		self.text = text
		
		# prepare hover state
		self.hovered = False
		
		# update image
		self.update()
		
	def set_rect(self):
		# get image rect
		self.rect = self.image.get_rect()
		
		# find screen vertical center
		ver_center = window_size[1] / 2
		
		# position vertically according to number of options in parent menu
		self.rect.top = ver_center - len(self.menu.options) / 2 * 32 + self.menu.options.index(self) * 32
		
		# center horizontally
		self.rect.centerx = self.menu.screen.get_rect().centerx


	def get_color(self):
		# return hover color if option is hovered
		if self.hovered:
			return MENU_OPTION_HOVER_COLOR
			
		# otherwise return base color
		else:
			return MENU_OPTION_COLOR


	def update(self):
		# render with large font and return surface
		self.image = XL_FONT.render(self.text, 0, self.get_color())


	def draw(self):
		self.menu.screen.blit(self.image, self.rect)