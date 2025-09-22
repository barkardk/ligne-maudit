"""
Simple Dragonteeth scene (Scene 4) - Just background and basic functionality
"""

import pygame
import os
import sys
from .game_state import GameState
from ..ui.quit_overlay import QuitOverlay

# Add the project root to the path to import assets
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from assets.sprites.protagonist import create_protagonist_animation_system

class DragonteethState(GameState):
    def __init__(self, screen, audio_manager=None):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Load dragonteeth background
        self.background = self.load_dragonteeth_background()

        # Create protagonist animation system
        self.protagonist_animation, self.using_sprite_sheet = create_protagonist_animation_system()

        # Protagonist starts at center
        self.protagonist_x = self.screen_width // 2 - 32
        self.protagonist_y = self.screen_height // 2 - 48

        # Movement system
        self.character_speed = 150
        self.last_facing_direction = 'down'

        # Quit overlay
        self.quit_overlay = QuitOverlay()

        # Fade-in transition system
        self.fade_in = True
        self.fade_timer = 0.0
        self.fade_duration = 1.0
        self.fade_alpha = 255

        # Fade-out transition system
        self.fade_out = False
        self.fade_out_timer = 0.0
        self.fade_out_duration = 1.0
        self.next_scene = None

        print("Dragonteeth state initialized - Simple scene 4!")

    def load_dragonteeth_background(self):
        """Load dragonteeth.png background or create fallback"""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            bg_path = os.path.join(project_root, "assets", "images", "backgrounds", "dragonteeth.png")
            print(f"Looking for dragonteeth.png at: {bg_path}")

            if os.path.exists(bg_path):
                background = pygame.image.load(bg_path)
                background = pygame.transform.scale(background, (self.screen_width, self.screen_height))
                print(f"Loaded dragonteeth background from: {bg_path}")
                return background
            else:
                print(f"dragonteeth.png not found, creating fallback")
                return self.create_fallback_background()

        except Exception as e:
            print(f"Error loading dragonteeth background: {e}")
            return self.create_fallback_background()

    def create_fallback_background(self):
        """Create a simple fallback background"""
        background = pygame.Surface((self.screen_width, self.screen_height))

        # Dark gradient background
        for y in range(self.screen_height):
            color_intensity = int(20 + (y / self.screen_height) * 40)
            color = (color_intensity, color_intensity + 5, color_intensity)
            pygame.draw.line(background, color, (0, y), (self.screen_width, y))

        # Add some simple shapes for visual interest
        pygame.draw.rect(background, (60, 60, 70), (100, 200, 200, 300))
        pygame.draw.circle(background, (50, 55, 60), (self.screen_width - 200, 300), 100)

        return background

    def start_fade_transition(self, next_scene):
        """Start fade out transition to next scene"""
        if self.fade_out:
            return

        print(f"Starting fade transition to {next_scene}")
        self.fade_out = True
        self.fade_out_timer = 0.0
        self.next_scene = next_scene

    def handle_event(self, event):
        # Handle quit overlay input first if it's visible
        if self.quit_overlay.is_visible():
            result = self.quit_overlay.handle_input(event)
            if result == "quit":
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return None
            elif result == "resume":
                return None
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.quit_overlay.show()
                return None

        return None

    def handle_movement(self, dt):
        """Handle basic movement"""
        keys = pygame.key.get_pressed()

        # Basic movement with arrow keys
        if keys[pygame.K_UP]:
            self.protagonist_y -= self.character_speed * dt
            self.protagonist_animation.play_animation('walk_up')
            self.last_facing_direction = 'up'

            # Return to scene 3 if at top
            if self.protagonist_y <= 50:
                self.start_fade_transition("behind_bunker")

        elif keys[pygame.K_DOWN]:
            self.protagonist_y += self.character_speed * dt
            self.protagonist_animation.play_animation('walk_down')
            self.last_facing_direction = 'down'

            # Limit at bottom
            if self.protagonist_y >= self.screen_height - 100:
                self.protagonist_y = self.screen_height - 100

        elif keys[pygame.K_LEFT]:
            self.protagonist_x -= self.character_speed * dt
            self.protagonist_animation.play_animation('walk_left')
            self.last_facing_direction = 'left'

            # Limit at left
            if self.protagonist_x <= 50:
                self.protagonist_x = 50

        elif keys[pygame.K_RIGHT]:
            self.protagonist_x += self.character_speed * dt
            self.protagonist_animation.play_animation('walk_right')
            self.last_facing_direction = 'right'

            # Limit at right
            if self.protagonist_x >= self.screen_width - 50:
                self.protagonist_x = self.screen_width - 50
        else:
            # Idle animation when not moving
            self.protagonist_animation.play_animation(f'idle_{self.last_facing_direction}')

    def update(self, dt):
        # Handle fade-in transition
        if self.fade_in:
            self.fade_timer += dt
            if self.fade_timer >= self.fade_duration:
                self.fade_in = False
                self.fade_timer = 0.0
                self.fade_alpha = 0
            else:
                progress = self.fade_timer / self.fade_duration
                self.fade_alpha = int(255 * (1 - progress))

        # Handle fade-out transition
        if self.fade_out:
            self.fade_out_timer += dt
            if self.fade_out_timer >= self.fade_out_duration:
                return self.next_scene
            else:
                progress = self.fade_out_timer / self.fade_out_duration
                self.fade_alpha = int(255 * progress)

        # Handle movement
        self.handle_movement(dt)

        # Update animations
        self.protagonist_animation.update(dt)

        return None

    def render(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))

        # Draw protagonist
        current_frame = self.protagonist_animation.get_current_frame()
        if current_frame:
            screen.blit(current_frame, (self.protagonist_x, self.protagonist_y))

        # Draw quit overlay
        if self.quit_overlay.is_visible():
            self.quit_overlay.render(screen)

        # Draw fade transition
        if self.fade_in or self.fade_out:
            fade_surface = pygame.Surface((self.screen_width, self.screen_height))
            fade_surface.set_alpha(self.fade_alpha)
            fade_surface.fill((0, 0, 0))
            screen.blit(fade_surface, (0, 0))