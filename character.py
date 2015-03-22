import direction
from action import Action
from queue import Queue


class Character(object):
    '''
    This class defines a game character.
    '''
    
    def __init__(self, name, max_health, move_range, sprite_path):
        self.name = name
        self.location = None
        self.facing = None
        self.map = None
        self.max_health = max_health
        self.health = max_health
        self.range = move_range
        self.sprite_path = sprite_path
        self.actions = []

    def get_all(self): #DEBUG METHOD
        ret = self.get_name() + str(self.get_location()) + str(self.get_facing())
        return ret
        
    def get_name(self):
        return self.name
    
    def get_location(self):
        return self.location
    
    def get_facing(self):
        return self.facing
    
    def set_facing(self, direction):
        self.facing = direction
    
    def get_map(self):
        return self.map
    
    def added_to_map(self, current_map, location, facing):
        self.map = current_map
        self.location = location
        self.facing = facing
        
    def get_max_health(self):
        return self.max_health
    
    def get_health(self):
        return self.health    
    
    def heal(self, amount):
        self.health += amount
    
    def damage(self, amount):
        self.health -= amount
        
    def get_range(self):
        return self.range
    
    def get_sprite_path(self):
        return self.sprite_path
    
    def get_actions(self):
        return self.actions
    
    def add_action(self, action_type, strength, action_range, description):
        self.actions.append( Action(self, action_type, strength, action_range, description) )
        
    def use_action(self, action_number, target_location):
        self.actions[action_number-1].perform(target_location)
        self.end_turn()
    
    def turn_to_direction(self, direction):
        self.facing = direction

    def has_turn(self):
        return self.map.get_turn_controller().get_current_character() == self
    
    def end_turn(self):
        return self.map.get_turn_controller().next()
    
    def within_range(self, move_range):
        '''
        Returns a list of the squares that are within a range from the character.
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
            u = q.get()
            n = u.get_neighbors()
            for v in n:
                if not self.map.get_square_at(v) == False:
                    square = self.map.get_square_at(v)
                    if square.visited == False and square.get_type().is_walkable() and square.is_empty():
                        square.range_count = self.map.get_square_at(u).range_count + 1
                        if square.range_count <= move_range:
                            square.visited = True
                            q.put(v)
                            if not square in within_range:
                                within_range.append(square)

            self.map.get_square_at(u).finished = True

        return within_range
            
    def get_shortest_path(self, location):
        '''
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
        ''' A helper method for move_to_coordinates() '''
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
        ''' A helper method for move_to_coordinates() '''
        self.turn_to_direction(direction)
        return self.move_forward()    
        
    def move_to_coordinates(self, target):
        if not self.has_turn():
            print("It's not {:}'s turn.".format(self.get_name()))           # Debugging print
            return False
        
        ret = False
        
        squares_within_range = self.within_range(self.range)
        
        if self.map.get_square_at(target) in squares_within_range:
            shortest_path = self.get_shortest_path(target)
            for step in shortest_path:
                
                #print(step)                                                            # Debugging print
                
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
        
                #self.map.print_simple()                                                 # Debugging print
            return ret
        
        elif not self.map.get_square_at(target) in squares_within_range:
            print("Out of range.")                                                      # Debugging print
        
        else:
            return ret
                
    def __str__(self):
        return self.get_name()