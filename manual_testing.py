from ai import Ai
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

'''
m.characters[0].use_action(1, Coordinates(5,5))
print(m.characters[1].health)

m.characters[1].end_turn()

m.characters[0].use_action(2, Coordinates(5,5))
m.characters[0].use_action(1, Coordinates(5,5))
print(m.characters[1].health)
'''

ai = Ai(m)

ai.character = m.characters[3]

m.turn_controller.next()
m.turn_controller.next()
m.turn_controller.next()

ai.make_move()
ai.make_move()
ai.make_move()

m.print_simple()

m.turn_controller.next()
m.turn_controller.next()
m.turn_controller.next()

ai.make_move()
ai.make_move()
ai.make_move()

m.print_simple()

m.turn_controller.next()
m.turn_controller.next()
m.turn_controller.next()

ai.make_move()
ai.make_move()
ai.make_move()

m.print_simple()