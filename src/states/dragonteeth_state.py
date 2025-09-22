"""
Simple Dragonteeth scene (Scene 4) - Just background and basic functionality
"""

import pygame
import os
import sys
from .game_state import GameState
from ..ui.quit_overlay import QuitOverlay
from ..effects.weather_system import WeatherSystem

# Add the project root to the path to import assets
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from assets.sprites.protagonist import create_protagonist_animation_system

class DragonteethState(GameState):
    def __init__(self, screen, audio_manager=None):
        import time
        print(f"[{time.time():.2f}] DragonteethState __init__ started")

        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        print(f"[{time.time():.2f}] Loading background...")
        # Load dragonteeth background
        self.background = self.load_dragonteeth_background()
        print(f"[{time.time():.2f}] Background loaded")

        # Create protagonist animation system (same as scene 3)
        self.protagonist_animation, self.using_sprite_sheet = create_protagonist_animation_system()

        # Smart scaling based on detected frame size (same as scene 3)
        current_frame = self.protagonist_animation.get_current_frame()
        if current_frame:
            frame_w, frame_h = current_frame.get_size()
            print(f"Detected frame size: {frame_w}x{frame_h}")

            # Smart scaling for large sprites (same logic as scene 3)
            if frame_w > 200 or frame_h > 200:
                print("Using 0.25x scale for very large sprites")
                self.character_display_scale = 0.25
            elif frame_w > 100 or frame_h > 100:
                print("Using 0.5x scale for large sprites")
                self.character_display_scale = 0.5
            else:
                print("Using 1.0x scale for normal-sized sprites")
                self.character_display_scale = 1.0
        else:
            print("Warning: No current frame available, using default scale")
            self.character_display_scale = 1.0

        # Set initial animation to face down
        self.protagonist_animation.play_animation('idle_down')

        # Scene 4 layout: divided into 3 equal horizontal parts
        self.scene_third_height = self.screen_height // 3
        self.lowest_third_top = 2 * self.scene_third_height  # Top of lowest third

        # Protagonist restricted to 30px left of center (was 50px right, now 80px left = -30px from center)
        self.protagonist_center_x = self.screen_width // 2 - 30  # 30px left of center
        self.protagonist_x = self.protagonist_center_x - 32  # Adjusted for sprite offset

        # Start point - 80px below the lowest third line
        self.start_position_y = self.lowest_third_top + 80  # 80px below lower limit line
        self.protagonist_y = self.start_position_y  # Start at this position

        # Movement restrictions - can move from scene 3 transition down to speech bubble
        self.min_y = self.lowest_third_top  # Center of lower third line (transition point)
        self.max_y = self.screen_height - 80  # Can reach bottom speech bubble area

        # Movement system - 20% slower in this scene
        self.character_speed = 120  # 150 * 0.8 = 120 (20% slower)
        self.last_facing_direction = 'down'

        # Dynamic scaling system based on vertical position in 80px range
        self.base_character_scale = self.character_display_scale  # Store original scale
        self.min_scale_factor = 0.3  # 70% smaller = 30% of original (at top - scene 3 transition)
        self.max_scale_factor = 1.0  # Same size as other scenes (at bottom - starting point)

        # Return collision box - positioned above new protagonist path
        self.return_collision_x = self.protagonist_center_x - 60  # Align with protagonist path
        self.return_collision_y = self.min_y - 40  # Just above the movement boundary
        self.return_collision_width = 120
        self.return_collision_height = 40
        self.near_return_collision = False

        # Bottom collision box for speech bubble
        self.bottom_collision_x = self.protagonist_center_x - 40  # Align with protagonist path
        self.bottom_collision_y = self.screen_height - 60  # Bottom area
        self.bottom_collision_width = 80
        self.bottom_collision_height = 40
        self.near_bottom_collision = False

        # Speech bubble system - manual control
        self.speech_active = False
        self.speech_text = "I should probably seek shelter from the storm"

        # Create weather system (same rain and thunder as other scenes)
        self.weather = WeatherSystem(self.screen_width, self.screen_height)

        # Customize puddle spawning for scene 4 - only in bottom 80%
        self.setup_scene4_puddles()

        # Quit overlay
        self.quit_overlay = QuitOverlay()

        # Transition system
        self.fade_in = True
        self.fade_timer = 0.0
        self.fade_duration = 0.1  # Very fast transition
        self.fade_alpha = 255

        # Fade-out transition system - slower for scene 3 return
        self.fade_out = False
        self.fade_out_timer = 0.0
        self.fade_out_duration = 1.0  # Slower transition back to scene 3
        self.next_scene = None

        # Transition delay system
        self.transition_delay = 0.0
        self.transition_delay_duration = 1.5  # 1.5 second delay before transition
        self.waiting_for_transition = False

        print("Dragonteeth scene ready")

    def load_dragonteeth_background(self):
        """Load dragonteeth.png background or create fallback"""
        import time
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            bg_path = os.path.join(project_root, "assets", "images", "backgrounds", "dragonteeth.png")
            print(f"[{time.time():.2f}] Checking for dragonteeth.png at: {bg_path}")

            if os.path.exists(bg_path):
                print(f"[{time.time():.2f}] Loading dragonteeth.png...")
                background = pygame.image.load(bg_path)
                print(f"[{time.time():.2f}] Scaling dragonteeth.png...")
                background = pygame.transform.scale(background, (self.screen_width, self.screen_height))
                print(f"[{time.time():.2f}] Dragonteeth.png loaded and scaled")
                return background
            else:
                print(f"[{time.time():.2f}] dragonteeth.png not found, creating fallback")
                return self.create_fallback_background()

        except Exception as e:
            print(f"[{time.time():.2f}] Error loading dragonteeth.png: {e}, creating fallback")
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

    def check_return_collision(self):
        """Check if protagonist hits the return collision box to go back to scene 3"""
        if self.fade_out:
            return

        # Get protagonist center with dynamic scaling
        current_frame = self.protagonist_animation.get_current_frame()
        if current_frame:
            current_scale = self.calculate_current_scale()
            sprite_width = int(current_frame.get_width() * current_scale)
            sprite_height = int(current_frame.get_height() * current_scale)
        else:
            sprite_width = 64
            sprite_height = 96

        protagonist_center_x = self.protagonist_x + sprite_width // 2
        protagonist_center_y = self.protagonist_y + sprite_height // 2

        # Check return collision box
        if (self.return_collision_x <= protagonist_center_x <= self.return_collision_x + self.return_collision_width and
            self.return_collision_y <= protagonist_center_y <= self.return_collision_y + self.return_collision_height):
            if not self.near_return_collision:
                print("Returning to scene 3")
                self.near_return_collision = True
                self.start_fade_transition("behind_bunker")
        else:
            self.near_return_collision = False

    def check_bottom_collision(self):
        """Check if protagonist hits the bottom collision box"""
        if self.fade_out:
            return

        # Get protagonist center with dynamic scaling
        current_frame = self.protagonist_animation.get_current_frame()
        if current_frame:
            current_scale = self.calculate_current_scale()
            sprite_width = int(current_frame.get_width() * current_scale)
            sprite_height = int(current_frame.get_height() * current_scale)
        else:
            sprite_width = 64
            sprite_height = 96

        protagonist_center_x = self.protagonist_x + sprite_width // 2
        protagonist_center_y = self.protagonist_y + sprite_height // 2

        # Check bottom collision box
        if (self.bottom_collision_x <= protagonist_center_x <= self.bottom_collision_x + self.bottom_collision_width and
            self.bottom_collision_y <= protagonist_center_y <= self.bottom_collision_y + self.bottom_collision_height):
            if not self.near_bottom_collision:
                print("Entered bottom area - showing speech bubble")
                self.near_bottom_collision = True
                self.speech_active = True
        else:
            self.near_bottom_collision = False

    def setup_scene4_puddles(self):
        """Setup puddles for scene 4 - only in bottom 80% of screen"""
        import random

        # Clear existing puddles
        self.weather.puddles = []

        # Calculate bottom 80% area
        puddle_start_y = self.screen_height * 0.2  # Start at 20% from top = bottom 80%
        puddle_end_y = self.screen_height - 30

        # Create initial puddles in bottom 80%
        initial_puddle_count = random.randint(8, 12)
        for _ in range(initial_puddle_count):
            x = random.uniform(100, self.screen_width - 100)
            y = random.uniform(puddle_start_y, puddle_end_y)
            max_size = random.uniform(20, 40)

            # Create puddle
            from ..effects.weather_system import Puddle
            puddle = Puddle(x, y, max_size)

            # Make initial puddles various sizes (some fully grown, some growing)
            growth_progress = random.uniform(0.3, 1.0)
            puddle.size = puddle.max_size * growth_progress

            self.weather.puddles.append(puddle)

        # Override the weather system's puddle spawning method for scene 4
        original_spawn_puddle = self.weather.spawn_puddle
        def scene4_spawn_puddle():
            x = random.uniform(100, self.screen_width - 100)
            y = random.uniform(puddle_start_y, puddle_end_y)  # Bottom 80% only
            max_size = random.uniform(15, 35)
            return Puddle(x, y, max_size)

        self.weather.spawn_puddle = scene4_spawn_puddle

        # Override the try_add_to_puddle method to restrict to bottom 80%
        original_try_add_to_puddle = self.weather.try_add_to_puddle
        def scene4_try_add_to_puddle(x, y):
            # Only allow puddle creation in bottom 80%
            if y >= puddle_start_y:
                original_try_add_to_puddle(x, y)

        self.weather.try_add_to_puddle = scene4_try_add_to_puddle

    def calculate_current_scale(self):
        """Calculate protagonist scale based on vertical position"""
        # Calculate position ratio from top to bottom of movement area
        movement_range = self.max_y - self.min_y  # Total vertical movement range
        current_offset = self.protagonist_y - self.min_y  # How far down from top

        if movement_range <= 0:
            return self.base_character_scale * self.min_scale_factor

        # Position ratio: 0.0 at top, 1.0 at bottom
        position_ratio = max(0.0, min(1.0, current_offset / movement_range))

        # Scale factor: min_scale_factor at top, max_scale_factor at bottom
        scale_factor = self.min_scale_factor + (self.max_scale_factor - self.min_scale_factor) * position_ratio

        return self.base_character_scale * scale_factor

    def render_speech_bubble(self, screen):
        """Render speech bubble above protagonist"""
        # Create font for speech text
        font = pygame.font.Font(None, 24)

        # Prepare text (split into multiple lines if needed)
        words = self.speech_text.split()
        lines = []
        current_line = ""
        max_width = 300

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())

        # Calculate bubble dimensions
        line_height = font.get_height()
        bubble_width = max(font.size(line)[0] for line in lines) + 20
        bubble_height = len(lines) * line_height + 20

        # Position bubble above protagonist
        bubble_x = self.protagonist_x + 32 - bubble_width // 2  # Center on protagonist
        bubble_y = self.protagonist_y - bubble_height - 20  # Above protagonist

        # Draw rounded bubble background
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)
        radius = 15  # Rounded corner radius

        # Create a surface for the rounded rectangle
        bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
        pygame.draw.rect(bubble_surface, (255, 255, 255), (0, 0, bubble_width, bubble_height), border_radius=radius)
        pygame.draw.rect(bubble_surface, (0, 0, 0), (0, 0, bubble_width, bubble_height), 3, border_radius=radius)

        # Blit the rounded bubble
        screen.blit(bubble_surface, (bubble_x, bubble_y))

        # Draw bubble pointer (small triangle)
        pointer_points = [
            (bubble_x + bubble_width // 2, bubble_y + bubble_height),
            (bubble_x + bubble_width // 2 - 10, bubble_y + bubble_height + 15),
            (bubble_x + bubble_width // 2 + 10, bubble_y + bubble_height + 15)
        ]
        pygame.draw.polygon(screen, (255, 255, 255), pointer_points)
        pygame.draw.polygon(screen, (0, 0, 0), pointer_points, 3)

        # Draw text lines
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, (0, 0, 0))
            text_x = bubble_x + 10
            text_y = bubble_y + 10 + i * line_height
            screen.blit(text_surface, (text_x, text_y))

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
        """Handle movement - restricted to up/down only in center column"""
        keys = pygame.key.get_pressed()

        movement_direction = None
        self.is_moving = False

        # Allow up/down movement between limits
        if keys[pygame.K_UP]:
            # Close speech bubble when up arrow is pressed
            if self.speech_active:
                self.speech_active = False
                print("Speech bubble closed by up arrow")

            new_y = self.protagonist_y - self.character_speed * dt
            # Check if reaching the center of lower third line (transition point)
            if new_y <= self.min_y:
                if not self.waiting_for_transition:
                    print("Reached center of lower third line - starting transition delay")
                    self.waiting_for_transition = True
                    self.transition_delay = 0.0
                # Stop movement at the boundary
                self.protagonist_y = self.min_y
            else:
                self.protagonist_y = new_y
                self.last_facing_direction = 'up'
                movement_direction = 'up'
                self.is_moving = True

        elif keys[pygame.K_DOWN]:
            # Cancel transition delay if moving back down
            if self.waiting_for_transition:
                print("Transition cancelled - moving back down")
                self.waiting_for_transition = False
                self.transition_delay = 0.0

            new_y = self.protagonist_y + self.character_speed * dt
            # Keep within bottom boundary
            if new_y <= self.max_y:
                self.protagonist_y = new_y
                self.last_facing_direction = 'down'
                movement_direction = 'down'
                self.is_moving = True

        # X position is locked - no left/right movement allowed
        self.protagonist_x = self.protagonist_center_x - 32

        # Handle animation based on movement
        if self.is_moving and movement_direction:
            # Play directional walking animation (only up/down)
            self.protagonist_animation.play_animation(f'walk_{movement_direction}')
        else:
            # Play idle animation in the last facing direction
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

        # Handle transition delay
        if self.waiting_for_transition:
            self.transition_delay += dt
            if self.transition_delay >= self.transition_delay_duration:
                print("Transition delay complete - starting fade to scene 3")
                self.start_fade_transition("behind_bunker")
                self.waiting_for_transition = False

        # Handle movement
        self.handle_movement(dt)

        # Check collisions
        self.check_return_collision()
        self.check_bottom_collision()

        # Update weather system
        self.weather.update(dt)

        # Update animation system
        self.protagonist_animation.update(dt)

        return None

    def render(self, screen):
        import time
        render_start = time.time()

        # Draw background
        screen.blit(self.background, (0, 0))

        # Draw protagonist with dynamic scaling
        protagonist_sprite = self.protagonist_animation.get_current_frame()
        if protagonist_sprite:
            # Use dynamic scale based on position
            current_scale = self.calculate_current_scale()
            scaled_width = int(protagonist_sprite.get_width() * current_scale)
            scaled_height = int(protagonist_sprite.get_height() * current_scale)
            scaled_sprite = pygame.transform.scale(protagonist_sprite, (scaled_width, scaled_height))
            screen.blit(scaled_sprite, (self.protagonist_x, self.protagonist_y))

        # Draw weather effects (rain and lightning over everything)
        self.weather.draw(screen)

        # Draw speech bubble if active
        if self.speech_active:
            self.render_speech_bubble(screen)

        # Draw quit overlay
        if self.quit_overlay.is_visible():
            self.quit_overlay.render(screen)

        # Draw fade transition
        if self.fade_in or self.fade_out:
            fade_surface = pygame.Surface((self.screen_width, self.screen_height))
            fade_surface.set_alpha(self.fade_alpha)
            fade_surface.fill((0, 0, 0))
            screen.blit(fade_surface, (0, 0))

        render_time = time.time() - render_start
        if render_time > 0.01:  # Only log if render takes more than 10ms
            print(f"[{time.time():.2f}] Dragonteeth render took {render_time:.3f}s")