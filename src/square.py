class Square(object):
	'''
	This class defines the Square object that represent a square on the map.
	'''
	
	def __init__(self, coordinates, squaretype):
		'''Constructor'''
		
		self.visited = False
		self.finished = False
		self.range_count = 0
		
		self.coordinates = coordinates
		self.type = squaretype
		self.character = None
		self.object = None
	
	
	def is_empty(self):
		'''Returns True of False depending on if the square is empty.'''
		
		if (self.character == None or self.character.dead) and self.object == None:
			return True
		else:
			return False


	def __str__(self):
		return "[{:}]".format(self.type)
