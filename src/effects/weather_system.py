"""Weather system with rain, lightning, and puddles"""

import pygame
import random
import math

class RainDrop:
    def __init__(self, x, y, speed, length=8, depth_layer=1):
        self.x = x
        self.y = y
        self.speed = speed
        self.length = length
        self.wind_offset = random.uniform(-0.5, 0.5)
        self.depth_layer = depth_layer  # 1=far, 2=mid, 3=close
        self.alpha = 30 + (depth_layer * 40)  # Far drops more transparent
        self.thickness = depth_layer  # Line thickness based on depth

    def update(self, dt, wind_strength=0.2):
        self.y += self.speed * dt
        self.x += wind_strength * self.speed * dt + self.wind_offset

    def is_off_screen(self, screen_height):
        return self.y > screen_height + 10

class Puddle:
    def __init__(self, x, y, max_size=30):
        self.x = x
        self.y = y
        self.size = 0
        self.max_size = max_size
        self.growth_rate = random.uniform(2, 5)  # pixels per second
        self.ripple_timer = 0
        self.alpha = 80

    def grow(self, dt):
        if self.size < self.max_size:
            self.size += self.growth_rate * dt
            self.size = min(self.size, self.max_size)

    def add_ripple(self):
        self.ripple_timer = 1.0  # 1 second ripple effect

    def update(self, dt):
        self.grow(dt)
        if self.ripple_timer > 0:
            self.ripple_timer -= dt

    def draw(self, surface):
        if self.size > 2:
            # Draw puddle as dark blue/gray oval
            puddle_color = (60, 80, 120, self.alpha)
            puddle_rect = pygame.Rect(
                int(self.x - self.size/2),
                int(self.y - self.size/4),
                int(self.size),
                int(self.size/2)
            )

            # Create puddle surface with alpha
            puddle_surface = pygame.Surface((int(self.size), int(self.size/2)), pygame.SRCALPHA)
            pygame.draw.ellipse(puddle_surface, puddle_color, puddle_surface.get_rect())
            surface.blit(puddle_surface, (puddle_rect.x, puddle_rect.y))

            # Draw ripples if recently hit
            if self.ripple_timer > 0:
                ripple_radius = int((1 - self.ripple_timer) * self.size * 0.7)
                if ripple_radius > 0:
                    pygame.draw.ellipse(
                        surface,
                        (100, 120, 160, int(60 * self.ripple_timer)),
                        (int(self.x - ripple_radius), int(self.y - ripple_radius/2),
                         ripple_radius * 2, ripple_radius),
                        2
                    )

class Lightning:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.duration = 0
        self.max_duration = 0.5  # 500ms flash for better visibility
        self.intensity = 0
        self.next_strike_time = 3.0  # First strike after 3 seconds
        self.timer = 0
        self.first_strike = True  # Track if this is the first strike

    def update(self, dt):
        self.timer += dt

        if not self.active:
            if self.timer >= self.next_strike_time:
                self.trigger_strike()
                self.first_strike = False  # Mark that first strike has occurred
        else:
            self.duration -= dt
            if self.duration <= 0:
                self.active = False
                self.intensity = 0
                # Set next strike time (randomized after first strike)
                if self.first_strike:
                    self.next_strike_time = 3.0  # Keep first strike at 3 seconds
                else:
                    self.next_strike_time = random.uniform(15, 45)  # Random subsequent strikes
                self.timer = 0
            else:
                # Flash intensity (quick bright flash, then fade)
                progress = 1 - (self.duration / self.max_duration)
                if progress < 0.3:
                    self.intensity = progress / 0.3  # Quick rise
                else:
                    self.intensity = 1 - ((progress - 0.3) / 0.7)  # Slower fade

    def trigger_strike(self):
        self.active = True
        self.duration = self.max_duration
        self.intensity = 1.0

    def draw_flash(self, surface):
        if self.active and self.intensity > 0:
            # Create white overlay for lightning flash - much brighter
            flash_alpha = int(150 * self.intensity)  # Increased from 80 to 150
            flash_surface = pygame.Surface((self.screen_width, self.screen_height))
            flash_surface.set_alpha(flash_alpha)
            flash_surface.fill((255, 255, 255))
            surface.blit(flash_surface, (0, 0))

            # Add debug print to verify lightning is triggering
            print(f"Lightning flash! Intensity: {self.intensity:.2f}, Alpha: {flash_alpha}")

class WeatherSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Rain system with depth layers
        self.raindrops = []
        self.rain_intensity = 80  # drops per second (reduced for slower feel)
        self.rain_speed_min = 140  # Slightly faster rain
        self.rain_speed_max = 230
        self.wind_strength = 0.15  # Gentler wind

        # Puddle system
        self.puddles = []
        self.puddle_spawn_timer = 0
        self.puddle_spawn_rate = 2.0  # seconds between puddle spawns

        # Lightning system
        self.lightning = Lightning(screen_width, screen_height)

        # Weather timing
        self.rain_spawn_timer = 0

        # Create initial puddles at startup
        self.create_initial_puddles()

    def spawn_raindrop(self):
        x = random.uniform(-50, self.screen_width + 50)  # Allow for wind drift
        y = random.uniform(-20, -10)

        # Create depth layers: 50% far, 30% mid, 20% close
        depth_chance = random.random()
        if depth_chance < 0.5:
            depth_layer = 1  # Far
            speed_multiplier = 0.7
        elif depth_chance < 0.8:
            depth_layer = 2  # Mid
            speed_multiplier = 1.0
        else:
            depth_layer = 3  # Close
            speed_multiplier = 1.3

        speed = random.uniform(self.rain_speed_min, self.rain_speed_max) * speed_multiplier
        length = random.uniform(4, 8) * depth_layer  # Far drops shorter
        return RainDrop(x, y, speed, length, depth_layer)

    def spawn_puddle(self):
        # Spawn puddles from door area down to bottom of screen
        # Door is at y=575, so allow puddles from y=575 down to screen bottom
        x = random.uniform(100, self.screen_width - 100)
        door_y = 575  # Bottom of door area
        y = random.uniform(door_y, self.screen_height - 30)
        max_size = random.uniform(15, 35)
        return Puddle(x, y, max_size)

    def create_initial_puddles(self):
        """Create puddles that are already present when the game starts"""
        initial_puddle_count = random.randint(8, 12)  # Start with 8-12 puddles

        for _ in range(initial_puddle_count):
            x = random.uniform(100, self.screen_width - 100)
            door_y = 575  # Bottom of door area
            y = random.uniform(door_y, self.screen_height - 30)

            # Make initial puddles various sizes (some fully grown, some growing)
            max_size = random.uniform(20, 40)
            puddle = Puddle(x, y, max_size)

            # Some puddles start partially or fully grown
            growth_progress = random.uniform(0.3, 1.0)  # 30% to 100% grown
            puddle.size = puddle.max_size * growth_progress

            self.puddles.append(puddle)

    def update(self, dt):
        # Spawn raindrops
        drops_to_spawn = int(self.rain_intensity * dt)
        for _ in range(drops_to_spawn):
            if random.random() < 0.8:  # Not every frame
                self.raindrops.append(self.spawn_raindrop())

        # Update raindrops
        for raindrop in self.raindrops[:]:
            raindrop.update(dt, self.wind_strength)
            if raindrop.is_off_screen(self.screen_height):
                self.raindrops.remove(raindrop)

                # Chance to create or grow a puddle where rain lands
                if random.random() < 0.1:  # 10% chance
                    # Only create puddles in the allowed area (door level and below)
                    puddle_y = max(575, self.screen_height - 20)  # Don't go above door level
                    self.try_add_to_puddle(raindrop.x, puddle_y)

        # Spawn puddles over time
        self.puddle_spawn_timer += dt
        if self.puddle_spawn_timer >= self.puddle_spawn_rate:
            if len(self.puddles) < 15:  # Limit puddle count
                self.puddles.append(self.spawn_puddle())
            self.puddle_spawn_timer = 0

        # Update puddles
        for puddle in self.puddles:
            puddle.update(dt)

        # Update lightning
        self.lightning.update(dt)

    def try_add_to_puddle(self, x, y):
        # Find nearby puddle or create new one
        for puddle in self.puddles:
            distance = math.sqrt((puddle.x - x)**2 + (puddle.y - y)**2)
            if distance < 50:
                puddle.add_ripple()
                return

        # Create new puddle if not too many
        if len(self.puddles) < 15:
            new_puddle = Puddle(x, y, random.uniform(20, 40))
            self.puddles.append(new_puddle)

    def draw_rain(self, surface):
        # Sort raindrops by depth layer (far to close)
        sorted_drops = sorted(self.raindrops, key=lambda drop: drop.depth_layer)

        for raindrop in sorted_drops:
            # Draw raindrop as a line
            start_x = int(raindrop.x)
            start_y = int(raindrop.y)
            end_x = int(raindrop.x + self.wind_strength * raindrop.length)
            end_y = int(raindrop.y + raindrop.length)

            if start_y < self.screen_height and end_y > 0:
                try:
                    # Darker rain colors based on depth
                    if raindrop.depth_layer == 1:  # Far
                        base_color = (45, 55, 75)  # Darker blue-gray
                        blur_effect = True
                    elif raindrop.depth_layer == 2:  # Mid
                        base_color = (65, 75, 95)  # Darker medium blue-gray
                        blur_effect = False
                    else:  # Close
                        base_color = (85, 95, 115)  # Darker lighter blue-gray
                        blur_effect = False

                    # Apply transparency
                    rain_color = (*base_color, raindrop.alpha)

                    # Draw main raindrop line
                    pygame.draw.line(surface, base_color,
                                   (start_x, start_y), (end_x, end_y),
                                   raindrop.thickness)

                    # Add blur effect for distant rain
                    if blur_effect and random.random() < 0.7:
                        # Draw additional fuzzy lines around the main drop
                        for offset in [-1, 1]:
                            fuzz_color = (base_color[0] // 2, base_color[1] // 2, base_color[2] // 2)
                            pygame.draw.line(surface, fuzz_color,
                                           (start_x + offset, start_y),
                                           (end_x + offset, end_y), 1)

                    # Add slight variation for realism
                    if random.random() < 0.2:
                        variation_color = (min(255, base_color[0] + 20),
                                         min(255, base_color[1] + 20),
                                         min(255, base_color[2] + 20))
                        pygame.draw.line(surface, variation_color,
                                       (start_x+1, start_y), (end_x+1, end_y), 1)
                except:
                    pass  # Handle edge cases

    def draw_puddles(self, surface):
        for puddle in self.puddles:
            puddle.draw(surface)

    def draw_lightning(self, surface):
        self.lightning.draw_flash(surface)

    def draw(self, surface):
        # Draw in order: puddles, rain, lightning flash
        self.draw_puddles(surface)
        self.draw_rain(surface)
        self.draw_lightning(surface)