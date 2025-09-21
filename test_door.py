#!/usr/bin/env python3
"""Test script to verify door interaction system"""

import pygame
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from src.states.field import FieldState

def test_door_interaction():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Door Interaction Test")

    field_state = FieldState(screen)

    # Test proximity detection
    print(f"Door position: ({field_state.door_x}, {field_state.door_y})")
    print(f"Interaction distance: {field_state.door_interaction_distance}")
    print(f"Initial protagonist position: ({field_state.protagonist_x}, {field_state.protagonist_y})")

    # Move protagonist near door
    field_state.protagonist_x = field_state.door_x - 30
    field_state.protagonist_y = field_state.door_y - 30

    print(f"Moved protagonist to: ({field_state.protagonist_x}, {field_state.protagonist_y})")

    # Test proximity detection
    field_state.check_door_proximity()

    print(f"Near door: {field_state.near_door}")
    print(f"Speech bubble visible: {field_state.speech_bubble.visible}")
    print(f"Interaction prompt visible: {field_state.interaction_prompt.visible}")

    pygame.quit()

if __name__ == "__main__":
    test_door_interaction()