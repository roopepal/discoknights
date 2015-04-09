import pygame, sys
pygame.init()



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