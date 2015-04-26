import pygame, sys

if not pygame.display.get_init():
	pygame.init()

class Button(object):
	hover = False
	
	def __init__(self, map_view, normal_img_path, hover_img_path, push_img_path, text, font, font_color):
		# set map view the button is on
		self.map_view = map_view
		
		# set surfaces and draw text
		self.normal_image = pygame.image.load(normal_img_path).convert_alpha()
		self.hover_image = pygame.image.load(hover_img_path).convert_alpha()
		self.push_image = pygame.image.load(push_img_path).convert_alpha()
		
		# set rect
		self.rect = self.normal_image.get_rect()
		
		# draw text and center on button
		self.text_image = font.render(text, 0, font_color)
		self.text_image.convert_alpha()
		
		# draw text on images
		self.normal_image.blit(self.text_image, self.text_image.get_rect(center = self.normal_image.get_rect().center))
		self.hover_image.blit(self.text_image, self.text_image.get_rect(center = self.hover_image.get_rect().center))
		self.push_image.blit(self.text_image, self.text_image.get_rect(center = self.push_image.get_rect().center))

		# update image
		self.update()

	
	def set_rect(self, pos):
		self.rect.topleft = pos
	
	
	def update(self):
		# set image according to mouse state
		if self.rect.collidepoint(pygame.mouse.get_pos()):
			if pygame.mouse.get_pressed()[0]:
				self.image = self.push_image
			else:
				self.image = self.hover_image
		else:
			self.image = self.normal_image
	
	
	def draw(self):
		# draw button on screen
		self.map_view.screen.blit(self.image, self.rect)