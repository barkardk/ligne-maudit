#!/usr/bin/env python3
"""Debug script to mirror field state creation exactly"""

import pygame
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def test_field_creation():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))

    # Import exactly like in field.py
    from assets.sprites.protagonist import create_protagonist_animation_system

    print("Creating protagonist animation system...")
    protagonist_animation, using_sprite_sheet = create_protagonist_animation_system()

    print(f"Using sprite sheet: {using_sprite_sheet}")

    # Test exactly like in field.py
    current_frame = protagonist_animation.get_current_frame()
    if current_frame:
        frame_w, frame_h = current_frame.get_size()
        print(f"Detected frame size: {frame_w}x{frame_h}")

        # Auto-adjust scaling based on frame size
        if frame_w <= 48 and frame_h <= 64:
            character_display_scale = 1.5  # 48x64 processed sprites
            print("Using 1.5x scale for processed sprites")
        elif frame_w <= 96 and frame_h <= 128:
            character_display_scale = 1.0  # Medium sprites
            print("Using 1.0x scale for medium sprites")
        elif frame_w <= 160 and frame_h <= 240:
            character_display_scale = 0.7  # Large sprites (128x192, etc.)
            print("Using 0.7x scale for large sprites")
        else:
            character_display_scale = 0.25  # Very large sprites (256x384) -> ~64x96 display
            print("Using 0.25x scale for very large sprites")
    else:
        character_display_scale = 1.0  # Default fallback
        print("No current frame, using default scale")

    print(f"Final character display scale: {character_display_scale}")

    pygame.quit()

if __name__ == "__main__":
    test_field_creation()