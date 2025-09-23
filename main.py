#!/usr/bin/env python3
"""
Ligne Maudite  - A Final Fantasy-style turn-based RPG
Set in the cursed underground bunkers of the Maginot Line during WWII.
"""

import pygame
import sys
import argparse
from src.game import Game

def main():
    parser = argparse.ArgumentParser(description='Ligne Maudite - Underground Bunker RPG')
    parser.add_argument('--scene',
                       help='Start directly in a specific scene (0=story, 1=forest path, 2=field, 3=behind bunker, 4=dragonteeth, 5=bunker interior, fight0=battle arena)')

    args = parser.parse_args()

    # Handle different scene types
    scene = args.scene
    if scene is not None:
        if scene == "fight0":
            start_scene = "fight0"
        else:
            try:
                start_scene = int(scene)
                if start_scene not in [0, 1, 2, 3, 4, 5]:
                    print("Invalid scene number. Use 0-5 or fight0")
                    sys.exit(1)
            except ValueError:
                print("Invalid scene. Use 0-5 or fight0")
                sys.exit(1)
    else:
        start_scene = None

    pygame.init()
    game = Game(start_scene=start_scene)
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
