from constants import *
from coordinates import map_to_screen
from direction import *
import pygame, os


class CharacterView(object):
	'''
	Defines a graphical view for the Character.
	'''
	
	def __init__(self, character):
		'''Constructor'''
		
		self.character = character
		
		# create dicts for images
		self.stand_images = {}
		self.walk_images = {}
		
		# position character in the center of the isometric tile
		self.draw_offset_x = CHARACTER_OFFSET_X
		self.draw_offset_y = CHARACTER_OFFSET_Y
		
		# load sprite images
		# there is one standing sprite for each direction
		for sprite_path in self.character.stand_sprite_paths:
			image = pygame.image.load( os.path.join(GRAPHICS_DIR, self.character.stand_sprite_paths[sprite_path] ) )
			self.stand_images[sprite_path] = image
		
		# check if walking sprites exist
		if self.character.walk_sprite_paths:			
			# create lists for walking sprites
			for direction in get_directions():
				self.walk_images[direction[1]] = []
			
			# there are multiple sprites for each walking direction
			for direction in self.character.walk_sprite_paths:
				for sprite_path in self.character.walk_sprite_paths[direction]:
					image = pygame.image.load( os.path.join(GRAPHICS_DIR, sprite_path ) )
					self.walk_images[direction].append(image)
		
		# set current image
		self.image = self.stand_images[ self.character.facing[1] ]
		self.rect = image.get_rect()
		
		# set position the first time
		self.set_screen_pos()
		
		# initialize animation frame index
		self.anim_frame = 0
		# initialize animation frame count for half speed updating
		self.frame_count = 0
	
	
	def set_screen_pos(self):
		'''Sets the position of the view to the square the character is in.'''
		
		# get position on map
		map_pos = self.character.coordinates
		
		# convert to screen coordinates
		screen_x, screen_y = map_to_screen(map_pos.x, map_pos.y)
		
		# add horizontal draw offset to prevent negative x coordinates
		screen_x += self.character.map.view.draw_offset_x
		
		# add map offset on screen
		screen_x += self.character.map.view.rect.topleft[0]
		screen_y += self.character.map.view.rect.topleft[1]
		
		# set position on screen
		self.rect.x = screen_x + self.draw_offset_x
		self.rect.y = screen_y + self.draw_offset_y
	
	
	def get_next_walk_frame(self):
		'''Returns the next walk animation frame image.'''
		
		# get number of sprites
		anim_len = len(self.walk_images[self.character.facing[1]])

		# increment frame count
		self.frame_count += 1
		
		# check if half speed, full speed may be too fast
		if HALF_SPEED_WALK:
			if self.frame_count % 2 == 0:
				self.anim_frame += 1
		else:
			self.anim_frame += 1
		
		# reset if over number of frames
		if self.anim_frame > anim_len - 1:
			self.anim_frame = 0
		
		# return the next image
		return self.walk_images[self.character.facing[1]][self.anim_frame]
		
	
	def update(self):
		'''Updates the image and the position of the view.'''
		
		if self.character.walking:
			# set turn status to moved
			self.character.has_moved = True
			
			# get current step
			step = self.character.walk_path[0]
			
			# set facing direction
			if self.character.coordinates.is_neighbor_at(step, UP):
				self.character.facing = UP
			elif self.character.coordinates.is_neighbor_at(step, RIGHT):
				self.character.facing = RIGHT
			elif self.character.coordinates.is_neighbor_at(step, DOWN):
				self.character.facing = DOWN
			elif self.character.coordinates.is_neighbor_at(step, LEFT):
				self.character.facing = LEFT
			
			# set image
			if self.walk_images:
				self.image = self.get_next_walk_frame()
			else:
				self.image = self.stand_images[self.character.facing[1]]
			
			# move image to facing direction
			self.rect.move_ip(self.character.facing[2][0], self.character.facing[2][1])
			
			# get target screen coordinates
			target_x, target_y = map_to_screen(step.x, step.y)
			
			# add offsets to account for map positioning
			target_x += self.character.map.view.rect.topleft[0] + self.character.map.view.draw_offset_x + self.character.view.draw_offset_x
			target_y += self.character.map.view.rect.topleft[1] + self.character.view.draw_offset_y
			
			# if reached step target, go to next step
			if self.rect.topleft == (target_x, target_y):
				# move in background logic
				self.character.move_forward()
				
				# remove walked step
				self.character.walk_path.remove(step)
				
				if len(self.character.walk_path) == 0:
					# stop walking
					self.character.walking = False
					
					# set standing image
					self.image = self.stand_images[self.character.facing[1]]
					
					# set AI action
					if self.character.ai:
						# send event to event queue with timer
						pygame.time.set_timer(AI_ACTION_EVENT, AI_DELAY)
						
					# if not AI, show hint to choose action or end turn
					else:
						self.character.map.view.trigger_event_text("Choose action or End turn")
		
		# if not walking
		else:
			self.image = self.stand_images[self.character.facing[1]]
						
			
	def draw(self):
		'''Draws the view on the screen.'''
		
		self.character.map.view.screen.blit(self.image, self.rect)

