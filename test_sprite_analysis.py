#!/usr/bin/env python3
import pygame
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from assets.sprites.smart_frame_detector import get_smart_frame_size

def main():
    pygame.init()
    # Create a minimal display for pygame
    pygame.display.set_mode((100, 100))

    print("Analyzing protagonist.png sprite sheet...")
    frame_w, frame_h = get_smart_frame_size("protagonist.png")

    if frame_w and frame_h:
        print(f"Recommended frame size: {frame_w}x{frame_h}")
    else:
        print("Could not determine frame size")

    pygame.quit()

if __name__ == "__main__":
    main()