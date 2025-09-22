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

from assets.backgrounds.collision_map import create_maginot_collision_map
from assets.backgrounds.image_collision_detector import create_smart_collision_map
from assets.sprites.protagonist import create_protagonist_animation_system
from assets.sprites.bullet import Bullet, get_direction_from_keys

class BehindBunkerState(GameState):
    def __init__(self, screen, audio_manager=None):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Create background - try behind_bunker.png first, fall back to generated
        self.background = self.load_behind_bunker_background()

        # Create collision map by analyzing the background image
        self.collision_map = create_smart_collision_map(self.background, self.screen_width, self.screen_height)

        # Create protagonist animation system
        self.protagonist_animation, self.using_sprite_sheet = create_protagonist_animation_system()

        # Smart scaling based on detected frame size (same as field state)
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

        # Protagonist position - start on the left side (came from front of bunker)
        self.protagonist_x = 100  # Left side
        self.protagonist_y = self.screen_height // 2  # Middle vertically

        # Movement
        self.move_speed = 100  # pixels per second
        self.is_moving = False
        self.last_facing_direction = 'down'  # Start facing down

        # Shooting
        self.bullets = []
        self.shoot_cooldown = 0.0
        self.shoot_delay = 0.2  # seconds between shots

        # UI components
        self.action_indicator = ActionIndicator(0, 0)
        self.interaction_prompt = InteractionPrompt()
        self.speech_bubble = SpeechBubble(0, 0, 200, 60)

        # Side transition areas (left and right edges to go back to field)
        self.transition_distance = 50  # pixels from edge
        self.near_left_transition = False
        self.near_right_transition = False
        self.transitioning = False

        # Horizontal boundary line - matches the bottom of scene 2's collision box
        # Scene 2 collision box: y=534, height=60, so bottom = 534+60 = 594
        self.horizontal_boundary_y = 534 + 60  # 594px - cannot go above this line

        # Red return collision box (right side) - moved 30px right, below boundary line
        self.return_collision_box_red_x = 2 * (self.screen_width // 4) + 50 + 50 + 30  # 642px
        self.return_collision_box_red_y = self.horizontal_boundary_y + 10  # 604px (10px below boundary line)
        self.return_collision_box_red_width = 80
        self.return_collision_box_red_height = int(60 * 1.25)  # 75px (25% taller)
        self.near_return_collision_box_red = False

        # Blue return collision box (left side) - moved 30px left from original position
        self.return_collision_box_blue_x = (2 * (self.screen_width // 4) + 50 + 50) - 300 - 30  # 282px
        self.return_collision_box_blue_y = self.horizontal_boundary_y + 10  # 604px (10px below boundary line)
        self.return_collision_box_blue_width = 80
        self.return_collision_box_blue_height = int(60 * 1.25)  # 75px (25% taller)
        self.near_return_collision_box_blue = False

        # Dragonteeth collision box at lowest center edge
        self.dragonteeth_collision_x = self.screen_width // 2 - 40  # Center horizontally
        self.dragonteeth_collision_y = self.screen_height - 70  # Bottom edge
        self.dragonteeth_collision_width = 80
        self.dragonteeth_collision_height = 60
        self.near_dragonteeth_collision = False

        # Transition cooldown to prevent endless loops
        self.transition_cooldown = 0.0
        self.transition_cooldown_duration = 10.0  # 10 seconds before allowing another transition

        # Quit overlay
        self.quit_overlay = QuitOverlay()

        # Create lighting effects
        self.light_manager = LightManager()
        # Add some ambient lighting behind the bunker
        self.light_manager.add_light(400, 200, radius=8, color=(255, 220, 120))
        self.light_manager.add_light(600, 300, radius=6, color=(200, 255, 200))

        # Create weather system (same rain and thunder as field)
        self.weather = WeatherSystem(self.screen_width, self.screen_height)

        # Use shared audio manager or create new one
        if audio_manager:
            self.audio = audio_manager
        else:
            self.audio = AudioManager()
            self.audio.load_ambient_pack()

        # Keep existing audio playing if not muted
        if not self.audio.is_muted_state():
            if not self.audio.is_ambient_playing():
                self.audio.play_ambient("forest_rain", loop=True, fade_in_ms=1000)
            if not self.audio.is_music_playing():
                self.audio.play_music("forest_rain_music", loop=True, fade_in_ms=1000)

        # Fade-in transition system
        self.fade_in = True
        self.fade_timer = 0.0
        self.fade_duration = 1.0  # 1 second fade-in
        self.fade_alpha = 255  # Start fully black, fade to transparent

        # Fade-out transition system
        self.fade_out = False
        self.fade_out_timer = 0.0
        self.fade_out_duration = 1.0  # 1 second fade-out
        self.next_scene = None

        print("Behind bunker state initialized - Explore behind the Maginot Line!")
        print(f"Collision areas detected: {len(self.collision_map.collision_rects)}")

    def load_behind_bunker_background(self):
        """Load behind_bunker.png background or create fallback"""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            bg_path = os.path.join(project_root, "assets", "images", "backgrounds", "behind_bunker.png")

            if os.path.exists(bg_path):
                background = pygame.image.load(bg_path)
                background = pygame.transform.scale(background, (self.screen_width, self.screen_height))
                print(f"Loaded behind bunker background from: {bg_path}")
                return background
            else:
                print(f"behind_bunker.png not found at {bg_path}, creating fallback")
                return self.create_fallback_background()

        except Exception as e:
            print(f"Error loading behind bunker background: {e}")
            return self.create_fallback_background()

    def create_fallback_background(self):
        """Create a fallback background showing the area behind the bunker"""
        background = pygame.Surface((self.screen_width, self.screen_height))

        # Dark stormy sky
        background.fill((30, 40, 50))

        # Draw bunker wall on the upper portion
        bunker_height = 200
        bunker_rect = pygame.Rect(0, 0, self.screen_width, bunker_height)
        pygame.draw.rect(background, (60, 55, 50), bunker_rect)

        # Add concrete texture to bunker
        for i in range(0, self.screen_width, 40):
            pygame.draw.line(background, (50, 45, 40), (i, 0), (i, bunker_height), 2)
        for i in range(0, bunker_height, 30):
            pygame.draw.line(background, (50, 45, 40), (0, i), (self.screen_width, i), 2)

        # Draw ground behind bunker
        ground_color = (40, 60, 30)  # Dark grass
        ground_rect = pygame.Rect(0, bunker_height, self.screen_width, self.screen_height - bunker_height)
        pygame.draw.rect(background, ground_color, ground_rect)

        # Add some scattered rocks and debris
        for i in range(15):
            rock_x = random.randint(50, self.screen_width - 50)
            rock_y = random.randint(bunker_height + 20, self.screen_height - 50)
            rock_size = random.randint(10, 25)
            pygame.draw.circle(background, (80, 70, 60), (rock_x, rock_y), rock_size)

        # Add some dark trees in the distance
        for i in range(8):
            tree_x = 100 + i * 120
            tree_y = bunker_height + 50
            tree_width = 20 + random.randint(-5, 5)
            tree_height = 80 + random.randint(-20, 20)
            pygame.draw.rect(background, (20, 30, 20), (tree_x, tree_y, tree_width, tree_height))

        return background

    def check_transition_areas(self):
        """Check if protagonist is near the edges to transition back to field"""
        if self.fade_out or self.transitioning:
            return

        # Get protagonist center
        current_frame = self.protagonist_animation.get_current_frame()
        if current_frame:
            sprite_width = int(current_frame.get_width() * self.character_display_scale)
            sprite_height = int(current_frame.get_height() * self.character_display_scale)
        else:
            sprite_width = 64
            sprite_height = 96

        protagonist_center_x = self.protagonist_x + sprite_width // 2
        protagonist_center_y = self.protagonist_y + sprite_height // 2

        # Check left edge
        if protagonist_center_x <= self.transition_distance:
            if not self.near_left_transition:
                print("Near left transition area - move left to return to field")
                self.near_left_transition = True
        else:
            self.near_left_transition = False

        # Check right edge
        if protagonist_center_x >= self.screen_width - self.transition_distance:
            if not self.near_right_transition:
                print("Near right transition area - move right to return to field")
                self.near_right_transition = True
        else:
            self.near_right_transition = False

        # Trigger transition if at the very edge
        if protagonist_center_x <= 10:  # Very left edge
            self.start_fade_transition("field_left")
        elif protagonist_center_x >= self.screen_width - 10:  # Very right edge
            self.start_fade_transition("field_right")

    def check_return_collision_box(self):
        """Check if protagonist is in the return collision box"""
        if self.fade_out or self.transitioning:
            return

        # Check transition cooldown to prevent endless loops
        if self.transition_cooldown > 0:
            return

        # Get protagonist center
        current_frame = self.protagonist_animation.get_current_frame()
        if current_frame:
            sprite_width = int(current_frame.get_width() * self.character_display_scale)
            sprite_height = int(current_frame.get_height() * self.character_display_scale)
        else:
            sprite_width = 64
            sprite_height = 96

        protagonist_center_x = self.protagonist_x + sprite_width // 2
        protagonist_center_y = self.protagonist_y + sprite_height // 2

        # Check red return collision box (right side) - automatically trigger transition when protagonist enters
        if (self.return_collision_box_red_x <= protagonist_center_x <= self.return_collision_box_red_x + self.return_collision_box_red_width and
            self.return_collision_box_red_y <= protagonist_center_y <= self.return_collision_box_red_y + self.return_collision_box_red_height):
            if not self.near_return_collision_box_red:
                print("Entering red return collision box - transitioning back to scene 2 (red)")
                self.near_return_collision_box_red = True
                # Automatically start transition back to scene 2, spawn at red box
                self.start_fade_transition("field_red")
        else:
            self.near_return_collision_box_red = False

        # Check blue return collision box (left side) - automatically trigger transition when protagonist enters
        if (self.return_collision_box_blue_x <= protagonist_center_x <= self.return_collision_box_blue_x + self.return_collision_box_blue_width and
            self.return_collision_box_blue_y <= protagonist_center_y <= self.return_collision_box_blue_y + self.return_collision_box_blue_height):
            if not self.near_return_collision_box_blue:
                print("Entering blue return collision box - transitioning back to scene 2 (blue)")
                self.near_return_collision_box_blue = True
                # Automatically start transition back to scene 2, spawn at blue box
                self.start_fade_transition("field_blue")
        else:
            self.near_return_collision_box_blue = False

    def check_dragonteeth_collision_box(self):
        """Check if protagonist is in the dragonteeth transition collision box"""
        if self.fade_out or self.transitioning:
            return

        # Check transition cooldown to prevent endless loops
        if self.transition_cooldown > 0:
            return

        # Get protagonist center
        current_frame = self.protagonist_animation.get_current_frame()
        if current_frame:
            sprite_width = int(current_frame.get_width() * self.character_display_scale)
            sprite_height = int(current_frame.get_height() * self.character_display_scale)
        else:
            sprite_width = 64
            sprite_height = 96

        protagonist_center_x = self.protagonist_x + sprite_width // 2
        protagonist_center_y = self.protagonist_y + sprite_height // 2

        # Check dragonteeth collision box - automatically trigger transition when protagonist enters
        if (self.dragonteeth_collision_x <= protagonist_center_x <= self.dragonteeth_collision_x + self.dragonteeth_collision_width and
            self.dragonteeth_collision_y <= protagonist_center_y <= self.dragonteeth_collision_y + self.dragonteeth_collision_height):
            if not self.near_dragonteeth_collision:
                print("Entering dragonteeth collision box - transitioning to scene 4")
                self.near_dragonteeth_collision = True
                self.start_fade_transition("dragonteeth")
        else:
            self.near_dragonteeth_collision = False

    def start_fade_transition(self, next_scene):
        """Start fade out transition to next scene"""
        if self.fade_out or self.transitioning:
            return

        print(f"Starting fade transition to {next_scene}")
        self.fade_out = True
        self.fade_out_timer = 0.0
        self.next_scene = next_scene
        self.transitioning = True

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

        return None  # Stay in this state

    def update(self, dt):
        # Don't update game logic if quit overlay is visible (pause the game)
        if self.quit_overlay.is_visible():
            return

        # Handle fade-in transition
        if self.fade_in:
            self.fade_timer += dt
            if self.fade_timer <= self.fade_duration:
                # Fade from black to transparent (255 to 0)
                progress = self.fade_timer / self.fade_duration
                self.fade_alpha = int(255 * (1.0 - progress))
            else:
                # Fade-in complete
                self.fade_in = False
                self.fade_alpha = 0

        # Handle fade-out transition
        if self.fade_out:
            self.fade_out_timer += dt
            if self.fade_out_timer <= self.fade_out_duration:
                # Fade from transparent to black (0 to 255)
                progress = self.fade_out_timer / self.fade_out_duration
                self.fade_alpha = int(255 * progress)
            else:
                # Fade-out complete - transition to next scene
                print(f"Fade out complete - transitioning to {self.next_scene}")
                return self.next_scene

        # Update transition cooldown
        if self.transition_cooldown > 0:
            self.transition_cooldown -= dt

        # Don't handle movement during fade transitions
        if self.fade_out:
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

        # Keep protagonist on screen with horizontal boundary restriction
        new_x = max(0, min(self.screen_width - sprite_width, new_x))
        # Cannot go higher than the horizontal boundary line
        min_y = self.horizontal_boundary_y
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

        # Check for transition areas
        self.check_transition_areas()
        self.check_return_collision_box()
        self.check_dragonteeth_collision_box()

        return None

    def render(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))

        # Draw lighting effects
        self.light_manager.draw(screen)

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

        # Draw weather effects (rain and lightning over everything)
        self.weather.draw(screen)

        # Draw collision debug if enabled
        self.collision_map.render_debug(screen)

        # Optional: Draw a simple UI element showing location
        font = pygame.font.Font(None, 24)
        location_text = font.render("Behind the Maginot Line - Press F to shoot!", True, (255, 255, 255))
        text_rect = location_text.get_rect()
        text_rect.topleft = (10, 10)

        # Draw text background
        bg_rect = text_rect.inflate(10, 5)
        pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
        screen.blit(location_text, text_rect)

        # Horizontal boundary line is invisible (collision only)

        # Draw both return collision boxes
        # Red return collision box (right side) at (642, 604) - RED
        return_collision_rect_red = pygame.Rect(self.return_collision_box_red_x, self.return_collision_box_red_y,
                                              self.return_collision_box_red_width, self.return_collision_box_red_height)
        # Red collision box is invisible

        # Blue return collision box (left side) at (282, 604) - BLUE
        return_collision_rect_blue = pygame.Rect(self.return_collision_box_blue_x, self.return_collision_box_blue_y,
                                               self.return_collision_box_blue_width, self.return_collision_box_blue_height)
        # Blue collision box is invisible

        # Draw dragonteeth collision box for visibility
        dragonteeth_collision_rect = pygame.Rect(self.dragonteeth_collision_x, self.dragonteeth_collision_y,
                                               self.dragonteeth_collision_width, self.dragonteeth_collision_height)
        pygame.draw.rect(screen, (255, 165, 0), dragonteeth_collision_rect)  # Orange box

        # Draw dragonteeth collision box label
        font = pygame.font.Font(None, 24)
        label_text = font.render("SCENE 4", True, (255, 255, 255))
        label_rect = label_text.get_rect()
        label_rect.centerx = self.dragonteeth_collision_x + self.dragonteeth_collision_width // 2
        label_rect.bottom = self.dragonteeth_collision_y - 5

        # Draw label background
        label_bg_rect = label_rect.inflate(10, 5)
        pygame.draw.rect(screen, (0, 0, 0, 180), label_bg_rect)
        screen.blit(label_text, label_rect)

        # Draw return collision box hint
        if self.near_return_collision_box_red or self.near_return_collision_box_blue:
            hint_font = pygame.font.Font(None, 28)
            hint_text = hint_font.render("Transitioning back to front...", True, (255, 255, 0))
            hint_rect = hint_text.get_rect()
            hint_rect.centerx = self.screen_width // 2
            hint_rect.bottom = self.screen_height - 60

            # Draw hint background
            hint_bg_rect = hint_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), hint_bg_rect)
            screen.blit(hint_text, hint_rect)

        # Draw transition hints if near edges
        if self.near_left_transition or self.near_right_transition:
            hint_font = pygame.font.Font(None, 28)
            hint_text = hint_font.render("Move to edge to return to front", True, (255, 255, 0))
            hint_rect = hint_text.get_rect()
            hint_rect.centerx = self.screen_width // 2
            hint_rect.bottom = self.screen_height - 20

            # Draw hint background
            hint_bg_rect = hint_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), hint_bg_rect)
            screen.blit(hint_text, hint_rect)

        # Draw UI components
        self.action_indicator.render(screen, self.speech_bubble.visible)
        self.interaction_prompt.render(screen)
        self.speech_bubble.render(screen)

        # Draw quit overlay on top of everything
        self.quit_overlay.render(screen)

        # Draw fade overlay if transitioning
        if (self.fade_in or self.fade_out) and self.fade_alpha > 0:
            # Use SRCALPHA surface for smooth fade without box outlines
            fade_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            fade_color = (0, 0, 0, self.fade_alpha)  # Black with alpha
            fade_surface.fill(fade_color)
            screen.blit(fade_surface, (0, 0))

    def cleanup(self):
        """Clean up resources when behind bunker state is destroyed"""
        # Don't cleanup shared audio manager - it's managed by the game instance
        pass