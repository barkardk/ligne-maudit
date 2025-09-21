#!/usr/bin/env python3
"""Test if there are collision areas blocking door access"""

import pygame
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from assets.backgrounds.collision_map import create_maginot_collision_map

def test_door_access():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))

    # Create collision map
    collision_map = create_maginot_collision_map(1024, 768)

    print(f"Total collision areas: {len(collision_map.collision_rects)}")

    # Door location
    door_x, door_y = 467, 575
    print(f"Door at: ({door_x}, {door_y})")

    # Test positions around the door
    test_positions = [
        (door_x, door_y - 60, "above door"),
        (door_x, door_y + 60, "below door"),
        (door_x - 60, door_y, "left of door"),
        (door_x + 60, door_y, "right of door"),
        (door_x, door_y, "at door"),
        (door_x - 30, door_y - 30, "northwest of door"),
        (door_x + 30, door_y - 30, "northeast of door"),
        (door_x - 30, door_y + 30, "southwest of door"),
        (door_x + 30, door_y + 30, "southeast of door"),
    ]

    # Test character size (64x96 from our scaling)
    char_width, char_height = 64, 96

    print("\nTesting door accessibility:")
    print("=" * 50)

    for test_x, test_y, description in test_positions:
        collision = collision_map.check_collision(test_x, test_y, char_width, char_height)
        status = "BLOCKED" if collision else "CLEAR"
        print(f"{description:20s} ({test_x:3d}, {test_y:3d}): {status}")

    # Check which collision rects are near the door
    print(f"\nCollision areas near door (within 150 pixels):")
    print("=" * 50)

    for i, rect in enumerate(collision_map.collision_rects):
        distance = ((rect.centerx - door_x)**2 + (rect.centery - door_y)**2)**0.5
        if distance < 150:
            print(f"Collision {i}: ({rect.x}, {rect.y}) size {rect.width}x{rect.height}, distance: {distance:.1f}")

    pygame.quit()

if __name__ == "__main__":
    test_door_access()