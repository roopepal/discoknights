from square import Square
from coordinates import Coordinates
#from character import Character
from turn import Turn

class Map(object):
    '''
    This class defines the map object that contains the game world.
    '''
    
    def __init__(self):
        self.characters = []
        self.squaretypes = {}
        self.turn_controller = Turn(self)
        
    def build_map(self, height, width, squares_input):
        self.height = height
        self.width = width
                
        self.squares = height * [None]
        for y in range(height): 
            self.squares[y] = width * [None]
        
        for y in range(height):
            for x in range(width):
                # If square type is properly configured                
                if squares_input[y][x] in self.squaretypes.keys():
                    self.squares[y][x] = Square(Coordinates(x,y), self.squaretypes[squares_input[y][x]])
                    
    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height
    
    def get_squares(self):
        return self.squares
    
    def get_square_at(self, coordinates):
        if self.contains_coordinates(coordinates):
            return self.squares[coordinates.get_y()][coordinates.get_x()]
        else:
            # raise an error
            # print("Cannot get square from outside the map.")
            return False
    
    def get_squaretypes(self):
        return self.squaretypes
    
    def add_squaretype(self, squaretype):
        if not squaretype.short in self.squaretypes:
            self.squaretypes[squaretype.short] = squaretype
      
    def add_character(self, character, coordinates, facing):
        if self.get_square_at(coordinates).is_empty():
            self.characters.append(character)
            self.turn_controller.add_character(character)
            self.get_square_at(coordinates).set_character(character)
            character.added_to_map(self,coordinates,facing)
        else:
            # raise an error
            print("Square wasn't empty. Cannot add character.")   
    
    def get_turn_controller(self):
        return self.turn_controller
    
    def contains_coordinates(self, coordinates):
        x = coordinates.get_x()
        y = coordinates.get_y()
        return 0 <= x < self.get_width() and 0 <= y < self.get_height()
    
    def print_map_only(self):
        l = [   [ str(s.get_type())[0] for s in self.squares[y] ] for y in range(self.height) ]
        for y in range(self.height):
            print(l[y])
        
    
    def print_simple(self):
        '''
        Prints a simplified version of the map with only one character representing a square or its contents.
        '''
        self.ret = ""
        for y in range(self.get_height()):
            for x in range(self.get_width()):
                if self.get_square_at(Coordinates(x,y)).is_empty():
                    self.ret = self.ret + str(self.get_square_at(Coordinates(x,y)).get_type())[0] + " "
                else:
                    self.ret = self.ret + self.get_square_at(Coordinates(x,y)).get_character().get_name()[0] + " "
            self.ret = self.ret + "\n"
        print(self.ret)
        
    def print_within_range(self, c, r):
        ''' Prints a map with movable squares marked with an x. '''
        within_range = c.within_range(r)
        self.ret = ""
        for y in range(self.get_height()):
            for x in range(self.get_width()):
                if self.get_square_at(Coordinates(x,y)).is_empty():
                    if self.get_square_at(Coordinates(x,y)) in within_range:
                        self.ret = self.ret + "x "
                    else:    
                        self.ret = self.ret + str(self.get_square_at(Coordinates(x,y)).get_type())[0] + " "
                else:
                    self.ret = self.ret + self.get_square_at(Coordinates(x,y)).get_character().get_name()[0] + " "
            self.ret = self.ret + "\n"
        print(self.ret)
    
    def print_range_counts(self):
        ''' Prints a map with movable squares marked with an x. '''
        self.ret = ""
        for y in range(self.get_height()):
            for x in range(self.get_width()):
                if self.get_square_at(Coordinates(x,y)).is_empty():
                    self.ret = self.ret + str(self.get_square_at(Coordinates(x,y)).range_count) + " "
                else:
                    self.ret = self.ret + self.get_square_at(Coordinates(x,y)).get_character().get_name()[0] + " "
            self.ret = self.ret + "\n"
        print(self.ret)
    
    
    
    
    
    
    def __str__(self):
        self.ret = ""
        for i in range(self.get_width()):
            for j in range(self.get_height()):
                self.ret = self.ret + str(self.squares[j][i].get_type()) + " " + str(self.squares[j][i].get_location()) + " "
            self.ret = self.ret + "\n"
        return self.ret
    
            
        