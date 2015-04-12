import pygame, sys
pygame.init()

class MenuOption: 
    hover = False

    def __init__(self, text):
        self.text = text
            
    def draw(self):
        self.set_rend()
        self.base_surface.blit(self.rend, self.rect)
        
    def set_rend(self):
        self.rend = super_large_font.render(self.text, False, self.get_color())
        
    def get_color(self):
        if self.hover:
            return (255, 255, 255)
        else:
            return (150, 150, 150)
        
    def set_rect(self, screen_surface, options_list):
        self.set_rend()
        self.rect = self.rend.get_rect()
        self.base_surface = screen_surface
        self.rect.centerx = screen_surface.get_rect().centerx
        self.rect.y = screen_surface.get_rect().centery - ( len(options_list) * 50 / 2 ) + ( options_list.index(self) * 50 )

class Button():
    hover = False
    
    def __init__(self, surface_normal, surface_hover, surface_push, pos):
        self.s_normal = surface_normal
        self.s_hover = surface_hover
        self.s_push = surface_push
        self.pos = pos
        self.hovered = False
        self.pushed = False
        self.dirty = False
        
        self.set_rect()
        
    def render_to(self, surface):
        if self.hovered:
            surface.blit(self.s_hover, self.rect)
        elif self.pushed:
            surface.blit(self.s_push, self.rect)
        else:    
            surface.blit(self.s_normal, self.rect)
    
    def set_rect(self):
        self.rect = self.s_normal.get_rect()
        self.rect.topleft = self.pos
        
font = pygame.font.Font("../coders_crux.ttf", 14)
large_font = pygame.font.Font("../coders_crux.ttf", 24)
super_large_font = pygame.font.Font("../coders_crux.ttf", 48)

# build end turn button background and text
end_turn_bg = pygame.image.load("../graphics/end_turn_button.gif")        
end_turn_text = large_font.render("End Turn", False, (255,255,255))
end_turn_text_pos = end_turn_text.get_rect()
end_turn_text_pos.centerx = end_turn_bg.get_rect().centerx
end_turn_text_pos.centery = end_turn_bg.get_rect().centery
end_turn_bg.blit(end_turn_text, end_turn_text_pos)

end_turn_bg_hover = pygame.image.load("../graphics/end_turn_button_hover.gif")        
end_turn_bg_hover.blit(end_turn_text, end_turn_text_pos)

end_turn_bg_push = pygame.image.load("../graphics/end_turn_button_push.gif")        
end_turn_bg_push.blit(end_turn_text, end_turn_text_pos)


# build action button background and text
action_bg = pygame.image.load("../graphics/action_button.gif")
action_text = font.render("Use", False, (255,255,255))
action_text_pos = action_text.get_rect()
action_text_pos.centerx = action_bg.get_rect().centerx
action_text_pos.centery = action_bg.get_rect().centery
action_bg.blit(action_text, action_text_pos)

action_bg_hover = pygame.image.load("../graphics/action_button_hover.gif")
action_bg_hover.blit(action_text, action_text_pos)

action_bg_push = pygame.image.load("../graphics/action_button_push.gif")
action_bg_push.blit(action_text, action_text_pos)