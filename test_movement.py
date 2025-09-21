#!/usr/bin/env python3
"""Test character movement to door location"""

import pygame
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from src.states.field import FieldState

def test_movement():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Movement Test")

    # Create field state
    field_state = FieldState(screen)

    print("=== MOVEMENT TEST ===")
    print(f"Screen size: {screen.get_size()}")
    print(f"Character starts at: ({field_state.protagonist_x}, {field_state.protagonist_y})")
    print(f"Door is at: ({field_state.door_x}, {field_state.door_y})")

    # Test if we can manually move character to door
    old_x = field_state.protagonist_x
    old_y = field_state.protagonist_y

    # Try to move character to door location
    field_state.protagonist_x = field_state.door_x
    field_state.protagonist_y = field_state.door_y

    print(f"Moved character to: ({field_state.protagonist_x}, {field_state.protagonist_y})")

    # Check proximity
    field_state.check_door_proximity()
    print(f"Near door after move: {field_state.near_door}")
    print(f"Speech bubble visible: {field_state.speech_bubble.visible}")

    # Test screen boundaries with door position
    sprite_width = 64  # Character display size
    sprite_height = 96

    print(f"\nScreen boundary check:")
    print(f"Max X position: {field_state.screen_width - sprite_width} (door X: {field_state.door_x})")
    print(f"Max Y position: {field_state.screen_height - sprite_height} (door Y: {field_state.door_y})")

    if field_state.door_x > field_state.screen_width - sprite_width:
        print("WARNING: Door X is beyond screen boundary!")
    if field_state.door_y > field_state.screen_height - sprite_height:
        print("WARNING: Door Y is beyond screen boundary!")

    # Test collision check at door location
    collision = field_state.collision_map.check_collision(
        field_state.door_x, field_state.door_y, sprite_width, sprite_height
    )
    print(f"Collision at door location: {collision}")

    pygame.quit()

if __name__ == "__main__":
    test_movement()