#!/usr/bin/env python3
"""Final test to verify sprite frames are correct and no overlap"""

import pygame
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from src.states.field import FieldState

def test_final_sprites():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Final Sprite Test")

    print("=== FINAL SPRITE TEST ===")

    # Create field state (exactly like the game does)
    field_state = FieldState(screen)

    print(f"Character display scale: {field_state.character_display_scale}")

    # Check the current frame
    current_frame = field_state.protagonist_animation.get_current_frame()
    if current_frame:
        frame_w, frame_h = current_frame.get_size()
        print(f"Current frame size: {frame_w}x{frame_h}")

        # Save the current frame to inspect visually
        pygame.image.save(current_frame, "final_test_frame.png")
        print("Saved final_test_frame.png for visual inspection")

        # Test different animations to see if they look correct
        animations_to_test = ['idle_down', 'walk_down', 'walk_left', 'walk_right']

        for anim_name in animations_to_test:
            field_state.protagonist_animation.play_animation(anim_name)
            field_state.protagonist_animation.update(0.1)  # Update animation
            test_frame = field_state.protagonist_animation.get_current_frame()

            if test_frame:
                print(f"{anim_name} frame size: {test_frame.get_size()}")
                pygame.image.save(test_frame, f"final_test_{anim_name}.png")
                print(f"Saved final_test_{anim_name}.png")

    print("\n=== FRAME SIZE ANALYSIS ===")
    print("Expected behavior:")
    print("- Frame size should be 256x384 (original sprite sheet)")
    print("- Display scale should be 0.25 for rendering")
    print("- No parts from adjacent frames should be visible")
    print("- Character should appear properly sized in game")

    # Verify the actual rendered size
    if current_frame:
        actual_w = int(current_frame.get_width() * field_state.character_display_scale)
        actual_h = int(current_frame.get_height() * field_state.character_display_scale)
        print(f"\nRendered size on screen: {actual_w}x{actual_h}")
        print("This should be around 64x96 pixels for good gameplay")

    print("\n=== TEST COMPLETE ===")
    print("Check the saved images to verify no overlap or artifacts!")

    pygame.quit()

if __name__ == "__main__":
    test_final_sprites()