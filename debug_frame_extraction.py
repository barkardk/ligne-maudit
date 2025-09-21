#!/usr/bin/env python3
"""Debug frame extraction to see what's happening"""

import pygame
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from assets.sprites.sprite_sheet_loader import SpriteSheet

def debug_frame_extraction():
    pygame.init()
    screen = pygame.display.set_mode((100, 100))

    # Create sprite sheet exactly like the game does
    sprite_sheet = SpriteSheet("protagonist.png", 256, 384, scale_factor=1.0)

    if sprite_sheet.sheet:
        print(f"Sheet size: {sprite_sheet.sheet.get_size()}")
        print(f"Frame size: {sprite_sheet.frame_width}x{sprite_sheet.frame_height}")
        print(f"Grid: {sprite_sheet.cols}x{sprite_sheet.rows}")
        print(f"Condition sprite_sheet.cols >= 4: {sprite_sheet.cols >= 4}")

        if sprite_sheet.cols >= 4:
            print("\n=== USING MAIN BRANCH (cols >= 4) ===")

            # Extract exactly like the code does
            print("Extracting idle frames...")
            idle_down = sprite_sheet.get_animation_frames(0, 0, 1, 'horizontal')
            print(f"idle_down frames: {len(idle_down)}")

            print("Extracting walking frames...")
            walk_down = sprite_sheet.get_animation_frames(1, 0, 3, 'horizontal')
            walk_left = sprite_sheet.get_animation_frames(1, 1, 3, 'horizontal')
            walk_right = sprite_sheet.get_animation_frames(1, 2, 3, 'horizontal')
            walk_up = sprite_sheet.get_animation_frames(1, 3, 3, 'horizontal')

            print(f"walk_down frames: {len(walk_down)}")
            print(f"walk_left frames: {len(walk_left)}")
            print(f"walk_right frames: {len(walk_right)}")
            print(f"walk_up frames: {len(walk_up)}")

        else:
            print("\n=== USING FALLBACK BRANCH (cols < 4) ===")
            # This shouldn't happen but let's see what would happen
            walk_down = sprite_sheet.get_animation_frames(0, 0, min(4, sprite_sheet.cols), 'horizontal')
            print(f"fallback walk_down frames: {len(walk_down)}")

        # Also test individual frame extraction
        print("\n=== TESTING INDIVIDUAL FRAMES ===")
        for row in range(min(2, sprite_sheet.rows)):
            for col in range(min(4, sprite_sheet.cols)):
                frame = sprite_sheet.get_frame(col, row)
                if frame:
                    print(f"Frame {col},{row}: exists, size {frame.get_size()}")
                else:
                    print(f"Frame {col},{row}: None")

    pygame.quit()

if __name__ == "__main__":
    debug_frame_extraction()