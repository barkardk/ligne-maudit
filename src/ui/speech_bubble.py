import pygame

class SpeechBubble:
    def __init__(self, x, y, width=80, height=40):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = False
        self.text = ""
        self.font = pygame.font.Font(None, 28)

    def show(self, text="!", x=None, y=None):
        """Show speech bubble with text at position"""
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self.text = text
        self.visible = True

    def hide(self):
        """Hide speech bubble"""
        self.visible = False

    def render(self, screen):
        """Render the speech bubble"""
        if not self.visible:
            return

        # Bubble colors
        bubble_color = (255, 255, 255)
        border_color = (0, 0, 0)
        text_color = (255, 0, 0)  # Red exclamation mark

        # Main bubble
        bubble_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.ellipse(screen, bubble_color, bubble_rect)
        pygame.draw.ellipse(screen, border_color, bubble_rect, 3)

        # Bubble tail (pointing down) - smaller proportional tail
        tail_points = [
            (self.x + self.width // 2 - 7, self.y + self.height),
            (self.x + self.width // 2, self.y + self.height + 10),
            (self.x + self.width // 2 + 7, self.y + self.height)
        ]
        pygame.draw.polygon(screen, bubble_color, tail_points)
        pygame.draw.polygon(screen, border_color, tail_points, 3)

        # Text (centered in bubble)
        if self.text:
            text_surface = self.font.render(self.text, True, text_color)
            text_rect = text_surface.get_rect()
            text_rect.center = (self.x + self.width // 2, self.y + self.height // 2)
            screen.blit(text_surface, text_rect)

class InteractionPrompt:
    def __init__(self):
        self.visible = False
        self.font = pygame.font.Font(None, 28)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def render(self, screen):
        """Render interaction prompt at bottom of screen"""
        if not self.visible:
            return

        # Background panel
        panel_height = 80
        panel_rect = pygame.Rect(0, screen.get_height() - panel_height, screen.get_width(), panel_height)
        pygame.draw.rect(screen, (0, 0, 0, 180), panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, 2)

        # Instructions - only X key now
        instruction = "Press X to investigate"

        text_surface = self.font.render(instruction, True, (255, 255, 255))
        y_pos = screen.get_height() - panel_height + 25  # Center vertically
        screen.blit(text_surface, (20, y_pos))