import pygame

class QuitOverlay:
    def __init__(self):
        self.visible = False
        self.selected_option = 0  # 0 = Resume, 1 = Quit
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)

        # Colors
        self.overlay_color = (0, 0, 0, 180)  # Semi-transparent black
        self.selected_color = (255, 255, 100)  # Yellow for selected option
        self.normal_color = (255, 255, 255)    # White for normal text
        self.border_color = (255, 255, 255)

    def show(self):
        """Show the quit overlay"""
        self.visible = True
        self.selected_option = 0  # Default to Resume

    def hide(self):
        """Hide the quit overlay"""
        self.visible = False

    def is_visible(self):
        """Check if overlay is visible"""
        return self.visible

    def handle_input(self, event):
        """Handle input events for the overlay"""
        if not self.visible:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_option = 0  # Resume
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_option = 1  # Quit
            elif event.key == pygame.K_RETURN:
                if self.selected_option == 0:
                    self.hide()
                    return "resume"
                else:
                    return "quit"
            elif event.key == pygame.K_ESCAPE:
                self.hide()
                return "resume"

        return None

    def render(self, screen):
        """Render the quit overlay"""
        if not self.visible:
            return

        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Draw semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Main panel dimensions
        panel_width = 400
        panel_height = 250
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2

        # Draw main panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (40, 40, 60), panel_rect)
        pygame.draw.rect(screen, self.border_color, panel_rect, 3)

        # Title
        title_text = self.font_large.render("Pause", True, self.normal_color)
        title_rect = title_text.get_rect()
        title_rect.centerx = panel_x + panel_width // 2
        title_rect.y = panel_y + 30
        screen.blit(title_text, title_rect)

        # Options
        options = ["Resume Game", "Quit Game"]
        option_y_start = panel_y + 100
        option_spacing = 60

        for i, option in enumerate(options):
            color = self.selected_color if i == self.selected_option else self.normal_color

            # Draw selection indicator
            if i == self.selected_option:
                indicator_x = panel_x + 50
                indicator_y = option_y_start + i * option_spacing + 10
                pygame.draw.polygon(screen, self.selected_color, [
                    (indicator_x, indicator_y),
                    (indicator_x + 15, indicator_y + 10),
                    (indicator_x, indicator_y + 20)
                ])

            # Draw option text
            option_text = self.font_medium.render(option, True, color)
            option_rect = option_text.get_rect()
            option_rect.x = panel_x + 80
            option_rect.y = option_y_start + i * option_spacing
            screen.blit(option_text, option_rect)

        # Instructions
        instructions = [
            "↑/↓ or W/S - Navigate",
            "ENTER - Select",
            "ESC - Resume"
        ]

        instruction_font = pygame.font.Font(None, 24)
        instruction_y = panel_y + panel_height + 20

        for i, instruction in enumerate(instructions):
            instruction_text = instruction_font.render(instruction, True, (200, 200, 200))
            instruction_rect = instruction_text.get_rect()
            instruction_rect.centerx = panel_x + panel_width // 2
            instruction_rect.y = instruction_y + i * 25
            screen.blit(instruction_text, instruction_rect)