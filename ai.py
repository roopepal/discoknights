from action import Action
import random

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
            if not c.ai and not c.dead:
                possible_targets.append(c)
                
        # Prepare for Lee algorithm for distance calculations. Make sure every square gets a distance value.
        self.character.within_range(self.character.map.width * self.character.map.height - 1)
        print("!")
        closest_enemy = None        
        closest_enemy_path = None
        closest_enemy_path_len = None
                
        for t in possible_targets:
            print(t)
            path = self.character.get_shortest_path(t.location)
            print("Got shortest path...")
            path_len = len(path)
            if not closest_enemy_path_len or path_len < closest_enemy_path_len:
                closest_enemy = t
                closest_enemy_path = path
                closest_enemy_path_len = path_len
            print(str(t) + " was the best target so far.")
        
        if len(closest_enemy_path) == 1:
            closest_enemy_path = []
        
        print(str(self.character) + " got target: " + str(closest_enemy))
        
        return closest_enemy, closest_enemy_path
        
    def get_next_move(self):
        '''Returns the coordinates on the path to the target character that are furthest but still in movement range.'''        
        target, steps = self.get_target()

        if len(steps) > 0:
            move_range = self.character.within_range(self.character.range)
        
            for i in range( len(steps) ):
                if self.character.map.get_square_at(steps[-1 - i]) in move_range:
                    print(str(self.character) + " got location " + str(steps[-1 - i]))
                    return steps[-1 - i]
        
        return False
    
    def get_action(self):
        '''Returns an action and the coordinates to perform it on.
           The action with the highest possible damage caused is selected.'''
        target = self.get_target()[0]
        target_in_range = False
        actions = self.character.actions
        chosen_action = None
        
        longest_range = None
        for action in actions:
            if longest_range == None or action.range > longest_range:
                longest_range = action.range
        
        within_range = self.character.within_range(longest_range, for_action=True)
        
        # check if target character is in action range
        for square in within_range:
            if square.character and square.character == target:
                target_in_range = True
        
        print("target in range: " + str(target_in_range))
                
        if target_in_range:
            distance_to_target = len(self.character.get_shortest_path(target.location))
            
            '''Get the action with the highest damage and enough range.
               A random term may affect the choice: a modifier drawn from 
               the normal distribution is added to the damage when choosing,
               so the AI is rational most of the time but not always. 
               If a stun action is possible, choose action or stun randomly.'''
            highest_damage = None
            highest_damage_action = None
            
            for action in actions:
                if action.range >= distance_to_target:
                    if action.type == Action.DAMAGE:
                        random_term = random.normalvariate(0, 7.75)
                        print(str(random_term))
                        damage = action.strength + random_term
                    #elif action.type == Action.STUN:
                    #    damage = 
                        
                    # if damage is higher than for any action so far
                    if highest_damage == None or damage > highest_damage:
                        highest_damage = damage
                        highest_damage_action = action
                    
            return highest_damage_action, target.location
        else:
            return False, False
        
    
    def make_move(self):
        '''Moves the AI player towards its target. For the command line version, not used in the GUI version.'''
        
        target = self.get_next_move()
                
        if target:
            self.character.move_to_coordinates(target)
            print(str(self.character) + " moved to " + str(target))
        
        self.character.end_turn()