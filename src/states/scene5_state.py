import pygame
import sys
import os
from .game_state import GameState
from ..ui.quit_overlay import QuitOverlay
from ..audio.audio_manager import AudioManager

# Add the project root to the path to import assets
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from assets.sprites.protagonist import create_protagonist_animation_system
from assets.backgrounds.collision_map import CollisionMap

class Scene5State(GameState):
    def __init__(self, screen, audio_manager=None):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Load bunker room background
        self.background = self.load_bunker_room_background()

        # Add puddle to the background
        self.add_puddle_to_background()

        # Create basic collision map
        self.collision_map = CollisionMap(self.screen_width, self.screen_height)

        # Create protagonist animation system
        self.protagonist_animation, self.using_sprite_sheet = create_protagonist_animation_system()

        # Smart scaling based on detected frame size (same logic as other scenes)
        current_frame = self.protagonist_animation.get_current_frame()
        if current_frame:
            frame_w, frame_h = current_frame.get_size()
            print(f"Detected frame size: {frame_w}x{frame_h}")

            # Auto-adjust scaling based on frame size
            if frame_w <= 48 and frame_h <= 64:
                self.character_display_scale = 1.5
                print("Using 1.5x scale for processed sprites")
            elif frame_w <= 96 and frame_h <= 128:
                self.character_display_scale = 1.0
                print("Using 1.0x scale for medium sprites")
            elif frame_w <= 160 and frame_h <= 240:
                self.character_display_scale = 0.7
                print("Using 0.7x scale for large sprites")
            elif frame_w == 256 and frame_h == 320:
                self.character_display_scale = 0.25
                print("Using 0.25x scale for 256x320 sprites")
            else:
                self.character_display_scale = 0.25
                print("Using 0.25x scale for very large sprites")
        else:
            self.character_display_scale = 1.0

        # Falling animation system
        self.is_falling = True
        self.fall_speed = 346  # pixels per second (20% slower: 432 * 0.8)
        self.landing_y = self.screen_height - (self.screen_height * 0.15) + 20  # 15% from bottom, moved down 20px

        # Start falling from top center
        self.protagonist_x = self.screen_width // 2 - 32  # Center horizontally
        self.protagonist_y = -100  # Start above screen

        # Target landing position
        self.target_x = self.screen_width // 2 - 32
        self.target_y = self.landing_y

        # Movement
        self.move_speed = 100
        self.is_moving = False
        self.last_facing_direction = 'down'

        # Set initial animation to falling
        self.protagonist_animation.play_animation('walk_down')

        # Transition system
        self.transitioning = False
        self.fade_transition = False
        self.fade_timer = 0.0
        self.fade_duration = 1.0
        self.fade_alpha = 0

        # Splash effect system
        self.splash_active = False
        self.splash_timer = 0.0
        self.splash_duration = 1.0  # 1 second splash effect
        self.splash_particles = []

        # Audio manager (no rain in this scene)
        if audio_manager:
            self.audio = audio_manager
        else:
            self.audio = AudioManager()
            self.audio.load_ambient_pack()

        # Start different ambient sound for indoor bunker
        if not self.audio.is_muted_state():
            self.audio.stop_ambient()  # Stop outdoor rain
            self.audio.play_ambient("cave_echo", loop=True, fade_in_ms=1000)  # Indoor ambient

        # Quit overlay
        self.quit_overlay = QuitOverlay()

        print("Scene 5 initialized - Inside the bunker!")

    def load_bunker_room_background(self):
        """Load bunker_room.png from scene5 folder or create fallback"""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            bg_path = os.path.join(project_root, "assets", "images", "backgrounds", "scene5", "bunker_room.png")

            if os.path.exists(bg_path):
                background = pygame.image.load(bg_path)
                background = pygame.transform.scale(background, (self.screen_width, self.screen_height))
                print(f"Loaded bunker room background from: {bg_path}")
                return background
            else:
                print(f"bunker_room.png not found at {bg_path}, creating fallback")
                return self.create_fallback_background()

        except Exception as e:
            print(f"Error loading bunker room background: {e}")
            return self.create_fallback_background()

    def create_fallback_background(self):
        """Create a fallback bunker room background"""
        background = pygame.Surface((self.screen_width, self.screen_height))

        # Dark bunker interior
        background.fill((40, 35, 30))

        # Draw concrete walls
        wall_color = (60, 55, 50)

        # Left wall
        pygame.draw.rect(background, wall_color, (0, 0, 50, self.screen_height))

        # Right wall
        pygame.draw.rect(background, wall_color, (self.screen_width - 50, 0, 50, self.screen_height))

        # Top wall/ceiling
        pygame.draw.rect(background, wall_color, (0, 0, self.screen_width, 80))

        # Bottom floor
        floor_color = (50, 45, 40)
        pygame.draw.rect(background, floor_color, (0, self.screen_height - 60, self.screen_width, 60))

        # Add some texture lines
        for i in range(0, self.screen_width, 40):
            pygame.draw.line(background, (50, 45, 40), (i, 0), (i, self.screen_height), 1)
        for i in range(0, self.screen_height, 30):
            pygame.draw.line(background, (50, 45, 40), (0, i), (self.screen_width, i), 1)

        # Add entrance hatch at top center
        hatch_width = 60
        hatch_height = 40
        hatch_x = (self.screen_width - hatch_width) // 2
        hatch_y = 10
        pygame.draw.rect(background, (80, 70, 60), (hatch_x, hatch_y, hatch_width, hatch_height))

        # Add visible puddle where protagonist lands (15% from bottom, moved down 20px)
        puddle_center_x = self.screen_width // 2
        puddle_center_y = int(self.screen_height - (self.screen_height * 0.15) + 20)
        puddle_width = 80
        puddle_height = 40

        # Draw puddle as dark water with reflective surface
        puddle_color = (30, 45, 65)  # Dark blue-gray water
        puddle_rect = pygame.Rect(puddle_center_x - puddle_width // 2, puddle_center_y - puddle_height // 2,
                                puddle_width, puddle_height)

        # Create oval-shaped puddle
        pygame.draw.ellipse(background, puddle_color, puddle_rect)

        # Add subtle highlight on top edge for water reflection
        highlight_rect = pygame.Rect(puddle_center_x - puddle_width // 2 + 5,
                                   puddle_center_y - puddle_height // 2 + 2,
                                   puddle_width - 10, 8)
        pygame.draw.ellipse(background, (50, 70, 90), highlight_rect)

        return background

    def add_puddle_to_background(self):
        """Add visible puddle to any background (fallback or loaded image)"""
        # Calculate puddle position (same as landing position, moved down 20px)
        puddle_center_x = self.screen_width // 2
        puddle_center_y = int(self.screen_height - (self.screen_height * 0.15) + 20)
        puddle_width = 80
        puddle_height = 40

        # Draw puddle as dark water with reflective surface
        puddle_color = (30, 45, 65)  # Dark blue-gray water
        puddle_rect = pygame.Rect(puddle_center_x - puddle_width // 2, puddle_center_y - puddle_height // 2,
                                puddle_width, puddle_height)

        # Create oval-shaped puddle
        pygame.draw.ellipse(self.background, puddle_color, puddle_rect)

        # Add subtle highlight on top edge for water reflection
        highlight_rect = pygame.Rect(puddle_center_x - puddle_width // 2 + 5,
                                   puddle_center_y - puddle_height // 2 + 2,
                                   puddle_width - 10, 8)
        pygame.draw.ellipse(self.background, (50, 70, 90), highlight_rect)

        # Add darker rim around puddle for depth
        rim_rect = pygame.Rect(puddle_center_x - puddle_width // 2 - 2, puddle_center_y - puddle_height // 2 - 2,
                             puddle_width + 4, puddle_height + 4)
        pygame.draw.ellipse(self.background, (20, 30, 40), rim_rect, 2)

    def create_splash_effect(self):
        """Create splash particles when landing in puddle"""
        import random
        import math

        self.splash_active = True
        self.splash_timer = 0.0
        self.splash_particles = []

        # Create splash particles around landing position
        center_x = self.protagonist_x + 32  # Center of protagonist
        center_y = self.protagonist_y + 64  # Bottom of protagonist

        for i in range(20):  # 20 splash particles
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            particle = {
                'x': center_x + random.uniform(-10, 10),
                'y': center_y + random.uniform(-5, 5),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - random.uniform(50, 100),  # Upward bias
                'size': random.uniform(2, 5),
                'life': 1.0,
                'color': (100, 120, 140)  # Water blue-gray
            }
            self.splash_particles.append(particle)

    def update_splash_effect(self, dt):
        """Update splash particle system"""
        if not self.splash_active:
            return

        self.splash_timer += dt

        # Update particles
        for particle in self.splash_particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vy'] += 300 * dt  # Gravity
            particle['life'] -= dt / self.splash_duration

            # Remove dead particles
            if particle['life'] <= 0:
                self.splash_particles.remove(particle)

        # End splash effect when timer expires
        if self.splash_timer >= self.splash_duration:
            self.splash_active = False
            self.splash_particles = []

    def draw_splash_effect(self, screen):
        """Draw splash particles"""
        if not self.splash_active:
            return

        for particle in self.splash_particles:
            if particle['life'] > 0:
                alpha = int(255 * particle['life'])
                size = int(particle['size'] * particle['life'])
                if size > 0:
                    # Create surface for particle with alpha
                    particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    color = (*particle['color'], alpha)
                    pygame.draw.circle(particle_surface, color, (size, size), size)
                    screen.blit(particle_surface, (int(particle['x'] - size), int(particle['y'] - size)))

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

        return None

    def update(self, dt):
        # Don't update game logic if quit overlay is visible
        if self.quit_overlay.is_visible():
            return

        # Handle falling animation
        if self.is_falling:
            self.protagonist_y += self.fall_speed * dt

            # Check if landed
            if self.protagonist_y >= self.target_y:
                self.protagonist_y = self.target_y
                self.is_falling = False
                print("Protagonist landed in bunker room with a splash!")
                # Create splash effect
                self.create_splash_effect()
                # Switch to idle animation
                self.protagonist_animation.play_animation('idle_down')

        # Handle normal movement only after landing
        if not self.is_falling:
            keys = pygame.key.get_pressed()
            self.is_moving = False

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

            # Get sprite dimensions for bounds checking
            current_frame = self.protagonist_animation.get_current_frame()
            if current_frame:
                sprite_width = int(current_frame.get_width() * self.character_display_scale)
                sprite_height = int(current_frame.get_height() * self.character_display_scale)
            else:
                sprite_width = 64
                sprite_height = 96

            # Keep protagonist on screen
            new_x = max(50, min(self.screen_width - 50 - sprite_width, new_x))  # Account for walls
            new_y = max(80, min(self.screen_height - 60 - sprite_height, new_y))  # Account for ceiling/floor

            # Update position
            self.protagonist_x = new_x
            self.protagonist_y = new_y

            # Handle animation based on movement
            if self.is_moving and movement_direction:
                self.protagonist_animation.play_animation(f'walk_{movement_direction}')
                self.last_facing_direction = movement_direction
            else:
                self.protagonist_animation.play_animation(f'idle_{self.last_facing_direction}')

        # Update animation system
        self.protagonist_animation.update(dt)

        # Update splash effect
        self.update_splash_effect(dt)

        return None

    def render(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))

        # Draw scene number
        scene_font = pygame.font.Font(None, 36)
        scene_text = scene_font.render("SCENE 5", True, (255, 255, 255))
        scene_rect = scene_text.get_rect()
        scene_rect.topright = (self.screen_width - 20, 20)

        # Draw scene background
        scene_bg_rect = scene_rect.inflate(10, 5)
        pygame.draw.rect(screen, (0, 0, 0, 180), scene_bg_rect)
        screen.blit(scene_text, scene_rect)

        # Draw protagonist
        protagonist_sprite = self.protagonist_animation.get_current_frame()
        if protagonist_sprite:
            if self.character_display_scale != 1.0:
                scaled_width = int(protagonist_sprite.get_width() * self.character_display_scale)
                scaled_height = int(protagonist_sprite.get_height() * self.character_display_scale)
                protagonist_sprite = pygame.transform.scale(protagonist_sprite, (scaled_width, scaled_height))

            screen.blit(protagonist_sprite, (int(self.protagonist_x), int(self.protagonist_y)))

        # Draw splash effect
        self.draw_splash_effect(screen)

        # Draw location text
        font = pygame.font.Font(None, 24)
        if self.is_falling:
            location_text = font.render("Falling into the bunker - SCENE 5", True, (255, 255, 255))
        else:
            location_text = font.render("Inside the bunker - SCENE 5", True, (255, 255, 255))

        text_rect = location_text.get_rect()
        text_rect.topleft = (10, 10)

        # Draw text background
        bg_rect = text_rect.inflate(10, 5)
        pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
        screen.blit(location_text, text_rect)

        # Draw quit overlay
        self.quit_overlay.render(screen)

    def cleanup(self):
        """Clean up resources when scene 5 state is destroyed"""
        pass