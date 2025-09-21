import pygame
from .sprite_sheet_loader import load_protagonist_from_sprite_sheet

def create_protagonist_sprite():
    """Create a small FF9-style protagonist sprite with blue pants and red sweater"""
    base_width = 24
    base_height = 32
    scale_factor = 2.52  # 2.8 * 0.9 = 10% smaller
    sprite_width = int(base_width * scale_factor)
    sprite_height = int(base_height * scale_factor)

    # Create at original size first
    base_sprite = pygame.Surface((base_width, base_height), pygame.SRCALPHA)

    # Define colors
    skin_color = (255, 220, 177)
    hair_color = (139, 69, 19)  # Brown hair
    red_sweater = (220, 20, 60)
    blue_pants = (30, 144, 255)
    shoe_color = (101, 67, 33)  # Brown shoes
    gun_color = (64, 64, 64)  # Dark gray gun

    # Head (circle)
    head_center = (base_width // 2, 8)
    pygame.draw.circle(base_sprite, skin_color, head_center, 6)

    # Hair (simple spiky style reminiscent of FF characters)
    hair_points = [
        (head_center[0] - 4, head_center[1] - 3),
        (head_center[0] - 2, head_center[1] - 6),
        (head_center[0], head_center[1] - 7),
        (head_center[0] + 2, head_center[1] - 6),
        (head_center[0] + 4, head_center[1] - 3),
        (head_center[0] + 3, head_center[1] + 2),
        (head_center[0] - 3, head_center[1] + 2)
    ]
    pygame.draw.polygon(base_sprite, hair_color, hair_points)

    # Eyes (simple dots)
    pygame.draw.circle(base_sprite, (0, 0, 0), (head_center[0] - 2, head_center[1] - 1), 1)
    pygame.draw.circle(base_sprite, (0, 0, 0), (head_center[0] + 2, head_center[1] - 1), 1)

    # Red sweater (upper body)
    sweater_rect = pygame.Rect(base_width // 2 - 6, 14, 12, 10)
    pygame.draw.rect(base_sprite, red_sweater, sweater_rect)

    # Arms
    left_arm = pygame.Rect(base_width // 2 - 8, 16, 3, 8)
    right_arm = pygame.Rect(base_width // 2 + 5, 16, 3, 8)
    pygame.draw.rect(base_sprite, red_sweater, left_arm)
    pygame.draw.rect(base_sprite, red_sweater, right_arm)

    # Hands
    pygame.draw.circle(base_sprite, skin_color, (base_width // 2 - 7, 24), 2)
    pygame.draw.circle(base_sprite, skin_color, (base_width // 2 + 6, 24), 2)

    # Blue pants
    pants_rect = pygame.Rect(base_width // 2 - 5, 24, 10, 6)
    pygame.draw.rect(base_sprite, blue_pants, pants_rect)

    # Shoes
    left_shoe = pygame.Rect(base_width // 2 - 5, 30, 4, 2)
    right_shoe = pygame.Rect(base_width // 2 + 1, 30, 4, 2)
    pygame.draw.rect(base_sprite, shoe_color, left_shoe)
    pygame.draw.rect(base_sprite, shoe_color, right_shoe)

    # Small gun in right hand
    gun_rect = pygame.Rect(base_width // 2 + 6, 20, 6, 3)
    pygame.draw.rect(base_sprite, gun_color, gun_rect)
    # Gun barrel
    barrel_rect = pygame.Rect(base_width // 2 + 12, 21, 3, 1)
    pygame.draw.rect(base_sprite, gun_color, barrel_rect)

    # Scale up the sprite 4x with nearest neighbor for pixel-perfect scaling
    scaled_sprite = pygame.transform.scale(base_sprite, (sprite_width, sprite_height))

    return scaled_sprite

def create_protagonist_animation_system():
    """
    Create protagonist animation system, trying sprite sheet first, then falling back to procedural
    """
    # Try to load from sprite sheet first
    animation_manager, sprite_sheet = load_protagonist_from_sprite_sheet()

    if animation_manager:
        print("Using sprite sheet for protagonist animations")
        return animation_manager, True

    print("No sprite sheet found, using procedural animations")

    # Fall back to procedural animation
    from .sprite_sheet_loader import AnimationManager
    animation_manager = AnimationManager()

    # Create procedural frames
    frames = create_protagonist_walking_frames()

    # Add procedural animations with directional idle poses
    animation_manager.add_animation('idle', [frames[0]], speed=1000)
    animation_manager.add_animation('idle_down', [frames[0]], speed=1000)
    animation_manager.add_animation('idle_left', [frames[0]], speed=1000)
    animation_manager.add_animation('idle_right', [frames[0]], speed=1000)
    animation_manager.add_animation('idle_up', [frames[0]], speed=1000)
    animation_manager.add_animation('walk_down', frames, speed=150)
    animation_manager.add_animation('walk_left', frames, speed=150)
    animation_manager.add_animation('walk_right', frames, speed=150)
    animation_manager.add_animation('walk_up', frames, speed=150)

    # Set default
    animation_manager.play_animation('idle')

    return animation_manager, False

def create_protagonist_walking_frames():
    """Create simple walking animation frames for the protagonist (fallback)"""
    frames = []

    # Base sprite
    base_sprite = create_protagonist_sprite()
    frames.append(base_sprite)

    # Walking frame 1 (left foot forward)
    frame1 = base_sprite.copy()
    # Slightly adjust foot positions for walking effect
    pygame.draw.rect(frame1, (30, 144, 255), (8, 30, 4, 2))  # Left foot forward
    pygame.draw.rect(frame1, (101, 67, 33), (8, 30, 4, 2))  # Left shoe forward
    frames.append(frame1)

    # Walking frame 2 (right foot forward)
    frame2 = base_sprite.copy()
    pygame.draw.rect(frame2, (30, 144, 255), (16, 30, 4, 2))  # Right foot forward
    pygame.draw.rect(frame2, (101, 67, 33), (16, 30, 4, 2))  # Right shoe forward
    frames.append(frame2)

    return frames