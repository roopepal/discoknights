from action import Action
from character import Character
from config_reader import ConfigReader
from coordinates import Coordinates
import direction
from isometric import *
from map import Map
import pygame, sys
from squaretype import SquareType
import ui

def main():

    def map_to_screen(x,y, offset_x=0, offset_y=0):
        screen_x = (x - y) * (tile_w / 2) + offset_x
        screen_y = (x + y) * (tile_h / 2) + offset_y
        return screen_x, screen_y
    
    def screen_to_map(x,y, offset_x=0, offset_y=0):
        x -= ( offset_x + tile_w / 2 )
        y -= offset_y
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
    
    def load_sprites():
        sprites = {}
    
        # For each character, load all sprites that are not already loaded
        for character in m.characters:
            
            for sprite in character.stand_sprites:
                if character.stand_sprites[sprite] not in sprites:
                    sprites[character.stand_sprites[sprite]] = pygame.image.load(character.stand_sprites[sprite]).convert_alpha()
                    print("Successfully loaded sprite '{:}'".format(character.stand_sprites[sprite]))
                
            for sprite_list in character.walk_sprites:
                for sprite in character.walk_sprites[sprite_list]:
                    if sprite not in sprites:
                        sprites[sprite] = pygame.image.load(sprite).convert_alpha()
                        print("Successfully loaded sprite '{:}'".format(sprite))
        
        return sprites
    
    def render_squares(surface):        
        for x in range(m.width):
            for y in range(m.height):
                square = m.get_square_at(Coordinates(x,y))
                screen_x, screen_y = map_to_screen(x,y)                
                if square.get_type() == m.get_squaretypes()["g"]:
                    surface.blit(grass_img, (screen_x, screen_y))
                elif square.get_type() == m.get_squaretypes()["w"]:
                    surface.blit(water_img, (screen_x, screen_y))
    
    def render_range(surface):
        for sq in within_range:
            sq_mx, sq_my = sq.location.x, sq.location.y
            sq_sx, sq_sy = map_to_screen(sq_mx, sq_my, map_offset_x, map_offset_y)
            if selected_action:
                if selected_action.type == Action.HEAL:
                    surface.blit( heal_target_img, (sq_sx, sq_sy) )
                else:
                    surface.blit( action_target_img, (sq_sx, sq_sy) )
            else:
                surface.blit( selected_img, (sq_sx, sq_sy) )
    
    def render_characters(surface, excluding=[]):
        # collect dirty rects
        dirty = []
        
        # For each square on the map, check if there's a character and if yes, draw it.
        for x in range(m.get_width()):
            for y in range(m.get_height()):
                square = m.get_square_at(Coordinates(x,y))
                # Translate coordinates
                screen_x, screen_y = map_to_screen(x,y, map_offset_x, map_offset_y)
                
                if square.has_character() and not square.character in excluding:
                    if square.character.facing == direction.UP: facing = "up"
                    elif square.character.facing == direction.DOWN: facing = "down"
                    elif square.character.facing == direction.LEFT: facing = "left"
                    elif square.character.facing == direction.RIGHT: facing = "right"
                    
                    # Draw sprite based on the direction facing
                    surface.blit(sprites[square.character.stand_sprites[facing]], (screen_x + character_offset_x, screen_y + character_offset_y))
                    dirty.append(pygame.Rect(48,48, screen_x+character_offset_x,screen_y+character_offset_y))
        
        return dirty
        
    def render_info_text(surface, text_to_display):
        text = font.render(text_to_display, 1, (10, 10, 10))
        textpos = text.get_rect()
        textpos.move_ip(0,screen_h - 16)
        textpos.centerx = screen.get_rect().centerx
        surface.blit(text, textpos)
        return textpos

    def render_char_info(surface, wanted=None):
        if wanted:
            if not isinstance(wanted, list):
                wanted = [wanted]
        else:
            wanted = m.characters
                
        count = 0
        ai_count = 1
        dirty = []
                
        for character in m.characters:
            
            if character in wanted:
                if character.has_turn():
                    char_info_surface = char_info_turn.copy()
                else:
                    char_info_surface = char_info.copy()
            
                head_image = pygame.image.load(character.stand_sprites["right"]).convert_alpha()
                head_image.set_clip(pygame.Rect(0,0, 20,20))
            
                char_info_surface.blit(head_image, (5,5), (8,5,24,24))
            
                text_line_1 = str(character.health) + "/"
                text_line_2 = str(character.max_health)
            
                t1 = font.render(text_line_1, 1, (10,10,10))
                t2 = font.render(text_line_2, 1, (10,10,10))
            
                t1_pos = t1.get_rect()
                t1_pos.move_ip(0,36)
                t1_pos.centerx = char_info_surface.get_rect().centerx
                char_info_surface.blit(t1, t1_pos)
            
                t2_pos = t2.get_rect()
                t2_pos.move_ip(0,46)
                t2_pos.centerx = char_info_surface.get_rect().centerx
                char_info_surface.blit(t2, t2_pos)            
                                
                if character.ai:
                    surface.blit(char_info_surface, (screen_w - ai_count * 34 - 5, 7))
                    dirty.append(pygame.Rect(32,58, screen_w - ai_count * 34 - 5,7))
                else:
                    surface.blit(char_info_surface, (7 + count* 34, 7))
                    dirty.append(pygame.Rect(32,58, 7+count*34,7))
            
            if character.ai: ai_count += 1
            else: count += 1
            

        return dirty
    
    def render_bottom_bar(surface):        
        #blit background bar
        bar = pygame.image.load("../graphics/bottom_bar.gif").convert()
        for i in range(surface.get_width() // 4):
            surface.blit(bar, (i*4, 0))
    
    def render_end_turn_button(surface):
        if end_turn_button.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                end_turn_button.pushed = True
            else:    
                end_turn_button.hovered = True
        else:
            end_turn_button.hovered = False
            end_turn_button.pushed = False
        
        end_turn_button.render_to(surface)        
        #return the button for dirty rects and mouse recognition
        return end_turn_button.rect
        
    def render_action_menu(surface):
        
        # blit menu bg
        actions_menu = pygame.image.load("../graphics/actions_menu.gif").convert()
        actions_menu.set_colorkey((0,0,0))
        surface.blit(actions_menu, (7, screen_h - 103))
        
        if selected_character:
            use_buttons = []
            count = 0
            for action in selected_character.actions:
                use_button = ui.Button(ui.action_bg, ui.action_bg_hover, ui.action_bg_push, (20, screen_h - 94 + count * 26))
                use_buttons.append(use_button)
                
                if use_button.rect.collidepoint(pygame.mouse.get_pos()):
                    if pygame.mouse.get_pressed()[0]:
                        use_button.pushed = True
                    else:    
                        use_button.hovered = True
                else:
                    use_button.hovered = False
                    use_button.pushed = False
                
                use_button.render_to(surface)
                
                text = action.description
                text = font.render(text, False, (10,10,10))
                text_pos = text.get_rect()
                text_pos.move_ip(80, screen_h - 84 + count * 26)
                surface.blit(text, text_pos)
                
                count += 1
            
            return use_buttons
        return []
    
    def render_effect_text(surface, count, text):
        if text:
            scr_loc = map_to_screen(action_target_loc.x, action_target_loc.y)
            location = (scr_loc[0] + 32 - text.get_width()/2 , scr_loc[1] - 40 - count*1)
            
            if count > 10:
                opacity = 255 - 12 * count
            else:
                opacity = 255
            
            blit_alpha(surface, text, location, opacity)
            
            count += 1
            if count > 20:
                count = 0
                return count, None
            
        return count, text
    
    def get_effect_text(action):
        if action.type == Action.HEAL:
            text = "+" + str(action.strength)
            color = (10, 200, 10)
        else:
            text = "-" + str(action.strength)
            color = (200, 10, 10)
            
        text_surface = med_font.render(text, False, color)
        return text_surface
        
    def blit_alpha(target, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pygame.Surface((source.get_width(), source.get_height())).convert_alpha()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)        
        target.blit(temp, location)
    
    
    ''' Game starts '''
    pygame.init()
    clock = pygame.time.Clock()
    fps = 150
    
    #read config from files
    r = ConfigReader()
    f = open('map_config', 'r')
    map_config = r.read_config(f)
    f.close()
    f = open('character_config', 'r')
    character_config = r.read_config(f)
    f.close()
    m = r.build_from_config(map_config, character_config)
    
    #set window size
    screen_w = 1280
    screen_h = 768
    #scaling = 1
    #screen = pygame.Surface((screen_w, screen_h))
    #window = pygame.display.set_mode((screen_w * scaling, screen_h * scaling))
    screen = pygame.display.set_mode((screen_w, screen_h))
    
    #initiate fonts
    font = pygame.font.Font("../coders_crux.ttf", 14)
    med_font = pygame.font.Font("../coders_crux.ttf", 16)
    
    #load sprites
    water_img = pygame.image.load('../graphics/water.png').convert()
    water_img.set_colorkey((0,0,0))
    grass_img = pygame.image.load('../graphics/grass.gif').convert()
    grass_img.set_colorkey((0,0,0))
    selected_img = pygame.image.load('../graphics/selected.gif').convert()
    selected_img.set_colorkey((0,0,0))
    action_target_img = pygame.image.load('../graphics/action_selected.gif').convert()
    action_target_img.set_colorkey((0,0,0))
    heal_target_img = pygame.image.load('../graphics/heal_selected.gif').convert()
    heal_target_img.set_colorkey((0,0,0))
    char_info = pygame.image.load("../graphics/char_info.gif").convert()
    char_info.set_colorkey((0,0,0))
    char_info_turn = pygame.image.load("../graphics/char_info_has_turn.gif").convert()
    char_info_turn.set_colorkey((0,0,0))
    
    sprites = load_sprites()
    
    #prepare the map
    tile_w = 64
    tile_h = 32
    map_w = m.width * tile_w
    map_offset_x = map_w / 2 - tile_w / 2
    map_offset_y = 64
    character_offset_x = 13
    character_offset_y = -30
    
    map_surface = pygame.Surface(( (m.width + m.height)*tile_w/2, (m.width + m.height)*(tile_h+8)/2))
    render_squares(map_surface)
    bottom_bar = pygame.Surface((screen_w, 28))
    render_bottom_bar(bottom_bar)
    end_turn_button = ui.Button(ui.end_turn_bg, ui.end_turn_bg_hover, ui.end_turn_bg_push, (screen_w - 135, screen_h - 71))
    

    #prepare the game loop control variables
    done = False
    selected_square_inside_map = False
    selected_character = m.turn_controller.current_character
    selected_action = None
    mouse_pos = None
    within_range = selected_character.within_range(selected_character.range)   
    text_to_display = None
    did_update_already = False
    did_move_already = False
    effect_fade_count = 0
    effect_text = None
    dirty_rects = []
    
    '''Initial render'''
    #map
    dirty_rects.append(screen.blit(map_surface, (map_offset_x, map_offset_y)))
    #move range for the first character
    render_range(screen)
    #bottom bar
    dirty_rects.append(screen.blit(bottom_bar, (0, screen_h-28)))
    #characters
    dirty_rects += render_characters(screen)
    #end turn button and action menu
    dirty_rects.append(render_end_turn_button(screen))
    use_buttons = render_action_menu(screen)
    for button in use_buttons:
        dirty_rects.append(button.rect)
    #character info
    dirty_rects += render_char_info(screen)
    
    pygame.display.update()
        
        
    ''' start main loop '''
    while not done:
        
        clock.tick(fps)
        dirty_rects = []
        did_update_already = False
        
        render_range(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            
            # move the map with arrow keys
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                map_offset_x -= 4
            if keys[pygame.K_RIGHT]:
                map_offset_x += 4
            if keys[pygame.K_UP]:
                map_offset_y -= 4
            if keys[pygame.K_DOWN]:
                map_offset_y += 4
            
            '''Get mouse position'''
            
            # get mouse position and convert to cartesian coordinates
            mouse_pos = pygame.mouse.get_pos()
            mx = mouse_pos[0]
            my = mouse_pos[1]
            
            
            '''Update buttons if mouse moves in or out'''
            
            if ( (end_turn_button.hovered and not end_turn_button.rect.collidepoint((mx,my))) or (not end_turn_button.hovered and end_turn_button.rect.collidepoint((mx,my))) ):  
                dirty_rects.append(render_end_turn_button(screen))
            
            for button in use_buttons:
                if (button.hovered and not button.rect.collidepoint((mx,my))) or (not button.hovered and button.rect.collidepoint((mx,my))):
                    use_buttons = render_action_menu(screen)
                    for button in use_buttons:
                        dirty_rects.append(button.rect)  
                
            
            '''Handle mouse clicks'''
            
            if event.type == pygame.MOUSEBUTTONUP:
                # reset button states
                end_turn_button.pushed = False
                for use_btn in use_buttons:
                    use_btn.pushed = False
                
                '''If End Turn was clicked or if a Use action button was clicked'''
                
                # recognize end turn button and action use buttons
                if end_turn_button.rect.collidepoint((mx,my)):
                    
                    #get current and next character
                    old_character = selected_character
                    text_to_display = m.turn_controller.current_character.end_turn()
                    selected_character = m.turn_controller.current_character
                    
                    # update the screen in the correct rendering order
                    within_range = selected_character.within_range(selected_character.range)
                    dirty_rects.append(screen.blit(map_surface, (map_offset_x, map_offset_y)))
                    render_range(screen)
                    render_characters(screen)
                    dirty_rects += render_char_info(screen, [old_character, selected_character])
                    render_end_turn_button(screen)
                    use_buttons = render_action_menu(screen)
                    for button in use_buttons:
                        dirty_rects.append(button.rect)
                    
                    # get the square where the character for next turn is
                    square = m.get_square_at(selected_character.location)
                    
                    selected_action = None
                    
                    break
                    
                else:
                    for use_btn in use_buttons:
                        if use_btn.rect.collidepoint((mx,my)):
                            selected_action = selected_character.actions[use_buttons.index(use_btn)]
                            within_range = selected_character.within_range(selected_action.range, for_action = True)
                            break
                
                
                '''Convert clicked coordinates to game map coordinates'''
                
                # map mouse x = mmx, map mouse y = mmy, i.e. which square on the map was clicked
                mouse_pos_map = screen_to_map(mx,my, map_offset_x, map_offset_y)
                mmx = mouse_pos_map[0]
                mmy = mouse_pos_map[1]
                
                
                '''Handle game events resulting from clicks'''
                
                # if a square on map was clicked
                if ( 0 <= mmx < m.get_width() ) and ( 0 <= mmy < m.get_height() ): 
                    selected_square_inside_map = True
                
                # if there is a square at the selected map coordinates
                if m.get_square_at(Coordinates(mmx, mmy)):
                    square = m.get_square_at(Coordinates(mmx, mmy))
                    
                    # if an empty square was clicked
                    if not square in within_range:
                        #selected_character = None
                        text_to_display = "Not within range."
                        print("Not within range.")
                        continue
                        
                    # if an action was selected
                    if selected_action:
                        if square in within_range:
                            # if there's a character in the target square
                            text_to_display = selected_action.perform(square.location)
                            action_target_loc = square.location
                            if square.has_character():
                                effect_text = get_effect_text(selected_action)
                            selected_action = None
                            #update character infos for current character, action target character, and the next turn character
                            old_character = selected_character
                            selected_character.end_turn()
                            selected_character = m.turn_controller.current_character
                            dirty_rects += render_char_info(screen,[square.character, selected_character, old_character])
                            #clear range
                            within_range = []
                            continue
                            
                    elif square in within_range and selected_character.has_turn():
                        
                        # set target map coordinates and get the shortest path there
                        target_map_loc = Coordinates(mmx,mmy) 
                        path = selected_character.get_shortest_path(target_map_loc)
                        
                        # walk the shortest path
                        for step in path:
                            
                            # get the current map and screen locations
                            current_map_loc = selected_character.location
                            current_scr_loc = map_to_screen(selected_character.location.x, selected_character.location.y, map_offset_x, map_offset_y)
                            
                            # set the target screen location for the current step
                            step_scr_target = map_to_screen(step.x, step.y, map_offset_x, map_offset_y)
                            
                            # determine if the character has walk sprites and prepare the animation
                            walk_animation = False
                            if len(selected_character.walk_sprites) > 0:
                                nr_of_sprites = len(selected_character.walk_sprites)
                                half_speed = True
                                frame_counter = 0
                                sprite_counter = 0
                                walk_animation = True
                            
                            # move the character according to the shortest path step
                            #up
                            if step.x == current_map_loc.x and step.y < current_map_loc.y:
                                selected_character.facing = direction.UP
                                facing = "up"
                            #down
                            elif step.x == current_map_loc.x and step.y > current_map_loc.y:
                                selected_character.facing = direction.DOWN
                                facing = "down"
                            #left
                            elif step.x < current_map_loc.x and step.y == current_map_loc.y:
                                selected_character.facing = direction.LEFT
                                facing = "left"
                            #right
                            elif step.x > current_map_loc.x and step.y == current_map_loc.y:
                                selected_character.facing = direction.RIGHT
                                facing = "right"
                            
                            # while the character has not reached the target
                            in_target = False
                            while not in_target:
                                if current_scr_loc == step_scr_target:
                                    in_target = True
                                
                                dirty_rects = []

                                clock.tick(fps)
                                # render squares, and all characters except the one that moves
                                screen.blit(map_surface, (map_offset_x,map_offset_y))
                                render_characters(screen, excluding=[selected_character])
                                dirty_rects.append(render_end_turn_button(screen))
                                #if text_to_display:
                                #    render_info_text(text_to_display)
                                use_buttons = render_action_menu(screen)
                                for button in use_buttons:
                                    dirty_rects.append(button.rect)
                                
                                # if walk sprites available
                                if walk_animation and not in_target:
                                    
                                    # render the current frame of the walk animation
                                    dirty_rects.append(screen.blit(sprites[selected_character.walk_sprites[facing][sprite_counter]], \
                                                (current_scr_loc[0] + character_offset_x, current_scr_loc[1] + character_offset_y)))
                                    
                                    # if animation is set to half speed, may look too fast if full speed
                                    if half_speed and frame_counter % 2 == 0:
                                        if sprite_counter < nr_of_sprites - 1:
                                            sprite_counter += 1
                                        else:
                                            sprite_counter = 0

                                    frame_counter += 1 
                                    
                                # if no walk sprites or if in target
                                else:
                                    screen.blit(sprites[selected_character.stand_sprites[facing]], (current_scr_loc[0] + character_offset_x, current_scr_loc[1] + character_offset_y))
                                
                                # move the character on screen according to the shortest path step
                                if facing == "up":
                                    current_scr_loc = (current_scr_loc[0] + 2, current_scr_loc[1] - 1)
                                elif facing == "down":
                                    current_scr_loc = (current_scr_loc[0] - 2, current_scr_loc[1] + 1)
                                elif facing == "left":
                                    current_scr_loc = (current_scr_loc[0] - 2, current_scr_loc[1] - 1)
                                elif facing == "right":
                                    current_scr_loc = (current_scr_loc[0] + 2, current_scr_loc[1] + 1)
                                
                                pygame.display.set_caption("fps: " + str(int(clock.get_fps())))
                                
                                print([str(r) for r in dirty_rects])
                                pygame.display.update(dirty_rects)
                                did_update_already = True
                            
                            #move in the background logic
                            selected_character.move_forward()
                            
                        # don't display range after the character has moved
                        within_range = []
                        
                    # if no character was selected and no action is selected                         
                    else:
                        #selected_character = None
                        pass
        
        #effect_fade_count, effect_text = render_effect_text(effect_fade_count, effect_text)
        
        # skip render if the screen was already updated in an inner loop
        if did_update_already:
            continue
        
        if end_turn_button.dirty:
            dirty_rects.append(render_end_turn_button(screen))
            end_turn_button.dirty = False
        for button in use_buttons:
            if button.dirty:
                render_action_menu(screen)
                button.dirty = False
                break
            
        if text_to_display:
            #screen.blit(bottom_bar, (0, screen_h-28))
            text_rect = render_info_text(screen, text_to_display)
            dirty_rects.append(text_rect)
            #print(text_rect)
            text_to_display = None
        
        pygame.display.set_caption("fps: " + str(int(clock.get_fps())))
        
        #pygame.transform.scale(screen, (screen_w * scaling, screen_h * scaling), window)
        #print(len(dirty_rects))
        #for rect in dirty_rects:
        #    print(rect)
        pygame.display.update(dirty_rects)
        
    pygame.quit()
    sys.exit()
    
if __name__ == "__main__": main()