import pygame
import os
from .game_state import GameState

class DoorState(GameState):
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Try to load door.png background
        self.background = self.load_door_background()

        print("Door close-up view - Press ESC to go back, ENTER to interact with door")

    def load_door_background(self):
        """Load door.png background or create a fallback"""
        try:
            # Try to load door.png from assets/images/backgrounds/
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            door_path = os.path.join(project_root, "assets", "images", "backgrounds", "door.png")

            if os.path.exists(door_path):
                background = pygame.image.load(door_path)
                # Scale to fit screen
                background = pygame.transform.scale(background, (self.screen_width, self.screen_height))
                print(f"Loaded door background from: {door_path}")
                return background
            else:
                print(f"door.png not found at {door_path}, creating fallback background")
                return self.create_fallback_background()

        except Exception as e:
            print(f"Error loading door background: {e}")
            return self.create_fallback_background()

    def create_fallback_background(self):
        """Create a simple fallback background showing a door close-up"""
        background = pygame.Surface((self.screen_width, self.screen_height))

        # Dark stone background
        background.fill((40, 35, 30))

        # Draw a large door in the center
        door_width = 400
        door_height = 600
        door_x = (self.screen_width - door_width) // 2
        door_y = (self.screen_height - door_height) // 2

        # Door frame (stone)
        frame_rect = pygame.Rect(door_x - 20, door_y - 20, door_width + 40, door_height + 40)
        pygame.draw.rect(background, (60, 55, 50), frame_rect)

        # Door itself (dark wood)
        door_rect = pygame.Rect(door_x, door_y, door_width, door_height)
        pygame.draw.rect(background, (45, 25, 15), door_rect)

        # Door panels
        panel_margin = 30
        panel_width = door_width - 2 * panel_margin
        panel_height = (door_height - 3 * panel_margin) // 2

        # Upper panel
        upper_panel = pygame.Rect(door_x + panel_margin, door_y + panel_margin, panel_width, panel_height)
        pygame.draw.rect(background, (35, 20, 10), upper_panel, 3)

        # Lower panel
        lower_panel = pygame.Rect(door_x + panel_margin, door_y + 2 * panel_margin + panel_height, panel_width, panel_height)
        pygame.draw.rect(background, (35, 20, 10), lower_panel, 3)

        # Door handle
        handle_x = door_x + door_width - 50
        handle_y = door_y + door_height // 2
        pygame.draw.circle(background, (80, 70, 60), (handle_x, handle_y), 15)
        pygame.draw.circle(background, (100, 90, 80), (handle_x, handle_y), 12)

        # Keyhole
        keyhole_x = handle_x - 60
        keyhole_y = handle_y
        pygame.draw.circle(background, (20, 15, 10), (keyhole_x, keyhole_y), 8)
        pygame.draw.circle(background, (10, 5, 0), (keyhole_x, keyhole_y), 6)

        # Add some texture lines to the door
        for i in range(5):
            y_pos = door_y + 50 + i * 100
            pygame.draw.line(background, (30, 15, 5), (door_x + 10, y_pos), (door_x + door_width - 10, y_pos), 2)

        return background

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Go back to field state
                return "field"
            elif event.key == pygame.K_RETURN:
                # Enter the door (go to puzzle)
                return "puzzle"

        return None  # Stay in this state

    def update(self, dt):
        # Nothing to update for static door view
        pass

    def render(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))

        # Draw instructions
        font = pygame.font.Font(None, 36)
        instructions = [
            "Door Close-up View",
            "",
            "ENTER - Open the door",
            "ESC - Go back"
        ]

        y_offset = 50
        for instruction in instructions:
            if instruction:  # Skip empty strings
                text = font.render(instruction, True, (255, 255, 255))
                text_rect = text.get_rect()
                text_rect.topleft = (50, y_offset)

                # Draw text background
                bg_rect = text_rect.inflate(20, 10)
                pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                screen.blit(text, text_rect)

            y_offset += 45

    def cleanup(self):
        """Clean up resources when door state is destroyed"""
        pass