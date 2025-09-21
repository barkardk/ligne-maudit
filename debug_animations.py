#!/usr/bin/env python3
"""
Debug animation extraction to see what frames are being used
"""
import pygame
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from assets.sprites.sprite_sheet_loader import load_protagonist_from_sprite_sheet

def main():
    pygame.init()
    pygame.display.set_mode((100, 100))  # Minimal display

    # Load the animation system
    animation_manager, sprite_sheet = load_protagonist_from_sprite_sheet()

    if animation_manager and sprite_sheet:
        print("Animation system loaded successfully!")
        print(f"Available animations: {list(animation_manager.animations.keys())}")

        # Test each animation
        animations_to_test = ['idle_down', 'walk_down', 'idle_left', 'walk_left']

        debug_dir = "debug_animations"
        os.makedirs(debug_dir, exist_ok=True)

        for anim_name in animations_to_test:
            if anim_name in animation_manager.animations:
                frames = animation_manager.animations[anim_name]['frames']
                print(f"\n{anim_name}: {len(frames)} frames")

                # Save each frame
                for i, frame in enumerate(frames):
                    if frame:
                        filename = f"{anim_name}_frame_{i}.png"
                        filepath = os.path.join(debug_dir, filename)
                        pygame.image.save(frame, filepath)
                        print(f"  Saved {filename} (size: {frame.get_size()})")

        print(f"\nAnimation frames saved to {debug_dir}/")
        print("Check these files to see if the animations look correct")

        # Also save raw extracted frames for comparison
        print("\nRaw frame extraction test:")
        for row in range(4):
            for col in range(4):
                frame = sprite_sheet.get_frame(col, row)
                if frame:
                    filename = f"raw_row{row}_col{col}.png"
                    filepath = os.path.join(debug_dir, filename)
                    pygame.image.save(frame, filepath)
                    print(f"Saved raw {filename}")

    else:
        print("Could not load animation system")

    pygame.quit()

if __name__ == "__main__":
    main()