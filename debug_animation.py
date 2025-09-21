#!/usr/bin/env python3
"""Debug script to check animation system frame sizes"""

import pygame
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from assets.sprites.protagonist import create_protagonist_animation_system

def debug_animation():
    pygame.init()
    screen = pygame.display.set_mode((100, 100))

    # Create animation system (same as in field.py)
    protagonist_animation, using_sprite_sheet = create_protagonist_animation_system()

    print(f"Using sprite sheet: {using_sprite_sheet}")

    # Check current frame size
    current_frame = protagonist_animation.get_current_frame()
    if current_frame:
        frame_w, frame_h = current_frame.get_size()
        print(f"Current frame size: {frame_w}x{frame_h}")

        # Save the frame to inspect
        pygame.image.save(current_frame, "debug_current_frame.png")
        print("Saved debug_current_frame.png")
    else:
        print("No current frame found")

    # Check if there are animations
    if hasattr(protagonist_animation, 'animations'):
        print(f"Available animations: {list(protagonist_animation.animations.keys())}")

        # Check a few different animations
        for anim_name in ['idle_down', 'walk_down']:
            if anim_name in protagonist_animation.animations:
                frames = protagonist_animation.animations[anim_name]['frames']
                if frames:
                    first_frame = frames[0]
                    print(f"{anim_name} frame size: {first_frame.get_size()}")
                    pygame.image.save(first_frame, f"debug_{anim_name}_frame.png")
                    print(f"Saved debug_{anim_name}_frame.png")

    pygame.quit()

if __name__ == "__main__":
    debug_animation()