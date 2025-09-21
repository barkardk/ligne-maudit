#!/usr/bin/env python3
"""Debug sprite frame extraction to find the overlap issue"""

import pygame
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from assets.sprites.sprite_sheet_loader import SpriteSheet

def debug_sprite_extraction():
    pygame.init()

    # Load the sprite sheet
    sprite_sheet = SpriteSheet("protagonist.png", 256, 384, scale_factor=1.0)

    if not sprite_sheet.sheet:
        print("Could not load sprite sheet!")
        return

    print(f"Sprite sheet loaded: {sprite_sheet.sheet.get_size()}")
    print(f"Frames: {sprite_sheet.cols}x{sprite_sheet.rows}")

    # Debug the frame extraction by saving several frames
    debug_frames = [
        (0, 0, "debug_frame_0_0.png"),
        (1, 0, "debug_frame_1_0.png"),
        (2, 0, "debug_frame_2_0.png"),
        (3, 0, "debug_frame_3_0.png"),
        (0, 1, "debug_frame_0_1.png"),
        (1, 1, "debug_frame_1_1.png"),
        (0, 2, "debug_frame_0_2.png"),
        (0, 3, "debug_frame_0_3.png"),
    ]

    for col, row, filename in debug_frames:
        if col < sprite_sheet.cols and row < sprite_sheet.rows:
            sprite_sheet.save_debug_frame(col, row, filename)

            # Also print the exact pixel coordinates being extracted
            x = col * sprite_sheet.frame_width
            y = row * sprite_sheet.frame_height
            print(f"Frame ({col},{row}) extracts pixels ({x},{y}) to ({x+sprite_sheet.frame_width},{y+sprite_sheet.frame_height})")
        else:
            print(f"Frame ({col},{row}) is out of bounds")

    pygame.quit()

if __name__ == "__main__":
    debug_sprite_extraction()