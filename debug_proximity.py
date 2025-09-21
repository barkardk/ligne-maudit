#!/usr/bin/env python3
"""Debug proximity detection"""

import pygame
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from src.states.field import FieldState

def debug_proximity():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))

    # Create field state
    field_state = FieldState(screen)

    # Move character to door location
    field_state.protagonist_x = field_state.door_x
    field_state.protagonist_y = field_state.door_y

    print("=== PROXIMITY DEBUG ===")
    print(f"Character position: ({field_state.protagonist_x}, {field_state.protagonist_y})")
    print(f"Door position: ({field_state.door_x}, {field_state.door_y})")
    print(f"Interaction distance: {field_state.door_interaction_distance}")

    # Manually calculate what the proximity function does
    current_frame = field_state.protagonist_animation.get_current_frame()
    if current_frame:
        frame_w = current_frame.get_width()
        frame_h = current_frame.get_height()
        print(f"Frame size: {frame_w}x{frame_h}")
        print(f"Display scale: {field_state.character_display_scale}")

        protagonist_center_x = field_state.protagonist_x + (frame_w * field_state.character_display_scale) // 2
        protagonist_center_y = field_state.protagonist_y + (frame_h * field_state.character_display_scale) // 2
    else:
        protagonist_center_x = field_state.protagonist_x + 32
        protagonist_center_y = field_state.protagonist_y + 48

    print(f"Character center: ({protagonist_center_x}, {protagonist_center_y})")

    distance = ((protagonist_center_x - field_state.door_x) ** 2 + (protagonist_center_y - field_state.door_y) ** 2) ** 0.5
    print(f"Distance to door: {distance:.1f}")
    print(f"Within interaction distance? {distance <= field_state.door_interaction_distance}")

    # Test a few positions around the door
    test_positions = [
        (field_state.door_x - 30, field_state.door_y - 30),
        (field_state.door_x, field_state.door_y - 50),
        (field_state.door_x + 30, field_state.door_y - 30),
    ]

    print(f"\nTesting nearby positions:")
    for test_x, test_y in test_positions:
        field_state.protagonist_x = test_x
        field_state.protagonist_y = test_y

        if current_frame:
            center_x = test_x + (frame_w * field_state.character_display_scale) // 2
            center_y = test_y + (frame_h * field_state.character_display_scale) // 2
        else:
            center_x = test_x + 32
            center_y = test_y + 48

        dist = ((center_x - field_state.door_x) ** 2 + (center_y - field_state.door_y) ** 2) ** 0.5
        within = dist <= field_state.door_interaction_distance
        print(f"Position ({test_x}, {test_y}) -> center ({center_x}, {center_y}) -> distance {dist:.1f} -> {within}")

    pygame.quit()

if __name__ == "__main__":
    debug_proximity()