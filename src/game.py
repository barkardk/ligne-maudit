import pygame
from .states.combat import CombatState
from .states.field import FieldState
from .states.scene0_state import Scene0State
from .states.intro_state import IntroState
from .states.puzzle_state import TicTacToePuzzleState
from .states.door_state import DoorState
from .states.box_state import BoxState
from .states.behind_bunker_state import BehindBunkerState
from .states.dragonteeth_state import DragonteethState
from .states.scene5_state import Scene5State
from .states.fight0_state import Fight0State
from .states.game_state import GameStateManager
from .audio.audio_manager import AudioManager

class Game:
    def __init__(self, start_scene=None):
        self.base_width = 1024
        self.base_height = 768
        self.screen_width = 1024
        self.screen_height = 768
        self.fullscreen = False
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.display_surface = pygame.Surface((self.base_width, self.base_height))  # Virtual screen
        pygame.display.set_caption("Ligne Maudite")

        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True

        # Create shared audio manager
        self.audio_manager = AudioManager()
        self.audio_manager.load_ambient_pack()

        self.state_manager = GameStateManager()

        # Start with specified scene or default to scene 0
        if start_scene == 0:
            print("Starting directly in Scene 0 (Story)")
            self.state_manager.push_state(Scene0State(self.display_surface, self.audio_manager))
        elif start_scene == 1:
            print("Starting directly in Scene 1 (Forest Path)")
            self.state_manager.push_state(IntroState(self.display_surface, self.audio_manager))
        elif start_scene == 2:
            print("Starting directly in Scene 2 (Field)")
            self.state_manager.push_state(FieldState(self.display_surface, self.audio_manager))
        elif start_scene == 3:
            print("Starting directly in Scene 3 (Behind Bunker)")
            self.state_manager.push_state(BehindBunkerState(self.display_surface, self.audio_manager))
        elif start_scene == 4:
            print("Starting directly in Scene 4 (Dragonteeth)")
            self.state_manager.push_state(DragonteethState(self.display_surface, self.audio_manager))
        elif start_scene == 5:
            print("Starting directly in Scene 5 (Bunker Interior)")
            self.state_manager.push_state(Scene5State(self.display_surface, self.audio_manager))
        elif start_scene == "fight0":
            print("Starting directly in Fight 0 (Battle Arena)")
            self.state_manager.push_state(Fight0State(self.display_surface, self.audio_manager))
        else:
            # Default to scene 0 (story)
            self.state_manager.push_state(Scene0State(self.display_surface, self.audio_manager))

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.fullscreen = not self.fullscreen

        if self.fullscreen:
            # Go fullscreen
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.screen_width = self.screen.get_width()
            self.screen_height = self.screen.get_height()
            print(f"Switched to fullscreen mode: {self.screen_width}x{self.screen_height}")
        else:
            # Go windowed
            self.screen_width = self.base_width
            self.screen_height = self.base_height
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            print("Switched to windowed mode")

        # Note: We don't update state screen references because they always use the virtual display_surface

    def handle_state_transition(self, new_state_name):
        """Handle transitions between game states"""
        if new_state_name == "puzzle":
            # Push puzzle state on top of current state
            puzzle_state = TicTacToePuzzleState(self.display_surface)
            self.state_manager.push_state(puzzle_state)
        elif new_state_name == "door":
            # Push door state on top of field state
            door_state = DoorState(self.display_surface)
            self.state_manager.push_state(door_state)
        elif new_state_name == "flash":
            # Push flash state on top of field state - check if flash has key
            field_state = self.state_manager.states[0]  # Get field state
            has_key = getattr(field_state, 'flash_has_key', True)
            flash_state = BoxState(self.display_surface, has_key)  # Reuse BoxState for flash
            self.state_manager.push_state(flash_state)
        elif new_state_name == "take_key":
            # Player took key - update field state and return
            field_state = self.state_manager.states[0]  # Get field state
            if hasattr(field_state, 'take_key_from_flash'):
                field_state.take_key_from_flash()
            self.state_manager.pop_state()  # Return to field
        elif new_state_name == "intro":
            # Transition from scene 0 to scene 1 (forest path with protagonist)
            self.state_manager.change_state(IntroState(self.display_surface, self.audio_manager))
        elif new_state_name == "field":
            # Check if we're transitioning from intro or returning from another state
            if len(self.state_manager.states) == 1:
                # Coming from intro - replace intro with field
                self.state_manager.change_state(FieldState(self.display_surface, self.audio_manager))
            else:
                # Return to field by popping current state
                self.state_manager.pop_state()
        elif new_state_name == "dragonteeth":
            # Transition to dragonteeth scene (scene 4)
            import time
            print(f"[{time.time():.2f}] Creating DragonteethState...")
            dragonteeth_state = DragonteethState(self.display_surface, self.audio_manager)
            print(f"[{time.time():.2f}] DragonteethState created, changing state...")
            self.state_manager.change_state(dragonteeth_state)
            print(f"[{time.time():.2f}] State changed to dragonteeth")
            print(f"[{time.time():.2f}] First render should happen next frame...")
        elif new_state_name in ["behind_bunker_left", "behind_bunker_right", "behind_bunker_red", "behind_bunker_blue"]:
            # Transition to behind bunker scene
            behind_bunker_state = BehindBunkerState(self.display_surface, self.audio_manager)
            # Set protagonist position based on which transition was used
            if new_state_name == "behind_bunker_left":
                behind_bunker_state.protagonist_x = behind_bunker_state.screen_width - 100  # Right side
            elif new_state_name == "behind_bunker_right":
                behind_bunker_state.protagonist_x = 100  # Left side
            elif new_state_name == "behind_bunker_red":
                # Spawn at red collision box position in scene 3
                behind_bunker_state.protagonist_x = behind_bunker_state.return_collision_box_red_x
                behind_bunker_state.protagonist_y = behind_bunker_state.return_collision_box_red_y
                # Set cooldown to prevent immediate re-triggering
                behind_bunker_state.transition_cooldown = behind_bunker_state.transition_cooldown_duration
            elif new_state_name == "behind_bunker_blue":
                # Spawn at blue collision box position in scene 3
                behind_bunker_state.protagonist_x = behind_bunker_state.return_collision_box_blue_x
                behind_bunker_state.protagonist_y = behind_bunker_state.return_collision_box_blue_y
                # Set cooldown to prevent immediate re-triggering
                behind_bunker_state.transition_cooldown = behind_bunker_state.transition_cooldown_duration
            self.state_manager.change_state(behind_bunker_state)
        elif new_state_name in ["field_left", "field_right", "field_center", "field_red", "field_blue"]:
            # Return to field from behind bunker
            field_state = FieldState(self.display_surface, self.audio_manager)
            # Set protagonist position based on which side they came from
            if new_state_name == "field_left":
                field_state.protagonist_x = 100  # Left side
            elif new_state_name == "field_right":
                field_state.protagonist_x = field_state.screen_width - 100  # Right side
            elif new_state_name == "field_red":
                # Return to red collision box position
                field_state.protagonist_x = field_state.collision_box_red_x
                field_state.protagonist_y = field_state.collision_box_red_y
                # Set cooldown to prevent immediate re-triggering
                field_state.transition_cooldown = field_state.transition_cooldown_duration
            elif new_state_name == "field_blue":
                # Return to blue collision box position
                field_state.protagonist_x = field_state.collision_box_blue_x
                field_state.protagonist_y = field_state.collision_box_blue_y
                # Set cooldown to prevent immediate re-triggering
                field_state.transition_cooldown = field_state.transition_cooldown_duration
            else:  # field_center
                # Return to exact collision box position
                field_collision_box_x = 2 * (field_state.screen_width // 4) + 50 + 50  # 612px
                field_collision_box_y = 2 * (field_state.screen_height // 4) + 200 - 50  # 534px
                field_state.protagonist_x = field_collision_box_x
                field_state.protagonist_y = field_collision_box_y
                # Set cooldown to prevent immediate re-triggering
                field_state.transition_cooldown = field_state.transition_cooldown_duration
            self.state_manager.change_state(field_state)
        elif new_state_name == "behind_bunker":
            # Return to behind bunker from dragonteeth
            behind_bunker_state = BehindBunkerState(self.display_surface, self.audio_manager)
            # Spawn at center bottom of behind bunker scene
            behind_bunker_state.protagonist_x = behind_bunker_state.screen_width // 2 - 32
            behind_bunker_state.protagonist_y = behind_bunker_state.screen_height - 100
            self.state_manager.change_state(behind_bunker_state)
        elif new_state_name == "bunker_interior":
            # Transition to scene 5 (bunker interior) when hitting the hatch
            print("Transitioning to Scene 5 (Bunker Interior)")
            scene5_state = Scene5State(self.display_surface, self.audio_manager)
            self.state_manager.change_state(scene5_state)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    # F11 for fullscreen toggle (common standard)
                    self.toggle_fullscreen()
                elif event.key == pygame.K_F12:
                    # F12 for fullscreen toggle (as requested - using F12 instead of F to avoid shooting conflict)
                    self.toggle_fullscreen()
                else:
                    # Pass other key events to current state
                    result = self.state_manager.handle_event(event)
                    if result:
                        self.handle_state_transition(result)
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
        # Clear virtual screen
        self.display_surface.fill((20, 20, 40))  # Dark bunker-like background

        # Render game to virtual screen
        self.state_manager.render(self.display_surface)

        # Scale virtual screen to real screen
        if self.fullscreen:
            # Stretch to fill entire screen
            scaled_surface = pygame.transform.scale(self.display_surface, (self.screen_width, self.screen_height))
            self.screen.blit(scaled_surface, (0, 0))
        else:
            # Direct blit in windowed mode
            self.screen.blit(self.display_surface, (0, 0))

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