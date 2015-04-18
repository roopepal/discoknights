from action import Action
from ai import Ai
from character import Character
from config_reader import ConfigReader
from coordinates import Coordinates
import direction
from map import Map
from object_type import ObjectType
import pygame, sys
from squaretype import SquareType
import ui

def main():
    def get_screen():
        return screen
        
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
    
        # For each squaretype, load sprites that are not loaded
        for squaretype in m.squaretypes:
            if m.squaretypes[squaretype].sprite not in sprites:
                sprites[m.squaretypes[squaretype].sprite] = pygame.image.load(m.squaretypes[squaretype].sprite).convert_alpha()
                print("Successfully loaded sprite '{:}'".format(m.squaretypes[squaretype].sprite))
        
        # For each object type, load sprites that are not loaded
        for object_type in m.object_types:
            if m.object_types[object_type].sprite not in sprites:
                sprites[m.object_types[object_type].sprite] = pygame.image.load(m.object_types[object_type].sprite).convert_alpha()
                print("Successfully loaded sprite '{:}'".format(m.object_types[object_type].sprite))
                
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
        surface.fill((0,0,0))
        for x in range(m.width):
            for y in range(m.height):
                square = m.get_square_at(Coordinates(x,y))
                screen_x, screen_y = map_to_screen(x,y)
                surface.blit(sprites[square.squaretype.sprite], (screen_x + map_offset_x, screen_y))
    
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
    
    def render_characters_and_objects(surface, walking=None, scr_loc=None, sprite_counter=None):
        # collect dirty rects
        dirty = []
        
        # For each square on the map, check if there's a character and if yes, draw it. Do this in the order of squares to maintain proper drawing order.
        for x in range(m.width):
            for y in range(m.height):
                square = m.get_square_at(Coordinates(x,y))
                character = square.character
                # Translate coordinates
                screen_x, screen_y = map_to_screen(x,y, map_offset_x, map_offset_y)
                
                if square.character and not square.character.dead:
                    if character.facing == direction.UP: facing = "up"
                    elif character.facing == direction.DOWN: facing = "down"
                    elif character.facing == direction.LEFT: facing = "left"
                    elif character.facing == direction.RIGHT: facing = "right"
                    
                    if character == walking:
                        # Draw sprite based on the direction facing
                        if character.walk_sprites:
                            dirty.append(surface.blit(sprites[character.walk_sprites[facing][sprite_counter]], (scr_loc[0] + character_offset_x, scr_loc[1] + character_offset_y))) 
                        else:
                            dirty.append(surface.blit(sprites[character.stand_sprites[facing]], (scr_loc[0] + character_offset_x, scr_loc[1] + character_offset_y))) 
                    else:
                        dirty.append( surface.blit(sprites[character.stand_sprites[facing]], (screen_x + character_offset_x, screen_y + character_offset_y)) )
                        #dirty.append(pygame.Rect(48,48, screen_x+character_offset_x,screen_y+character_offset_y))
                
                elif square.object:
                    dirty.append( surface.blit(sprites[square.object.type.sprite], (screen_x + square.object.type.offset_x, screen_y + square.object.type.offset_y)) )
        
        return dirty
        
    def render_info_text(surface, text_to_display):
        text = font.render(text_to_display, 1, (10, 10, 10))
        textpos = text.get_rect()
        textpos.move_ip(0,screen_h - 16)
        textpos.centerx = screen.get_rect().centerx
        bgpos = pygame.Rect(0,0,(screen_w - 128*2 - 14), 28)
        bgpos.centerx = textpos.centerx
        surface.blit(bottom_bar.subsurface(bgpos), (bgpos.x, screen_h-28))
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
                elif character.dead:
                    char_info_surface = char_info_dead.copy()
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
        actions_menu = pygame.image.load("../graphics/actions_menu.gif").convert_alpha()
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
                
                text = action.description + " (" + str(action.strength) + ")"
                text = font.render(text, False, (10,10,10))
                text_pos = text.get_rect()
                text_pos.move_ip(65, screen_h - 84 + count * 26)
                surface.blit(text, text_pos)
                
                count += 1
            
            return use_buttons
        return []
    
    def render_effect_text(surface, count, text_surface):
        if text_surface:
            scr_loc = map_to_screen(action_target_loc.x, action_target_loc.y)
            x = scr_loc[0] + 32 - text_surface.get_width()/2 + map_offset_x
            y = scr_loc[1] - 40 - count*1 + map_offset_y
            location = (x, y)
            
            if count > 10:
                opacity = 255 - 12 * count
            else:
                opacity = 255
            
            #surface.blit(map_surface, (map_offset_x + map_fix_x, map_offset_y))
            blit_alpha(surface, text_surface, location, opacity)
            
            count += 1
            if count > 20:
                count = 0
                return count, None
            
        return count, text_surface
    
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
        '''Blits opaque element while keeping per pixel alpha in other parts of the surface.'''
        x = location[0]
        y = location[1]
        temp = pygame.Surface((source.get_width(), source.get_height())).convert_alpha()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)        
        target.blit(temp, location)
    
    def blit_map(surface):
        return surface.blit(map_surface, (map_offset_x + map_fix_x, map_offset_y))
    
    ''' Game starts '''
    pygame.init()
    clock = pygame.time.Clock()
    fps = 40
    
    #read config from files
    r = ConfigReader()
    f = open('map_config', 'r')
    map_config = r.read_config(f)
    f.close()
    f = open('character_config', 'r')
    character_config = r.read_config(f)
    f.close()
    
    m = r.build_from_config(map_config, character_config)
    ai = Ai(m)
    
    #set window size
    screen_w = 960
    screen_h = 576
    screen = pygame.display.set_mode((screen_w, screen_h))
    
    #initiate fonts
    font = pygame.font.Font("../coders_crux.ttf", 14)
    med_font = pygame.font.Font("../coders_crux.ttf", 16)
    
    #load sprites
    selected_img = pygame.image.load('../graphics/selected.gif').convert_alpha()
    action_target_img = pygame.image.load('../graphics/action_selected.gif').convert_alpha()
    heal_target_img = pygame.image.load('../graphics/heal_selected.gif').convert_alpha()
    char_info = pygame.image.load("../graphics/char_info.gif").convert_alpha()
    char_info_turn = pygame.image.load("../graphics/char_info_has_turn.gif").convert_alpha()
    char_info_dead = pygame.image.load("../graphics/char_info_dead.gif").convert_alpha()
    sprites = load_sprites()
    
    #prepare the map and rendering offsets
    tile_w = 64
    tile_h = 32
    map_w = (m.width + m.height) * tile_w / 2
    map_h = (m.width + m.height) * tile_h / 2 + 8
    map_offset_x = map_w / 2 - tile_w / 2
    map_offset_y = 0
    character_offset_x = 13
    character_offset_y = -30
    #create a separate surface for the map and render squares on it
    map_surface = pygame.Surface((map_w, map_h))
    render_squares(map_surface)
    
    bottom_menu_rect = pygame.Rect(0, screen_h-128, screen_w, 128)
    bottom_bar = pygame.Surface((screen_w, 28))
    render_bottom_bar(bottom_bar)
    end_turn_button = ui.Button(ui.end_turn_bg, ui.end_turn_bg_hover, ui.end_turn_bg_push, (screen_w - 135, screen_h - 71))
    
    #prepare pause menu
    options = [ ui.MenuOption("NEW GAME"),
                ui.MenuOption("QUIT") ]
    [ option.set_rect(screen, options) for option in options ]
    
    #prepare the game loop control variables
    done = False
    selected_square_inside_map = False
    selected_character = m.turn_controller.current_character
    selected_action = None
    mouse_pos = None
    within_range = selected_character.within_range(selected_character.range)   
    text_to_display = None
    saved_text = None
    did_update_already = False
    did_move_already = False
    effect_fade_count = 0
    effect_text = None
    dirty_rects = []
    refresh_map = False
    walk = False
    path_to_move = False
    
    '''Initial render'''
    screen.fill((0,0,0))
    #map, the map_fix_x fixes horizontal positioning, and the offsets center the map on the screen
    map_fix_x = tile_w / 2 - map_surface.get_rect().w/2
    map_offset_x += screen_w / 2 - map_w / 2
    map_offset_y += screen_h / 2 - map_h / 2
        
    in_menu = True
    paused = False
          
    #debug milliseconds from last frame
    new_time, old_time = None, None    
    
    
    #----------------------------------------------------------------------------------------
    
    ''' start main loop '''
    while not done:
            
        clock.tick(fps)
        dirty_rects = []
        did_update_already = False
        
        '''Render menu if game is in menu'''
        while in_menu:
            #draw menu and options    
            screen.fill((0, 0, 0))
            
            if paused:
                resume = ui.large_font.render("Press Esc to resume game.", True, (255,255,255))
                resume_rect = resume.get_rect()
                resume_rect.centerx = screen.get_rect().centerx
                resume_rect.y = 20
                screen.blit(resume, resume_rect)
            
            for option in options:
                if option.rect.collidepoint(pygame.mouse.get_pos()):
                    option.hover = True
                else:
                    option.hover = False
                option.draw()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    in_menu = False
                    done = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and paused:
                    in_menu = False
                    refresh_map = True
                if event.type == pygame.MOUSEBUTTONUP:
                    for option in options:
                        if option.text == "QUIT" and option.rect.collidepoint(pygame.mouse.get_pos()):
                            in_menu = False
                            done = True
                        if option.text == "NEW GAME" and option.rect.collidepoint(pygame.mouse.get_pos()):
                            #read config from files
                            r = ConfigReader()
                            f = open('map_config', 'r')
                            map_config = r.read_config(f)
                            f.close()
                            f = open('character_config', 'r')
                            character_config = r.read_config(f)
                            f.close()

                            m = r.build_from_config(map_config, character_config)
                            ai.m = m
                            
                            m.turn_controller.reset()
                            selected_character = m.turn_controller.current_character
                            selected_action = None
                            within_range = selected_character.within_range(selected_character.range)   
                            text_to_display = None
                            mouse_pos = None
                            in_menu = False
                            refresh_map = True
                            
            if new_time:
                old_time = new_time
            new_time = pygame.time.get_ticks()
            if new_time and old_time:
                pygame.display.set_caption("fps: " + str(int(clock.get_fps())) + " ms: " + str(new_time-old_time))
                
            pygame.display.update()
        
        if refresh_map:
            screen.fill((0,0,0))
            #map, range and characters
            dirty_rects.append(blit_map(screen).inflate(20,20))
            render_range(screen)
            render_characters_and_objects(screen)
            #menu elements
            screen.blit(bottom_bar, (0, screen_h-28))
            if saved_text:
                text_to_display = saved_text
            render_end_turn_button(screen)
            use_buttons = render_action_menu(screen)
            render_char_info(screen)
            
            refresh_map = False
        
        # move the map with arrow keys
        keys = pygame.key.get_pressed()
        if not (map_offset_x + map_fix_x) < (-map_w + tile_w / 2 - (screen_w - map_w)):
            if keys[pygame.K_LEFT]: 
                map_offset_x -= 10
                refresh_map = True
        if not (map_offset_x + map_fix_x) > (map_w - tile_w / 2 + (screen_w - map_w)):
            if keys[pygame.K_RIGHT]:
                map_offset_x += 10
                refresh_map = True
        if not (map_offset_y) < (-map_h + tile_h / 2):
            if keys[pygame.K_UP]:
                map_offset_y -= 10
                refresh_map = True
        if not (map_offset_y) > (map_h - tile_h / 2 + (screen_h - map_h)):
            if keys[pygame.K_DOWN]:
                map_offset_y += 10
                refresh_map = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                
            '''Use Esc to go into pause menu'''
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                in_menu = True
                paused = True
                
            #if not in menu
            else:
                '''Get mouse position'''
            
                # get mouse position and convert to cartesian coordinates
                mouse_pos = pygame.mouse.get_pos()
                mx = mouse_pos[0]
                my = mouse_pos[1]
            
            
                '''Update buttons if mouse moves in or out'''
            
                if ( (end_turn_button.hovered and not end_turn_button.rect.collidepoint((mx,my))) or (not end_turn_button.hovered and end_turn_button.rect.collidepoint((mx,my))) ):  
                    dirty_rects.append(render_end_turn_button(screen))
            
                else:
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
                
                    '''If End Turn was clicked, or if a Use action button was clicked'''
                
                    # recognize end turn button
                    if end_turn_button.rect.collidepoint((mx,my)):
                        #get current and next character
                        old_character = selected_character
                        text_to_display = m.turn_controller.current_character.end_turn()
                        selected_character = m.turn_controller.current_character
                        
                        # update range with new character
                        if not selected_character.ai:
                            within_range = selected_character.within_range(selected_character.range)
                        else:
                            within_range = []
                        # get the square where the character for next turn is
                        square = m.get_square_at(selected_character.location)
                        selected_action = None
                        refresh_map = True
                        continue
                    
                    #recognize action use buttons
                    else:
                        for use_btn in use_buttons:
                            if use_btn.rect.collidepoint((mx,my)):
                                selected_action = selected_character.actions[use_buttons.index(use_btn)]
                                within_range = selected_character.within_range(selected_action.range, for_action = True)
                                refresh_map = True
                                break
                
                
                    '''Convert clicked coordinates to game map coordinates'''
                
                    # map mouse x = mmx, map mouse y = mmy, i.e. which square on the map was clicked
                    mouse_pos_map = screen_to_map(mx,my, map_offset_x, map_offset_y)
                    mmx = mouse_pos_map[0]
                    mmy = mouse_pos_map[1]
                
                
                    '''Handle game events resulting from clicks'''
                
                    # if the click was inside the map
                    if ( 0 <= mmx < m.get_width() ) and ( 0 <= mmy < m.get_height() ): 
                        selected_square_inside_map = True
                
                    # if there is a square at the selected map coordinates
                    if m.get_square_at(Coordinates(mmx, mmy)):
                        square = m.get_square_at(Coordinates(mmx, mmy))
                    
                        # if an empty square was clicked
                        if not square in within_range:
                            #selected_character = None
                            text_to_display = "Not within range."
                            continue
                        
                        '''Use action if an action was selected, otherwise move'''
                    
                        if selected_action:
                            if square in within_range:
                                # set the correct facing direction for the attacking character
                                if square.location.x == selected_character.location.x and square.location.y < selected_character.location.y:
                                    selected_character.facing = direction.UP
                                elif square.location.x == selected_character.location.x and square.location.y > selected_character.location.y:
                                    selected_character.facing = direction.DOWN
                                elif square.location.x < selected_character.location.x and square.location.y == selected_character.location.y:
                                    selected_character.facing = direction.LEFT
                                elif square.location.x > selected_character.location.x and square.location.y == selected_character.location.y:
                                    selected_character.facing = direction.RIGHT
                                
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
                                within_range = selected_character.within_range(selected_character.range)
                                refresh_map = True
                                continue
                    
                        elif square in within_range and selected_character.has_turn():
                            target_map_loc = Coordinates(mmx,mmy)
                            walk = True
        
        
        
        
        '''if AI's turn, get AI movement'''
        if selected_character.ai and not selected_character.has_moved:
            target_map_loc = ai.get_next_move()
            print(str(selected_character) + " moving to " + str(target_map_loc))
            # If gets a target, move, otherwise proceed to action
            if target_map_loc:
                walk = True
            else:
                selected_character.has_moved = True
            #else:
            #    selected_character.end_turn()
            #    selected_character = m.turn_controller.current_character
        
        if walk:
            # remove range
            blit_map(screen)
            
            # set target map coordinates and get the shortest path there
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
                if step.x == current_map_loc.x and step.y < current_map_loc.y:
                    selected_character.facing = direction.UP
                    facing = "up"
                elif step.x == current_map_loc.x and step.y > current_map_loc.y:
                    selected_character.facing = direction.DOWN
                    facing = "down"
                elif step.x < current_map_loc.x and step.y == current_map_loc.y:
                    selected_character.facing = direction.LEFT
                    facing = "left"
                elif step.x > current_map_loc.x and step.y == current_map_loc.y:
                    selected_character.facing = direction.RIGHT
                    facing = "right"
            
                dirty_rects_moving = []
                # while the character has not reached the target
                while not current_scr_loc == step_scr_target:
                    clock.tick(0)
                    map_rect = blit_map(screen)
                
                    pygame.event.pump()
                    
                    # if walk sprites available
                    if walk_animation:
                        # if animation is set to half speed, may look too fast if full speed
                        if half_speed and frame_counter % 2 == 0:
                            if sprite_counter < nr_of_sprites - 1:
                                sprite_counter += 1
                            else:
                                sprite_counter = 0
                            
                        frame_counter += 1 
                        dirty_rects_moving += render_characters_and_objects(screen, selected_character, current_scr_loc, sprite_counter)
                
                    # if no walk sprites or if in target
                    else:
                        dirty_rects_moving += render_characters_and_objects(screen, selected_character, current_scr_loc)
                
                    # move the character on screen according to the shortest path step
                    if facing == "up":
                        current_scr_loc = (current_scr_loc[0] + 2, current_scr_loc[1] - 1)
                    elif facing == "down":
                        current_scr_loc = (current_scr_loc[0] - 2, current_scr_loc[1] + 1)
                    elif facing == "left":
                        current_scr_loc = (current_scr_loc[0] - 2, current_scr_loc[1] - 1)
                    elif facing == "right":
                        current_scr_loc = (current_scr_loc[0] + 2, current_scr_loc[1] + 1)
                
                    # if map goes under the menus
                    if map_rect.colliderect(bottom_menu_rect):
                        screen.blit(bottom_bar, (0, screen_h-28))
                        render_end_turn_button(screen)
                        use_buttons = render_action_menu(screen)
                
                    #display fps and milliseconds between frames
                    if new_time:
                        old_time = new_time
                    new_time = pygame.time.get_ticks()
                    if old_time and new_time:
                        pygame.display.set_caption("fps: " + str(int(clock.get_fps())) + " ms: " + str(new_time-old_time))
                
                    #print([str(r) for r in dirty_rects_moving])
                    pygame.display.update(dirty_rects_moving)
                    #did_update_already = True
                    dirty_rects_moving = []
            
                #move in the background logic
                selected_character.move_to_coordinates(step)
                
            else:
                #selected_character.end_turn()                   #TODO this will not update range for 1st character
                #selected_character = m.turn_controller.current_character
                #within_range = selected_character.within_range(selected_character.range)
                
                blit_map(screen)
                dirty_rects += render_characters_and_objects(screen)
                pygame.display.update(dirty_rects)
            
            text_to_display = "Choose action."
            refresh_map = True
            path_to_move = False
            walk = False
            #did_update_already = True    
            
        # don't display range after the character has moved
        if selected_character.has_moved:
            within_range = []    
                
                
                
                
                
                
        
        if effect_text:
            effect_fade_count, effect_text = render_effect_text(screen, effect_fade_count, effect_text)
            # if was not reset
            if effect_text:
                dirty_rects.append(effect_text.get_rect().inflate(0,2))
            refresh_map = True
        
        # skip render if the screen was already updated in an inner loop
        if did_update_already:
            continue
        
        # if buttons need to be refreshed
        if end_turn_button.dirty:
            dirty_rects.append(render_end_turn_button(screen))
            end_turn_button.dirty = False
        for button in use_buttons:
            if button.dirty:
                render_action_menu(screen)
                dirty_rects.append(button.rect)
                button.dirty = False
                break
            
        if text_to_display:
            text_rect = render_info_text(screen, text_to_display)
            dirty_rects.append(text_rect)
            saved_text = text_to_display
            text_to_display = None
            
        # show fps and milliseconds
        if new_time:
            old_time = new_time
        new_time = pygame.time.get_ticks()
        if new_time and old_time:
            pygame.display.set_caption("fps: " + str(int(clock.get_fps())) + " ms: " + str(new_time-old_time))
        
        #print([str(r) for r in dirty_rects])
        pygame.display.update(dirty_rects)
        
    pygame.quit()
    sys.exit()
    
if __name__ == "__main__": main()