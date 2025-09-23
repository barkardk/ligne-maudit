import pygame
import os
from .game_state import GameState

class TicTacToePuzzleState(GameState):
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Load door background
        self.background = self.load_door_background()

        # Tic-tac-toe board (3x3 grid)
        self.board = [[None for _ in range(3)] for _ in range(3)]

        # Puzzle solution (simpler pattern - just 3 X's in top row)
        self.solution = [
            ['X', 'X', 'X'],
            [None, None, None],
            [None, None, None]
        ]

        # Current player symbol
        self.current_symbol = 'X'

        # Grid settings
        self.grid_size = 300
        self.cell_size = self.grid_size // 3
        self.grid_x = self.screen_width // 4 - self.grid_size // 2  # Left side
        self.grid_y = (self.screen_height - self.grid_size) // 2

        # UI
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)

        # Game state
        self.puzzle_solved = False
        self.selected_cell = [0, 0]  # For keyboard navigation

        print("Tic-tac-toe puzzle loaded! Match the pattern to unlock the door.")

    def load_door_background(self):
        """Load door.png background or create fallback"""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            door_path = os.path.join(project_root, "assets", "images", "backgrounds", "scene2", "door.png")

            if os.path.exists(door_path):
                background = pygame.image.load(door_path)
                background = pygame.transform.scale(background, (self.screen_width, self.screen_height))
                print(f"Loaded door background from: {door_path}")
                return background
            else:
                print(f"door.png not found at {door_path}, creating fallback")
                return self.create_fallback_background()

        except Exception as e:
            print(f"Error loading door background: {e}")
            return self.create_fallback_background()

    def create_fallback_background(self):
        """Create a fallback door background"""
        background = pygame.Surface((self.screen_width, self.screen_height))
        background.fill((40, 30, 20))  # Dark brown

        # Draw a large door outline
        door_width = 300
        door_height = 500
        door_x = (self.screen_width - door_width) // 2
        door_y = (self.screen_height - door_height) // 2

        # Door frame
        pygame.draw.rect(background, (80, 60, 40), (door_x - 10, door_y - 10, door_width + 20, door_height + 20))
        # Door itself
        pygame.draw.rect(background, (60, 45, 30), (door_x, door_y, door_width, door_height))
        # Door panels
        pygame.draw.rect(background, (50, 35, 20), (door_x + 20, door_y + 20, door_width - 40, door_height - 40), 3)

        return background

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_y or event.key == pygame.K_ESCAPE:
                # Return to field scene
                return "field"
            elif event.key == pygame.K_r:
                # Reset puzzle
                self.reset_puzzle()
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                # Place symbol in selected cell
                self.place_symbol()
            elif event.key == pygame.K_TAB:
                # Switch symbol
                self.current_symbol = 'O' if self.current_symbol == 'X' else 'X'
            # Arrow key navigation
            elif event.key == pygame.K_LEFT:
                self.selected_cell[0] = max(0, self.selected_cell[0] - 1)
            elif event.key == pygame.K_RIGHT:
                self.selected_cell[0] = min(2, self.selected_cell[0] + 1)
            elif event.key == pygame.K_UP:
                self.selected_cell[1] = max(0, self.selected_cell[1] - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_cell[1] = min(2, self.selected_cell[1] + 1)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.handle_mouse_click(event.pos)

        return None  # Stay in this state

    def handle_mouse_click(self, pos):
        """Handle mouse clicks on the grid"""
        mouse_x, mouse_y = pos

        # Check if click is within grid
        if (self.grid_x <= mouse_x <= self.grid_x + self.grid_size and
            self.grid_y <= mouse_y <= self.grid_y + self.grid_size):

            # Calculate grid position
            grid_x = (mouse_x - self.grid_x) // self.cell_size
            grid_y = (mouse_y - self.grid_y) // self.cell_size

            # Place symbol
            self.selected_cell = [grid_x, grid_y]
            self.place_symbol()

    def place_symbol(self):
        """Place current symbol in selected cell"""
        col, row = self.selected_cell

        if self.board[row][col] is None:
            self.board[row][col] = self.current_symbol
            self.check_solution()

    def check_solution(self):
        """Check if the puzzle is solved"""
        if self.board == self.solution:
            self.puzzle_solved = True
            print("Puzzle solved! The door unlocks...")

    def reset_puzzle(self):
        """Reset the puzzle board"""
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.puzzle_solved = False

    def update(self, dt):
        # No real-time updates needed for this puzzle
        pass

    def render(self, screen):
        # Draw door background
        screen.blit(self.background, (0, 0))

        # Semi-transparent overlay for better text visibility
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Title
        title_text = self.font.render("Door Lock Puzzle", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 50))
        screen.blit(title_text, title_rect)

        # Draw main puzzle grid (center-left)
        self.draw_grid(screen)

        # Draw solution pattern on the right side
        if not self.puzzle_solved:
            self.draw_solution_pattern(screen)
        else:
            success_text = self.font.render("DOOR UNLOCKED!", True, (0, 255, 0))
            success_rect = success_text.get_rect(center=(self.screen_width * 3 // 4, 200))
            screen.blit(success_text, success_rect)

        # Draw current symbol indicator
        symbol_text = self.small_font.render(f"Current symbol: {self.current_symbol}", True, (255, 255, 255))
        screen.blit(symbol_text, (50, self.screen_height - 150))

        # Controls
        controls = [
            "Arrow keys: Navigate",
            "Space/Enter: Place symbol",
            "Tab: Switch X/O",
            "R: Reset puzzle",
            "ESC: Return to door"
        ]

        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, (200, 200, 200))
            screen.blit(text, (50, self.screen_height - 120 + i * 25))

    def draw_solution_pattern(self, screen):
        """Draw the target pattern on the right side"""
        pattern_size = 150
        pattern_cell_size = pattern_size // 3
        pattern_x = self.screen_width * 3 // 4 - pattern_size // 2  # Right side
        pattern_y = 150

        # Draw background panel
        panel_rect = pygame.Rect(pattern_x - 15, pattern_y - 40, pattern_size + 30, pattern_size + 50)
        pygame.draw.rect(screen, (255, 255, 255, 200), panel_rect)  # Semi-transparent white
        # Yellow border is invisible

        # Draw title above the pattern
        title_text = self.small_font.render("TARGET:", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(pattern_x + pattern_size // 2, pattern_y - 20))
        screen.blit(title_text, title_rect)

        # Draw pattern grid
        for row in range(3):
            for col in range(3):
                cell_x = pattern_x + col * pattern_cell_size
                cell_y = pattern_y + row * pattern_cell_size

                # Cell background
                pygame.draw.rect(screen, (240, 240, 240),
                               (cell_x, cell_y, pattern_cell_size, pattern_cell_size))
                pygame.draw.rect(screen, (0, 0, 0),
                               (cell_x, cell_y, pattern_cell_size, pattern_cell_size), 2)

                # Draw symbol
                symbol = self.solution[row][col]
                if symbol:
                    color = (255, 0, 0) if symbol == 'X' else (0, 0, 255)  # Red X, Blue O
                    font = pygame.font.Font(None, int(pattern_cell_size * 0.6))
                    text = font.render(symbol, True, color)
                    text_rect = text.get_rect(center=(cell_x + pattern_cell_size // 2,
                                                    cell_y + pattern_cell_size // 2))
                    screen.blit(text, text_rect)

    def draw_grid(self, screen):
        """Draw the main puzzle grid"""
        for row in range(3):
            for col in range(3):
                cell_x = self.grid_x + col * self.cell_size
                cell_y = self.grid_y + row * self.cell_size

                # Cell background
                if [col, row] == self.selected_cell:
                    # Highlight selected cell
                    pygame.draw.rect(screen, (80, 80, 120),
                                   (cell_x, cell_y, self.cell_size, self.cell_size))
                else:
                    pygame.draw.rect(screen, (60, 60, 60),
                                   (cell_x, cell_y, self.cell_size, self.cell_size))

                # Cell border
                pygame.draw.rect(screen, (200, 200, 200),
                               (cell_x, cell_y, self.cell_size, self.cell_size), 3)

                # Draw symbol if present
                symbol = self.board[row][col]
                if symbol:
                    color = (255, 100, 100) if symbol == 'X' else (100, 100, 255)
                    text = self.font.render(symbol, True, color)
                    text_rect = text.get_rect(center=(cell_x + self.cell_size // 2,
                                                    cell_y + self.cell_size // 2))
                    screen.blit(text, text_rect)