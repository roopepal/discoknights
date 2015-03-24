import pygame, sys
from config_reader import ConfigReader
from map import Map
from character import Character
from squaretype import SquareType
from coordinates import Coordinates
import direction

map_input = [["w","w","w","w","w","w","w","w","w","w"],
             ["w","w","g","g","g","g","g","g","g","w"],
             ["w","g","g","g","g","g","g","g","g","w"],
             ["w","g","g","g","g","g","g","g","g","w"],
             ["w","g","g","g","g","g","g","g","g","w"],
             ["w","g","g","g","g","w","w","w","w","w"],
             ["w","g","g","g","g","w","g","g","g","w"],
             ["w","w","w","w","w","w","g","g","g","w"],
             ["w","g","g","g","g","g","g","g","g","w"],
             ["w","w","w","w","w","w","w","w","w","w"]]

def main():
    
    ''' Helper methods defined '''
    
    def map_to_screen(x,y):
        screen_x = (x - y) * (tile_w / 2) + map_offset_x
        screen_y = (x + y) * (tile_h / 2) + map_offset_y
        return screen_x, screen_y
        
    def screen_to_map(x,y):
        x -= ( map_offset_x + tile_w / 2 )
        y -= map_offset_y
        x = x / 2
        map_x = (y + x)/(tile_h)
        map_y = (y - x)/(tile_h)
        if map_x < 0:
            map_x -= 1
        if map_y < 0:
            map_y -= 1    
        return int(map_x), int(map_y)
    
    def square_clicked(screen_x, screen_y):
        x = screen_x
        y = screen_y
        map_x = ( x / (tile_w / 2) + y / (tile_h / 2) ) / 2
        map_y = ( y / (tile_h / 2) - (y / (tile_w / 2)) ) / 2
        return (map_x, map_y)
    
    
    ''' Game starts '''
    
    pygame.init()
    
    font = pygame.font.Font(None, 14)
    
    
    screen_w = 640
    screen_h = 480
    tile_w = 64
    tile_h = 32
    water_img = pygame.image.load('../graphics/water2.png')
    grass_img = pygame.image.load('../graphics/grass.gif')
    hero1_img = pygame.image.load('../graphics/hero1.gif')
    selected_img = pygame.image.load('../graphics/selected.png')
    
    f = open('game_config', 'r')
    r = ConfigReader()
    config = r.read_config(f)
    f.close()

    m = r.map_from_config(config)
    
    map_w = m.get_width() * tile_w
    map_offset_x = map_w / 2 - tile_w / 2
    map_offset_y = 64
      
    
    charA = Character("A", 100, 2,  '../graphics/hero1.gif')
    m.add_character(charA, Coordinates(1,1), direction.RIGHT)
    
    charB = Character("B", 100, 2,  '../graphics/hero1.gif')
    m.add_character(charB, Coordinates(4,4), direction.RIGHT)
    
    
    
    '''
    Set scaling here. For the best result, use 1 or 2.
    '''
    scaling = 1
    
    #screen = pygame.Surface((screen_w, screen_h))
    #window = pygame.display.set_mode((screen_w * scaling, screen_h * scaling))
    screen = pygame.display.set_mode((screen_w * scaling, screen_h * scaling))
    
    done = False
    selected = False
    selected_character = None
    mouse_pos = None
    within_range = []    
    text_to_display = None
    
    while not done:
        
        pygame.draw.rect(screen,(255,255,255),(0,0,screen_w,20))
        
        if text_to_display:
            text = font.render(text_to_display, 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.move_ip(0,5)
            textpos.centerx = screen.get_rect().centerx
            screen.blit(text, textpos)
        
        for x in range(m.get_width()):
            for y in range(m.get_height()):
                square = m.get_square_at(Coordinates(x,y))
                screen_x, screen_y = map_to_screen(x,y)
      
                if square.get_type() == m.get_squaretypes()["g"]:
                    screen.blit(grass_img, (screen_x, screen_y))
                elif square.get_type() == m.get_squaretypes()["w"]:
                    screen.blit(water_img, (screen_x, screen_y))
        
        if selected:
            mx, my = screen_to_map(mouse_pos[0], mouse_pos[1])
            sx, sy = map_to_screen(mx, my)
            
            if ( 0 <= mx < m.get_width() ) and ( 0 <= my < m.get_height() ): 
                screen.blit( selected_img, (sx, sy) )
            
            if selected_character and selected_character.has_turn():
                for sq in within_range:
                    sq_mx, sq_my = sq.get_location().get_x(), sq.get_location().get_y()
                    sq_sx, sq_sy = map_to_screen(sq_mx, sq_my)
                    screen.blit( selected_img, (sq_sx, sq_sy) )
        
        for x in range(m.get_width()):
            for y in range(m.get_height()):
                square = m.get_square_at(Coordinates(x,y))
                screen_x, screen_y = map_to_screen(x,y)

                if not square.is_empty():
                    screen.blit(hero1_img, (screen_x + 18, screen_y - 20))
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                mx = mouse_pos[0]
                my = mouse_pos[1]
                mmx = screen_to_map(mx,my)[0]
                mmy = screen_to_map(mx,my)[1]
                
                
                if ( 0 <= mmx < m.get_width() ) and ( 0 <= mmy < m.get_height() ): 
                    selected = True
                    #print(screen_to_map(mx, my))                    # Debugging print

                
                if m.get_square_at(Coordinates(mmx, mmy)):    
                    square = m.get_square_at(Coordinates(mmx, mmy))
                    
                    if not square.is_empty() and not selected_character == m.get_turn_controller().get_current_character():
                        selected_character = square.get_character()
                        if selected_character.has_turn():
                            within_range = selected_character.within_range(selected_character.get_range())
                        else:
                            text_to_display = "It's not this character's turn."
                            #print("It's not this character's turn.\n")                        # Debugging print
                    
                    if ( not square in within_range ) and square.is_empty():
                        selected_character = None
                    
                    if selected_character:
                        if square in within_range:
                            if selected_character.has_turn():
                                selected_character.move_to_coordinates(Coordinates(mmx,mmy))
                                text_to_display = selected_character.end_turn()
                                selected_character = False
                    
                    else:
                        within_range = []
                
                        
        
        
        #pygame.transform.scale(screen, (screen_w * scaling, screen_h * scaling), window)
        
        pygame.display.update()
        
    pygame.quit()
    sys.exit()
    
main()