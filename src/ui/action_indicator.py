"""Action indicator for showing when interactions are available"""

import pygame
import math

class ActionIndicator:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visible = False

        # Try to load a system font, fallback to default
        try:
            self.font = pygame.font.SysFont('Arial', 48, bold=True)
            print("ActionIndicator: Using Arial font")
        except:
            try:
                self.font = pygame.font.Font(None, 48)
                print("ActionIndicator: Using default pygame font")
            except Exception as e:
                print(f"ActionIndicator: Font loading failed: {e}")
                # Last resort - use get_default_font
                self.font = pygame.font.Font(pygame.font.get_default_font(), 48)
                print("ActionIndicator: Using system default font")

        self.pulse_timer = 0
        self.pulse_speed = 3.0  # Speed of pulsing animation

    def show(self, x=None, y=None):
        """Show the action indicator at position"""
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self.visible = True
        print(f"ActionIndicator shown at ({self.x}, {self.y})")

    def hide(self):
        """Hide the action indicator"""
        self.visible = False

    def update(self, dt):
        """Update the pulsing animation"""
        if self.visible:
            self.pulse_timer += dt * self.pulse_speed

    def render(self, screen, speech_bubble_visible=False):
        """Render the bright yellow exclamation mark with pulsing effect"""
        if not self.visible or speech_bubble_visible:
            return

        # Calculate pulsing effect (0.8 to 1.2 scale)
        pulse_scale = 1.0 + 0.2 * math.sin(self.pulse_timer)

        # Colors - bright yellow with black outline for the exclamation mark only
        yellow = (255, 255, 0)      # Bright yellow
        black = (0, 0, 0)           # Black outline

        # Draw standalone yellow exclamation mark (no circle background)
        # Main vertical line (thicker and taller)
        line_width = max(4, int(8 * pulse_scale))
        line_height = int(20 * pulse_scale)

        # Draw black outline for the line
        outline_rect = pygame.Rect(
            int(self.x - line_width//2 - 1),
            int(self.y - line_height//2 - 3),
            line_width + 2,
            line_height + 2
        )
        pygame.draw.rect(screen, black, outline_rect)

        # Draw yellow line
        line_rect = pygame.Rect(
            int(self.x - line_width//2),
            int(self.y - line_height//2 - 2),
            line_width,
            line_height
        )
        pygame.draw.rect(screen, yellow, line_rect)

        # Dot at bottom with outline
        dot_size = max(4, int(6 * pulse_scale))
        dot_y = int(self.y + line_height//2 + dot_size + 2)

        # Draw black outline for dot
        pygame.draw.circle(screen, black, (int(self.x), dot_y), dot_size + 1)
        # Draw yellow dot
        pygame.draw.circle(screen, yellow, (int(self.x), dot_y), dot_size)