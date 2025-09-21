import pygame
import os
from .smart_frame_detector import get_smart_frame_size

class SpriteSheet:
    def __init__(self, filename, frame_width, frame_height, scale_factor=1):
        """
        Load a sprite sheet and set up frame extraction

        Args:
            filename: Path to sprite sheet image
            frame_width: Width of each frame in pixels
            frame_height: Height of each frame in pixels
            scale_factor: How much to scale the sprites (1 = original size)
        """
        self.filename = filename
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.scale_factor = scale_factor
        self.sheet = None
        self.frames = {}

        self.load_sheet()

    def load_sheet(self):
        """Load the sprite sheet image"""
        try:
            # Try to load the sprite sheet
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            sheet_path = os.path.join(project_root, "assets", "images", "sprites", self.filename)

            if os.path.exists(sheet_path):
                self.sheet = pygame.image.load(sheet_path).convert_alpha()
                sheet_width, sheet_height = self.sheet.get_size()
                print(f"Loaded sprite sheet: {self.filename}")
                print(f"Sheet size: {sheet_width}x{sheet_height} pixels")
                print(f"Trying frame size: {self.frame_width}x{self.frame_height}")

                # Calculate how many frames we can extract
                self.cols = sheet_width // self.frame_width
                self.rows = sheet_height // self.frame_height
                print(f"This gives us: {self.cols}x{self.rows} frames")

                # Check if this looks reasonable
                total_frames = self.cols * self.rows
                if total_frames < 4:
                    print(f"WARNING: Only {total_frames} frames detected - frame size might be wrong")
                elif total_frames > 100:
                    print(f"WARNING: {total_frames} frames detected - frame size might be too small")
                else:
                    print(f"Frame extraction looks good: {total_frames} total frames")

            else:
                print(f"Sprite sheet not found: {sheet_path}")
                self.sheet = None

        except pygame.error as e:
            print(f"Error loading sprite sheet {self.filename}: {e}")
            self.sheet = None

    def get_frame(self, col, row):
        """Extract a single frame from the sprite sheet"""
        if not self.sheet:
            return None

        # Calculate position on sprite sheet
        x = col * self.frame_width
        y = row * self.frame_height

        # Create frame cache key
        cache_key = f"{col}_{row}"

        # Return cached frame if available
        if cache_key in self.frames:
            return self.frames[cache_key]

        # Extract the frame
        frame_rect = pygame.Rect(x, y, self.frame_width, self.frame_height)
        frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        frame.blit(self.sheet, (0, 0), frame_rect)

        # Scale if needed
        if self.scale_factor != 1:
            new_width = int(self.frame_width * self.scale_factor)
            new_height = int(self.frame_height * self.scale_factor)
            frame = pygame.transform.scale(frame, (new_width, new_height))

        # Cache the frame
        self.frames[cache_key] = frame
        return frame

    def get_animation_frames(self, start_col, start_row, num_frames, direction='horizontal'):
        """
        Extract a sequence of frames for animation

        Args:
            start_col: Starting column
            start_row: Starting row
            num_frames: Number of frames to extract
            direction: 'horizontal' or 'vertical'
        """
        frames = []

        for i in range(num_frames):
            if direction == 'horizontal':
                col = start_col + i
                row = start_row
            else:  # vertical
                col = start_col
                row = start_row + i

            frame = self.get_frame(col, row)
            if frame:
                frames.append(frame)

        return frames

    def save_debug_frame(self, col, row, filename):
        """Save a single frame for debugging purposes"""
        frame = self.get_frame(col, row)
        if frame:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            debug_path = os.path.join(project_root, "debug_frames")
            os.makedirs(debug_path, exist_ok=True)
            pygame.image.save(frame, os.path.join(debug_path, filename))
            print(f"Saved debug frame: {filename}")

class AnimationManager:
    def __init__(self):
        self.animations = {}
        self.current_animation = None
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 200  # milliseconds per frame
        self.loop = True

    def add_animation(self, name, frames, speed=200, loop=True):
        """Add an animation sequence"""
        self.animations[name] = {
            'frames': frames,
            'speed': speed,
            'loop': loop
        }

    def play_animation(self, name, restart=False):
        """Start playing an animation"""
        if name in self.animations:
            if self.current_animation != name or restart:
                self.current_animation = name
                self.current_frame = 0
                self.animation_timer = 0

                # Update settings from animation
                anim = self.animations[name]
                self.animation_speed = anim['speed']
                self.loop = anim['loop']

    def update(self, dt):
        """Update animation frame"""
        if not self.current_animation or self.current_animation not in self.animations:
            return

        self.animation_timer += dt * 1000  # convert to milliseconds

        if self.animation_timer >= self.animation_speed:
            frames = self.animations[self.current_animation]['frames']

            if self.loop:
                self.current_frame = (self.current_frame + 1) % len(frames)
            else:
                self.current_frame = min(self.current_frame + 1, len(frames) - 1)

            self.animation_timer = 0

    def get_current_frame(self):
        """Get the current animation frame"""
        if not self.current_animation or self.current_animation not in self.animations:
            return None

        frames = self.animations[self.current_animation]['frames']
        if frames and self.current_frame < len(frames):
            return frames[self.current_frame]
        return None

def load_protagonist_from_sprite_sheet():
    """
    Load protagonist animations from sprite sheet
    This function will look for common sprite sheet filenames
    """
    # Common sprite sheet filenames to try
    possible_files = [
        "protagonist.png",
        "character.png",
        "player.png",
        "hero.png",
        "main_character.png"
    ]

    # Try different common frame sizes for SNES/PS1 era sprites
    frame_sizes = [
        (256, 320), # Correct frame size - prevents overlap
        (256, 384), # Previous incorrect size
        (48, 64),   # Processed sprites (for future use)
        (64, 96),   # Alternative high-res
        (32, 48),   # Standard SNES tall
        (24, 32),   # Medium
        (128, 192), # Half of high-res
        (16, 24),   # Small SNES style
        (32, 32),   # Square
        (48, 48),   # Larger square
        (64, 64),   # Large square
        (16, 32),   # Narrow tall
        (20, 32),   # Slightly wider tall
        (16, 16),   # Very small square
        (24, 24),   # Small square
    ]

    animation_manager = AnimationManager()

    for filename in possible_files:
        # Try smart detection first
        smart_width, smart_height = get_smart_frame_size(filename)
        if smart_width and smart_height:
            print(f"Smart detection suggests frame size: {smart_width}x{smart_height}")
            # Only use smart detection if it gives reasonable results
            if smart_width >= 32 and smart_height >= 32:
                frame_sizes.insert(0, (smart_width, smart_height))  # Try this first

        for frame_width, frame_height in frame_sizes:
            sprite_sheet = SpriteSheet(filename, frame_width, frame_height, scale_factor=1.0)

            if sprite_sheet.sheet:
                print(f"Using sprite sheet: {filename} with frame size {frame_width}x{frame_height}")

                # Save some debug frames to see what we're extracting
                try:
                    sprite_sheet.save_debug_frame(0, 0, "frame_0_0.png")
                    sprite_sheet.save_debug_frame(1, 0, "frame_1_0.png")
                    sprite_sheet.save_debug_frame(0, 1, "frame_0_1.png")
                    print("Saved debug frames to debug_frames/ folder")
                except:
                    print("Could not save debug frames")

                # Extract common animation sequences
                # Assuming typical RPG sprite sheet layout:
                # Row 0: Down-facing walk cycle
                # Row 1: Left-facing walk cycle
                # Row 2: Right-facing walk cycle
                # Row 3: Up-facing walk cycle

                # Walking animations - assume first frame is idle, next 3 are walking
                # For 4x4 grid: idle + 3 walking frames per row
                if sprite_sheet.cols >= 4:
                    # Extract idle frame (first in each row) - Fix left direction
                    idle_down = sprite_sheet.get_animation_frames(0, 0, 1, 'horizontal')
                    idle_left = sprite_sheet.get_animation_frames(0, 2, 1, 'horizontal')  # Try row 2 for left
                    idle_right = sprite_sheet.get_animation_frames(0, 1, 1, 'horizontal')  # Try row 1 for right
                    idle_up = sprite_sheet.get_animation_frames(0, 3, 1, 'horizontal')  # Row 3 for up

                    # Extract walking frames (frames 1, 2, 3 in each row)
                    walk_down = sprite_sheet.get_animation_frames(1, 0, 3, 'horizontal')
                    walk_left = sprite_sheet.get_animation_frames(1, 2, 3, 'horizontal')  # Try row 2 for left
                    walk_right = sprite_sheet.get_animation_frames(1, 1, 3, 'horizontal')  # Try row 1 for right
                    walk_up = sprite_sheet.get_animation_frames(1, 3, 3, 'horizontal')  # Row 3 for up
                else:
                    # Fallback for smaller grids
                    walk_down = sprite_sheet.get_animation_frames(0, 0, min(4, sprite_sheet.cols), 'horizontal')
                    walk_left = sprite_sheet.get_animation_frames(0, 2, min(4, sprite_sheet.cols), 'horizontal')  # Try row 2 for left
                    walk_right = sprite_sheet.get_animation_frames(0, 1, min(4, sprite_sheet.cols), 'horizontal')  # Try row 1 for right
                    walk_up = sprite_sheet.get_animation_frames(0, 3, min(4, sprite_sheet.cols), 'horizontal')  # Row 3 for up

                    idle_down = [walk_down[0]] if walk_down else []
                    idle_left = [walk_left[0]] if walk_left else []
                    idle_right = [walk_right[0]] if walk_right else []
                    idle_up = [walk_up[0]] if walk_up else []

                print(f"Extracted animations: down={len(walk_down)}, left={len(walk_left)}, right={len(walk_right)}, up={len(walk_up)}")

                # Add animations with proper idle and walking frames
                if idle_down:
                    animation_manager.add_animation('idle_down', idle_down, speed=1000)
                    animation_manager.add_animation('idle', idle_down, speed=1000)  # Default idle

                if idle_left:
                    animation_manager.add_animation('idle_left', idle_left, speed=1000)

                if idle_right:
                    animation_manager.add_animation('idle_right', idle_right, speed=1000)

                if idle_up:
                    animation_manager.add_animation('idle_up', idle_up, speed=1000)

                if walk_down:
                    animation_manager.add_animation('walk_down', walk_down, speed=200)

                if walk_left:
                    animation_manager.add_animation('walk_left', walk_left, speed=200)

                if walk_right:
                    animation_manager.add_animation('walk_right', walk_right, speed=200)

                if walk_up:
                    animation_manager.add_animation('walk_up', walk_up, speed=200)

                # Set default animation
                animation_manager.play_animation('idle')

                return animation_manager, sprite_sheet

    print("No sprite sheet found, falling back to procedural sprite")
    return None, None