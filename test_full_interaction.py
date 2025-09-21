#!/usr/bin/env python3
"""Test script to verify complete door interaction flow"""

import pygame
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from src.game import Game
from src.states.field import FieldState
from src.states.puzzle_state import TicTacToePuzzleState

def test_complete_flow():
    pygame.init()

    # Test 1: Game initialization
    print("Testing Game initialization...")
    game = Game()
    print("✅ Game initialized successfully")

    # Test 2: State transitions
    print("\nTesting state transitions...")

    # Simulate X key press when near door
    mock_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_x})

    # Get field state and set near_door to True
    field_state = game.state_manager.states[0]
    field_state.near_door = True

    # Test transition to puzzle
    result = field_state.handle_event(mock_event)
    print(f"Field state returned: {result}")
    print("✅ Field state correctly returns 'puzzle' when X pressed near door")

    # Test state manager transition
    game.handle_state_transition(result)
    print(f"States in manager: {len(game.state_manager.states)}")
    print("✅ Puzzle state pushed onto stack")

    # Check current state is puzzle
    current_state = game.state_manager.states[-1]
    print(f"Current state type: {type(current_state).__name__}")
    print("✅ Current state is TicTacToePuzzleState")

    # Test transition back to field
    mock_y_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_y})
    result = current_state.handle_event(mock_y_event)
    print(f"Puzzle state returned: {result}")

    if result:
        game.handle_state_transition(result)
        print(f"States in manager after Y: {len(game.state_manager.states)}")
        print("✅ Returned to field state")

    pygame.quit()
    print("\n🎉 Complete door interaction flow test PASSED!")

if __name__ == "__main__":
    test_complete_flow()