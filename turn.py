class TurnController(object):
    
    def __init__(self, current_map):
        self.map = current_map
        
        self.characters = []
        self.current_character = None
        
        self.current_has_moved = False
        
    def add_character(self, character):
        self.characters.append(character)
        
        # If this was the first character added, reset the turn cycle.
        if len(self.characters) == 1:
            self.reset()
        
    def reset(self):
        if not len(self.characters) == 0:
            self.current_character = self.characters[0]
        else:
            print("No characters in turn controller.")          # Debugging print
            
    def get_current_character(self):
        return self.current_character
    
    def was_moved(self):
        self.current_has_moved = True
    
    def has_moved(self):
        return self.current_has_moved
    
    def next(self):
        current_index = self.characters.index(self.current_character)
        if current_index < ( len(self.characters) - 1 ):
            self.current_character = self.characters[ current_index + 1 ]
        else:
            self.current_character = self.characters[0]
        
        if self.current_character.stunned > 0:
            # set message variable here also                                #TODO!
            self.current_character.stunned -= 1
            self.next()
        elif self.current_character.dead:
            self.next()
        else:    
            self.current_has_moved = False
            ret = "Move or choose an action."
    
            return ret
    