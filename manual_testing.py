from map import Map
from character import Character
from squaretype import SquareType
from coordinates import Coordinates
import direction
from config_reader import ConfigReader

import json

r = ConfigReader()

f = open('map_config', 'r')
map_config = r.read_config(f)
f.close()

f = open('character_config', 'r')
character_config = r.read_config(f)
f.close()

m = r.build_from_config(map_config, character_config)

m.print_simple()

print( json.dumps( m.characters[0].walk_sprites, indent = 2))


'''
m.characters[0].use_action(1, Coordinates(5,5))
print(m.characters[1].health)

m.characters[1].end_turn()

m.characters[0].use_action(2, Coordinates(5,5))
m.characters[0].use_action(1, Coordinates(5,5))
print(m.characters[1].health)
'''

