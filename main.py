#!/usr/bin/env python3
"""
Ligne Maudite  - A Final Fantasy-style turn-based RPG
Set in the cursed underground bunkers of the Maginot Line during WWII.
"""

import pygame
import sys
from src.game import Game

def main():
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
