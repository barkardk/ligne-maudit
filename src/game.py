import pygame
from .states.combat import CombatState
from .states.field import FieldState
from .states.intro_state import IntroState
from .states.puzzle_state import TicTacToePuzzleState
from .states.door_state import DoorState
from .states.box_state import BoxState
from .states.game_state import GameStateManager
from .audio.audio_manager import AudioManager

class Game:
    def __init__(self):
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Ligne Maudite")

        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True

        # Create shared audio manager
        self.audio_manager = AudioManager()
        self.audio_manager.load_ambient_pack()

        self.state_manager = GameStateManager()
        self.state_manager.push_state(IntroState(self.screen, self.audio_manager))

    def handle_state_transition(self, new_state_name):
        """Handle transitions between game states"""
        if new_state_name == "puzzle":
            # Push puzzle state on top of current state
            puzzle_state = TicTacToePuzzleState(self.screen)
            self.state_manager.push_state(puzzle_state)
        elif new_state_name == "door":
            # Push door state on top of field state
            door_state = DoorState(self.screen)
            self.state_manager.push_state(door_state)
        elif new_state_name == "flash":
            # Push flash state on top of field state - check if flash has key
            field_state = self.state_manager.states[0]  # Get field state
            has_key = getattr(field_state, 'flash_has_key', True)
            flash_state = BoxState(self.screen, has_key)  # Reuse BoxState for flash
            self.state_manager.push_state(flash_state)
        elif new_state_name == "take_key":
            # Player took key - update field state and return
            field_state = self.state_manager.states[0]  # Get field state
            if hasattr(field_state, 'take_key_from_flash'):
                field_state.take_key_from_flash()
            self.state_manager.pop_state()  # Return to field
        elif new_state_name == "field":
            # Check if we're transitioning from intro or returning from another state
            if len(self.state_manager.states) == 1:
                # Coming from intro - replace intro with field
                self.state_manager.change_state(FieldState(self.screen, self.audio_manager))
            else:
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
        # Check if current state wants to transition
        if self.state_manager.states:
            result = self.state_manager.states[-1].update(dt)
            if result:
                self.handle_state_transition(result)
        else:
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

        # Cleanup audio when game ends
        if hasattr(self, 'audio_manager'):
            self.audio_manager.cleanup()