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
    parser.add_argument('--scene', type=int, choices=[0, 1, 2, 3, 4, 5],
                       help='Start directly in a specific scene (0=story, 1=forest path, 2=field, 3=behind bunker, 4=dragonteeth, 5=bunker interior)')

    args = parser.parse_args()

    pygame.init()
    game = Game(start_scene=args.scene)
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
