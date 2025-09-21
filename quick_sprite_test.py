#!/usr/bin/env python3
"""
Quick test to see what's being extracted from the sprite sheet
"""
import pygame
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    pygame.init()
    pygame.display.set_mode((100, 100))  # Minimal display

    # Test extraction with 256x384 frames
    sheet_path = "assets/images/sprites/protagonist.png"

    try:
        sheet = pygame.image.load(sheet_path).convert_alpha()
        width, height = sheet.get_size()
        print(f"Sprite sheet loaded: {width}x{height}")

        # Extract 4x4 grid with 256x384 frames
        frame_w, frame_h = 256, 384

        print(f"Extracting {frame_w}x{frame_h} frames...")
        print(f"This gives us {width//frame_w}x{height//frame_h} grid")

        # Extract and save first few frames
        debug_dir = "debug_frames"
        os.makedirs(debug_dir, exist_ok=True)

        for row in range(min(2, height//frame_h)):
            for col in range(min(2, width//frame_w)):
                x = col * frame_w
                y = row * frame_h

                # Extract frame
                frame_rect = pygame.Rect(x, y, frame_w, frame_h)
                frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), frame_rect)

                # Save frame
                filename = f"extracted_frame_row{row}_col{col}.png"
                pygame.image.save(frame, os.path.join(debug_dir, filename))
                print(f"Saved {filename} (size: {frame.get_size()})")

        print(f"\nFrames saved to {debug_dir}/")
        print("Check these files to see if the character sprites look correct")

    except Exception as e:
        print(f"Error: {e}")

    pygame.quit()

if __name__ == "__main__":
    main()