class Action(object):
    
    DAMAGE = 1
    HEAL = 2
    STUN = 3
    
    def __init__(self, character, action_type, strength, action_range, description):
        self.type = action_type
        self.strength = strength
        self.range = action_range
        self.description = description
        self.character = character
        
    def get_type(self):
        return self.type
    
    def get_strength(self):
        return self.strength
    
    def get_range(self):
        return self.range
    
    def get_description(self):
        return self.description
    
    def get_character(self):
        return self.character
    
    def perform(self, target_location):
        current_location = self.character.location                                                # NOTE: for range calculation
        target_character = self.character.map.get_square_at(target_location).character
        
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
            return "Used '" + self.description + "' on " + self.character.map.get_square_at(target_location).character.name
        
    def __str__(self):
        return self.description