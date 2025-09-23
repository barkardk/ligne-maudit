import pygame
import os
import random
from .sprite_sheet_loader import SpriteSheet, AnimationManager
from .smart_frame_detector import get_smart_frame_size

def create_rat_animation_system():
    """Create enemy animation system - randomly choose single or dual enemies"""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # Random choice: 1/3 chance each for cockroach, frog, or both
        choice = random.choice(["cockroach", "frog", "both"])

        if choice == "cockroach":
            enemy_data, success = create_cockroach_animation_system(project_root)
            if success:
                return enemy_data, success, "cockroach", 3, "BITE"
        elif choice == "frog":
            enemy_data, success = create_frog_animation_system(project_root)
            if success:
                return enemy_data, success, "frog", 4, "POISON"
        else:  # both - start with cockroach, will switch to frog during combat
            enemy_data, success = create_cockroach_animation_system(project_root)
            if success:
                return enemy_data, success, "both", [3, 4], ["BITE", "POISON"]

        # Fallback if creation fails
        return create_fallback_rat_animation(), False, "rat", 5, "CLAWS"

    except Exception as e:
        print(f"Error loading enemy sprite sheet: {e}")
        return create_fallback_rat_animation(), False, "rat", 5, "CLAWS"

def create_rat_sprite_animation_system(project_root):
    """Create rat animation system from rat.png sprite sheet"""
    try:
        rat_path = os.path.join(project_root, "assets", "images", "sprites", "enemies", "rat.png")

        # Create sprite sheet with correct frame size for 2x4 grid
        # The sprite sheet is 1024x1536, so each frame is 512x384
        # But we need more height to include the feet - let's try 512x400
        frame_width = 512
        frame_height = 400
        rat_sheet = SpriteSheet(rat_path, frame_width, frame_height)

        if not rat_sheet.sheet:
            print("Failed to load rat sprite sheet, using fallback")
            return create_fallback_rat_animation(), False

        sheet_width, sheet_height = rat_sheet.sheet.get_size()
        cols = 2  # Known to be 2 columns
        rows = 4  # Known to be 4 rows
        print(f"Rat sprite sheet: {sheet_width}x{sheet_height}")
        print(f"Grid: {cols}x{rows} frames of {frame_width}x{frame_height}")

        # Test frame extraction
        test_frame = rat_sheet.get_frame(0, 0)
        if test_frame:
            print(f"Test frame extracted successfully: {test_frame.get_size()}")
        else:
            print("Failed to extract test frame")

        # Extract all 8 frames in 2x4 pattern (2 columns, 4 rows)
        all_frames = []
        for row in range(rows):
            for col in range(cols):
                frame = rat_sheet.get_frame(col, row)
                if frame:
                    all_frames.append(frame)
                    # Save debug frames to verify extraction
                    if len(all_frames) <= 8:
                        rat_sheet.save_debug_frame(col, row, f"debug_rat_2x4_{row}_{col}.png")

        print(f"Extracted {len(all_frames)} rat frames from 2x4 grid")

        if len(all_frames) < 8:
            print(f"Warning: Only extracted {len(all_frames)} frames, expected 8")

        # Create animation manager
        animation_manager = AnimationManager()

        # With 8 frames in 2x4 grid, organize as follows:
        # Row 0 (Frames 0-1): Initial anticipation/idle
        # Row 1 (Frames 2-3): Attack wind-up
        # Row 2 (Frames 4-5): Attack impact
        # Row 3 (Frames 6-7): Recovery/waiting

        # Initial selection phase - gentle idle breathing
        if len(all_frames) >= 2:
            initial_frames = [all_frames[0], all_frames[1]]  # Row 0
            animation_manager.add_animation('initial_selection', initial_frames, speed=800, loop=True)
        else:
            animation_manager.add_animation('initial_selection', [all_frames[0]], speed=800, loop=True)

        # Rat attack sequence - wind-up to impact
        if len(all_frames) >= 6:
            attack_sequence = [
                all_frames[2],  # Wind up start (row 1, col 0)
                all_frames[3],  # Wind up end (row 1, col 1)
                all_frames[4],  # IMPACT! (row 2, col 0)
                all_frames[5]   # Impact end (row 2, col 1)
            ]
            animation_manager.add_animation('rat_attack', attack_sequence, speed=300, loop=False)
        elif len(all_frames) >= 4:
            animation_manager.add_animation('rat_attack', all_frames[2:6], speed=300, loop=False)
        else:
            animation_manager.add_animation('rat_attack', all_frames[:2], speed=300, loop=False)

        # Waiting phase - recovery and neutral pose
        if len(all_frames) >= 8:
            waiting_frames = [all_frames[6], all_frames[7]]  # Row 3
            animation_manager.add_animation('waiting', waiting_frames, speed=900, loop=True)
        else:
            animation_manager.add_animation('waiting', [all_frames[-1]], speed=900, loop=True)

        # Set default animation to initial selection
        animation_manager.play_animation('initial_selection')

        print("Rat animation system created with 2x4 sprite sheet")
        return animation_manager, True

    except Exception as e:
        print(f"Error loading rat sprite sheet: {e}")
        return create_fallback_rat_animation(), False

def create_cockroach_animation_system(project_root):
    """Create cockroach animation system from cockroach.png sprite sheet"""
    try:
        cockroach_path = os.path.join(project_root, "assets", "images", "sprites", "enemies", "cockroach.png")

        # Cockroach sprite sheet is 3x3 grid (3 columns, 3 rows) = 9 frames
        # 1024x1024 sheet divided by 3x3 = 341x341 per frame
        frame_width = 341
        frame_height = 341
        cockroach_sheet = SpriteSheet(cockroach_path, frame_width, frame_height)

        if not cockroach_sheet.sheet:
            print("Failed to load cockroach sprite sheet, using fallback")
            return create_fallback_rat_animation(), False

        sheet_width, sheet_height = cockroach_sheet.sheet.get_size()
        cols = 3  # Known to be 3 columns
        rows = 3  # Known to be 3 rows
        print(f"Cockroach sprite sheet: {sheet_width}x{sheet_height}")
        print(f"Grid: {cols}x{rows} frames of {frame_width}x{frame_height}")

        # Test frame extraction
        test_frame = cockroach_sheet.get_frame(0, 0)
        if test_frame:
            print(f"Test cockroach frame extracted successfully: {test_frame.get_size()}")
        else:
            print("Failed to extract test cockroach frame")

        # Extract all 9 frames in 3x3 pattern
        all_frames = []
        for row in range(rows):
            for col in range(cols):
                frame = cockroach_sheet.get_frame(col, row)
                if frame:
                    all_frames.append(frame)
                    # Save debug frames to verify extraction
                    if len(all_frames) <= 9:
                        cockroach_sheet.save_debug_frame(col, row, f"debug_cockroach_3x3_{row}_{col}.png")

        print(f"Extracted {len(all_frames)} cockroach frames from 3x3 grid")

        if len(all_frames) < 9:
            print(f"Warning: Only extracted {len(all_frames)} frames, expected 9")

        # Create animation manager
        animation_manager = AnimationManager()

        # With 9 frames in 3x3 grid, organize as follows:
        # Row 0 (Frames 0-2): Initial anticipation/idle
        # Row 1 (Frames 3-5): Attack sequence
        # Row 2 (Frames 6-8): Recovery/waiting

        # Initial selection phase - gentle idle movement
        if len(all_frames) >= 3:
            initial_frames = [all_frames[0], all_frames[1], all_frames[2]]  # Row 0
            animation_manager.add_animation('initial_selection', initial_frames, speed=600, loop=True)
        else:
            animation_manager.add_animation('initial_selection', [all_frames[0]], speed=600, loop=True)

        # Cockroach attack sequence
        if len(all_frames) >= 6:
            attack_sequence = [
                all_frames[3],  # Attack start (row 1, col 0)
                all_frames[4],  # Attack mid (row 1, col 1)
                all_frames[5]   # Attack end (row 1, col 2)
            ]
            animation_manager.add_animation('rat_attack', attack_sequence, speed=250, loop=False)
        else:
            animation_manager.add_animation('rat_attack', all_frames[3:6] if len(all_frames) >= 6 else all_frames[:3], speed=250, loop=False)

        # Waiting phase - recovery and neutral pose
        if len(all_frames) >= 9:
            waiting_frames = [all_frames[6], all_frames[7], all_frames[8]]  # Row 2
            animation_manager.add_animation('waiting', waiting_frames, speed=800, loop=True)
        else:
            animation_manager.add_animation('waiting', [all_frames[-1]], speed=800, loop=True)

        # Set default animation to initial selection
        animation_manager.play_animation('initial_selection')

        print("Cockroach animation system created with 3x3 sprite sheet")
        return animation_manager, True

    except Exception as e:
        print(f"Error loading cockroach sprite sheet: {e}")
        return create_fallback_rat_animation(), False

def create_frog_animation_system(project_root):
    """Create poison frog animation system from poison_frog.png sprite sheet"""
    try:
        frog_path = os.path.join(project_root, "assets", "images", "sprites", "enemies", "poison_frog.png")

        # Poison frog sprite sheet is also 3x3 grid (3 columns, 3 rows) = 9 frames
        # Same frame size as cockroach
        frame_width = 341
        frame_height = 341
        frog_sheet = SpriteSheet(frog_path, frame_width, frame_height)

        if not frog_sheet.sheet:
            print("Failed to load poison frog sprite sheet, using fallback")
            return create_fallback_rat_animation(), False

        sheet_width, sheet_height = frog_sheet.sheet.get_size()
        cols = 3  # Known to be 3 columns
        rows = 3  # Known to be 3 rows
        print(f"Poison frog sprite sheet: {sheet_width}x{sheet_height}")
        print(f"Grid: {cols}x{rows} frames of {frame_width}x{frame_height}")

        # Test frame extraction
        test_frame = frog_sheet.get_frame(0, 0)
        if test_frame:
            print(f"Test frog frame extracted successfully: {test_frame.get_size()}")
        else:
            print("Failed to extract test frog frame")

        # Extract all 9 frames in 3x3 pattern
        all_frames = []
        for row in range(rows):
            for col in range(cols):
                frame = frog_sheet.get_frame(col, row)
                if frame:
                    all_frames.append(frame)
                    # Save debug frames to verify extraction
                    if len(all_frames) <= 9:
                        frog_sheet.save_debug_frame(col, row, f"debug_frog_3x3_{row}_{col}.png")

        print(f"Extracted {len(all_frames)} frog frames from 3x3 grid")

        if len(all_frames) < 9:
            print(f"Warning: Only extracted {len(all_frames)} frames, expected 9")

        # Create animation manager
        animation_manager = AnimationManager()

        # With 9 frames in 3x3 grid for poison frog:
        # Row 0 (Frames 0-2): Initial idle/anticipation
        # Row 1 (Frames 3-5): Poison spewing attack sequence (mouth opening, spewing)
        # Row 2 (Frames 6-8): Recovery/waiting (mouth closing, return to idle)

        # Initial selection phase - gentle idle breathing
        if len(all_frames) >= 3:
            initial_frames = [all_frames[0], all_frames[1], all_frames[2]]  # Row 0
            animation_manager.add_animation('initial_selection', initial_frames, speed=700, loop=True)
        else:
            animation_manager.add_animation('initial_selection', [all_frames[0]], speed=700, loop=True)

        # Poison frog attack sequence - spewing poison
        if len(all_frames) >= 6:
            attack_sequence = [
                all_frames[3],  # Mouth opening (row 1, col 0)
                all_frames[4],  # Spewing poison (row 1, col 1)
                all_frames[5]   # Full poison spray (row 1, col 2)
            ]
            animation_manager.add_animation('rat_attack', attack_sequence, speed=300, loop=False)
        else:
            animation_manager.add_animation('rat_attack', all_frames[3:6] if len(all_frames) >= 6 else all_frames[:3], speed=300, loop=False)

        # Waiting phase - recovery and return to neutral
        if len(all_frames) >= 9:
            waiting_frames = [all_frames[6], all_frames[7], all_frames[8]]  # Row 2
            animation_manager.add_animation('waiting', waiting_frames, speed=850, loop=True)
        else:
            animation_manager.add_animation('waiting', [all_frames[-1]], speed=850, loop=True)

        # Set default animation to initial selection
        animation_manager.play_animation('initial_selection')

        print("Poison frog animation system created with 3x3 sprite sheet")
        return animation_manager, True

    except Exception as e:
        print(f"Error loading poison frog sprite sheet: {e}")
        return create_fallback_rat_animation(), False

def create_fallback_rat_animation():
    """Create a fallback rat animation using the existing custom drawn rat"""
    # Create a dummy animation manager with the custom rat
    animation_manager = AnimationManager()

    # Create a basic rat sprite
    rat_surface = create_basic_rat_sprite()

    # Add simple animations with the correct names for the combat system
    animation_manager.add_animation('initial_selection', [rat_surface], speed=1000, loop=True)
    animation_manager.add_animation('rat_attack', [rat_surface], speed=500, loop=False)
    animation_manager.add_animation('waiting', [rat_surface], speed=1000, loop=True)

    animation_manager.play_animation('initial_selection')

    print("Using fallback rat animation")
    return animation_manager

def create_basic_rat_sprite():
    """Create a basic rat sprite as fallback"""
    rat_surface = pygame.Surface((64, 48), pygame.SRCALPHA)

    # Body (large gray oval)
    pygame.draw.ellipse(rat_surface, (100, 90, 80), (16, 16, 40, 24))
    pygame.draw.ellipse(rat_surface, (120, 110, 100), (18, 18, 36, 20))  # Lighter belly

    # Head (larger gray circle)
    pygame.draw.circle(rat_surface, (110, 100, 90), (12, 24), 12)
    pygame.draw.circle(rat_surface, (130, 120, 110), (12, 24), 10)  # Lighter face

    # Ears (larger triangular ears)
    pygame.draw.polygon(rat_surface, (80, 70, 60), [(4, 16), (8, 8), (12, 16)])
    pygame.draw.polygon(rat_surface, (60, 50, 40), [(8, 16), (12, 8), (16, 16)])
    # Inner ears (pink)
    pygame.draw.polygon(rat_surface, (200, 150, 150), [(6, 14), (8, 10), (10, 14)])
    pygame.draw.polygon(rat_surface, (200, 150, 150), [(10, 14), (12, 10), (14, 14)])

    # Eyes (larger black eyes with white pupils)
    pygame.draw.circle(rat_surface, (0, 0, 0), (8, 20), 3)
    pygame.draw.circle(rat_surface, (0, 0, 0), (16, 20), 3)
    pygame.draw.circle(rat_surface, (255, 255, 255), (9, 19), 1)
    pygame.draw.circle(rat_surface, (255, 255, 255), (17, 19), 1)

    # Nose (small pink triangle)
    pygame.draw.polygon(rat_surface, (200, 100, 100), [(11, 26), (13, 26), (12, 28)])

    # Mouth (small line)
    pygame.draw.line(rat_surface, (0, 0, 0), (12, 28), (12, 30), 1)

    # Front paws
    pygame.draw.circle(rat_surface, (90, 80, 70), (20, 35), 4)
    pygame.draw.circle(rat_surface, (90, 80, 70), (28, 35), 4)

    # Back paws
    pygame.draw.ellipse(rat_surface, (90, 80, 70), (45, 32, 8, 12))
    pygame.draw.ellipse(rat_surface, (90, 80, 70), (52, 32, 8, 12))

    # Tail (thicker curved tail)
    tail_points = [(56, 28), (58, 26), (60, 22), (61, 18), (62, 14)]
    for i in range(len(tail_points)-1):
        pygame.draw.line(rat_surface, (90, 80, 70), tail_points[i], tail_points[i+1], 3)

    # Whiskers (longer black lines)
    pygame.draw.line(rat_surface, (0, 0, 0), (0, 22), (8, 20), 1)
    pygame.draw.line(rat_surface, (0, 0, 0), (0, 24), (8, 24), 1)
    pygame.draw.line(rat_surface, (0, 0, 0), (0, 26), (8, 28), 1)

    return rat_surface