import direction
from action import Action
from queue import Queue


class Character(object):
    '''
    Defines a game character.
    '''
    
    def __init__(self, name, max_health, move_range, is_ai):
        '''Constructs a new game character.'''
        self.name = name
        self.location = None
        self.facing = None
        self.map = None
        self.max_health = max_health
        self.health = max_health
        self.range = move_range
        self.stand_sprites = {}
        self.walk_sprites = {}
        self.actions = []
        self.stunned = 0
        self.ai = is_ai
        self.has_moved = False
        self.dead = False
    
    def added_to_map(self, current_map, location, facing):
        '''Takes care of updating the character attributes when the character is added to a map.'''
        self.map = current_map
        self.location = location
        self.facing = facing
        
    def get_max_health(self):
        return self.max_health
    
    def get_health(self):
        return self.health    
    
    def heal(self, amount):
        '''Increases the character's health points by the given amount.'''
        self.health += amount
    
    def damage(self, amount):
        '''Decreases the character's health points by the given amount'''
        self.health -= amount
        if self.health <= 0:
            self.dead = True
            self.health = 0
    
    def stun(self, turns):
        '''Stuns the character for the given amount of turns.'''
        self.stunned += turns
        print(self.name, self.stunned)
    
    def get_range(self):
        return self.range
    
    def get_sprite_path(self):
        return self.sprite_path
    
    def get_actions(self):
        return self.actions
    
    def add_action(self, action_type, strength, action_range, description):
        '''Adds an action that the character can perform.'''
        self.actions.append( Action(self, action_type, strength, action_range, description) )
        
    def use_action(self, action_number, target_location):
        '''Performs the given action at the target location.'''
        if not self.has_turn():
            print("It's not {:}'s turn.".format(self.get_name()))           # Debugging print
            return False
        elif self.stunned > 0:
            print("{:} is stunned.".format(self.name))
            return False
        
        else:
            self.actions[action_number-1].perform(target_location)
            self.end_turn()
            return True
    
    def turn_to_direction(self, direction):
        '''Changes the direction the character is facing.'''
        self.facing = direction

    def has_turn(self):
        '''Returns True if it is the character's turn.'''
        return self.map.turn_controller.current_character == self
    
    def end_turn(self):
        '''Gives the turn to the next character.'''
        self.has_moved = False
        return self.map.get_turn_controller().next()
    
    def within_range(self, move_range, for_action=False):
        '''
        Returns a list of the squares that are within the given range from the character.
        Based on the BFS algorithm.
        
        Also sets the range_counts for squares to be used with the get_shortest_path() method.
        '''      
        within_range = []
        s = self.get_location()
        q = Queue()
        squares_in_map = self.map.get_squares()
        
        for row in squares_in_map:
            for square in row:
                square.visited = False
                square.finished = False         #Not needed?
                square.range_count = 0
        
        self.map.get_square_at(s).visited = True
        q.put(s)
        
        while not q.empty():
            #get next square from queue
            u = q.get()
            #get neighboring squares
            n = u.get_neighbors()
            for v in n:
                #if there is a square at v
                if not self.map.get_square_at(v) == False:
                    square = self.map.get_square_at(v)
                    #if the square hasn't been visited and is of a walkable type and empty
                    if square.visited == False and square.get_type().is_walkable():
                        #set range count from starting point
                        square.range_count = self.map.get_square_at(u).range_count + 1
                        #if square is still within range, put in queue
                        if square.range_count <= move_range:
                            square.visited = True
                            #if for action, does not need to be empty
                            if for_action and not square.object:
                                q.put(v)
                                if not square in within_range and not square.character == self:
                                    within_range.append(square)
                            #if for movement, needs to be empty
                            elif square.is_empty():
                                q.put(v)
                                if not square in within_range:
                                    within_range.append(square)

            self.map.get_square_at(u).finished = True
        
        #print("Calculated range.")
        return within_range
            
    def get_shortest_path(self, location):
        '''
        Gets the shortest path from the character to the given location. Uses Lee algorithm.
		
		Assumes that the method within_range() has been run right before this so that the range_counts in squares are correct.
        
        In this game, there is no such scenario where this method would be needed without first calling the within_range() method.
        This saves time since the O(MN) method does not need to be repeated.
        '''
        
        path = []
        s = self.get_location()     #start location
        e = location                #end location
        path.append(e)
        
        current_range_count = self.map.get_square_at(e).range_count 
        
        # Trace back from the end, return statement breaks the loop
        while True:
            n = e.get_neighbors()
            for v in n:
                if v == s:
                    path.reverse()
                    return path
                    
                elif self.map.get_square_at(v).range_count < current_range_count and self.map.get_square_at(v).get_type().is_walkable() and self.map.get_square_at(v).is_empty():
                    path.append(v)
                    e = v
                    current_range_count = self.map.get_square_at(e).range_count
                    break    
    
    def move_forward(self):
        '''
		Moves one step to the direction the character is facing.
		'''
        target_location = self.get_location().get_neighbor(self.get_facing())
        target_square = self.map.get_square_at(target_location)
        
        if target_square.get_type().is_walkable() and target_square.is_empty():
            self.map.get_square_at(self.location).set_character(None)
            self.location = target_location
            self.map.get_square_at(target_location).set_character(self)
            return True
        else:
            return False
        
    def move_to_direction(self, direction):
        '''
		Moves one step to the given direction.
		A helper method for move_to_coordinates().
		'''
        self.turn_to_direction(direction)
        return self.move_forward()    
        
    def move_to_coordinates(self, target):
        '''
        Moves the character to the given target coordinates, if the coordinates are within the move range of the character.
        '''
        if not self.has_turn():
            print("It's not {:}'s turn.".format(self.get_name()))           # Debugging print
            return False
        elif self.stunned:
            print("{:} is stunned".format(self.name))
        ret = False
        
        squares_within_range = self.within_range(self.range)
        
        if self.map.get_square_at(target) in squares_within_range:
            shortest_path = self.get_shortest_path(target)
            for step in shortest_path:
                                
                target_x = step.get_x()
                target_y = step.get_y()
                self_x = self.get_location().get_x()
                self_y = self.get_location().get_y()
                
                if ( target_x - self_x == 0 ) and ( target_y - self_y == -1 ):
                    ret = self.move_to_direction(direction.UP)
                if ( target_x - self_x == 1 ) and ( target_y - self_y == 0 ):
                    ret = self.move_to_direction(direction.RIGHT)
                if ( target_x - self_x == 0 ) and ( target_y - self_y == 1 ):
                    ret = self.move_to_direction(direction.DOWN)
                if ( target_x - self_x == -1 ) and ( target_y - self_y == 0 ):
                    ret = self.move_to_direction(direction.LEFT)
            
            self.has_moved = True
            return ret
        
        elif not self.map.get_square_at(target) in squares_within_range:
            print("Out of range.")                                                      # Debugging print
        
        else:
            return ret
                
    def __str__(self):
        return self.name
