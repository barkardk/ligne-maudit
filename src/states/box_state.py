import pygame
import os
from .game_state import GameState
from ..ui.quit_overlay import QuitOverlay

class BoxState(GameState):
    def __init__(self, screen, box_has_key=True):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Box state
        self.box_has_key = box_has_key
        self.awaiting_response = True
        self.selected_option = 0  # 0 = Yes, 1 = No

        # Load box interior background
        self.background = self.load_box_background()

        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)

        # Quit overlay
        self.quit_overlay = QuitOverlay()

        print("Box opened - You see a key inside!" if box_has_key else "Box opened - It's empty.")

    def load_box_background(self):
        """Load the appropriate box interior background"""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

            # Choose the right background based on whether box has key
            if self.box_has_key:
                bg_path = os.path.join(project_root, "assets", "images", "backgrounds", "inside_box.png")
            else:
                bg_path = os.path.join(project_root, "assets", "images", "backgrounds", "inside_empty_box.png")

            if os.path.exists(bg_path):
                background = pygame.image.load(bg_path)
                background = pygame.transform.scale(background, (self.screen_width, self.screen_height))
                print(f"Loaded box background from: {bg_path}")
                return background
            else:
                print(f"Box background not found at {bg_path}, creating fallback")
                return self.create_fallback_background()

        except Exception as e:
            print(f"Error loading box background: {e}")
            return self.create_fallback_background()

    def create_fallback_background(self):
        """Create a fallback background showing box interior"""
        background = pygame.Surface((self.screen_width, self.screen_height))
        background.fill((60, 50, 40))  # Dark wood interior

        # Draw box interior borders
        border_thickness = 20
        inner_rect = pygame.Rect(border_thickness, border_thickness,
                               self.screen_width - 2 * border_thickness,
                               self.screen_height - 2 * border_thickness)
        pygame.draw.rect(background, (80, 70, 60), inner_rect)

        # Box interior shadow/depth
        shadow_rect = pygame.Rect(30, 30, self.screen_width - 60, self.screen_height - 60)
        pygame.draw.rect(background, (40, 30, 20), shadow_rect)

        if self.box_has_key:
            # Draw a simple key in the center
            key_x = self.screen_width // 2
            key_y = self.screen_height // 2

            # Key shaft
            key_rect = pygame.Rect(key_x - 40, key_y - 5, 60, 10)
            pygame.draw.rect(background, (200, 180, 100), key_rect)

            # Key head (circle)
            pygame.draw.circle(background, (200, 180, 100), (key_x - 35, key_y), 15)
            pygame.draw.circle(background, (40, 30, 20), (key_x - 35, key_y), 8)

            # Key teeth
            teeth_rects = [
                pygame.Rect(key_x + 15, key_y - 5, 5, 8),
                pygame.Rect(key_x + 22, key_y - 5, 3, 5)
            ]
            for rect in teeth_rects:
                pygame.draw.rect(background, (200, 180, 100), rect)

        return background

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
            elif event.key == pygame.K_BACKSPACE:
                # Close without taking anything
                return "field"
            elif self.awaiting_response and self.box_has_key:
                if event.key == pygame.K_y:
                    return "take_key"
                elif event.key == pygame.K_n:
                    return "field"
            elif not self.box_has_key:  # Empty
                if event.key == pygame.K_ESCAPE:
                    return "field"

        return None

    def update(self, dt):
        # Don't update game logic if quit overlay is visible (pause the game)
        if self.quit_overlay.is_visible():
            return
        # Static state, nothing to update
        pass

    def render(self, screen):
        # Draw background image (should be visible now)
        screen.blit(self.background, (0, 0))

        if self.box_has_key and self.awaiting_response:
            # Text asking about taking key (positioned at bottom of screen)
            question_text = self.font_medium.render("Take the key?", True, (255, 255, 255))
            question_rect = question_text.get_rect()
            question_rect.centerx = self.screen_width // 2
            question_rect.y = self.screen_height - 150

            # Add background for text
            bg_rect = question_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            screen.blit(question_text, question_rect)

            # Simple Y/N instruction
            instruction_text = self.font_small.render("Y - Yes    N - No    ESC - Leave", True, (200, 200, 200))
            instruction_rect = instruction_text.get_rect()
            instruction_rect.centerx = self.screen_width // 2
            instruction_rect.y = question_rect.bottom + 20

            # Add background for instruction
            inst_bg_rect = instruction_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), inst_bg_rect)
            screen.blit(instruction_text, instruction_rect)

        else:  # Empty or key taken
            empty_text = self.font_medium.render("Empty.", True, (255, 255, 255))
            empty_rect = empty_text.get_rect()
            empty_rect.center = (self.screen_width // 2, self.screen_height - 150)

            # Add background for text
            bg_rect = empty_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            screen.blit(empty_text, empty_rect)

            exit_text = self.font_small.render("ESC - Leave", True, (200, 200, 200))
            exit_rect = exit_text.get_rect()
            exit_rect.centerx = self.screen_width // 2
            exit_rect.y = empty_rect.bottom + 20

            # Add background for instruction
            exit_bg_rect = exit_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), exit_bg_rect)
            screen.blit(exit_text, exit_rect)

        # Draw quit overlay on top of everything
        self.quit_overlay.render(screen)

    def cleanup(self):
        """Clean up resources"""
        pass