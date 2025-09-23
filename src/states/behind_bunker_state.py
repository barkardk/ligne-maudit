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
from assets.sprites.sprite_sheet_loader import SpriteSheet

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

        # Red return collision box (right side) - moved 30px right, moved up 20px, 30% shorter
        self.return_collision_box_red_x = 2 * (self.screen_width // 4) + 50 + 50 + 30  # 642px
        self.return_collision_box_red_y = self.horizontal_boundary_y + 10 - 20  # 584px (moved up 20px)
        self.return_collision_box_red_width = int(80 * 0.8)  # 64px (width kept same as before)
        self.return_collision_box_red_height = int(60 * 1.25 * 0.8 * 0.7)  # 42px (30% shorter from 60px)
        self.near_return_collision_box_red = False

        # Blue return collision box (left side) - moved 30px left from original position, moved up 20px, 30% shorter
        self.return_collision_box_blue_x = (2 * (self.screen_width // 4) + 50 + 50) - 300 - 30  # 282px
        self.return_collision_box_blue_y = self.horizontal_boundary_y + 10 - 20  # 584px (moved up 20px)
        self.return_collision_box_blue_width = int(80 * 0.8)  # 64px (width kept same as before)
        self.return_collision_box_blue_height = int(60 * 1.25 * 0.8 * 0.7)  # 42px (30% shorter from 60px)
        self.near_return_collision_box_blue = False

        # Dragonteeth collision box - at bottom of image, 80px left of center
        self.dragonteeth_collision_x = self.screen_width // 2 - 60 - 80  # 80px left of center
        self.dragonteeth_collision_y = self.screen_height - 60  # Very bottom of image
        self.dragonteeth_collision_width = 120  # Wide for easier access
        self.dragonteeth_collision_height = 60   # Tall enough to detect collision
        self.near_dragonteeth_collision = False

        # Bunker door hatch collision box - blue 50x50 box in lower center
        self.hatch_collision_x = self.screen_width // 2 - 25 - 100 - 40 - 40 + 80 + 20 - 20 + 50  # Center horizontally (50px wide), moved 50px left total (50px right from previous)
        self.hatch_collision_y = self.screen_height - 200 + 80 - 40  # Lower center area, moved 40px down total
        self.hatch_collision_width = 50
        self.hatch_collision_height = 50
        self.near_hatch_collision = False

        # Hatch interaction system
        self.hatch_interaction_state = "none"  # none, wondering, prompting, struggling1, pausing, struggling2, opening, falling
        self.hatch_interaction_timer = 0.0
        self.hatch_speech_bubble = None
        self.hatch_is_open = False
        self.hatch_opening_progress = 0.0  # 0.0 to 1.0
        self.hatch_positioned = False  # Track if protagonist has been positioned on hatch

        # Transition cooldown to prevent endless loops
        self.transition_cooldown = 0.0
        self.transition_cooldown_duration = 2.0  # 2 seconds before allowing another transition

        # Hatch inspection animation system
        self.setup_hatch_inspection_animation()

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
        self.fade_out_duration = 0.1  # Fast fade-out
        self.next_scene = None

        print("Behind bunker state initialized - Explore behind the Maginot Line!")
        print(f"Collision areas detected: {len(self.collision_map.collision_rects)}")

    def load_behind_bunker_background(self):
        """Load behind_bunker.png background or create fallback"""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            bg_path = os.path.join(project_root, "assets", "images", "backgrounds", "scene3", "behind_bunker.png")

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
        """Check if protagonist is in the dragonteeth transition collision box - fixed for down arrow access"""
        if self.fade_out or self.transitioning:
            return

        # Check transition cooldown to prevent endless loops
        if self.transition_cooldown > 0:
            print(f"Dragonteeth collision check blocked by cooldown: {self.transition_cooldown:.1f}s remaining")
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

        # Debug: Always show position when near the bottom of the screen
        if protagonist_center_y > self.screen_height - 200:
            print(f"Protagonist at ({protagonist_center_x:.1f}, {protagonist_center_y:.1f})")
            print(f"Dragonteeth box: x={self.dragonteeth_collision_x}-{self.dragonteeth_collision_x + self.dragonteeth_collision_width}, y={self.dragonteeth_collision_y}-{self.dragonteeth_collision_y + self.dragonteeth_collision_height}")
            print(f"Hatch interaction state: {self.hatch_interaction_state}")
            print(f"Movement restricted: {self.hatch_interaction_state in ['struggling1', 'pausing', 'struggling2', 'opening']}")
            print(f"Transition cooldown: {self.transition_cooldown:.1f}")
            print(f"Fade out: {self.fade_out}, Transitioning: {self.transitioning}")

        # Check dragonteeth collision box
        if (self.dragonteeth_collision_x <= protagonist_center_x <= self.dragonteeth_collision_x + self.dragonteeth_collision_width and
            self.dragonteeth_collision_y <= protagonist_center_y <= self.dragonteeth_collision_y + self.dragonteeth_collision_height):
            if not self.near_dragonteeth_collision:
                print("SUCCESS: Entering dragonteeth collision box - transitioning to scene 4")
                self.near_dragonteeth_collision = True
                # Automatically start transition to scene 4
                self.start_fade_transition("dragonteeth")
        else:
            self.near_dragonteeth_collision = False

    def check_hatch_collision_box(self):
        """Check if protagonist is in the bunker door hatch collision box"""
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

        # Check bunker door hatch collision box
        hatch_collision = (self.hatch_collision_x <= protagonist_center_x <= self.hatch_collision_x + self.hatch_collision_width and
                          self.hatch_collision_y <= protagonist_center_y <= self.hatch_collision_y + self.hatch_collision_height)

        # Debug hatch collision
        if protagonist_center_y > self.screen_height - 200:
            print(f"Hatch box: x={self.hatch_collision_x}-{self.hatch_collision_x + self.hatch_collision_width}, y={self.hatch_collision_y}-{self.hatch_collision_y + self.hatch_collision_height}")
            print(f"Protagonist center: ({protagonist_center_x:.1f}, {protagonist_center_y:.1f}), sprite: {sprite_width}x{sprite_height}")
            print(f"X check: {self.hatch_collision_x} <= {protagonist_center_x:.1f} <= {self.hatch_collision_x + self.hatch_collision_width} = {self.hatch_collision_x <= protagonist_center_x <= self.hatch_collision_x + self.hatch_collision_width}")
            print(f"Y check: {self.hatch_collision_y} <= {protagonist_center_y:.1f} <= {self.hatch_collision_y + self.hatch_collision_height} = {self.hatch_collision_y <= protagonist_center_y <= self.hatch_collision_y + self.hatch_collision_height}")
            print(f"In hatch collision: {hatch_collision}, near_hatch_collision: {self.near_hatch_collision}")

        if hatch_collision:
            if not self.near_hatch_collision:
                print("Near bunker hatch - starting interaction sequence")
                self.near_hatch_collision = True
                # Start the interaction sequence
                if self.hatch_interaction_state == "none":
                    self.start_hatch_interaction()
        else:
            if self.near_hatch_collision:
                print("Moving away from hatch - resetting interaction")
            self.near_hatch_collision = False
            # Reset interaction if moving away
            if self.hatch_interaction_state in ["none", "wondering", "prompting"]:
                if self.hatch_interaction_state != "none":
                    print(f"Resetting hatch interaction from {self.hatch_interaction_state} to none")
                self.hatch_interaction_state = "none"
                self.hatch_speech_bubble = None
                self.hatch_positioned = False  # Allow positioning again next time

    def setup_hatch_inspection_animation(self):
        """Setup the hatch inspection animation using protagonist angles sprite sheet"""
        try:
            # Load the protagonist angles sprite sheet
            # Based on the image, it's 4x4 grid, so each frame is likely 256x384 (1024/4 x 1536/4)
            self.angles_sprite_sheet = SpriteSheet("protagonist_angles.png", 256, 384)

            # Extract the last row (row 3) for hatch inspection animation
            # This appears to be a crouching/inspection sequence
            self.hatch_inspection_frames = []
            for col in range(4):  # 4 frames in the last row
                frame = self.angles_sprite_sheet.get_frame(col, 3)  # Row 3 (last row)
                if frame:
                    self.hatch_inspection_frames.append(frame)

            print(f"Loaded {len(self.hatch_inspection_frames)} hatch inspection frames")

            # Animation state
            self.is_inspecting_hatch = False
            self.inspection_frame_index = 0
            self.inspection_frame_timer = 0.0
            self.inspection_frame_duration = 0.4  # 400ms per frame
            self.inspection_trigger_key = pygame.K_e  # E key to inspect hatch

        except Exception as e:
            print(f"Error setting up hatch inspection animation: {e}")
            self.hatch_inspection_frames = []

    def is_near_hatch(self):
        """Check if protagonist is near the hatch area (back of bunker)"""
        # Define hatch area - assume it's on the back/top part of the bunker
        hatch_area_x = self.screen_width // 2 - 100  # Center area
        hatch_area_y = 200  # Top part of screen
        hatch_area_width = 200
        hatch_area_height = 150

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

        # Check if protagonist is in hatch area
        return (hatch_area_x <= protagonist_center_x <= hatch_area_x + hatch_area_width and
                hatch_area_y <= protagonist_center_y <= hatch_area_y + hatch_area_height)

    def start_hatch_inspection(self):
        """Start the hatch inspection animation"""
        if self.hatch_inspection_frames:
            print("Starting hatch inspection animation - Press E to stop")
            self.is_inspecting_hatch = True
            self.inspection_frame_index = 0
            self.inspection_frame_timer = 0.0

    def stop_hatch_inspection(self):
        """Stop the hatch inspection animation"""
        print("Stopping hatch inspection animation")
        self.is_inspecting_hatch = False
        self.inspection_frame_index = 0
        self.inspection_frame_timer = 0.0

    def update_hatch_inspection(self, dt):
        """Update the hatch inspection animation"""
        if not self.is_inspecting_hatch or not self.hatch_inspection_frames:
            return

        self.inspection_frame_timer += dt
        if self.inspection_frame_timer >= self.inspection_frame_duration:
            self.inspection_frame_timer = 0.0
            self.inspection_frame_index += 1

            # Loop the animation or stop after one cycle
            if self.inspection_frame_index >= len(self.hatch_inspection_frames):
                self.inspection_frame_index = 0  # Loop animation
                # Or uncomment below to stop after one cycle:
                # self.is_inspecting_hatch = False

    def draw_rusty_iron_hatch(self, screen):
        """Draw an old iron rusty door hatch with rounded edges"""
        hatch_x = self.hatch_collision_x
        hatch_y = self.hatch_collision_y
        hatch_w = self.hatch_collision_width
        hatch_h = self.hatch_collision_height

        # Base moss green colors to blend with environment
        moss_green = (76, 91, 61)
        dark_moss = (45, 55, 35)
        forest_green = (58, 73, 42)
        weathered_green = (65, 80, 50)

        # Create surface for rounded corners
        hatch_surface = pygame.Surface((hatch_w, hatch_h), pygame.SRCALPHA)

        # Draw main hatch body with rounded rectangle effect
        corner_radius = 8

        # Fill main area
        main_rect = pygame.Rect(corner_radius, 0, hatch_w - 2 * corner_radius, hatch_h)
        pygame.draw.rect(hatch_surface, dark_moss, main_rect)

        main_rect = pygame.Rect(0, corner_radius, hatch_w, hatch_h - 2 * corner_radius)
        pygame.draw.rect(hatch_surface, dark_moss, main_rect)

        # Draw rounded corners
        for x in range(corner_radius):
            for y in range(corner_radius):
                distance = ((corner_radius - x - 1) ** 2 + (corner_radius - y - 1) ** 2) ** 0.5
                if distance <= corner_radius:
                    # Top-left corner
                    hatch_surface.set_at((x, y), dark_moss)
                    # Top-right corner
                    hatch_surface.set_at((hatch_w - x - 1, y), dark_moss)
                    # Bottom-left corner
                    hatch_surface.set_at((x, hatch_h - y - 1), dark_moss)
                    # Bottom-right corner
                    hatch_surface.set_at((hatch_w - x - 1, hatch_h - y - 1), dark_moss)

        # Add moss and weathering patches
        import random
        random.seed(42)  # Consistent pattern
        for i in range(15):
            patch_x = random.randint(2, hatch_w - 3)
            patch_y = random.randint(2, hatch_h - 3)
            patch_size = random.randint(2, 5)
            patch_color = forest_green if i % 2 == 0 else moss_green
            pygame.draw.circle(hatch_surface, patch_color, (patch_x, patch_y), patch_size)

        # Add weathered rivets/bolts
        rivet_positions = [
            (8, 8), (hatch_w - 8, 8),
            (8, hatch_h - 8), (hatch_w - 8, hatch_h - 8),
            (hatch_w // 2, 8), (hatch_w // 2, hatch_h - 8)
        ]
        for rivet_x, rivet_y in rivet_positions:
            pygame.draw.circle(hatch_surface, weathered_green, (rivet_x, rivet_y), 3)
            pygame.draw.circle(hatch_surface, (35, 45, 25), (rivet_x, rivet_y), 2)

        # Add central handle/latch
        handle_x = hatch_w // 2
        handle_y = hatch_h // 2
        handle_rect = pygame.Rect(handle_x - 6, handle_y - 3, 12, 6)
        pygame.draw.rect(hatch_surface, weathered_green, handle_rect)
        pygame.draw.rect(hatch_surface, (35, 45, 25), handle_rect, 1)

        # Draw edge highlights and shadows for 3D effect
        # Highlight top and left edges (lighter moss green)
        pygame.draw.line(hatch_surface, (95, 115, 75), (corner_radius, 0), (hatch_w - corner_radius, 0), 2)
        pygame.draw.line(hatch_surface, (95, 115, 75), (0, corner_radius), (0, hatch_h - corner_radius), 2)

        # Shadow bottom and right edges (darker moss green)
        pygame.draw.line(hatch_surface, (25, 35, 15), (corner_radius, hatch_h - 1), (hatch_w - corner_radius, hatch_h - 1), 2)
        pygame.draw.line(hatch_surface, (25, 35, 15), (hatch_w - 1, corner_radius), (hatch_w - 1, hatch_h - corner_radius), 2)

        # Apply brightness when near
        if self.near_hatch_collision:
            # Create a bright overlay
            overlay = pygame.Surface((hatch_w, hatch_h), pygame.SRCALPHA)
            overlay.fill((255, 255, 150, 50))  # Yellow highlight when near
            hatch_surface.blit(overlay, (0, 0))

        # Draw black hole if hatch is open
        if self.hatch_is_open:
            hole_surface = pygame.Surface((hatch_w, hatch_h), pygame.SRCALPHA)
            hole_surface.fill((0, 0, 0))  # Pure black hole
            screen.blit(hole_surface, (hatch_x, hatch_y))
        else:
            # Blit the hatch to the main screen
            screen.blit(hatch_surface, (hatch_x, hatch_y))

    def start_hatch_interaction(self):
        """Start the hatch interaction sequence"""
        # Position protagonist on top of the hatch (centered) - only once
        if not self.hatch_positioned:
            hatch_center_x = self.hatch_collision_x + self.hatch_collision_width // 2
            hatch_center_y = self.hatch_collision_y + self.hatch_collision_height // 2

            # Center protagonist sprite on the hatch
            current_frame = self.protagonist_animation.get_current_frame()
            if current_frame:
                sprite_width = int(current_frame.get_width() * self.character_display_scale)
                sprite_height = int(current_frame.get_height() * self.character_display_scale)
            else:
                sprite_width = 64
                sprite_height = 96

            self.protagonist_x = hatch_center_x - sprite_width // 2
            self.protagonist_y = hatch_center_y - sprite_height // 2
            self.hatch_positioned = True

        self.hatch_interaction_state = "wondering"
        self.hatch_interaction_timer = 0.0
        self.hatch_speech_bubble = SpeechBubble(
            self.protagonist_x, self.protagonist_y - 50, 300, 60
        )
        self.hatch_speech_bubble.show("I wonder if I can get this rusty hatch opened.")

    def update_hatch_interaction(self, dt):
        """Update the hatch interaction sequence - simplified"""
        if self.hatch_interaction_state == "none":
            return

        self.hatch_interaction_timer += dt
        print(f"Hatch update: state={self.hatch_interaction_state}, timer={self.hatch_interaction_timer:.1f}, dt={dt:.3f}")

        if self.hatch_interaction_state == "wondering":
            # Show wondering text for 3 seconds, then prompt
            if self.hatch_interaction_timer >= 3.0:
                print("Moving from wondering to prompting")
                self.hatch_interaction_state = "prompting"
                self.hatch_interaction_timer = 0.0
                self.hatch_speech_bubble.show("Press X to try opening the hatch")

        elif self.hatch_interaction_state == "struggling1":
            # Struggle for 2 seconds then fall immediately
            if self.hatch_interaction_timer >= 2.0:
                print("Struggling complete - falling into hatch!")
                self.hatch_speech_bubble.show("Aaaaaaaaaahhh!")
                self.hatch_is_open = True
                self.hatch_opening_progress = 1.0
                print("Starting immediate transition to scene 5!")
                self.start_fade_transition("bunker_interior")
                self.hatch_interaction_state = "falling"  # Set to falling to prevent re-triggering

    def handle_hatch_interaction_input(self, event):
        """Handle input for hatch interaction"""
        if event.type == pygame.KEYDOWN:
            print(f"Key pressed: {pygame.key.name(event.key)}, hatch state: {self.hatch_interaction_state}")
            if event.key == pygame.K_x and self.hatch_interaction_state == "prompting":
                print("X key pressed during prompting - starting struggle sequence")
                # Start struggling sequence
                self.hatch_interaction_state = "struggling1"
                self.hatch_interaction_timer = 0.0
                self.hatch_speech_bubble.show("Struggling...")
                return True
            elif event.key == pygame.K_x:
                print(f"X key pressed but wrong state: {self.hatch_interaction_state}")
        return False

    def start_fade_transition(self, next_scene):
        """Start fade out transition to next scene - simplified version"""
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
            elif event.key == self.inspection_trigger_key:  # E key for hatch inspection
                if self.is_inspecting_hatch:
                    # Stop inspection if already inspecting
                    self.stop_hatch_inspection()
                elif self.hatch_inspection_frames:
                    # Check if protagonist is near the back of the bunker (hatch area)
                    if self.is_near_hatch():
                        self.start_hatch_inspection()
                    else:
                        print("Move closer to the hatch to inspect it")
            elif event.key == pygame.K_c:
                # Toggle collision debug mode
                self.collision_map.toggle_debug()
            elif event.key == pygame.K_SPACE:
                # Toggle audio mute
                self.audio.toggle_mute()

            # Handle hatch interaction input (always check this)
            if self.handle_hatch_interaction_input(event):
                return None

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

        # Handle fade-out transition - simplified
        if self.fade_out:
            self.fade_out_timer += dt
            if self.fade_out_timer >= self.fade_out_duration:
                # Fade-out complete - transition to next scene
                print(f"Fade out complete - transitioning to {self.next_scene}")
                return self.next_scene
            else:
                # Fade from transparent to black (0 to 255)
                progress = self.fade_out_timer / self.fade_out_duration
                self.fade_alpha = int(255 * progress)

        # Update transition cooldown
        if self.transition_cooldown > 0:
            self.transition_cooldown -= dt

        # Don't handle movement during fade transitions
        if self.fade_out:
            return

        keys = pygame.key.get_pressed()
        self.is_moving = False

        # Restrict movement only during falling state
        if self.hatch_interaction_state in ["falling"]:
            # No movement allowed during falling
            return

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

        # Update animation system (only if not inspecting hatch)
        if not self.is_inspecting_hatch:
            self.protagonist_animation.update(dt)

        # Update hatch inspection animation
        self.update_hatch_inspection(dt)

        # Update hatch interaction sequence
        self.update_hatch_interaction(dt)

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
        self.check_hatch_collision_box()

        return None

    def render(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))

        # Draw lighting effects
        self.light_manager.draw(screen)

        # Draw bullets
        for bullet in self.bullets:
            bullet.render(screen)

        # Draw protagonist (hatch inspection animation takes priority)
        if self.is_inspecting_hatch and self.hatch_inspection_frames:
            # Show hatch inspection animation
            if self.inspection_frame_index < len(self.hatch_inspection_frames):
                inspection_sprite = self.hatch_inspection_frames[self.inspection_frame_index]
                # Scale to match protagonist size
                if self.character_display_scale != 1.0:
                    scaled_width = int(inspection_sprite.get_width() * self.character_display_scale)
                    scaled_height = int(inspection_sprite.get_height() * self.character_display_scale)
                    inspection_sprite = pygame.transform.scale(inspection_sprite, (scaled_width, scaled_height))
                screen.blit(inspection_sprite, (int(self.protagonist_x), int(self.protagonist_y)))
        else:
            # Show normal protagonist animation
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

        # Draw scene number
        scene_font = pygame.font.Font(None, 36)
        scene_text = scene_font.render("SCENE 3", True, (255, 255, 255))
        scene_rect = scene_text.get_rect()
        scene_rect.topright = (self.screen_width - 20, 20)

        # Draw scene background
        scene_bg_rect = scene_rect.inflate(10, 5)
        pygame.draw.rect(screen, (0, 0, 0, 180), scene_bg_rect)
        screen.blit(scene_text, scene_rect)

        # Optional: Draw a simple UI element showing location
        font = pygame.font.Font(None, 24)
        location_text = font.render("Behind the Maginot Line - SCENE 3", True, (255, 255, 255))
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
        pygame.draw.rect(screen, (255, 0, 0), return_collision_rect_red, 2)  # Red border
        if self.near_return_collision_box_red:
            # Fill with semi-transparent red when near
            pygame.draw.rect(screen, (255, 0, 0, 100), return_collision_rect_red)

        # Blue return collision box (left side) at (282, 604) - BLUE
        return_collision_rect_blue = pygame.Rect(self.return_collision_box_blue_x, self.return_collision_box_blue_y,
                                               self.return_collision_box_blue_width, self.return_collision_box_blue_height)
        pygame.draw.rect(screen, (0, 0, 255), return_collision_rect_blue, 2)  # Blue border
        if self.near_return_collision_box_blue:
            # Fill with semi-transparent blue when near
            pygame.draw.rect(screen, (0, 0, 255, 100), return_collision_rect_blue)

        # Dragonteeth collision box is invisible (collision only)

        # Draw bunker door hatch collision box - old iron rusty door with rounded edges
        self.draw_rusty_iron_hatch(screen)

        # Draw hatch inspection area hint when nearby
        if self.is_near_hatch() and not self.is_inspecting_hatch:
            hint_font = pygame.font.Font(None, 28)
            hint_text = hint_font.render("Press E to inspect hatch", True, (255, 255, 0))
            hint_rect = hint_text.get_rect()
            hint_rect.centerx = self.screen_width // 2
            hint_rect.centery = 150  # Above hatch area

            # Draw hint background
            hint_bg_rect = hint_rect.inflate(10, 5)
            pygame.draw.rect(screen, (0, 0, 0, 180), hint_bg_rect)
            screen.blit(hint_text, hint_rect)

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

        # Draw hatch interaction speech bubble
        if self.hatch_speech_bubble and self.hatch_speech_bubble.visible:
            self.hatch_speech_bubble.render(screen)

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