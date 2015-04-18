class Ai(object):    
    def __init__(self, current_map):
        self.m = current_map
        self.character = None
        
    def get_target(self):
        '''Returns the closest enemy character and the shortest path to it.'''
        self.character = self.m.turn_controller.current_character
        # Get possible targets, do not include self and other AI characters.
        possible_targets = []

        for c in self.m.characters:
            if not c.ai:
                possible_targets.append(c)
                
        # Prepare for Lee algorithm for distance calculations. Make sure every square gets a distance value.
        self.character.within_range(self.character.map.width * self.character.map.height - 1)
        self.m.print_range_counts()
        closest_enemy = None        
        closest_enemy_path = None
        closest_enemy_path_len = None
                
        for t in possible_targets:
            path = self.character.get_shortest_path(t.location)
            path_len = len(path)
            if not closest_enemy_path_len or path_len < closest_enemy_path_len:
                closest_enemy = t
                closest_enemy_path = path
                closest_enemy_path_len = path_len
        
        if len(closest_enemy_path) == 1:
            closest_enemy_path = []
        
        print(str(self.character) + " got target: " + str(closest_enemy))

        return closest_enemy, closest_enemy_path
        
    def get_next_move(self):
        '''Returns the coordinates on the path to the target character that are furthest but still in range.'''        
        target, steps = self.get_target()

        if len(steps) > 0:
            move_range = self.character.within_range(self.character.range)
        
            for i in range( len(steps) ):
                if self.character.map.get_square_at(steps[-1 - i]) in move_range:
                    print(str(self.character) + " got location " + str(steps[-1 - i]))
                    return steps[-1 - i]
        
        return False
        
        #attack_range = self.character.within_range(self.character.action_range, for_action = True)
        #
        #if self.map.get_square_at(target.location) in attack_range:
        #    print("Can attack " + str(target) + ".") 
                
    def make_move(self):
        target = self.get_next_move()
        
        print(target)
        
        if target:
            self.character.move_to_coordinates(target)
            print(str(self.character) + " moved to " + str(target))
        
        self.character.end_turn()