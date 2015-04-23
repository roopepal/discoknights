class Action(object):
	
	# Action types
	DAMAGE = 1
	HEAL = 2
	STUN = 3
	
	def __init__(self, character, action_type, strength, action_range, name):
		self.type = action_type
		self.strength = strength
		self.range = action_range
		self.name = name
		self.character = character


	def get_action_range(self):
		'''
		Returns a list of the coordinates that are within the
		action's range from the character. The square must not
		have an object in it to be included.
		
		Based on the BFS algorithm.
		'''
		action_range = self.range
		
		in_range = []
		squares_in_map = self.charactermap.squares
		start = self.character.coordinates
		queue = Queue()

		# reset the status of all squares
		for row in squares_in_map:
			for square in row:
				# visited flag
				square.visited = False
				# steps from start
				square.range_count = 0
		
		# put the start coordinates into the queue
		queue.put(start)
		self.character.map.get_square_at(start).visited = True

		while not queue.empty():
			# get next coordinates from queue
			current = queue.get()
			# get neighboring coordinates
			neighbors = current.get_neighbors()
			for n in neighbors:
				# get neighbor square at coordinates n
				square = self.character.map.get_square_at(n)
				# if there is a square at n
				if square:
					# if the square does not have an object in it
					if square.visited == False and square.object == None:
						# set range count from start to be one more than for the current square
						square.range_count = self.character.map.get_square_at(current).range_count + 1
						# if square is still within range, put in queue
						if square.range_count <= action_range:
							square.visited = True
							queue.put(n)
							# if not already in the list that will be returned, add
							if not square.coordinates in in_range:
								in_range.append(square.coordinates)
		return in_range
		

	def perform(self, target_coordinates):
		current_coordinates = self.character.coordinates
		target_character = self.character.map.get_square_at(target_coordinates).character

		if not target_character:
			print("Missed!")
			return "Missed!"
		else:
			if self.type == Action.DAMAGE:
				target_character.damage(self.strength)
			elif self.type == Action.HEAL:
				target_character.heal(self.strength)
			elif self.type == Action.STUN:
				target_character.stun(self.strength)
				print("Stunned {:} for {:} turns.".format(target_character, self.strength))
			return "Used '" + self.name + "' on " + self.character.map.get_square_at(target_coordinates).character.name


	def __str__(self):
		return self.name