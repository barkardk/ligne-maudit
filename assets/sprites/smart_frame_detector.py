import pygame

def analyze_sprite_sheet_dimensions(image_path):
    """
    Analyze a sprite sheet to determine the most likely frame size
    """
    try:
        sheet = pygame.image.load(image_path).convert_alpha()
        width, height = sheet.get_size()

        print(f"Analyzing sprite sheet: {width}x{height} pixels")

        # Common sprite sheet layouts and their typical frame counts
        common_layouts = [
            # (frames_wide, frames_tall, typical_frame_width, typical_frame_height)
            (4, 4, width//4, height//4),    # 4x4 grid - most common for character sheets
            (3, 4, width//3, height//4),    # 3x4 grid
            (4, 8, width//4, height//8),    # 4x8 grid
            (8, 4, width//8, height//4),    # 8x4 grid
            (6, 8, width//6, height//8),    # 6x8 grid
            (8, 8, width//8, height//8),    # 8x8 grid
            (12, 8, width//12, height//8),  # 12x8 grid
            (16, 16, width//16, height//16), # 16x16 grid
            (8, 12, width//8, height//12),  # 8x12 grid
            (16, 12, width//16, height//12), # 16x12 grid
            (32, 24, width//32, height//24), # 32x24 grid (for very detailed sheets)
        ]

        # Score each layout based on how reasonable the frame size looks
        best_score = 0
        best_layout = None

        for frames_w, frames_h, frame_w, frame_h in common_layouts:
            score = score_frame_size(frame_w, frame_h, frames_w, frames_h)
            print(f"Layout {frames_w}x{frames_h}: frame size {frame_w}x{frame_h}, score: {score}")

            if score > best_score:
                best_score = score
                best_layout = (frames_w, frames_h, frame_w, frame_h)

        if best_layout:
            frames_w, frames_h, frame_w, frame_h = best_layout
            print(f"Best layout: {frames_w}x{frames_h} frames of {frame_w}x{frame_h} pixels each")
            return frame_w, frame_h
        else:
            print("Could not determine good frame size")
            return None, None

    except Exception as e:
        print(f"Error analyzing sprite sheet: {e}")
        return None, None

def score_frame_size(frame_w, frame_h, frames_w, frames_h):
    """
    Score how good a frame size looks for a character sprite
    Higher score = better
    """
    score = 0

    # Prefer frame sizes that are reasonable for characters (expanded for high-res)
    if 16 <= frame_w <= 512 and 16 <= frame_h <= 512:
        score += 50

    # Prefer slightly taller than wide (typical for characters)
    if frame_h >= frame_w:
        score += 20

    # Prefer common character sprite sizes (including high-resolution)
    common_sizes = [
        (16, 24), (24, 32), (32, 32), (32, 48), (48, 64), (64, 64),
        (64, 96), (96, 128), (128, 192), (256, 384)  # High-res sizes
    ]
    for common_w, common_h in common_sizes:
        if abs(frame_w - common_w) <= 16 and abs(frame_h - common_h) <= 16:
            score += 100
            break

    # Special bonus for 1024x1536 sheets with 4x4 layout (256x384 frames)
    if frame_w == 256 and frame_h == 384:
        score += 150

    # Special bonus for processed sprite sheets with 48x64 frames (from slice_scale_pack)
    if frame_w == 48 and frame_h == 64:
        score += 200  # Highest priority for processed sprites

    # Prefer layouts that would have 12-64 total frames (reasonable for sprite sheets)
    total_frames = frames_w * frames_h
    if 12 <= total_frames <= 64:
        score += 30
    elif 64 < total_frames <= 128:
        score += 10

    # Avoid tiny frames
    if frame_w < 12 or frame_h < 12:
        score -= 100

    # Avoid huge frames
    if frame_w > 200 or frame_h > 200:
        score -= 50

    return score

def get_smart_frame_size(filename):
    """
    Get the best frame size for a sprite sheet using smart analysis
    """
    import os

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sheet_path = os.path.join(project_root, "assets", "images", "sprites", filename)

    if os.path.exists(sheet_path):
        return analyze_sprite_sheet_dimensions(sheet_path)
    else:
        return None, None