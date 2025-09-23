import pygame
import sys
import os
import random
import math
from .game_state import GameState
from ..audio.audio_manager import AudioManager
from ..ui.quit_overlay import QuitOverlay

class Scene0State(GameState):
    def __init__(self, screen, audio_manager=None):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Load bunker background from scene0 folder
        self.background = self.load_bunker_background()

        # Story text system - moved from IntroState
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
            "Press ENTER to continue..."
        ]

        # Auto-scrolling story system
        self.text_scroll = 0.0  # Current scroll position (float for smooth scrolling)
        self.scroll_speed = 20.0  # Pixels per second scroll speed
        self.line_height = 32
        self.visible_lines = 12  # Number of lines visible at once
        self.max_scroll = max(0, len(self.story_text) * self.line_height - (self.visible_lines * self.line_height))

        # Load font
        try:
            font_candidates = [
                'Times New Roman',  # Classic serif
                'Georgia',         # Web-safe serif
                'Garamond',        # Classic book font
                'Book Antiqua',    # Victorian-style
                'Palatino',        # Elegant serif
            ]
            self.text_font = None
            for font_name in font_candidates:
                try:
                    self.text_font = pygame.font.SysFont(font_name, 22)
                    print(f"Using font: {font_name}")
                    break
                except:
                    continue

            if self.text_font is None:
                self.text_font = pygame.font.Font(None, 22)
                print("Using default pygame font")

        except:
            self.text_font = pygame.font.Font(None, 22)

        self.text_visible = True

        # Auto-scroll timing
        self.auto_scroll_timer = 0.0
        self.auto_scroll_delay = 2.0  # 2 second delay before starting scroll
        self.story_finished = False

        # Fade transition system
        self.fade_transition = False
        self.fade_timer = 0.0
        self.fade_duration = 1.0
        self.fade_alpha = 0

        # Text fade-out system
        self.text_fade_out = False
        self.text_fade_timer = 0.0
        self.text_fade_duration = 2.0
        self.text_alpha = 255

        # Birds flying animation
        self.birds = []
        self.setup_birds()

        # Wind and sunshine effects
        self.wind_particles = []
        self.setup_wind_particles()
        self.sun_position = (self.screen_width - 150, 100)
        self.sun_rays = []
        self.setup_sun_rays()

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

        # Quit overlay
        self.quit_overlay = QuitOverlay()

        print("Scene 0 initialized - Story intro with bunker background")

    def load_bunker_background(self):
        """Load bunker.png from scene0 folder or create fallback"""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            bg_path = os.path.join(project_root, "assets", "images", "backgrounds", "scene0", "bunker.png")

            if os.path.exists(bg_path):
                background = pygame.image.load(bg_path)
                background = pygame.transform.scale(background, (self.screen_width, self.screen_height))
                print(f"Loaded bunker background from: {bg_path}")
                return background
            else:
                print(f"bunker.png not found at {bg_path}, creating fallback")
                return self.create_fallback_background()

        except Exception as e:
            print(f"Error loading bunker background: {e}")
            return self.create_fallback_background()

    def create_fallback_background(self):
        """Create a fallback bunker background"""
        background = pygame.Surface((self.screen_width, self.screen_height))

        # Sky gradient (light blue to darker blue)
        for y in range(self.screen_height // 2):
            progress = y / (self.screen_height // 2)
            color_r = int(135 + (70 * progress))  # Light blue to darker
            color_g = int(206 + (80 * progress))
            color_b = int(235 + (20 * progress))
            pygame.draw.line(background, (color_r, color_g, color_b), (0, y), (self.screen_width, y))

        # Ground
        ground_color = (90, 80, 60)
        ground_rect = pygame.Rect(0, self.screen_height // 2, self.screen_width, self.screen_height // 2)
        pygame.draw.rect(background, ground_color, ground_rect)

        # Simple bunker outline
        bunker_width = 400
        bunker_height = 200
        bunker_x = (self.screen_width - bunker_width) // 2
        bunker_y = self.screen_height // 2 - 50
        pygame.draw.rect(background, (80, 70, 60), (bunker_x, bunker_y, bunker_width, bunker_height))

        return background

    def setup_birds(self):
        """Setup flying birds"""
        for i in range(2):  # 2 birds as requested
            bird = {
                'x': random.randint(-100, self.screen_width + 100),
                'y': random.randint(50, 200),
                'speed_x': random.uniform(30, 60),
                'speed_y': random.uniform(-10, 10),
                'wing_phase': random.uniform(0, 2 * math.pi),
                'wing_speed': random.uniform(8, 12)
            }
            self.birds.append(bird)

    def setup_wind_particles(self):
        """Setup wind particles for atmospheric effect"""
        for i in range(20):
            particle = {
                'x': random.randint(0, self.screen_width),
                'y': random.randint(0, self.screen_height // 2),
                'speed_x': random.uniform(20, 40),
                'speed_y': random.uniform(-5, 5),
                'alpha': random.randint(30, 80),
                'size': random.randint(1, 3)
            }
            self.wind_particles.append(particle)

    def setup_sun_rays(self):
        """Setup sun rays for sunshine effect"""
        for i in range(8):
            angle = i * (2 * math.pi / 8)
            ray = {
                'angle': angle,
                'length': random.randint(80, 120),
                'alpha': random.randint(40, 80)
            }
            self.sun_rays.append(ray)

    def update_birds(self, dt):
        """Update bird positions and animation"""
        for bird in self.birds:
            bird['x'] += bird['speed_x'] * dt
            bird['y'] += bird['speed_y'] * dt
            bird['wing_phase'] += bird['wing_speed'] * dt

            # Reset bird if it flies off screen
            if bird['x'] > self.screen_width + 100:
                bird['x'] = -100
                bird['y'] = random.randint(50, 200)

    def update_wind_particles(self, dt):
        """Update wind particle positions"""
        for particle in self.wind_particles:
            particle['x'] += particle['speed_x'] * dt
            particle['y'] += particle['speed_y'] * dt

            # Reset particle if it goes off screen
            if particle['x'] > self.screen_width:
                particle['x'] = -10
                particle['y'] = random.randint(0, self.screen_height // 2)

    def draw_bird(self, screen, bird):
        """Draw a simple animated bird"""
        x, y = int(bird['x']), int(bird['y'])
        wing_offset = int(math.sin(bird['wing_phase']) * 5)

        # Bird body (simple oval)
        pygame.draw.ellipse(screen, (40, 40, 40), (x - 3, y - 2, 6, 4))

        # Wings (simple lines that flap)
        pygame.draw.line(screen, (40, 40, 40), (x - 8, y + wing_offset), (x + 8, y - wing_offset), 2)

    def draw_wind_particles(self, screen):
        """Draw wind particles"""
        for particle in self.wind_particles:
            x, y = int(particle['x']), int(particle['y'])
            size = particle['size']
            alpha = particle['alpha']

            # Create a small surface for the particle with alpha
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color = (200, 200, 255, alpha)  # Light blue-white
            pygame.draw.circle(particle_surface, color, (size, size), size)
            screen.blit(particle_surface, (x - size, y - size))

    def draw_sun_and_rays(self, screen):
        """Draw sun with rays"""
        sun_x, sun_y = self.sun_position

        # Draw sun rays
        for ray in self.sun_rays:
            end_x = sun_x + math.cos(ray['angle']) * ray['length']
            end_y = sun_y + math.sin(ray['angle']) * ray['length']

            # Create surface for ray with alpha
            ray_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            color = (255, 255, 200, ray['alpha'])
            pygame.draw.line(ray_surface, color, (sun_x, sun_y), (end_x, end_y), 3)
            screen.blit(ray_surface, (0, 0))

        # Draw sun
        pygame.draw.circle(screen, (255, 255, 150), (sun_x, sun_y), 25)
        pygame.draw.circle(screen, (255, 255, 200), (sun_x, sun_y), 20)

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
            elif event.key == pygame.K_SPACE:
                self.audio.toggle_mute()
            elif event.key == pygame.K_RETURN:
                # Skip to scene 1 (intro with protagonist)
                print("Skipping to Scene 1...")
                self.fade_transition = True
                self.fade_timer = 0.0

        return None

    def update(self, dt):
        # Don't update game logic if quit overlay is visible
        if self.quit_overlay.is_visible():
            return

        # Handle auto-scrolling story
        if not self.story_finished:
            self.auto_scroll_timer += dt
            if self.auto_scroll_timer >= self.auto_scroll_delay:
                # Start smooth scrolling
                if self.text_scroll < self.max_scroll:
                    self.text_scroll += self.scroll_speed * dt
                    if self.text_scroll >= self.max_scroll:
                        self.text_scroll = self.max_scroll
                        # Story finished scrolling - start fade out
                        if not self.text_fade_out:
                            self.text_fade_out = True
                            self.text_fade_timer = 0.0
                            print("Story finished scrolling - starting fade out...")

        # Handle text fade-out
        if self.text_fade_out and not self.story_finished:
            self.text_fade_timer += dt
            if self.text_fade_timer <= self.text_fade_duration:
                # Fade text from visible to invisible
                progress = self.text_fade_timer / self.text_fade_duration
                self.text_alpha = int(255 * (1.0 - progress))
            else:
                # Fade complete - transition to scene 1
                self.text_alpha = 0
                self.text_visible = False
                self.story_finished = True
                print("Text fade complete - transitioning to Scene 1...")
                self.fade_transition = True
                self.fade_timer = 0.0

        # Update atmospheric effects
        self.update_birds(dt)
        self.update_wind_particles(dt)

        # Handle fade transition
        if self.fade_transition:
            self.fade_timer += dt
            if self.fade_timer <= self.fade_duration:
                # Fade to black
                progress = self.fade_timer / self.fade_duration
                self.fade_alpha = int(255 * progress)
            else:
                # Fade complete - transition to scene 1
                print("Fade transition complete - switching to Scene 1!")
                return "intro"

        return None

    def render(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))

        # Draw atmospheric effects behind text
        self.draw_sun_and_rays(screen)
        self.draw_wind_particles(screen)

        # Draw birds
        for bird in self.birds:
            self.draw_bird(screen, bird)

        # Draw story text if visible
        if self.text_visible:
            # Calculate text area in center of screen
            text_area_width = self.screen_width - 100
            text_area_height = self.visible_lines * self.line_height
            text_start_x = 50
            text_start_y = (self.screen_height - text_area_height) // 2

            # Create a clipping area for smooth scrolling
            clip_rect = pygame.Rect(text_start_x - 10, text_start_y, text_area_width + 20, text_area_height)

            # Save the current clipping area
            original_clip = screen.get_clip()
            screen.set_clip(clip_rect)

            # Draw all text lines with smooth pixel-level scrolling
            for i, line in enumerate(self.story_text):
                line_y = text_start_y + (i * self.line_height) - self.text_scroll

                # Only render lines that are visible
                if line_y > text_start_y + text_area_height + self.line_height:
                    break
                if line_y < text_start_y - self.line_height:
                    continue

                if line:  # Skip empty lines for rendering
                    # Add text shadow for better readability
                    shadow_surface = self.text_font.render(line, True, (0, 0, 0))
                    shadow_surface.set_alpha(self.text_alpha)
                    screen.blit(shadow_surface, (text_start_x + 2, line_y + 2))

                    # Main text
                    text_surface = self.text_font.render(line, True, (240, 230, 210))
                    text_surface.set_alpha(self.text_alpha)
                    screen.blit(text_surface, (text_start_x, line_y))

            # Restore clipping
            screen.set_clip(original_clip)

        # Draw scene number and instructions
        scene_font = pygame.font.Font(None, 36)
        scene_text = scene_font.render("SCENE 0", True, (255, 255, 255))
        scene_rect = scene_text.get_rect()
        scene_rect.topright = (self.screen_width - 20, 20)

        # Draw scene background
        scene_bg_rect = scene_rect.inflate(10, 5)
        pygame.draw.rect(screen, (0, 0, 0, 180), scene_bg_rect)
        screen.blit(scene_text, scene_rect)

        instructions = "Story scrolling... • ENTER Skip to game • SPACE Toggle audio • ESC Quit"
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
            fade_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            fade_color = (0, 0, 0, self.fade_alpha)
            fade_surface.fill(fade_color)
            screen.blit(fade_surface, (0, 0))

        # Draw quit overlay on top of everything
        self.quit_overlay.render(screen)

    def cleanup(self):
        """Clean up resources when scene 0 state is destroyed"""
        pass