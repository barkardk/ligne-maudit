import pygame
import sys
import os
from .game_state import GameState
from ..audio.audio_manager import AudioManager
from ..effects.weather_system import WeatherSystem

# Add the project root to the path to import assets
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from assets.sprites.protagonist import create_protagonist_animation_system
from assets.backgrounds.collision_map import CollisionMap

class IntroState(GameState):
    def __init__(self, screen, audio_manager=None):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Exit collision box - middle center (define early for background creation)
        self.exit_x = (self.screen_width // 2) - 10  # Center horizontally
        self.exit_y = (self.screen_height // 2) - 10  # Middle of screen
        self.exit_width = 20
        self.exit_height = 20

        # Load forest path background
        self.background = self.load_background()

        # Create collision map for path restrictions
        self.collision_map = self.create_forest_path_collision_map()

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

        # Store base scale for perspective calculations
        self.base_character_scale = self.character_display_scale

        # Set initial animation to face up (towards exit)
        self.protagonist_animation.play_animation('idle_up')

        # Protagonist position - very bottom of screen, ready to walk up
        self.protagonist_x = self.screen_width // 2 - 32  # Center horizontally
        self.protagonist_y = self.screen_height - 100  # Very bottom of screen

        # Movement
        self.move_speed = 100  # pixels per second
        self.is_moving = False
        self.last_facing_direction = 'up'  # Start facing up (towards exit)


        # Story text system
        self.story_text = [
            "Elvira runs through the dark forest, her heart pounding.",
            "",
            "Behind her, the sounds of pursuit grow fainter, but she",
            "cannot slow down. Not yet.",
            "",
            "The Directorate has taken everything from her - her home,",
            "her freedom, and worst of all, her beloved.",
            "",
            "Marcus is imprisoned in their fortress, awaiting a fate",
            "she dare not imagine.",
            "",
            "She must find a way to rescue him, but first she needs",
            "shelter from the storm.",
            "",
            "Ahead, through the rain, she glimpses the outline of an",
            "old fortification - the Maginot Line.",
            "",
            "Perhaps there she can find refuge... and plan her next move.",
            "",
            "Movement unlocked - Walk north to reach the Maginot Line."
        ]

        # Auto-scrolling story system
        self.text_scroll = 0  # Current scroll position
        self.max_scroll = max(0, len(self.story_text) - 8)  # Max lines that can be scrolled
        self.text_font = pygame.font.Font(None, 28)
        self.text_visible = True

        # Auto-scroll timing
        self.auto_scroll_timer = 0.0
        self.auto_scroll_delay = 3.0  # 3 seconds per section
        self.story_finished = False
        self.movement_locked = True  # Lock movement until story finishes
        self.transitioning = False  # Prevent repeated transitions

        # Fade transition system
        self.fade_transition = False
        self.fade_timer = 0.0
        self.fade_duration = 1.0  # 1 second fade
        self.fade_alpha = 0  # Current fade alpha (0 = no fade, 255 = full black)

        # Use shared audio manager or create new one
        if audio_manager:
            self.audio = audio_manager
        else:
            self.audio = AudioManager()
            self.audio.load_ambient_pack()

        # Start ambient sound and music only if not muted
        if not self.audio.is_muted_state():
            self.audio.play_ambient("forest_rain", loop=True, fade_in_ms=3000)
            self.audio.play_music("forest_rain_music", loop=True, fade_in_ms=3000)

        # Create weather system
        self.weather = WeatherSystem(self.screen_width, self.screen_height)

        print("Intro state initialized - Walk north to reach the Maginot Line!")
        print(f"Exit area at: ({self.exit_x}, {self.exit_y}) - {self.exit_width}x{self.exit_height}")

    def load_background(self):
        """Load forest_path background or create fallback"""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            bg_path = os.path.join(project_root, "assets", "images", "backgrounds", "forest_path.png")

            if os.path.exists(bg_path):
                background = pygame.image.load(bg_path)
                background = pygame.transform.scale(background, (self.screen_width, self.screen_height))
                print(f"Loaded forest path background from: {bg_path}")
                return background
            else:
                print(f"forest_path.png not found at {bg_path}, creating fallback")
                return self.create_fallback_background()

        except Exception as e:
            print(f"Error loading forest path background: {e}")
            return self.create_fallback_background()

    def create_fallback_background(self):
        """Create a fallback forest path background"""
        background = pygame.Surface((self.screen_width, self.screen_height))

        # Dark forest background
        background.fill((20, 30, 20))

        # Draw forest path
        path_width = 150
        path_x = (self.screen_width - path_width) // 2

        # Path gets wider towards bottom (perspective)
        for y in range(0, self.screen_height, 5):
            progress = y / self.screen_height
            current_width = int(path_width * (0.5 + progress * 0.5))
            current_x = (self.screen_width - current_width) // 2

            path_color = (60 + int(20 * progress), 50 + int(15 * progress), 30 + int(10 * progress))
            pygame.draw.rect(background, path_color, (current_x, y, current_width, 5))

        # Draw some trees on the sides
        tree_color = (15, 25, 15)
        for i in range(20):
            # Left side trees
            tree_x = 20 + (i % 5) * 40
            tree_y = 50 + i * 35
            tree_width = 30 + (i % 3) * 10
            tree_height = 40 + (i % 4) * 20
            pygame.draw.rect(background, tree_color, (tree_x, tree_y, tree_width, tree_height))

            # Right side trees
            tree_x = self.screen_width - 80 - (i % 5) * 40
            pygame.draw.rect(background, tree_color, (tree_x, tree_y, tree_width, tree_height))

        # Draw exit area indicator in middle (subtle)
        exit_rect = pygame.Rect(self.exit_x, self.exit_y, self.exit_width, self.exit_height)
        pygame.draw.rect(background, (40, 60, 40), exit_rect)

        return background

    def create_forest_path_collision_map(self):
        """Create collision map to restrict movement to the middle path"""
        collision_map = CollisionMap(self.screen_width, self.screen_height)

        # Calculate path dimensions - path in the middle third of the lower half
        # Split screen in half, then split lower half in three parts
        lower_half_start = self.screen_height // 2
        lower_third_width = self.screen_width // 3

        # Path is in the middle third of the lower half
        path_left = lower_third_width
        path_right = 2 * lower_third_width
        path_top = lower_half_start
        path_bottom = self.screen_height

        # Create collision blocks for left and right sides of lower half
        # Left side - from left edge to path start
        collision_map.add_collision_rect(0, path_top, path_left, path_bottom - path_top)

        # Right side - from path end to right edge
        collision_map.add_collision_rect(path_right, path_top, self.screen_width - path_right, path_bottom - path_top)

        # Upper half - entire area above the middle line
        collision_map.add_collision_rect(0, 0, self.screen_width, lower_half_start)

        print(f"Forest path collision created:")
        print(f"  Path area: x={path_left}-{path_right}, y={path_top}-{path_bottom}")
        print(f"  Left block: (0, {path_top}, {path_left}, {path_bottom - path_top})")
        print(f"  Right block: ({path_right}, {path_top}, {self.screen_width - path_right}, {path_bottom - path_top})")
        print(f"  Upper block: (0, 0, {self.screen_width}, {lower_half_start})")

        return collision_map

    def calculate_perspective_scale(self):
        """Calculate perspective scaling based on protagonist position"""
        # Get position relative to screen
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Calculate distance from bottom of screen (0.0 = bottom, 1.0 = center)
        # As she moves up (toward center), she should get smaller (going away)
        # As she moves down (toward bottom), she should get larger (coming closer)
        y_progress = (self.screen_height - self.protagonist_y) / (self.screen_height / 2)
        y_progress = max(0.0, min(1.0, y_progress))  # Clamp between 0 and 1

        # Scale from 1.0 (full size at bottom) to 0.6 (60% size at center)
        perspective_multiplier = 1.0 - (y_progress * 0.4)  # Goes from 1.0 to 0.6

        # Apply perspective to base scale
        self.character_display_scale = self.base_character_scale * perspective_multiplier

        # Debug info
        if hasattr(self, 'debug_counter'):
            self.debug_counter += 1
            if self.debug_counter % 60 == 0:  # Print every second at 60fps
                print(f"Y: {self.protagonist_y}, Progress: {y_progress:.2f}, Scale: {perspective_multiplier:.2f}")
        else:
            self.debug_counter = 0

    def check_exit_collision(self):
        """Check if protagonist reached the exit area"""
        # Get protagonist bounds
        current_frame = self.protagonist_animation.get_current_frame()
        if current_frame:
            sprite_width = int(current_frame.get_width() * self.character_display_scale)
            sprite_height = int(current_frame.get_height() * self.character_display_scale)
        else:
            sprite_width = 64
            sprite_height = 96

        protagonist_rect = pygame.Rect(self.protagonist_x, self.protagonist_y, sprite_width, sprite_height)
        exit_rect = pygame.Rect(self.exit_x, self.exit_y, self.exit_width, self.exit_height)

        return protagonist_rect.colliderect(exit_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Skip intro and go to main scene
                return "field"
            elif event.key == pygame.K_h:
                # Toggle text visibility
                self.text_visible = not self.text_visible
            elif event.key == pygame.K_SPACE:
                # Toggle audio mute
                self.audio.toggle_mute()
            elif event.key == pygame.K_RETURN:
                # Hide text completely and unlock movement
                self.text_visible = False
                self.story_finished = True
                self.movement_locked = False
                print("Text hidden - Movement unlocked!")
            elif event.key == pygame.K_c:
                # Toggle collision debug mode
                self.collision_map.toggle_debug()

        return None

    def update(self, dt):
        # Handle auto-scrolling story
        if not self.story_finished:
            self.auto_scroll_timer += dt
            if self.auto_scroll_timer >= self.auto_scroll_delay:
                self.auto_scroll_timer = 0.0
                if self.text_scroll < self.max_scroll:
                    self.text_scroll += 1
                else:
                    # Story finished scrolling
                    self.story_finished = True
                    self.movement_locked = False
                    print("Story finished - Movement unlocked!")

        # Handle movement only if not locked
        keys = pygame.key.get_pressed()
        self.is_moving = False

        if not self.movement_locked:
            # Calculate perspective scaling based on current position
            self.calculate_perspective_scale()

            # Handle movement
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

            # Get the actual frame size for bounds checking
            current_frame = self.protagonist_animation.get_current_frame()
            if current_frame:
                sprite_width = int(current_frame.get_width() * self.character_display_scale)
                sprite_height = int(current_frame.get_height() * self.character_display_scale)
            else:
                sprite_width = 64
                sprite_height = 96

            # Keep protagonist on screen
            new_x = max(0, min(self.screen_width - sprite_width, new_x))
            new_y = max(0, min(self.screen_height - sprite_height, new_y))

            # Check collision and get valid position
            self.protagonist_x, self.protagonist_y = self.collision_map.get_valid_position(
                old_x, old_y, new_x, new_y, sprite_width, sprite_height
            )

            # Handle animation based on movement
            if self.is_moving and movement_direction:
                # Play directional walking animation
                self.protagonist_animation.play_animation(f'walk_{movement_direction}')
                # Remember the last facing direction
                self.last_facing_direction = movement_direction
            else:
                # Play idle animation in the last facing direction
                self.protagonist_animation.play_animation(f'idle_{self.last_facing_direction}')

            # Check if protagonist reached the exit
            if self.check_exit_collision() and not self.transitioning and not self.fade_transition:
                print("Exit collision detected - starting fade transition to Maginot Line!")
                self.transitioning = True
                self.fade_transition = True
                self.fade_timer = 0.0
        else:
            # Movement locked - calculate perspective and play idle animation
            self.calculate_perspective_scale()
            self.protagonist_animation.play_animation(f'idle_{self.last_facing_direction}')

        # Update animation system
        self.protagonist_animation.update(dt)

        # Update weather system
        self.weather.update(dt)

        # Handle fade transition
        if self.fade_transition:
            self.fade_timer += dt
            # Calculate fade alpha (fade to black first, then complete transition)
            if self.fade_timer <= self.fade_duration:
                # Fade to black (0 to 255)
                progress = self.fade_timer / self.fade_duration
                self.fade_alpha = int(255 * progress)
            else:
                # Fade complete - transition to next scene
                print("Fade transition complete - switching to Maginot Line!")
                return "field"

        return None

    def render(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))

        # Draw protagonist (scaled down for display)
        protagonist_sprite = self.protagonist_animation.get_current_frame()
        if protagonist_sprite:
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

        # Draw story text if visible
        if self.text_visible:
            # Create semi-transparent overlay covering the full screen
            text_overlay = pygame.Surface((self.screen_width, self.screen_height))
            text_overlay.set_alpha(180)
            text_overlay.fill((0, 0, 0))
            screen.blit(text_overlay, (0, 0))

            # Calculate text area in center of screen
            text_area_width = self.screen_width - 100  # 50px margin on each side
            text_area_height = self.screen_height - 200  # 100px margin top and bottom
            text_start_x = 50
            text_start_y = 100

            # Draw scrollable text
            y_offset = text_start_y
            line_height = 35
            max_lines = min(len(self.story_text), (text_area_height // line_height))

            for i in range(self.text_scroll, min(len(self.story_text), self.text_scroll + max_lines)):
                if y_offset + line_height > text_start_y + text_area_height:
                    break

                line = self.story_text[i]
                if line:  # Skip empty lines for rendering, but count them for spacing
                    text_surface = self.text_font.render(line, True, (255, 255, 255))
                    screen.blit(text_surface, (text_start_x, y_offset))
                y_offset += line_height

            # Draw scroll indicator at bottom center
            if len(self.story_text) > max_lines:
                scroll_info = f"({self.text_scroll + 1}-{min(self.text_scroll + max_lines, len(self.story_text))} of {len(self.story_text)})"
                scroll_text = pygame.font.Font(None, 24).render(scroll_info, True, (150, 150, 150))
                scroll_rect = scroll_text.get_rect()
                scroll_rect.centerx = self.screen_width // 2
                scroll_rect.y = self.screen_height - 40
                screen.blit(scroll_text, scroll_rect)

        # Draw instructions
        if self.movement_locked:
            if self.text_visible:
                instructions = "Story auto-scrolling... • ENTER Skip story • SPACE Toggle audio • H Hide text • C Debug"
            else:
                instructions = "Story playing... • ENTER Skip story • SPACE Toggle audio • H Show text • C Debug"
        else:
            if self.text_visible:
                instructions = "Walk north to Maginot Line • SPACE Toggle audio • H Hide text • C Debug • ESC Skip"
            else:
                instructions = "Walk north to Maginot Line • SPACE Toggle audio • H Show story • C Debug • ESC Skip"

        instruction_font = pygame.font.Font(None, 24)
        instruction_text = instruction_font.render(instructions, True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect()
        instruction_rect.center = (self.screen_width // 2, 30)

        # Draw instruction background
        bg_rect = instruction_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
        screen.blit(instruction_text, instruction_rect)

        # Draw fade overlay if transitioning
        if self.fade_transition and self.fade_alpha > 0:
            fade_surface = pygame.Surface((self.screen_width, self.screen_height))
            fade_surface.set_alpha(self.fade_alpha)
            fade_surface.fill((0, 0, 0))  # Black fade
            screen.blit(fade_surface, (0, 0))

    def cleanup(self):
        """Clean up resources when intro state is destroyed"""
        # Don't cleanup shared audio manager - it's managed by the game instance
        pass