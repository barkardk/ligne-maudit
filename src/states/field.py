import pygame
import sys
import os
from .game_state import GameState
from ..ui.speech_bubble import SpeechBubble, InteractionPrompt

# Add the project root to the path to import assets
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from assets.backgrounds.maginot_exterior import create_maginot_exterior_background, add_birds_to_scene
from assets.backgrounds.image_loader import load_concept_art_background, blend_concept_with_generated
from assets.backgrounds.collision_map import create_maginot_collision_map
from assets.backgrounds.image_collision_detector import create_smart_collision_map
from assets.sprites.protagonist import create_protagonist_animation_system
from assets.sprites.bullet import Bullet, get_direction_from_keys

class FieldState(GameState):
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Create background - try concept art first, fall back to generated
        generated_bg = create_maginot_exterior_background(self.screen_width, self.screen_height)
        generated_bg = add_birds_to_scene(generated_bg)

        # Try to load concept art and blend with generated background
        self.background = load_concept_art_background(
            self.screen_width,
            self.screen_height,
            fallback_function=lambda w, h: generated_bg
        )

        # Create collision map by analyzing the background image
        self.collision_map = create_smart_collision_map(self.background, self.screen_width, self.screen_height)

        # Create protagonist animation system
        self.protagonist_animation, self.using_sprite_sheet = create_protagonist_animation_system()

        # Smart scaling based on detected frame size
        current_frame = self.protagonist_animation.get_current_frame()
        if current_frame:
            frame_w, frame_h = current_frame.get_size()
            print(f"Detected frame size: {frame_w}x{frame_h}")

            # Auto-adjust scaling based on frame size
            if frame_w <= 48 and frame_h <= 64:
                self.character_display_scale = 1.5  # 48x64 processed sprites
                print("Using 1.5x scale for processed sprites")
            elif frame_w <= 96 and frame_h <= 128:
                self.character_display_scale = 1.0  # Medium sprites
                print("Using 1.0x scale for medium sprites")
            elif frame_w <= 160 and frame_h <= 240:
                self.character_display_scale = 0.7  # Large sprites (128x192, etc.)
                print("Using 0.7x scale for large sprites")
            else:
                self.character_display_scale = 0.25  # Very large sprites (256x384) -> ~64x96 display
                print("Using 0.25x scale for very large sprites")
        else:
            self.character_display_scale = 1.0  # Default fallback

        # Protagonist position
        self.protagonist_x = 100
        self.protagonist_y = self.screen_height // 2 + 50

        # Movement
        self.move_speed = 100  # pixels per second
        self.is_moving = False
        self.last_facing_direction = 'down'  # Remember last facing direction

        # Shooting
        self.bullets = []
        self.shoot_cooldown = 0.0
        self.shoot_delay = 0.2  # seconds between shots

        # Door interaction
        self.speech_bubble = SpeechBubble(0, 0)
        self.interaction_prompt = InteractionPrompt()
        self.near_door = False
        self.door_interaction_distance = 45  # pixels (smaller)

        # Get door position - lower third center
        self.door_x = 467  # 25 pixels to the right
        self.door_y = 575  # 25 pixels up

        print("Field state initialized - Press arrow keys to move, F to shoot, C to toggle collision debug!")
        print(f"Collision areas detected: {len(self.collision_map.collision_rects)}")
        print(f"Door located at: ({self.door_x}, {self.door_y})")

    def check_door_proximity(self):
        """Check if protagonist is near the door and handle speech bubble"""
        # Calculate distance from protagonist to door
        protagonist_center_x = self.protagonist_x + (self.protagonist_animation.get_current_frame().get_width() * self.character_display_scale) // 2 if self.protagonist_animation.get_current_frame() else self.protagonist_x + 32
        protagonist_center_y = self.protagonist_y + (self.protagonist_animation.get_current_frame().get_height() * self.character_display_scale) // 2 if self.protagonist_animation.get_current_frame() else self.protagonist_y + 48

        distance = ((protagonist_center_x - self.door_x) ** 2 + (protagonist_center_y - self.door_y) ** 2) ** 0.5

        if distance <= self.door_interaction_distance:
            if not self.near_door:
                self.show_door_interaction()
            self.near_door = True
        else:
            if self.near_door:
                self.hide_door_interaction()
            self.near_door = False

    def show_door_interaction(self):
        """Show door interaction UI"""
        # Position speech bubble above the door
        bubble_x = self.door_x - 60  # Center bubble over door
        bubble_y = self.door_y - 80  # Above the door
        self.speech_bubble.show("!", bubble_x, bubble_y)
        self.interaction_prompt.show()

    def hide_door_interaction(self):
        """Hide door interaction UI"""
        self.speech_bubble.hide()
        self.interaction_prompt.hide()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # You can add a menu state or return to main menu here
                pass
            elif event.key == pygame.K_c:
                # Toggle collision debug mode
                self.collision_map.toggle_debug()
            elif event.key == pygame.K_x and self.near_door:
                # Enter puzzle scene
                return "puzzle"
            elif event.key == pygame.K_y and self.near_door:
                # Walk away from door
                self.hide_door_interaction()

        return None  # Stay in this state

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.is_moving = False

        # Handle movement with collision detection
        old_x = self.protagonist_x
        old_y = self.protagonist_y
        new_x = old_x
        new_y = old_y
        movement_direction = None

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_x -= self.move_speed * dt
            self.is_moving = True
            movement_direction = 'left'
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_x += self.move_speed * dt
            self.is_moving = True
            movement_direction = 'right'
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            new_y -= self.move_speed * dt
            self.is_moving = True
            movement_direction = 'up'
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_y += self.move_speed * dt
            self.is_moving = True
            movement_direction = 'down'

        # Get the actual frame from animation to determine size
        current_frame = self.protagonist_animation.get_current_frame()
        if current_frame:
            # Use the actual displayed size (scaled down)
            sprite_width = int(current_frame.get_width() * self.character_display_scale)
            sprite_height = int(current_frame.get_height() * self.character_display_scale)
        else:
            # Fallback dimensions
            sprite_width = int(64 * 2.52 * self.character_display_scale)
            sprite_height = int(96 * 2.52 * self.character_display_scale)

        # Keep protagonist on screen
        new_x = max(0, min(self.screen_width - sprite_width, new_x))
        new_y = max(0, min(self.screen_height - sprite_height, new_y))

        # Check collision and get valid position
        self.protagonist_x, self.protagonist_y = self.collision_map.get_valid_position(
            old_x, old_y, new_x, new_y, sprite_width, sprite_height
        )

        # Handle shooting
        self.shoot_cooldown -= dt
        if keys[pygame.K_f] and self.shoot_cooldown <= 0:
            direction_x, direction_y = get_direction_from_keys(keys)
            # Create bullet at protagonist's gun position (accounting for display scale)
            if current_frame:
                # Use actual frame dimensions
                gun_x_offset = current_frame.get_width() * 0.7 * self.character_display_scale  # Right side of character
                gun_y_offset = current_frame.get_height() * 0.6 * self.character_display_scale  # Gun height
            else:
                # Fallback calculations
                gun_x_offset = (12 * 2.52) + (8 * 2.52) * self.character_display_scale
                gun_y_offset = (21 * 2.52) * self.character_display_scale

            bullet_x = self.protagonist_x + gun_x_offset
            bullet_y = self.protagonist_y + gun_y_offset
            bullet = Bullet(bullet_x, bullet_y, direction_x, direction_y)
            self.bullets.append(bullet)
            self.shoot_cooldown = self.shoot_delay

        # Update bullets
        for bullet in self.bullets[:]:  # Use slice copy to avoid modification during iteration
            bullet.update(dt)
            if bullet.is_off_screen(self.screen_width, self.screen_height):
                self.bullets.remove(bullet)

        # Handle animation based on movement
        if self.is_moving and movement_direction:
            # Play directional walking animation
            self.protagonist_animation.play_animation(f'walk_{movement_direction}')
            # Remember the last facing direction
            self.last_facing_direction = movement_direction
        else:
            # Play idle animation in the last facing direction
            self.protagonist_animation.play_animation(f'idle_{self.last_facing_direction}')

        # Update animation system
        self.protagonist_animation.update(dt)

        # Check proximity to door
        self.check_door_proximity()

    def render(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))

        # Draw bullets
        for bullet in self.bullets:
            bullet.render(screen)

        # Draw protagonist (scaled down for display)
        protagonist_sprite = self.protagonist_animation.get_current_frame()
        if protagonist_sprite:
            original_size = protagonist_sprite.get_size()

            # Scale the sprite down for display
            if self.character_display_scale != 1.0:
                scaled_width = int(protagonist_sprite.get_width() * self.character_display_scale)
                scaled_height = int(protagonist_sprite.get_height() * self.character_display_scale)
                protagonist_sprite = pygame.transform.scale(protagonist_sprite, (scaled_width, scaled_height))

            screen.blit(protagonist_sprite, (int(self.protagonist_x), int(self.protagonist_y)))

        # Draw collision debug if enabled
        self.collision_map.render_debug(screen)

        # Optional: Draw a simple UI element showing location
        font = pygame.font.Font(None, 24)
        location_text = font.render("Outside the Maginot Line - Press F to shoot!", True, (255, 255, 255))
        text_rect = location_text.get_rect()
        text_rect.topleft = (10, 10)

        # Draw text background
        bg_rect = text_rect.inflate(10, 5)
        pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
        screen.blit(location_text, text_rect)

        # Draw door interaction UI
        self.speech_bubble.render(screen)
        self.interaction_prompt.render(screen)