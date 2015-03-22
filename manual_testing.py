from map import Map
from character import Character
from squaretype import SquareType
from coordinates import Coordinates
import direction

map_input = [["w","w","w","w","w","w","w","w","w","w"],
             ["w","r","g","g","g","g","g","g","g","w"],
             ["w","r","r","r","r","g","g","g","g","w"],
             ["w","g","g","g","r","g","g","g","g","w"],
             ["w","g","g","g","r","w","g","g","g","w"],
             ["w","g","g","g","w","w","g","g","g","w"],
             ["w","g","g","g","r","g","g","g","g","w"],
             ["w","g","g","g","r","r","r","g","g","w"],
             ["w","g","g","g","g","g","r","g","g","w"],
             ["w","w","w","w","w","w","w","w","w","w"]]

m = Map(10,10)

m.add_squaretype( SquareType("water", False) )
m.add_squaretype( SquareType("grass", True) )
m.add_squaretype( SquareType("road", True) )

m.build_map(map_input)

charA = Character("A", 100, 3, '../graphics/hero1.gif')
charB = Character("B", 100, 3, '../graphics/hero1.gif')

charA.add_action(1, 10, 10, "Hit")
charB.add_action(1, 10, 10, "Hit")

m.add_character(charA, Coordinates(4,4), direction.RIGHT)
m.add_character(charB, Coordinates(3,4), direction.RIGHT)

m.print_simple()



#m.print_simple()
#print("A: {:}, B: {:}".format(charA.get_health(), charB.get_health()))
#charA.use_action(1, charB.get_location())
#print("A: {:}, B: {:}".format(charA.get_health(), charB.get_health()))
#charA.use_action(1, Coordinates(1,1))

print("Character A tries to move to (3,6).")
charA.move_to_coordinates(Coordinates(3,6))
charA.end_turn()

print("Character B tries to move to (4,3).")
success = charB.move_to_coordinates(Coordinates(4,3))
if success: print("Successful.")
print("Character B hits character A.")
charB.use_action(1, Coordinates(4,4))

