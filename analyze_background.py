#!/usr/bin/env python3
"""
Analyze the background image to identify doors and entrances
"""
import pygame
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from assets.backgrounds.image_loader import load_concept_art_background
from assets.backgrounds.maginot_exterior import create_maginot_exterior_background, add_birds_to_scene

def main():
    pygame.init()
    screen = pygame.display.set_mode((1200, 900))
    pygame.display.set_caption("Background Analysis - Door Detection")

    # Load the background
    generated_bg = create_maginot_exterior_background(1024, 768)
    generated_bg = add_birds_to_scene(generated_bg)

    background = load_concept_art_background(
        1024, 768,
        fallback_function=lambda w, h: generated_bg
    )

    # Scale background for display
    scaled_bg = pygame.transform.scale(background, (1024, 768))

    clock = pygame.time.Clock()
    running = True

    # Analysis mode
    show_analysis = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    show_analysis = not show_analysis
                elif event.key == pygame.K_s:
                    # Save analyzed image
                    save_door_analysis(background)

        screen.fill((40, 40, 40))

        # Draw background
        screen.blit(scaled_bg, (50, 50))

        if show_analysis:
            # Analyze and mark potential door locations
            analyze_doors(screen, scaled_bg, (50, 50))

        # Draw UI
        font = pygame.font.Font(None, 36)
        title = font.render("Background Door Analysis", True, (255, 255, 255))
        screen.blit(title, (50, 10))

        instructions = [
            "SPACE: Toggle door analysis",
            "S: Save analysis to file",
            "Look for dark rectangular areas (doors/entrances)"
        ]

        small_font = pygame.font.Font(None, 24)
        for i, instruction in enumerate(instructions):
            text = small_font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (50, screen.get_height() - 100 + i * 25))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def analyze_doors(screen, background, offset):
    """Analyze the background for door-like features"""
    bg_width, bg_height = background.get_size()

    # Look for dark rectangular areas that could be doors
    potential_doors = []

    # Sample the background for dark areas
    for y in range(0, bg_height, 20):
        for x in range(0, bg_width, 20):
            if x < bg_width and y < bg_height:
                pixel_color = background.get_at((x, y))
                r, g, b = pixel_color[:3]

                # Look for dark areas (potential entrances)
                if r < 60 and g < 60 and b < 60:
                    potential_doors.append((x, y))

    # Draw potential door locations
    for x, y in potential_doors:
        screen_x = offset[0] + x
        screen_y = offset[1] + y
        pygame.draw.circle(screen, (255, 0, 0), (screen_x, screen_y), 3)

    # Based on the procedural background, mark known structures
    # Bunker location (from maginot_exterior.py)
    bunker_width = 180
    bunker_height = 80
    bunker_x = bg_width // 2 - bunker_width // 2 + 50
    bunker_y = bg_height // 3 + 40

    # Mark bunker area
    pygame.draw.rect(screen, (0, 255, 0),
                    (offset[0] + bunker_x, offset[1] + bunker_y, bunker_width, bunker_height), 2)

    # Mark entrance area (from procedural code)
    entrance_width = 25
    entrance_height = 35
    entrance_x = bunker_x + 30
    entrance_y = bunker_y + bunker_height - entrance_height

    pygame.draw.rect(screen, (255, 255, 0),
                    (offset[0] + entrance_x, offset[1] + entrance_y, entrance_width, entrance_height), 3)

    # Add labels
    font = pygame.font.Font(None, 24)

    # Bunker label
    bunker_label = font.render("Bunker Structure", True, (0, 255, 0))
    screen.blit(bunker_label, (offset[0] + bunker_x, offset[1] + bunker_y - 25))

    # Entrance label
    entrance_label = font.render("Main Entrance", True, (255, 255, 0))
    screen.blit(entrance_label, (offset[0] + entrance_x, offset[1] + entrance_y - 25))

    # Coordinates display
    coord_text = font.render(f"Entrance at: ({entrance_x}, {entrance_y})", True, (255, 255, 255))
    screen.blit(coord_text, (offset[0] + 20, offset[1] + bg_height + 20))

def save_door_analysis(background):
    """Save an analyzed version of the background"""
    analyzed = background.copy()

    # Mark the door location
    bunker_width = 180
    bunker_height = 80
    bg_width, bg_height = background.get_size()
    bunker_x = bg_width // 2 - bunker_width // 2 + 50
    bunker_y = bg_height // 3 + 40

    entrance_width = 25
    entrance_height = 35
    entrance_x = bunker_x + 30
    entrance_y = bunker_y + bunker_height - entrance_height

    # Draw entrance marker
    pygame.draw.rect(analyzed, (255, 255, 0),
                    (entrance_x, entrance_y, entrance_width, entrance_height), 3)

    pygame.image.save(analyzed, "background_door_analysis.png")
    print("Saved door analysis to background_door_analysis.png")
    print(f"Door location: x={entrance_x}, y={entrance_y}")
    print(f"Door size: {entrance_width}x{entrance_height}")

if __name__ == "__main__":
    main()