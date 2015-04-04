import cProfile, pstats, io
pr = cProfile.Profile()
pr.enable()


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
    
    ''' Helper methods defined '''
    
    tile_w = 64
    tile_h = 32

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
    
    def render_squares(surface):        
        for x in range(m.width):
            for y in range(m.height):
                square = m.get_square_at(Coordinates(x,y))
                screen_x, screen_y = map_to_screen(x,y)
                
                print("{:}, {:} to {:}, {:}".format(x,y,screen_x, screen_y))
                
                if square.get_type() == m.get_squaretypes()["g"]:
                    surface.blit(grass_img, (screen_x, screen_y))
                elif square.get_type() == m.get_squaretypes()["w"]:
                    surface.blit(water_img, (screen_x, screen_y))
    
    def render_range():
        for sq in within_range:
            sq_mx, sq_my = sq.location.x, sq.location.y
            sq_sx, sq_sy = map_to_screen(sq_mx, sq_my, map_offset_x, map_offset_y)
            if selected_action:
                if selected_action.type == Action.HEAL:
                    screen.blit( heal_target_img, (sq_sx, sq_sy) )
                else:
                    screen.blit( action_target_img, (sq_sx, sq_sy) )
            else:
                screen.blit( selected_img, (sq_sx, sq_sy) )
    
    def render_all_characters(excluding=[]):
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
                    screen.blit(sprites[square.character.stand_sprites[facing]], (screen_x + character_offset_x, screen_y + character_offset_y))
    
    def load_sprites():
        sprites = {}
    
        # For each character, load all sprites that are not already loaded
        for character in m.characters:
            
            for sprite in character.stand_sprites:
                if character.stand_sprites[sprite] not in sprites:
                    print("Loading sprite '{:}'".format(character.stand_sprites[sprite]))
                    sprites[character.stand_sprites[sprite]] = pygame.image.load(character.stand_sprites[sprite]).convert_alpha()
                
            for sprite_list in character.walk_sprites:
                for sprite in character.walk_sprites[sprite_list]:
                    if sprite not in sprites:
                        print("Loading sprite '{:}'".format(sprite))
                        sprites[sprite] = pygame.image.load(sprite).convert_alpha()
        
        return sprites
        
    def render_bottom_menu_text(text_to_display):
        text = font.render(text_to_display, 1, (10, 10, 10))
        textpos = text.get_rect()
        textpos.move_ip(0,screen_h - 16)
        textpos.centerx = screen.get_rect().centerx
        screen.blit(text, textpos)

    def render_char_info():
        char_info_sprites = ["../graphics/char_info.gif", "../graphics/char_info_has_turn.gif"]
        
        count = 0
        ai_count = 1
        
        for character in m.characters:
            
            if character.has_turn():
                char_info = pygame.image.load(char_info_sprites[1]).convert_alpha()
            else:
                char_info = pygame.image.load(char_info_sprites[0]).convert_alpha()
            
            head_image = pygame.image.load(character.stand_sprites["right"]).convert_alpha()
            head_image.set_clip(pygame.Rect(0,0, 20,20))
            
            char_info.blit(head_image, (5,5), (8,5,24,24))
            
            text_line_1 = str(character.health) + "/"
            text_line_2 = str(character.max_health)
            
            t1 = font.render(text_line_1, 1, (10,10,10))
            t2 = font.render(text_line_2, 1, (10,10,10))
            
            t1_pos = t1.get_rect()
            t1_pos.move_ip(0,36)
            t1_pos.centerx = char_info.get_rect().centerx
            char_info.blit(t1, t1_pos)
            
            t2_pos = t2.get_rect()
            t2_pos.move_ip(0,46)
            t2_pos.centerx = char_info.get_rect().centerx
            char_info.blit(t2, t2_pos)            
            
            if character.ai:
                screen.blit(char_info, (screen_w - ai_count * 34 - 5, 7))
                ai_count += 1
            else:
                screen.blit(char_info, (7 + count* 34, 7))
                count += 1
            
        
    def render_bottom_menu():
        bottom_menu_sprites = ["../graphics/actions_menu.gif", "../graphics/bottom_bar.gif"]
        
        #blit background bar
        #bottom_bar = pygame.image.load(bottom_menu_sprites[1]).convert_alpha()
        #for i in range(screen_w // 4):
        #    screen.blit(bottom_bar, (i*4, screen_h-28))
        
        # blit actions menu
        actions_menu = pygame.image.load(bottom_menu_sprites[0]).convert_alpha()
        screen.blit(actions_menu, (7, screen_h - 103))
        
        # blit end button and text
        end_turn_button = ui.Button(ui.end_turn_bg, ui.end_turn_bg_hover, ui.end_turn_bg_push, (screen_w - 135, screen_h - 71))
        if end_turn_button.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                end_turn_button.pushed = True
            else:    
                end_turn_button.hovered = True
        else:
            end_turn_button.hovered = False
            end_turn_button.pushed = False
        end_turn_button.render_to(screen)
        
        return end_turn_button
        
    def render_bottom_menu_actions():
        if selected_character and selected_character.has_turn():
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
                use_button.render_to(screen)
                
                text = action.description
                text = font.render(text, False, (10,10,10))
                text_pos = text.get_rect()
                text_pos.move_ip(80, screen_h - 84 + count * 26)
                screen.blit(text, text_pos)
                
                count += 1
            
            return use_buttons
        return []
    
    def render_effect_text(count, text):
        if text:
            scr_loc = map_to_screen(action_target_loc.x, action_target_loc.y)
            location = (scr_loc[0] + 32 - text.get_width()/2 , scr_loc[1] - 40 - count*1)
            
            if count > 10:
                opacity = 255 - 12 * count
            else:
                opacity = 255
            
            blit_alpha(screen, text, location, opacity)
            
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
    
    screen_w = 640 
    screen_h = 480
    
    '''
    Set scaling here. For the best result, use 1 or 2.
    '''
    #scaling = 1
    
    #screen = pygame.Surface((screen_w, screen_h))
    #window = pygame.display.set_mode((screen_w * scaling, screen_h * scaling))
    screen = pygame.display.set_mode((screen_w, screen_h))
    
    font = pygame.font.Font("../coders_crux.ttf", 14)
    med_font = pygame.font.Font("../coders_crux.ttf", 16)
    
    water_img = pygame.image.load('../graphics/water.png').convert_alpha()
    grass_img = pygame.image.load('../graphics/grass.gif').convert_alpha()
    selected_img = pygame.image.load('../graphics/selected.gif').convert_alpha()
    action_target_img = pygame.image.load('../graphics/action_selected.gif').convert_alpha()
    heal_target_img = pygame.image.load('../graphics/heal_selected.gif').convert_alpha()
    
    r = ConfigReader()
    
    f = open('map_config', 'r')
    map_config = r.read_config(f)
    f.close()

    f = open('character_config', 'r')
    character_config = r.read_config(f)
    f.close()

    m = r.build_from_config(map_config, character_config)
    
    sprites = load_sprites()
    
    map_w = m.width * tile_w
    map_offset_x = map_w / 2 - tile_w / 2
    map_offset_y = 64
    character_offset_x = 13
    character_offset_y = -30
    
    map_surface = pygame.Surface(( (m.width + m.height)*tile_w/2, (m.width + m.height)*(tile_h+8)/2))
    render_squares(map_surface)
    
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
    
    clock = pygame.time.Clock()
    fps = 90
        
    while not done:
        clock.tick(fps)
        
        did_update_already = False
        
            
        screen.blit(map_surface, (map_offset_x, map_offset_y))                
        render_range()
        render_all_characters()
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                
                pr.disable()
                
                s = io.StringIO()
                sortby = 'cumulative'
                ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
                
                ps.strip_dirs().sort_stats('cumulative').print_stats()
                print(s.getvalue())
                
                done = True
            
            # move map with arrow keys
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                map_offset_x -= 4
            if keys[pygame.K_RIGHT]:
                map_offset_x += 4
            if keys[pygame.K_UP]:
                map_offset_y -= 4
            if keys[pygame.K_DOWN]:
                map_offset_y += 4
                    
            # get mouse position and convert to cartesian coordinates
            mouse_pos = pygame.mouse.get_pos()
            mx = mouse_pos[0]
            my = mouse_pos[1]
            
            if event.type == pygame.MOUSEBUTTONUP:
                # reset button states
                end_turn_button.pushed = False
                for use_btn in use_buttons:
                    use_btn.pushed = False
                
                # recognize end turn button and action use buttons
                if end_turn_button.rect.collidepoint((mx,my)):
                    print("End Turn button was clicked")
                    text_to_display = m.turn_controller.current_character.end_turn()
                    selected_character = m.turn_controller.current_character
                    square = m.get_square_at(selected_character.location)
                    within_range = m.turn_controller.current_character.within_range(m.turn_controller.current_character.range)
                    selected_action = None
                    break
                    
                else:
                    for use_btn in use_buttons:
                        if use_btn.rect.collidepoint((mx,my)):
                            selected_action = selected_character.actions[use_buttons.index(use_btn)]
                            within_range = selected_character.within_range(selected_action.range, for_action = True)
                            break
                
                # map mouse x = mmx, map mouse y = mmy, i.e. which square on the map was clicked
                mouse_pos_map = screen_to_map(mx,my, map_offset_x, map_offset_y)
                mmx = mouse_pos_map[0]
                mmy = mouse_pos_map[1]
                
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
                            selected_character.end_turn()
                            selected_character = None
                            within_range = []
                            continue
                            
                    elif selected_character:
                        if square in within_range and selected_character.has_turn():
                            
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
                                while not current_scr_loc == step_scr_target:
                                    
                                    # cap FPS
                                    clock.tick(fps)
                                    # render squares, selected square marker, and all characters except the one that moves
                                    screen.blit(map_surface, (map_offset_x,map_offset_y))
                                    render_all_characters(excluding=[selected_character])
                                    render_char_info()
                                    end_turn_button = render_bottom_menu()
                                    if text_to_display:
                                        render_bottom_menu_text(text_to_display)
                                    use_buttons = render_bottom_menu_actions()
                                    
                                    # if walk sprites available
                                    if walk_animation:
                                        
                                        # render the current frame of the walk animation
                                        screen.blit(sprites[selected_character.walk_sprites[facing][sprite_counter]], (current_scr_loc[0] + character_offset_x, current_scr_loc[1] + character_offset_y))
                                        
                                        # if animation is set to half speed, may look too fast if full speed
                                        if half_speed and frame_counter % 2 == 0:
                                            if sprite_counter < nr_of_sprites - 1:
                                                sprite_counter += 1
                                            else:
                                                sprite_counter = 0

                                        frame_counter += 1 
                                        
                                    # if no walk sprites
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
                                    
                                    pygame.display.update()
                                    did_update_already = True
                                
                                #move in the background logic
                                selected_character.move_forward()
                                
                            # don't display range after the character has moved
                            within_range = []
                    
                    # if no character was selected and no action is selected                         
                    else:
                        #selected_character = None
                        pass
        
        effect_fade_count, effect_text = render_effect_text(effect_fade_count, effect_text)
        
        # skip render if the screen was already updated in an inner loop
        if did_update_already:
            continue
        
        render_char_info()
        end_turn_button = render_bottom_menu()
        if text_to_display:
            render_bottom_menu_text(text_to_display)
        use_buttons = render_bottom_menu_actions()
        
        pygame.display.set_caption("fps: " + str(int(clock.get_fps())))
        
        #pygame.transform.scale(screen, (screen_w * scaling, screen_h * scaling), window)
        pygame.display.update()
        
    pygame.quit()
    sys.exit()
    
if __name__ == "__main__": main()