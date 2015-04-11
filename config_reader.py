from action import Action
from map import Map
from object_type import ObjectType
from squaretype import SquareType
from character import Character
from coordinates import Coordinates
import direction

#import json

class ConfigReader(object):
    
    def read_config(self, input):
        
        self.config = []
        self.current_line = ''
        self.line_count = 0
        self.block_index = -1
        
        def nl():
            self.current_line = input.readline().strip()
            self.line_count += 1
                                            
        #try:

        self.lines_in_file = 0
        for line in input:
            self.lines_in_file += 1
        
        input.seek(0)   
        
        nl()
        
        #header_parts = self.current_line.split()
        
        '''
        if header_parts[0] != "DISCO":
            # raise error
            print()
        if header_parts[1] != "KNIGHTS":
            # raise error
        if header_parts[2].strip().lower() != 'config':
            # raise error
        '''
                    
        while self.line_count <= self.lines_in_file:                
            
            # If line doesn't start with #, go to the next line
            if not self.current_line.startswith('#'): 
                nl()
            
            # If the line is empty or a comment, jump back to the beginning of the loop
            if self.current_line == '' or self.current_line.startswith("//"):
                continue
            
            # A block was found, add a new item to the dictionary
            self.config.append({'id' : self.current_line.strip("#")})
            self.block_index += 1
            nl()
            
            # While still in the same block and rows left in file
            while not self.current_line.startswith('#') and self.line_count <= self.lines_in_file:
                                
                # Skip empty lines and comments
                if self.current_line == '' or self.current_line.startswith("//"):
                    nl()
                
                elif ":" in self.current_line:
                    line_parts = self.current_line.split(":")
                    # If there's a beginning bracket after the colon, put the following into a list or a dict
                    if line_parts[1].strip() == "{":
                        
                        # Save the key, it will be lost if a dict is created
                        key = line_parts[0]
                        nl()
                        
                        # If there is a colon, create a dict
                        if ":" in self.current_line:
                            self.config[self.block_index][key] = {}
                            
                            while not "}" in self.current_line:
                                line_parts = self.current_line.split(":")
                                
                                # If there is multiple values, create a list of the values
                                if "," in line_parts[1]:
                                    self.config[self.block_index][key][line_parts[0]] = [ value.strip() for value in line_parts[1].split(",") ]
                                else:
                                    self.config[self.block_index][key][line_parts[0]] = line_parts[1].strip()
                                nl()
                        
                        # If there is no colon, create a list
                        else:
                            self.config[self.block_index][key] = []

                            while not "}" in self.current_line:
                                self.config[self.block_index][key].append(self.current_line.split())
                                nl()
                        
                        # Ending bracket was found, go to next line
                        nl()
                    
                    # If there's no beginning bracket, just take the value and do not create another structure
                    else:
                        self.config[self.block_index][line_parts[0]] = line_parts[1].strip()
                        nl()
        
        #print("The following config was created:")
        #print(json.dumps(self.config, indent=2))
        
        return self.config
        
        #except:
            #print("There was an error.")
    
    def build_from_config(self, map_config, character_config):
        
        m = Map()
        
        for item in map_config:
            if item["id"].lower() == "squaretype":
                print("Building squaretype '{:}'...".format(item["name"]))
                m.add_squaretype(
                    SquareType(
                        item["name"],
                        item["short"],
                        (item["walkable"].lower() in ["true"]),
                        item["sprite"]
                        )
                    )
            
            elif item["id"].lower() == "object":
                print("Building object type '{:}'...".format(item["name"]))
                m.add_object_type(
                    ObjectType(
                        item["name"],
                        item["short"],
                        item["sprite"],
                        int(item["offset_x"]),
                        int(item["offset_y"])
                        )
                    )
            
            elif item["id"].lower() == "map":
                print("Building map...")
                m.build_map(
                    int( item["height"] ), 
                    int( item["width"] ), 
                    item["squares"]
                    )
                
        for item in character_config:

            if item["id"].lower() == "character":
                print("Building character '{:}'...".format(item["name"]))
                new_character = Character(
                                    item["name"],
                                    int(item["max_health"]),
                                    int(item["move_range"]),
                                    item["is_ai"].lower() == "true"
                                    )
                                    
                if 'stand_sprites' in item:
                    new_character.stand_sprites = item["stand_sprites"]
                
                if 'walk_sprites' in item:
                    new_character.walk_sprites = item["walk_sprites"]
                
                coordinates = Coordinates(int(item["x"]), int(item["y"]))
                if m.contains_coordinates(coordinates) and m.get_square_at(coordinates).squaretype.walkable:
                    m.add_character(new_character, Coordinates(int(item["x"]), int(item["y"])), getattr(direction, item["facing"].upper()))
                elif not m.get_square_at(coordinates).squaretype.walkable:
                    print("Cannot add character to {:}, square type '{:}' not walkable.".format(coordinates, m.get_square_at(coordinates).squaretype.name))
                elif not m.contains_coordinates(coordinates):
                    print("Cannot add character to {:}, out of bounds.".format(coordinates))
                
                for item2 in character_config:
                    if item2["id"].lower() == "action" and item2["character"] == new_character.name:
                        if len(new_character.actions) > 3:
                            print("Cannot have more than 3 actions.")
                        else:
                            print("Adding action {:} to character {:}...".format(item2["name"], item2["character"]))
                            new_character.add_action(
                                    getattr(Action, item2["type"].upper()),
                                    int(item2["strength"]),
                                    int(item2["max_range"]),
                                    item2["name"]
                                    )
            
        print("Map built successfully.")
        return m