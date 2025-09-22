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
from ..objects.animated_rock import AnimatedRock

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

        # Door interaction with multi-stage workflow
        self.action_indicator = ActionIndicator(0, 0)
        self.interaction_prompt = InteractionPrompt()
        self.speech_bubble = SpeechBubble(0, 0, 200, 60)  # Larger for longer text
        self.near_door = False
        self.door_interaction_distance = 45  # pixels (smaller)

        # Door interaction states
        self.door_interaction_state = 'none'  # 'none', 'approaching', 'heavy_message', 'confirm_open', 'struggling', 'unlocking'
        self.door_message_timer = 0.0
        self.door_message_duration = 3.0  # 3 seconds before auto-advance
        self.has_key = False  # Track if player has picked up the key

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

        # Animated rock - place it on the right side of the screen, much lower down
        self.animated_rock = AnimatedRock(700, 700)
        self.near_rock = False
        self.is_sitting = False

        # Side transition areas (left and right edges to go to behind bunker)
        self.transition_distance = 50  # pixels from edge
        self.near_left_transition = False
        self.near_right_transition = False

        # Grid-based collision boxes (4x4 grid)
        self.grid_width = self.screen_width // 4  # 256px per grid cell
        self.grid_height = self.screen_height // 4  # 192px per grid cell

        # Red collision box (right side) - moved 30px right
        self.collision_box_red_x = 2 * self.grid_width + 50 + 50 + 30  # 612px + 30px = 642px
        self.collision_box_red_y = 2 * self.grid_height + 200 - 50  # 534px
        self.collision_box_red_width = 80
        self.collision_box_red_height = 60
        self.near_collision_box_red = False

        # Blue collision box (left side) - moved 30px left from original left position
        self.collision_box_blue_x = (2 * self.grid_width + 50 + 50) - 300 - 30  # 612px - 300px - 30px = 282px
        self.collision_box_blue_y = 2 * self.grid_height + 200 - 50  # 534px
        self.collision_box_blue_width = 80
        self.collision_box_blue_height = 60
        self.near_collision_box_blue = False

        # Transition cooldown to prevent endless loops
        self.transition_cooldown = 0.0
        self.transition_cooldown_duration = 10.0  # 10 seconds before allowing another transition

        # Fade-out transition system
        self.fade_out = False
        self.fade_out_timer = 0.0
        self.fade_out_duration = 1.0  # 1 second fade-out
        self.next_scene = None

        # Realistic flickering light effect
        self.flicker_timer = 0.0
        self.flicker_sequence = []  # Queue of flicker events
        self.current_flicker_intensity = 0.4  # Higher base dim glow for better visibility
        self.flicker_target_intensity = 0.2
        self.flicker_fade_speed = 8.0  # How fast intensity changes
        self.next_event_time = random.uniform(0.5, 2.0)
        self.is_white_flash = False

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

        # Fade-in transition system
        self.fade_in = True
        self.fade_timer = 0.0
        self.fade_duration = 1.0  # 1 second fade-in
        self.fade_alpha = 255  # Start fully black, fade to transparent

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
        self.has_key = True  # Player now has the key
        print("You took the key! The flash area is now inactive.")

    def generate_flicker_sequence(self):
        """Generate a realistic sequence of flicker events"""
        current_time = self.flicker_timer

        # Choose type of flicker pattern
        pattern_type = random.choice(['gentle', 'stutter', 'surge', 'white_flash'])

        if pattern_type == 'gentle':
            # Gentle brightness change (more visible)
            self.flicker_sequence = [
                {'time': current_time + 0.1, 'intensity': random.uniform(0.6, 0.9)},
                {'time': current_time + 0.8, 'intensity': random.uniform(0.2, 0.4)}
            ]
            self.next_event_time = current_time + random.uniform(1.5, 3.0)  # More frequent

        elif pattern_type == 'stutter':
            # Quick stuttering flickers (more visible)
            self.flicker_sequence = [
                {'time': current_time + 0.05, 'intensity': 0.9},
                {'time': current_time + 0.15, 'intensity': 0.2},
                {'time': current_time + 0.25, 'intensity': 0.8},
                {'time': current_time + 0.35, 'intensity': 0.3},
                {'time': current_time + 0.45, 'intensity': 0.6}
            ]
            self.next_event_time = current_time + random.uniform(1.0, 2.5)  # More frequent

        elif pattern_type == 'surge':
            # Gradual buildup and fade (more visible)
            self.flicker_sequence = [
                {'time': current_time + 0.2, 'intensity': 0.6},
                {'time': current_time + 0.5, 'intensity': 1.0},
                {'time': current_time + 1.0, 'intensity': 0.7},
                {'time': current_time + 1.5, 'intensity': 0.3}
            ]
            self.next_event_time = current_time + random.uniform(2.0, 4.5)  # More frequent

        elif pattern_type == 'white_flash':
            # Bright white flash followed by dimming (more visible)
            self.flicker_sequence = [
                {'time': current_time + 0.02, 'intensity': 1.0, 'white_flash': True},
                {'time': current_time + 0.1, 'intensity': 0.8},
                {'time': current_time + 0.5, 'intensity': 0.4},
                {'time': current_time + 1.0, 'intensity': 0.2}
            ]
            self.next_event_time = current_time + random.uniform(3.0, 6.0)  # More frequent

    def check_door_proximity(self):
        """Check if protagonist is near the door and handle multi-stage interaction"""
        # Calculate distance from protagonist to door
        protagonist_center_x = self.protagonist_x + (self.protagonist_animation.get_current_frame().get_width() * self.character_display_scale) // 2 if self.protagonist_animation.get_current_frame() else self.protagonist_x + 32
        protagonist_center_y = self.protagonist_y + (self.protagonist_animation.get_current_frame().get_height() * self.character_display_scale) // 2 if self.protagonist_animation.get_current_frame() else self.protagonist_y + 48

        distance = ((protagonist_center_x - self.door_x) ** 2 + (protagonist_center_y - self.door_y) ** 2) ** 0.5

        if distance <= self.door_interaction_distance:
            if not self.near_door:
                self.start_door_interaction()
            self.near_door = True
        else:
            if self.near_door:
                self.end_door_interaction()
            self.near_door = False

    def start_door_interaction(self):
        """Start the door interaction workflow"""
        if self.door_interaction_state == 'none':
            # Show exclamation mark and start heavy message
            indicator_x = self.door_x
            indicator_y = self.door_y - 60  # Above the door
            self.action_indicator.show(indicator_x, indicator_y)

            # Show speech bubble with "this door looks really heavy"
            bubble_x = self.door_x - 100  # Position to the left of door
            bubble_y = self.door_y - 120  # Above the door
            self.speech_bubble.show("This door looks really heavy", bubble_x, bubble_y)

            self.door_interaction_state = 'heavy_message'
            self.door_message_timer = 0.0
            print("Door interaction started: showing heavy message")

    def end_door_interaction(self):
        """End door interaction and reset state"""
        if not self.near_flash:  # Only hide if not near flash
            self.action_indicator.hide()
            self.interaction_prompt.hide()
        self.speech_bubble.hide()
        self.door_interaction_state = 'none'
        self.door_message_timer = 0.0
        print("Door interaction ended")

    def advance_door_interaction(self):
        """Advance to next stage of door interaction"""
        if self.door_interaction_state == 'heavy_message':
            # Move to confirmation stage
            self.speech_bubble.show("Open door?", self.door_x - 100, self.door_y - 120)
            self.interaction_prompt.show()
            self.door_interaction_state = 'confirm_open'
            self.door_message_timer = 0.0
            print("Door interaction: showing open confirmation")
        elif self.door_interaction_state == 'confirm_open':
            # Player pressed Y - attempt to open door
            self.attempt_door_open()

    def attempt_door_open(self):
        """Attempt to open the door based on key possession"""
        if self.has_key:
            # Player has key - ask about unlocking
            self.speech_bubble.show("Unlock door?", self.door_x - 100, self.door_y - 120)
            self.door_interaction_state = 'unlocking'
            self.door_message_timer = 0.0
            print("Door interaction: asking about unlocking with key")
        else:
            # Player doesn't have key - struggle and say it's locked
            self.speech_bubble.show("It's locked!", self.door_x - 100, self.door_y - 120)
            self.door_interaction_state = 'struggling'
            self.door_message_timer = 0.0
            print("Door interaction: door is locked, showing struggle message")

    def attempt_door_unlock(self):
        """Try to unlock door with key"""
        # Key doesn't fit - show message
        self.speech_bubble.show("The key doesn't fit", self.door_x - 100, self.door_y - 120)
        self.door_interaction_state = 'struggling'  # Reuse struggling state for timeout
        self.door_message_timer = 0.0
        print("Door interaction: key doesn't fit message")

    def check_rock_proximity(self):
        """Check if protagonist is near the rock"""
        if self.is_sitting:
            return  # Don't check proximity while sitting

        # Get protagonist sprite dimensions
        current_frame = self.protagonist_animation.get_current_frame()
        if current_frame:
            sprite_width = int(current_frame.get_width() * self.character_display_scale)
            sprite_height = int(current_frame.get_height() * self.character_display_scale)
        else:
            sprite_width = 64
            sprite_height = 96

        # Check if protagonist is near rock
        was_near_rock = self.near_rock
        self.near_rock = self.animated_rock.check_proximity(
            self.protagonist_x, self.protagonist_y, sprite_width, sprite_height
        )

        # Print debug info when proximity changes
        if self.near_rock != was_near_rock:
            if self.near_rock:
                print("Near rock - Press ENTER to sit")
            else:
                print("Left rock area")

    def sit_on_rock(self):
        """Make protagonist sit on the rock"""
        if not self.near_rock or self.is_sitting:
            return

        # Move protagonist to sitting position
        sit_x, sit_y = self.animated_rock.get_sitting_position()
        self.protagonist_x = sit_x
        self.protagonist_y = sit_y

        # Set sitting state
        self.is_sitting = True
        self.animated_rock.is_occupied = True

        # Set idle animation facing down
        self.protagonist_animation.play_animation('idle_down')
        self.last_facing_direction = 'down'

        print("Protagonist is now sitting on the rock")

    def stand_up_from_rock(self):
        """Make protagonist stand up from the rock"""
        if not self.is_sitting:
            return

        # Move protagonist slightly away from rock
        self.protagonist_x += 10  # Move slightly right
        self.protagonist_y += 40  # Move down from rock

        # Clear sitting state
        self.is_sitting = False
        self.animated_rock.is_occupied = False

        print("Protagonist stood up from the rock")

    def check_side_transitions(self):
        """Check if protagonist is near the side edges to transition to behind bunker"""
        if self.fade_out or hasattr(self, 'transitioning') and self.transitioning:
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
                print("Near left transition area - move left to go behind bunker")
                self.near_left_transition = True
        else:
            self.near_left_transition = False

        # Check right edge
        if protagonist_center_x >= self.screen_width - self.transition_distance:
            if not self.near_right_transition:
                print("Near right transition area - move right to go behind bunker")
                self.near_right_transition = True
        else:
            self.near_right_transition = False

        # Trigger transition if at the very edge
        if protagonist_center_x <= 10:  # Very left edge
            self.start_fade_transition("behind_bunker_left")
        elif protagonist_center_x >= self.screen_width - 10:  # Very right edge
            self.start_fade_transition("behind_bunker_right")

    def start_fade_transition(self, next_scene):
        """Start fade out transition to next scene"""
        if self.fade_out or hasattr(self, 'transitioning') and self.transitioning:
            return

        print(f"Starting fade transition to {next_scene}")
        self.fade_out = True
        self.fade_out_timer = 0.0
        self.next_scene = next_scene
        if not hasattr(self, 'transitioning'):
            self.transitioning = False
        self.transitioning = True

    def check_collision_boxes(self):
        """Check if protagonist is in any of the grid-based collision boxes"""
        if self.fade_out or hasattr(self, 'transitioning') and self.transitioning:
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

        # Check red collision box (right side) - automatically trigger transition when protagonist enters
        if (self.collision_box_red_x <= protagonist_center_x <= self.collision_box_red_x + self.collision_box_red_width and
            self.collision_box_red_y <= protagonist_center_y <= self.collision_box_red_y + self.collision_box_red_height):
            if not self.near_collision_box_red:
                print("Entering red collision box - transitioning to behind bunker scene (red)")
                self.near_collision_box_red = True
                # Automatically start transition to scene 3, spawn at red box
                self.start_fade_transition("behind_bunker_red")
        else:
            self.near_collision_box_red = False

        # Check blue collision box (left side) - automatically trigger transition when protagonist enters
        if (self.collision_box_blue_x <= protagonist_center_x <= self.collision_box_blue_x + self.collision_box_blue_width and
            self.collision_box_blue_y <= protagonist_center_y <= self.collision_box_blue_y + self.collision_box_blue_height):
            if not self.near_collision_box_blue:
                print("Entering blue collision box - transitioning to behind bunker scene (blue)")
                self.near_collision_box_blue = True
                # Automatically start transition to scene 3, spawn at blue box
                self.start_fade_transition("behind_bunker_blue")
        else:
            self.near_collision_box_blue = False

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
                if self.door_interaction_state == 'heavy_message':
                    # Advance from heavy message to confirmation
                    self.advance_door_interaction()
                elif self.door_interaction_state == 'confirm_open':
                    # Show Y/N instruction instead of auto-opening
                    pass
            elif event.key == pygame.K_y and self.near_door:
                if self.door_interaction_state == 'confirm_open':
                    # Player confirms opening door
                    self.attempt_door_open()
                elif self.door_interaction_state == 'unlocking':
                    # Player confirms unlocking with key
                    self.attempt_door_unlock()
            elif event.key == pygame.K_n and self.near_door:
                if self.door_interaction_state == 'confirm_open' or self.door_interaction_state == 'unlocking':
                    # Player cancels - go back to heavy message
                    self.speech_bubble.show("This door looks really heavy", self.door_x - 100, self.door_y - 120)
                    self.interaction_prompt.hide()
                    self.door_interaction_state = 'heavy_message'
                    self.door_message_timer = 0.0
            elif event.key == pygame.K_RETURN and self.near_flash:
                # Interact with flash
                return "flash"
            elif event.key == pygame.K_RETURN and self.near_rock and not self.is_sitting:
                # Sit on rock
                self.sit_on_rock()
            elif event.key == pygame.K_RETURN and self.is_sitting:
                # Stand up from rock
                self.stand_up_from_rock()

        return None  # Stay in this state

    def update(self, dt):
        # Don't update game logic if quit overlay is visible (pause the game)
        if self.quit_overlay.is_visible():
            return

        keys = pygame.key.get_pressed()
        self.is_moving = False

        # Handle movement with collision detection (only if not sitting)
        if not self.is_sitting:
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
        else:
            # If sitting, no movement but keep current position
            old_x = self.protagonist_x
            old_y = self.protagonist_y
            new_x = old_x
            new_y = old_y
            movement_direction = None

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

        # Only update position if not sitting
        if not self.is_sitting:
            # Keep protagonist on screen and add door height restriction
            new_x = max(0, min(self.screen_width - sprite_width, new_x))
            # Don't allow protagonist to go higher than the door's top edge
            min_y = max(0, self.door_y - 50)  # Allow some space above door
            new_y = max(min_y, min(self.screen_height - sprite_height, new_y))

            # Check collision and get valid position
            self.protagonist_x, self.protagonist_y = self.collision_map.get_valid_position(
                old_x, old_y, new_x, new_y, sprite_width, sprite_height
            )

        # Handle shooting (only if not sitting)
        self.shoot_cooldown -= dt
        if keys[pygame.K_f] and self.shoot_cooldown <= 0 and not self.is_sitting:
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

        # Update realistic flickering light effect
        if not self.flash_discovered:
            self.flicker_timer += dt

            # Check if it's time for next flicker event
            if self.flicker_timer >= self.next_event_time:
                self.generate_flicker_sequence()

            # Process current flicker sequence
            if self.flicker_sequence:
                event = self.flicker_sequence[0]
                if self.flicker_timer >= event['time']:
                    self.flicker_target_intensity = event['intensity']
                    self.is_white_flash = event.get('white_flash', False)
                    self.flicker_sequence.pop(0)

            # Smoothly transition current intensity toward target
            intensity_diff = self.flicker_target_intensity - self.current_flicker_intensity
            if abs(intensity_diff) > 0.01:
                self.current_flicker_intensity += intensity_diff * self.flicker_fade_speed * dt
            else:
                self.current_flicker_intensity = self.flicker_target_intensity
                self.is_white_flash = False  # White flash only lasts one frame

        # Update door interaction workflow
        if self.near_door and self.door_interaction_state != 'none':
            self.door_message_timer += dt

            # Auto-advance after timeout
            if self.door_message_timer >= self.door_message_duration:
                if self.door_interaction_state == 'heavy_message':
                    self.advance_door_interaction()
                elif self.door_interaction_state in ['struggling', 'unlocking']:
                    # Return to heavy message after struggle/key failure
                    self.speech_bubble.show("This door looks really heavy", self.door_x - 100, self.door_y - 120)
                    self.interaction_prompt.hide()
                    self.door_interaction_state = 'heavy_message'
                    self.door_message_timer = 0.0

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

        # Check proximity to door, flash, and rock
        self.check_door_proximity()
        self.check_flash_proximity()
        self.check_rock_proximity()

        # Check side transitions (only if not sitting)
        if not self.is_sitting:
            self.check_side_transitions()
            self.check_collision_boxes()

        # Update animated rock
        self.animated_rock.update(dt)

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

    def render(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))

        # Draw lighting effects
        self.light_manager.draw(screen)

        # Draw bullets
        for bullet in self.bullets:
            bullet.render(screen)

        # Draw realistic flickering light effect (more visible and sharper)
        if not self.flash_discovered and self.current_flicker_intensity > 0.02:  # Lower threshold for visibility
            # Boost intensity for better visibility
            intensity = min(1.0, self.current_flicker_intensity * 1.5)

            # Choose colors based on white flash state
            if self.is_white_flash:
                # Bright white flash with blue-white tint
                core_color = (255, 255, 255)
                outer_color = (220, 240, 255)
                glow_color = (180, 200, 255)
            else:
                # Brighter purple magical light for better visibility
                core_color = (220, 150, 255)
                outer_color = (160, 100, 240)
                glow_color = (120, 80, 200)

            # Create realistic light falloff with multiple layers (larger radius)
            max_radius = 25  # Increased from 15 for better visibility
            layers = [
                {'radius': max_radius, 'color': glow_color, 'alpha_mult': 0.25},      # More visible outer glow
                {'radius': max_radius * 0.7, 'color': outer_color, 'alpha_mult': 0.45}, # More visible mid layer
                {'radius': max_radius * 0.4, 'color': core_color, 'alpha_mult': 0.75},  # Brighter core
                {'radius': max_radius * 0.2, 'color': core_color, 'alpha_mult': 1.0}    # Full intensity center
            ]

            for layer in layers:
                radius = int(layer['radius'] * intensity)
                if radius > 1:  # Lower minimum radius
                    alpha = int(255 * intensity * layer['alpha_mult'])
                    alpha = min(255, max(0, alpha))

                    # Create surface for proper alpha blending
                    light_surface = pygame.Surface((radius * 4, radius * 4))
                    light_surface.set_colorkey((0, 0, 0))  # Make black transparent
                    light_surface.set_alpha(alpha)

                    # Draw sharper gradient circle for more defined light
                    for i in range(radius, 0, -2):  # Step by 2 for sharper edges
                        circle_alpha = int((i / radius) * 255)
                        falloff = (i / radius) ** 0.7  # Sharper falloff curve
                        color_with_alpha = tuple(int(c * falloff) for c in layer['color'])
                        pygame.draw.circle(light_surface, color_with_alpha,
                                         (radius * 2, radius * 2), i)

                    # Blit to screen
                    screen.blit(light_surface,
                              (self.flash_x - radius * 2, self.flash_y - radius * 2))

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

        # Draw animated rock
        self.animated_rock.render(screen)
        if self.near_rock:
            self.animated_rock.render_interaction_hint(screen)

        # Draw transition hints if near edges
        if self.near_left_transition or self.near_right_transition:
            hint_font = pygame.font.Font(None, 28)
            hint_text = hint_font.render("Move to edge to go behind bunker", True, (255, 255, 0))
            hint_rect = hint_text.get_rect()
            hint_rect.centerx = self.screen_width // 2
            hint_rect.bottom = self.screen_height - 60

            # Draw hint background
            hint_bg_rect = hint_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), hint_bg_rect)
            screen.blit(hint_text, hint_rect)

        # Draw collision box hints (though transition is now automatic)
        if self.near_collision_box_red or self.near_collision_box_blue:
            hint_font = pygame.font.Font(None, 28)
            hint_text = hint_font.render("Transitioning to behind bunker...", True, (255, 255, 0))
            hint_rect = hint_text.get_rect()
            hint_rect.centerx = self.screen_width // 2
            hint_rect.bottom = self.screen_height - 100

            # Draw hint background
            hint_bg_rect = hint_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), hint_bg_rect)
            screen.blit(hint_text, hint_rect)

        # ALWAYS draw both collision box squares for visualization
        # Red collision box (right side) at (642, 534) - RED
        collision_box_red_rect = pygame.Rect(self.collision_box_red_x, self.collision_box_red_y,
                                            self.collision_box_red_width, self.collision_box_red_height)
        # Red collision box is invisible

        # Blue collision box (left side) at (282, 534) - BLUE
        collision_box_blue_rect = pygame.Rect(self.collision_box_blue_x, self.collision_box_blue_y,
                                             self.collision_box_blue_width, self.collision_box_blue_height)
        # Blue collision box is invisible

        # Draw grid overlay for reference (optional debug)
        if hasattr(self.collision_map, 'debug_mode') and self.collision_map.debug_mode:
            # Draw grid lines
            for i in range(5):  # 4 sections = 5 lines
                x = i * self.grid_width
                y = i * self.grid_height
                # Vertical lines
                pygame.draw.line(screen, (100, 100, 100), (x, 0), (x, self.screen_height), 1)
                # Horizontal lines
                pygame.draw.line(screen, (100, 100, 100), (0, y), (self.screen_width, y), 1)

        # Draw door interaction UI
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
        """Clean up resources when field state is destroyed"""
        # Don't cleanup shared audio manager - it's managed by the game instance
        pass