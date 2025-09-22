"""Animated rock object that the protagonist can sit on"""

import pygame
import math
import random

class AnimatedRock:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 50

        # Animation properties
        self.bob_timer = 0.0
        self.bob_speed = 1.5
        self.bob_amplitude = 3.0
        self.base_y = y

        # Sparkle animation
        self.sparkle_timer = 0.0
        self.sparkles = []
        self.next_sparkle_time = random.uniform(0.5, 2.0)

        # Interaction properties
        self.is_occupied = False
        self.interaction_distance = 40

        # Colors
        self.base_color = (120, 110, 100)
        self.highlight_color = (140, 130, 120)
        self.shadow_color = (80, 70, 60)

    def update(self, dt):
        """Update rock animations"""
        # Gentle bobbing animation
        self.bob_timer += dt * self.bob_speed
        self.y = self.base_y + math.sin(self.bob_timer) * self.bob_amplitude

        # Update sparkles
        self.sparkle_timer += dt

        # Generate new sparkles occasionally
        if self.sparkle_timer >= self.next_sparkle_time:
            self.add_sparkle()
            self.sparkle_timer = 0.0
            self.next_sparkle_time = random.uniform(1.0, 3.0)

        # Update existing sparkles
        for sparkle in self.sparkles[:]:
            sparkle['timer'] += dt
            sparkle['y'] -= sparkle['speed'] * dt
            sparkle['alpha'] = max(0, sparkle['alpha'] - dt * 200)

            if sparkle['timer'] > sparkle['lifetime'] or sparkle['alpha'] <= 0:
                self.sparkles.remove(sparkle)

    def add_sparkle(self):
        """Add a magical sparkle effect"""
        sparkle = {
            'x': self.x + random.randint(10, self.width - 10),
            'y': self.y + random.randint(5, self.height - 5),
            'speed': random.uniform(20, 40),
            'timer': 0.0,
            'lifetime': random.uniform(1.0, 2.0),
            'alpha': 255,
            'color': random.choice([
                (255, 255, 200),  # Soft yellow
                (200, 255, 255),  # Soft cyan
                (255, 200, 255),  # Soft magenta
                (200, 255, 200)   # Soft green
            ])
        }
        self.sparkles.append(sparkle)

    def check_proximity(self, protagonist_x, protagonist_y, sprite_width, sprite_height):
        """Check if protagonist is near the rock"""
        # Calculate protagonist center
        protag_center_x = protagonist_x + sprite_width // 2
        protag_center_y = protagonist_y + sprite_height // 2

        # Calculate rock center
        rock_center_x = self.x + self.width // 2
        rock_center_y = self.y + self.height // 2

        # Calculate distance
        distance = ((protag_center_x - rock_center_x) ** 2 + (protag_center_y - rock_center_y) ** 2) ** 0.5

        return distance <= self.interaction_distance

    def get_sitting_position(self):
        """Get the position where protagonist should sit"""
        return (
            self.x + self.width // 2 - 32,  # Center horizontally, adjust for sprite width
            self.y - 30   # Sit on top of rock (above the rock surface)
        )

    def render(self, screen):
        """Render the animated rock"""
        # Draw shadow
        shadow_rect = pygame.Rect(self.x + 5, self.base_y + self.height - 5, self.width, 8)
        shadow_alpha = max(50, int(100 - abs(self.y - self.base_y) * 10))
        shadow_surface = pygame.Surface((self.width, 8))
        shadow_surface.set_alpha(shadow_alpha)
        shadow_surface.fill(self.shadow_color)
        screen.blit(shadow_surface, (self.x + 5, self.base_y + self.height - 5))

        # Draw main rock body (oval shape)
        rock_rect = pygame.Rect(self.x, int(self.y), self.width, self.height)
        pygame.draw.ellipse(screen, self.base_color, rock_rect)

        # Draw rock highlights for 3D effect
        highlight_rect = pygame.Rect(self.x + 5, int(self.y) + 5, self.width - 20, self.height - 20)
        pygame.draw.ellipse(screen, self.highlight_color, highlight_rect)

        # Draw rock texture lines
        for i in range(3):
            start_x = self.x + 15 + i * 20
            start_y = int(self.y) + 10 + i * 5
            end_x = start_x + 25
            end_y = start_y + 8
            pygame.draw.line(screen, self.shadow_color, (start_x, start_y), (end_x, end_y), 2)

        # Draw sparkles
        for sparkle in self.sparkles:
            # Create sparkle surface with alpha
            sparkle_surface = pygame.Surface((6, 6))
            sparkle_surface.set_alpha(int(sparkle['alpha']))
            sparkle_surface.fill(sparkle['color'])

            # Draw sparkle as a small star shape
            sparkle_x = int(sparkle['x'])
            sparkle_y = int(sparkle['y'])

            # Draw + shape for sparkle
            pygame.draw.line(sparkle_surface, sparkle['color'], (1, 3), (5, 3), 1)
            pygame.draw.line(sparkle_surface, sparkle['color'], (3, 1), (3, 5), 1)

            screen.blit(sparkle_surface, (sparkle_x - 3, sparkle_y - 3))

    def render_interaction_hint(self, screen):
        """Render interaction hint when protagonist is near"""
        # Small text above the rock
        font = pygame.font.Font(None, 24)
        text = font.render("Press ENTER to sit", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.centerx = self.x + self.width // 2
        text_rect.bottom = int(self.y) - 10

        # Background for text
        bg_rect = text_rect.inflate(10, 5)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
        screen.blit(text, text_rect)