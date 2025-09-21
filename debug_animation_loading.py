#!/usr/bin/env python3
"""Debug animation loading to see exact code path"""

import pygame
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from assets.sprites.sprite_sheet_loader import load_protagonist_from_sprite_sheet

def debug_animation_loading():
    pygame.init()
    screen = pygame.display.set_mode((100, 100))

    print("=== TESTING EXACT GAME CODE PATH ===")

    # Run the exact same function the game uses
    animation_manager, sprite_sheet_used = load_protagonist_from_sprite_sheet()

    if animation_manager:
        print(f"Animation manager created successfully")
        print(f"Using sprite sheet: {sprite_sheet_used}")

        # Check available animations
        if hasattr(animation_manager, 'animations'):
            print(f"Available animations: {list(animation_manager.animations.keys())}")

            # Check frame counts for each animation
            for anim_name, anim_data in animation_manager.animations.items():
                frame_count = len(anim_data['frames'])
                print(f"{anim_name}: {frame_count} frames")
    else:
        print("Animation manager was None")

    pygame.quit()

if __name__ == "__main__":
    debug_animation_loading()