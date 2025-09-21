"""Flickering light effects for atmospheric lighting"""

import pygame
import random
import math

class FlickeringLight:
    def __init__(self, x, y, base_radius=8, color=(255, 200, 100)):
        """
        Create a flickering light effect

        Args:
            x, y: Position of the light
            base_radius: Base size of the light
            color: RGB color tuple (default warm yellow)
        """
        self.x = x
        self.y = y
        self.base_radius = base_radius
        self.color = color

        # Animation state
        self.brightness = 1.0
        self.radius = base_radius
        self.flicker_timer = 0.0
        self.flicker_speed = random.uniform(0.1, 0.3)  # Random flicker rate

        # Offset for subtle movement
        self.offset_x = 0
        self.offset_y = 0
        self.movement_timer = 0.0

    def update(self, dt):
        """Update the light animation"""
        # Update flicker timing
        self.flicker_timer += dt
        self.movement_timer += dt

        # Brightness flicker (varies between 0.3 and 1.0)
        brightness_variation = math.sin(self.flicker_timer * 15) * 0.1
        random_flicker = random.uniform(-0.2, 0.2) if random.random() < 0.1 else 0
        self.brightness = max(0.3, min(1.0, 0.7 + brightness_variation + random_flicker))

        # Size variation (subtle)
        size_variation = math.sin(self.flicker_timer * 8) * 0.3
        self.radius = self.base_radius + size_variation

        # Subtle position movement
        self.offset_x = math.sin(self.movement_timer * 2) * 1.5
        self.offset_y = math.cos(self.movement_timer * 1.5) * 1.0

        # Random speed changes
        if random.random() < 0.02:  # 2% chance per frame
            self.flicker_speed = random.uniform(0.1, 0.3)

    def draw(self, surface):
        """Draw the flickering light with glow effect"""
        # Calculate current position
        current_x = int(self.x + self.offset_x)
        current_y = int(self.y + self.offset_y)

        # Create color with current brightness
        current_color = tuple(int(c * self.brightness) for c in self.color)

        # Draw multiple circles for glow effect
        for i in range(3):
            glow_radius = int(self.radius * (1.5 - i * 0.3))
            glow_alpha = int(80 * self.brightness * (1 - i * 0.3))

            if glow_radius > 0 and glow_alpha > 0:
                # Create a surface for the glow circle with alpha
                glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow_surface,
                    (*current_color, glow_alpha),
                    (glow_radius, glow_radius),
                    glow_radius
                )

                # Blit with proper positioning
                surface.blit(
                    glow_surface,
                    (current_x - glow_radius, current_y - glow_radius),
                    special_flags=pygame.BLEND_ALPHA_SDL2
                )

        # Draw the core light (brightest)
        core_radius = max(1, int(self.radius * 0.5))
        core_color = tuple(min(255, int(c * self.brightness * 1.2)) for c in self.color)
        pygame.draw.circle(surface, core_color, (current_x, current_y), core_radius)

class LightManager:
    """Manages multiple light effects"""

    def __init__(self):
        self.lights = []

    def add_light(self, x, y, radius=8, color=(255, 200, 100)):
        """Add a new flickering light"""
        light = FlickeringLight(x, y, radius, color)
        self.lights.append(light)
        return light

    def update(self, dt):
        """Update all lights"""
        for light in self.lights:
            light.update(dt)

    def draw(self, surface):
        """Draw all lights"""
        for light in self.lights:
            light.draw(surface)

    def clear(self):
        """Remove all lights"""
        self.lights.clear()