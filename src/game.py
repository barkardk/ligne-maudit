import pygame
from .states.combat import CombatState
from .states.field import FieldState
from .states.puzzle_state import TicTacToePuzzleState
from .states.game_state import GameStateManager

class Game:
    def __init__(self):
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Ligne Maudite")

        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True

        self.state_manager = GameStateManager()
        self.state_manager.push_state(FieldState(self.screen))

    def handle_state_transition(self, new_state_name):
        """Handle transitions between game states"""
        if new_state_name == "puzzle":
            # Push puzzle state on top of field state
            puzzle_state = TicTacToePuzzleState(self.screen)
            self.state_manager.push_state(puzzle_state)
        elif new_state_name == "field":
            # Return to field by popping current state
            self.state_manager.pop_state()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                result = self.state_manager.handle_event(event)
                if result:
                    self.handle_state_transition(result)

    def update(self, dt):
        self.state_manager.update(dt)

    def render(self):
        self.screen.fill((20, 20, 40))  # Dark bunker-like background
        self.state_manager.render(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0

            self.handle_events()
            self.update(dt)
            self.render()

            if self.state_manager.should_quit():
                self.running = False