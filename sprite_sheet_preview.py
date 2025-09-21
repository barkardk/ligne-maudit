#!/usr/bin/env python3
"""
Visual sprite sheet frame preview tool
Helps you see exactly what frames are being extracted
"""
import pygame
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from assets.sprites.sprite_sheet_loader import SpriteSheet

def main():
    pygame.init()

    # Create a window to show the preview
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Sprite Sheet Frame Preview")
    clock = pygame.time.Clock()

    # Load sprite sheet with different frame sizes to test
    test_sizes = [
        (64, 96),   # Smart detection suggestion
        (32, 48),   # Half size
        (128, 192), # Double size
        (48, 64),   # Different ratio
        (96, 128),  # Larger
        (80, 120),  # Custom size
    ]

    current_size_index = 0
    sprite_sheets = []

    # Load all test sizes
    for frame_w, frame_h in test_sizes:
        sheet = SpriteSheet("protagonist.png", frame_w, frame_h, scale_factor=2)
        sprite_sheets.append((sheet, frame_w, frame_h))

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Cycle through different frame sizes
                    current_size_index = (current_size_index + 1) % len(sprite_sheets)
                    print(f"Switched to frame size: {test_sizes[current_size_index]}")
                elif event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((50, 50, 50))

        # Get current sprite sheet
        current_sheet, frame_w, frame_h = sprite_sheets[current_size_index]

        if current_sheet.sheet:
            # Show info
            font = pygame.font.Font(None, 36)
            info_text = font.render(f"Frame size: {frame_w}x{frame_h} (Press SPACE to cycle)", True, (255, 255, 255))
            screen.blit(info_text, (10, 10))

            # Show grid info
            grid_text = font.render(f"Grid: {current_sheet.cols}x{current_sheet.rows} frames", True, (255, 255, 255))
            screen.blit(grid_text, (10, 50))

            # Show first few frames to see what we're extracting
            y_offset = 100
            for row in range(min(4, current_sheet.rows)):
                x_offset = 10
                for col in range(min(8, current_sheet.cols)):
                    frame = current_sheet.get_frame(col, row)
                    if frame:
                        screen.blit(frame, (x_offset, y_offset))

                        # Draw frame border
                        frame_rect = pygame.Rect(x_offset, y_offset, frame.get_width(), frame.get_height())
                        pygame.draw.rect(screen, (100, 100, 100), frame_rect, 1)

                        # Label the frame
                        label_font = pygame.font.Font(None, 24)
                        label = label_font.render(f"{col},{row}", True, (255, 255, 0))
                        screen.blit(label, (x_offset, y_offset - 20))

                        x_offset += frame.get_width() + 10

                y_offset += (frame.get_height() if frame else 100) + 30
        else:
            error_text = font.render("Could not load sprite sheet", True, (255, 0, 0))
            screen.blit(error_text, (10, 100))

        # Instructions
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "SPACE: Cycle through frame sizes",
            "ESC: Exit",
            "Look for the size where characters look complete"
        ]

        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            screen.blit(text, (10, screen.get_height() - 80 + i * 25))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()