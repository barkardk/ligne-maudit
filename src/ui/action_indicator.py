"""Action indicator for showing when interactions are available"""

import pygame
import math

class ActionIndicator:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visible = False
        self.font = pygame.font.Font(None, 48)  # Large font for visibility
        self.pulse_timer = 0
        self.pulse_speed = 3.0  # Speed of pulsing animation

    def show(self, x=None, y=None):
        """Show the action indicator at position"""
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self.visible = True

    def hide(self):
        """Hide the action indicator"""
        self.visible = False

    def update(self, dt):
        """Update the pulsing animation"""
        if self.visible:
            self.pulse_timer += dt * self.pulse_speed

    def render(self, screen):
        """Render the bright yellow exclamation mark with pulsing effect"""
        if not self.visible:
            return

        # Calculate pulsing effect (0.8 to 1.2 scale)
        pulse_scale = 1.0 + 0.2 * math.sin(self.pulse_timer)

        # Colors - very bright yellow with dark outline
        yellow = (255, 255, 0)      # Bright yellow
        dark_yellow = (200, 200, 0) # Darker yellow for shadow
        black = (0, 0, 0)           # Black outline

        # Create exclamation mark text
        exclamation_text = "!"

        # Render text at different sizes for outline effect
        base_font_size = int(48 * pulse_scale)
        font = pygame.font.Font(None, base_font_size)

        # Create outlined exclamation mark
        # Render black outline (slightly offset in all directions)
        outline_offsets = [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)]

        for offset_x, offset_y in outline_offsets:
            outline_surface = font.render(exclamation_text, True, black)
            outline_rect = outline_surface.get_rect()
            outline_rect.center = (self.x + offset_x, self.y + offset_y)
            screen.blit(outline_surface, outline_rect)

        # Render main yellow exclamation mark
        text_surface = font.render(exclamation_text, True, yellow)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.x, self.y)
        screen.blit(text_surface, text_rect)

        # Add a subtle glow effect
        glow_size = int(base_font_size * 1.3)
        glow_font = pygame.font.Font(None, glow_size)
        glow_surface = glow_font.render(exclamation_text, True, dark_yellow)
        glow_surface.set_alpha(100)  # Semi-transparent glow
        glow_rect = glow_surface.get_rect()
        glow_rect.center = (self.x, self.y)
        screen.blit(glow_surface, glow_rect)