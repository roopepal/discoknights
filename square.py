class Square(object):
    '''
    This class defines the Square object that represent a square on the map.
    '''
    
    visited = False
    finished = False
    range_count = 0
    
    def __init__(self, coordinates, squaretype):
        self.location = coordinates
        self.squaretype = squaretype
        self.character = None
        self.object = None
    
    def get_location(self):
        return self.location
    
    def get_type(self):
        return self.squaretype
    
    def print_type(self):
        print(self.squaretype)
    
    def get_character(self):
        return self.character
    
    def set_character(self, character):
        self.character = character

    def has_character(self):
        if self.character == None:
            return False
        else:
            return True
    
    def is_empty(self):
        if (self.character == None or self.character.dead) and self.object == None:
            return True
        else:
            return False
        
    def __str__(self):
        return "[{:}]".format(self.squaretype)
        