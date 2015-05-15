from constants import *

class Menu(object):
	'''
	A menu that contains the menu options.
	'''
	
	def __init__(self, state):
		'''Constructor'''
		
		# set state
		self.state = state
		
		# set screen
		self.screen = self.state.screen
		
		# menu options
		self.options = []


class MenuOption(object):
	'''
	A menu option with a function.
	'''
	
	def __init__(self, menu, text, function=None, func_parameter=None, greyed=False):
		'''Constructor'''
		
		# set parent menu
		self.menu = menu
		
		# set text and helper for updating it
		self.text = text
		self.update_text = True
		
		# set function
		self.function = function
		# set parameter
		self.func_parameter = func_parameter
		
		# prepare images
		self.set_images()
		self.rect = self.normal_image.get_rect()
		
		# set option state helpers
		self.hovered = False
		self.greyed = greyed
		
		# update image
		self.update()


	def set_images(self):
		'''Prepare Surfaces from the text.'''
		
		self.normal_image = XL_FONT.render(self.text, 0, MENU_OPTION_COLOR)
		self.hover_image = XL_FONT.render(self.text, 0, MENU_OPTION_HOVER_COLOR)
		self.greyed_image = XL_FONT.render(self.text, 0, MENU_OPTION_GREYED_COLOR)
		
		
	def set_rect(self):
		'''Set menu option position based on option count in the parent menu.'''
		
		# get image rect
		self.rect = self.image.get_rect()
		
		# find screen vertical center
		ver_center = WINDOW_SIZE[1] / 2
		
		# position vertically according to number of options in the menu
		self.rect.top = ver_center - len(self.menu.options) / 2 * 64 + self.menu.options.index(self) * 64
		
		# center horizontally
		self.rect.centerx = self.menu.screen.get_rect().centerx

	
	def update(self):
		'''Updates the menu option images.'''
		
		# update text surfaces if needed
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
		'''Draws the menu option to the screen.'''
		
		self.menu.screen.blit(self.image, self.rect)
		
		

class MenuOptionMapImage(MenuOption):
	'''
	Defines a menu option with a picture of a map.
	'''
	
	def __init__(self, menu, text, function=None, func_parameter=None, greyed=False ):
		'''Constructor'''
		
		super(MenuOptionMapImage, self).__init__(menu, text, function, func_parameter, greyed)
		
		# Build a picture of the map
		## build the map with the config reader
		self.map = self.menu.state.state_mgr.config_reader.get_map(self.menu.state, func_parameter)
		
		# get map count
		self.map_count = self.menu.state.state_mgr.map_count
		
		# calculate image size to adapt to multiple map counts, allow 1/4 of screen for margins
		# aspect ratio 1:1.95 for square isometric maps
		self.image_width = int((WINDOW_SIZE[0] - WINDOW_SIZE[0]/4) / self.map_count)
		self.image_height = int(self.image_width/1.95)
		
		## get map view image and scale smaller
		self.map_view_image = self.map.view.squares_image
		self.map_view_image = pygame.transform.smoothscale(self.map_view_image, (self.image_width, self.image_height))

		## build a rectangle with a border
		### 1) make a white rectangle 2) make a slightly smaller black rectangle
		self.map_image = pygame.Surface((self.image_width, self.image_height)).convert()
		self.map_image.fill(WHITE)
		black_square = pygame.Surface((self.image_width - 2, self.image_height - 2)).convert()
		self.map_image.blit(black_square, black_square.get_rect(center=self.map_image.get_rect().center))

		## blit map view image centered on the bordered rectangle
		self.map_image.blit(self.map_view_image, self.map_view_image.get_rect(center=self.map_image.get_rect().center))
		
	
	def set_rect(self):
		'''Sets the position of the options based on the available map count.'''
		
		# map number
		map_number = self.func_parameter
		
		# allow 1/16 of screen for margins between images
		margin_width = int(WINDOW_SIZE[0] / 16 / (self.map_count - 1))
		
		# get text and map image rects
		self.rect = self.image.get_rect()
		self.map_image_rect = self.map_image.get_rect()
		
		# find screen center
		hor_center = WINDOW_SIZE[0] / 2
		ver_center = WINDOW_SIZE[1] / 2
		
		# position text and map image vertically
		self.rect.top = ver_center
		self.map_image_rect.top = ver_center - 150
		
		# position horizontally according to number of maps
		## take into account map image width and margin between maps
		map_hor_pos = hor_center - (self.map_count * self.image_width + (self.map_count - 1) * margin_width) / 2 \
						+ (map_number - 1) * (self.image_width + margin_width)
		self.map_image_rect.left = map_hor_pos
		
		## center text with the map image
		self.rect.centerx = self.map_image_rect.centerx
	
	
	def draw(self):
		'''Draws the text and image to the screen.'''
		
		self.menu.screen.blit(self.image, self.rect)
		self.menu.screen.blit(self.map_image, self.map_image_rect)
