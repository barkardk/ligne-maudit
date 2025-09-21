#!/usr/bin/env python3
"""Visual test to show where the door is located"""

import pygame
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from src.states.field import FieldState
from assets.backgrounds.collision_map import create_maginot_collision_map

def show_door_location():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Door Location Visualization")

    # Create field state to get current door coordinates
    field_state = FieldState(screen)

    print("=== DOOR LOCATION ANALYSIS ===")
    print(f"Screen size: {screen.get_size()}")
    print(f"Door coordinates in field.py: ({field_state.door_x}, {field_state.door_y})")
    print(f"Door interaction distance: {field_state.door_interaction_distance}")

    # Check collision map calculation
    collision_map = create_maginot_collision_map(1024, 768)

    # Create a visual representation
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Draw background
        screen.blit(field_state.background, (0, 0))

        # Draw door location as a bright red circle
        pygame.draw.circle(screen, (255, 0, 0), (int(field_state.door_x), int(field_state.door_y)), 10)

        # Draw door interaction area as a semi-transparent circle
        door_surface = pygame.Surface((field_state.door_interaction_distance * 2, field_state.door_interaction_distance * 2))
        door_surface.set_alpha(100)
        door_surface.fill((255, 255, 0))
        pygame.draw.circle(door_surface, (255, 255, 0),
                          (field_state.door_interaction_distance, field_state.door_interaction_distance),
                          field_state.door_interaction_distance)
        screen.blit(door_surface, (field_state.door_x - field_state.door_interaction_distance,
                                  field_state.door_y - field_state.door_interaction_distance))

        # Draw protagonist for reference
        protagonist_sprite = field_state.protagonist_animation.get_current_frame()
        if protagonist_sprite and field_state.character_display_scale != 1.0:
            scaled_width = int(protagonist_sprite.get_width() * field_state.character_display_scale)
            scaled_height = int(protagonist_sprite.get_height() * field_state.character_display_scale)
            protagonist_sprite = pygame.transform.scale(protagonist_sprite, (scaled_width, scaled_height))

        if protagonist_sprite:
            screen.blit(protagonist_sprite, (int(field_state.protagonist_x), int(field_state.protagonist_y)))

        # Draw legend
        font = pygame.font.Font(None, 24)
        legend_texts = [
            "RED CIRCLE = Door location",
            "YELLOW AREA = Interaction zone",
            "BLUE CHARACTER = Protagonist",
            "ESC = Exit"
        ]

        for i, text in enumerate(legend_texts):
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.topleft = (10, 50 + i * 25)

            # Background for text
            bg_rect = text_rect.inflate(10, 5)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            screen.blit(text_surface, text_rect)

        pygame.display.flip()
        clock.tick(60)

    print("\n=== COORDINATE ANALYSIS ===")
    print("If the red circle is NOT on a door in the background image,")
    print("then the door coordinates need to be adjusted.")
    print(f"Current door position: ({field_state.door_x}, {field_state.door_y})")

    pygame.quit()

if __name__ == "__main__":
    show_door_location()