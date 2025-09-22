import pygame
import sys
import os
import random
from .game_state import GameState
from ..ui.speech_bubble import SpeechBubble, InteractionPrompt
from ..ui.action_indicator import ActionIndicator
from ..ui.quit_overlay import QuitOverlay
from ..effects.light_effect import LightManager
from ..effects.weather_system import WeatherSystem
from ..audio.audio_manager import AudioManager

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
    def __init__(self, screen, audio_manager=None):
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
            elif frame_w == 256 and frame_h == 320:
                self.character_display_scale = 0.25  # 256x320 sprites -> ~64x80 display
                print("Using 0.25x scale for 256x320 sprites")
            else:
                self.character_display_scale = 0.25  # Very large sprites (256x384) -> ~64x96 display
                print("Using 0.25x scale for very large sprites")
        else:
            self.character_display_scale = 1.0  # Default fallback

        # Set initial animation to face down (towards player)
        self.protagonist_animation.play_animation('idle_down')

        # Protagonist position - bottom center, ready to walk up the path
        self.protagonist_x = self.screen_width // 2 - 32  # Center horizontally
        self.protagonist_y = self.screen_height - 100  # Bottom of screen with some margin

        # Movement
        self.move_speed = 100  # pixels per second
        self.is_moving = False
        self.last_facing_direction = 'down'  # Start facing down (towards player)

        # Shooting
        self.bullets = []
        self.shoot_cooldown = 0.0
        self.shoot_delay = 0.2  # seconds between shots

        # Door interaction
        self.action_indicator = ActionIndicator(0, 0)
        self.interaction_prompt = InteractionPrompt()
        self.near_door = False
        self.door_interaction_distance = 45  # pixels (smaller)

        # Quit overlay
        self.quit_overlay = QuitOverlay()

        # Flash interaction - lower half, left side
        self.flash_x = 195  # Left side of screen
        self.flash_y = 595  # Lower half
        self.flash_size = 15  # 15x15 collision box
        self.near_flash = False
        self.flash_interaction_distance = 30  # pixels
        self.flash_has_key = True  # Initially has key
        self.flash_discovered = False  # Track if flash has been discovered

        # Flickering light effect
        self.flicker_timer = 0.0
        self.flicker_base_interval = 0.8  # Base flicker rate
        self.flicker_variance = 0.6  # Random variance for natural flickering
        self.flicker_duration = 0.1  # Very brief flicker
        self.show_flicker = False
        self.flicker_intensity = 0.0  # Intensity of current flicker
        self.next_flicker_time = 0.0

        # Get door position - lower third center
        self.door_x = 467  # 25 pixels to the right
        self.door_y = 575  # 25 pixels up

        # Create lighting effects
        self.light_manager = LightManager()
        # Add flickering light in tower window (estimated position above and to the right of door)
        tower_window_x = self.door_x + 54  # To the right of door (moved 26 pixels left total)
        tower_window_y = self.door_y - 150  # Above the door
        self.light_manager.add_light(tower_window_x, tower_window_y, radius=6, color=(255, 220, 120))

        # Create weather system
        self.weather = WeatherSystem(self.screen_width, self.screen_height)

        # Use shared audio manager or create new one
        if audio_manager:
            self.audio = audio_manager
        else:
            self.audio = AudioManager()
            self.audio.load_ambient_pack()

        # Only start audio if not already playing and not muted (to preserve mute state)
        if not self.audio.is_muted_state():
            if not self.audio.is_ambient_playing():
                self.audio.play_ambient("forest_rain", loop=True, fade_in_ms=3000)
            if not self.audio.is_music_playing():
                self.audio.play_music("forest_rain_music", loop=True, fade_in_ms=3000)

        print("Field state initialized - Press arrow keys to move, F to shoot, C to toggle collision debug, SPACE to toggle audio!")
        print(f"Collision areas detected: {len(self.collision_map.collision_rects)}")
        print(f"Door located at: ({self.door_x}, {self.door_y})")
        print(f"Flash located at: ({self.flash_x}, {self.flash_y})")
        print(f"Tower window light at: ({tower_window_x}, {tower_window_y})")

    def check_flash_proximity(self):
        """Check if protagonist is near the flash and handle interaction UI"""
        # Only check proximity if flash hasn't been discovered
        if self.flash_discovered:
            if self.near_flash:
                self.hide_flash_interaction()
            self.near_flash = False
            return

        # Calculate distance from protagonist to flash center
        protagonist_center_x = self.protagonist_x + (self.protagonist_animation.get_current_frame().get_width() * self.character_display_scale) // 2 if self.protagonist_animation.get_current_frame() else self.protagonist_x + 32
        protagonist_center_y = self.protagonist_y + (self.protagonist_animation.get_current_frame().get_height() * self.character_display_scale) // 2 if self.protagonist_animation.get_current_frame() else self.protagonist_y + 48

        flash_center_x = self.flash_x + self.flash_size // 2
        flash_center_y = self.flash_y + self.flash_size // 2

        distance = ((protagonist_center_x - flash_center_x) ** 2 + (protagonist_center_y - flash_center_y) ** 2) ** 0.5

        if distance <= self.flash_interaction_distance:
            if not self.near_flash:
                self.show_flash_interaction()
            self.near_flash = True
        else:
            if self.near_flash:
                self.hide_flash_interaction()
            self.near_flash = False

    def show_flash_interaction(self):
        """Show flash interaction UI"""
        # Position yellow exclamation mark above the flash
        indicator_x = self.flash_x + self.flash_size // 2
        indicator_y = self.flash_y - 40  # Above the flash
        self.action_indicator.show(indicator_x, indicator_y)
        self.interaction_prompt.show()

    def hide_flash_interaction(self):
        """Hide flash interaction UI"""
        if not self.near_door:  # Only hide if not near door
            self.action_indicator.hide()
            self.interaction_prompt.hide()

    def take_key_from_flash(self):
        """Called when player takes key from flash"""
        self.flash_has_key = False
        self.flash_discovered = True
        print("You took the key! The flash area is now inactive.")

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
        # Position yellow exclamation mark above the door
        indicator_x = self.door_x
        indicator_y = self.door_y - 60  # Above the door
        self.action_indicator.show(indicator_x, indicator_y)
        self.interaction_prompt.show()

    def hide_door_interaction(self):
        """Hide door interaction UI"""
        if not self.near_flash:  # Only hide if not near flash
            self.action_indicator.hide()
            self.interaction_prompt.hide()

    def handle_event(self, event):
        # Handle quit overlay input first if it's visible
        if self.quit_overlay.is_visible():
            result = self.quit_overlay.handle_input(event)
            if result == "quit":
                # Signal the game to quit
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return None
            elif result == "resume":
                # Resume game (overlay already hidden)
                return None
            # If quit overlay is visible, don't handle other inputs
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Show quit overlay
                self.quit_overlay.show()
            elif event.key == pygame.K_c:
                # Toggle collision debug mode
                self.collision_map.toggle_debug()
            elif event.key == pygame.K_SPACE:
                # Toggle audio mute
                self.audio.toggle_mute()
            elif event.key == pygame.K_RETURN and self.near_door:
                # Enter door close-up view
                return "door"
            elif event.key == pygame.K_RETURN and self.near_flash:
                # Interact with flash
                return "flash"

        return None  # Stay in this state

    def update(self, dt):
        # Don't update game logic if quit overlay is visible (pause the game)
        if self.quit_overlay.is_visible():
            return

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

        # Keep protagonist on screen and add door height restriction
        new_x = max(0, min(self.screen_width - sprite_width, new_x))
        # Don't allow protagonist to go higher than the door's top edge
        min_y = max(0, self.door_y - 50)  # Allow some space above door
        new_y = max(min_y, min(self.screen_height - sprite_height, new_y))

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

        # Update lighting effects
        self.light_manager.update(dt)

        # Update weather system
        self.weather.update(dt)

        # Update action indicator animation
        self.action_indicator.update(dt)

        # Update flickering light effect
        if not self.flash_discovered:
            self.flicker_timer += dt

            # Check if it's time for next flicker
            if self.flicker_timer >= self.next_flicker_time:
                # Start new flicker
                self.show_flicker = True
                self.flicker_intensity = random.uniform(0.3, 1.0)  # Random intensity
                # Set next flicker time with variance
                self.next_flicker_time = self.flicker_timer + self.flicker_base_interval + random.uniform(-self.flicker_variance, self.flicker_variance)

            # Check if current flicker should end
            if self.show_flicker and self.flicker_timer >= self.next_flicker_time - self.flicker_duration:
                self.show_flicker = False

        # Check proximity to door and flash
        self.check_door_proximity()
        self.check_flash_proximity()

    def render(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))

        # Draw lighting effects
        self.light_manager.draw(screen)

        # Draw bullets
        for bullet in self.bullets:
            bullet.render(screen)

        # Draw flickering purple light effect
        if not self.flash_discovered and self.show_flicker:
            # Calculate alpha based on intensity for subtle effect
            base_alpha = int(80 * self.flicker_intensity)  # Very subtle

            # Purple color variations
            purple_base = (120, 80, 150)  # Muted purple
            purple_bright = (160, 120, 200)  # Slightly brighter purple

            # Create subtle glow effect with multiple circles
            for i, radius in enumerate([8, 6, 4, 2]):
                alpha = max(20, base_alpha - (i * 15))
                color = purple_base if i > 1 else purple_bright

                # Create surface for alpha blending
                glow_surface = pygame.Surface((radius * 2, radius * 2))
                glow_surface.set_alpha(alpha)
                glow_surface.fill(color)

                # Draw as soft circle
                pygame.draw.circle(glow_surface, color, (radius, radius), radius)
                screen.blit(glow_surface, (self.flash_x - radius, self.flash_y - radius))

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

        # Draw weather effects (rain and lightning over everything)
        self.weather.draw(screen)

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
        self.action_indicator.render(screen)
        self.interaction_prompt.render(screen)

        # Draw quit overlay on top of everything
        self.quit_overlay.render(screen)

    def cleanup(self):
        """Clean up resources when field state is destroyed"""
        # Don't cleanup shared audio manager - it's managed by the game instance
        pass