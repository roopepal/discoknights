class ObjectType(object):
	'''
	Defines a map object type.
	'''
	
	def __init__(self, name, short, sprite_path, offset_x, offset_y):
		'''Constructor'''
		
		self.name = name
		self.short = short
		self.sprite_path = sprite_path
		self.offset_x = offset_x
		self.offset_y = offset_y

	def __str__(self):
		return self.name