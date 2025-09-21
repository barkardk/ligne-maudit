#!/usr/bin/env python3
"""
Test walking animation to see frame sequence
"""
import pygame
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from assets.sprites.protagonist import create_protagonist_animation_system

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Walking Animation Test")
    clock = pygame.time.Clock()

    # Create animation system
    animation_manager, using_sprite_sheet = create_protagonist_animation_system()

    # Test variables
    current_test = 'walk_down'
    frame_time = 0
    manual_frame = 0

    font = pygame.font.Font(None, 36)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Cycle through animations
                    tests = ['idle_down', 'walk_down', 'idle_left', 'walk_left', 'idle_right', 'walk_right', 'idle_up', 'walk_up']
                    current_index = tests.index(current_test) if current_test in tests else 0
                    current_test = tests[(current_index + 1) % len(tests)]
                    animation_manager.play_animation(current_test, restart=True)
                    print(f"Testing: {current_test}")

        # Update animation
        animation_manager.play_animation(current_test)
        animation_manager.update(dt)

        # Draw
        screen.fill((50, 50, 50))

        # Show current animation
        current_frame = animation_manager.get_current_frame()
        if current_frame:
            # Scale down for display
            scaled_frame = pygame.transform.scale(current_frame, (128, 192))
            screen.blit(scaled_frame, (300, 150))

        # Show info
        info_text = font.render(f"Animation: {current_test}", True, (255, 255, 255))
        screen.blit(info_text, (50, 50))

        frame_info = font.render(f"Frame: {animation_manager.current_frame}", True, (255, 255, 255))
        screen.blit(frame_info, (50, 100))

        if current_test in animation_manager.animations:
            frame_count = len(animation_manager.animations[current_test]['frames'])
            count_info = font.render(f"Total frames: {frame_count}", True, (255, 255, 255))
            screen.blit(count_info, (50, 150))

        instructions = [
            "SPACE: Next animation",
            "Watch the frame counter",
            "Look for unwanted frames"
        ]

        small_font = pygame.font.Font(None, 24)
        for i, instruction in enumerate(instructions):
            text = small_font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (50, 400 + i * 30))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()