import pygame
import os
from .sprite_sheet_loader import SpriteSheet

class RabbitAnimation:
    def __init__(self):
        self.sprites = {}
        self.current_animation = None
        self.current_frame = 0
        self.frame_timer = 0.0
        self.frame_duration = 0.3  # Default frame duration
        self.loop = True
        self.animation_finished = False

        # Animation definitions for natural rabbit behavior
        self.animations = {
            'idle': {
                'frames': [0, 1, 2, 3, 4, 5],  # 6 frames for idle/nose twitching
                'duration': 0.8,  # Much slower for natural look - holds each frame longer
                'loop': True
            },
            'alert': {
                'frames': [6, 7, 8],  # 3 frames for alert state
                'duration': 0.2,  # Quick reaction
                'loop': False
            },
            'jump': {
                'frames': [9, 10, 11, 12, 13],  # 5 frames for jump away
                'duration': 0.12,  # Fast escape
                'loop': False
            },
            'hop': {
                'frames': [14, 15, 16],  # 3 frames for small hops
                'duration': 0.15,  # Slightly slower hops
                'loop': True
            }
        }

        self.load_sprites()

    def load_sprites(self):
        """Load rabbit sprite sheet"""
        try:
            print(f"Loading rabbit sprites...")

            # TEMPORARY: Force fallback to test positioning
            print("TEMPORARY: Using fallback sprite to test positioning")
            self.create_fallback_sprite()
            return

            # Try different frame sizes for the 1024x1024 sprite sheet
            frame_sizes_to_try = [
                (128, 128),  # Original assumption - 8x8 grid
                (256, 256),  # 4x4 grid - larger frames
                (512, 512),  # 2x2 grid - very large frames
                (64, 64),    # 16x16 grid - smaller frames
                (170, 170),  # ~6x6 grid - alternative size
            ]

            sprite_sheet = None
            for frame_width, frame_height in frame_sizes_to_try:
                print(f"Trying frame size: {frame_width}x{frame_height}")
                test_sheet = SpriteSheet("frames/rabbit.png", frame_width, frame_height, scale_factor=1.0)

                if test_sheet.sheet:
                    sheet_size = test_sheet.sheet.get_size()
                    cols = sheet_size[0] // frame_width
                    rows = sheet_size[1] // frame_height
                    total_frames = cols * rows

                    print(f"Sheet size: {sheet_size}, Grid: {cols}x{rows}, Total frames: {total_frames}")

                    # Check if we have at least 17 frames for our animations
                    if total_frames >= 17:
                        sprite_sheet = test_sheet
                        print(f"Using frame size: {frame_width}x{frame_height}")
                        break
                    else:
                        print(f"Not enough frames ({total_frames} < 17), trying next size...")

            if sprite_sheet and sprite_sheet.sheet:
                print(f"Rabbit sprite sheet loaded: {sprite_sheet.sheet.get_size()}")
                print(f"Using frame size: {sprite_sheet.frame_width}x{sprite_sheet.frame_height}")
                print(f"Grid layout: {sprite_sheet.cols}x{sprite_sheet.rows}")

                # Extract all 17 frames we need
                frames_loaded = 0
                for i in range(min(17, sprite_sheet.cols * sprite_sheet.rows)):
                    row = i // sprite_sheet.cols
                    col = i % sprite_sheet.cols
                    frame = sprite_sheet.get_frame(col, row)
                    if frame:
                        self.sprites[i] = frame
                        frames_loaded += 1
                        if i < 5:  # Only log first 5 frames to avoid spam
                            print(f"Loaded frame {i} at ({col}, {row}) - size: {frame.get_size()}")

                print(f"Successfully loaded {frames_loaded} rabbit frames")

                # Save debug frames to check what we're getting
                for debug_idx in [0, 1, 6, 9]:  # Save idle, alert, jump start frames
                    if debug_idx in self.sprites:
                        try:
                            current_dir = os.path.dirname(__file__)
                            project_root = os.path.dirname(os.path.dirname(current_dir))
                            debug_path = os.path.join(project_root, f"debug_rabbit_frame_{debug_idx}.png")
                            pygame.image.save(self.sprites[debug_idx], debug_path)
                            print(f"Saved debug rabbit frame {debug_idx} to: {debug_path}")
                        except Exception as e:
                            print(f"Could not save debug frame {debug_idx}: {e}")

                # Start with idle animation if we have frames
                if self.sprites:
                    self.play_animation('idle')
                else:
                    print("No frames loaded, using fallback")
                    self.create_fallback_sprite()

            else:
                print(f"Rabbit sprite sheet not found or no suitable frame size")
                self.create_fallback_sprite()

        except Exception as e:
            print(f"Error loading rabbit sprites: {e}")
            self.create_fallback_sprite()

    def create_fallback_sprite(self):
        """Create a realistic-looking rabbit sprite"""
        def create_rabbit_frame(nose_twitch=0, ear_twitch=0, blink=False):
            frame = pygame.Surface((128, 128), pygame.SRCALPHA)

            # More realistic rabbit colors
            fur_color = (160, 130, 95)      # Natural brown fur
            ear_inner = (255, 200, 180)     # Light pink inner ear
            nose_color = (180, 90, 120)     # Dark pink nose
            tail_color = (250, 250, 250)    # White tail

            # Body (more oval, rabbit-like proportions)
            pygame.draw.ellipse(frame, fur_color, (25, 55, 75, 50))

            # Head (more elongated, less round)
            pygame.draw.ellipse(frame, fur_color, (35, 25, 55, 40))

            # Ears (long, pointed, more rabbit-like)
            ear_left_x = 48 + ear_twitch
            ear_right_x = 72 - ear_twitch
            # Left ear
            pygame.draw.polygon(frame, fur_color, [(ear_left_x, 5), (ear_left_x+8, 5), (ear_left_x+6, 35), (ear_left_x+2, 35)])
            pygame.draw.polygon(frame, ear_inner, [(ear_left_x+1, 8), (ear_left_x+7, 8), (ear_left_x+5, 30), (ear_left_x+3, 30)])
            # Right ear
            pygame.draw.polygon(frame, fur_color, [(ear_right_x, 5), (ear_right_x+8, 5), (ear_right_x+6, 35), (ear_right_x+2, 35)])
            pygame.draw.polygon(frame, ear_inner, [(ear_right_x+1, 8), (ear_right_x+7, 8), (ear_right_x+5, 30), (ear_right_x+3, 30)])

            # Eyes (more realistic, not perfect circles)
            if not blink:
                # Open eyes
                pygame.draw.ellipse(frame, (0, 0, 0), (52, 32, 6, 4))
                pygame.draw.ellipse(frame, (0, 0, 0), (70, 32, 6, 4))
                # Eye highlights
                pygame.draw.circle(frame, (255, 255, 255), (54, 33), 1)
                pygame.draw.circle(frame, (255, 255, 255), (72, 33), 1)
            else:
                # Closed eyes (blinking)
                pygame.draw.line(frame, (0, 0, 0), (52, 34), (58, 34), 2)
                pygame.draw.line(frame, (0, 0, 0), (70, 34), (76, 34), 2)

            # Nose (more triangular, realistic)
            nose_x = 64 + nose_twitch
            nose_points = [(nose_x-2, 42), (nose_x+2, 42), (nose_x, 45)]
            pygame.draw.polygon(frame, nose_color, nose_points)

            # Mouth (subtle)
            pygame.draw.arc(frame, (100, 80, 60), (60, 44, 8, 6), 0, 3.14, 1)

            # Whiskers (thinner, more natural)
            pygame.draw.line(frame, (60, 50, 40), (42, 40), (50, 39), 1)
            pygame.draw.line(frame, (60, 50, 40), (42, 44), (50, 43), 1)
            pygame.draw.line(frame, (60, 50, 40), (78, 39), (86, 40), 1)
            pygame.draw.line(frame, (60, 50, 40), (78, 43), (86, 44), 1)

            # Front paws (more detailed)
            pygame.draw.ellipse(frame, fur_color, (48, 82, 10, 12))
            pygame.draw.ellipse(frame, fur_color, (70, 82, 10, 12))
            # Paw pads
            pygame.draw.ellipse(frame, (120, 90, 70), (50, 88, 6, 4))
            pygame.draw.ellipse(frame, (120, 90, 70), (72, 88, 6, 4))

            # Fluffy tail (more realistic)
            pygame.draw.circle(frame, tail_color, (92, 68), 9)
            pygame.draw.circle(frame, (220, 220, 220), (90, 66), 6)  # Inner fluff

            return frame

        # Create more natural animation sequence
        animations = {
            # Idle: mostly still with occasional nose twitches
            'idle': [
                create_rabbit_frame(),                    # Frame 0: normal
                create_rabbit_frame(),                    # Frame 1: normal
                create_rabbit_frame(),                    # Frame 2: normal
                create_rabbit_frame(nose_twitch=1),       # Frame 3: slight nose twitch
                create_rabbit_frame(),                    # Frame 4: normal
                create_rabbit_frame(),                    # Frame 5: normal
            ],
            # Alert: ears perk up
            'alert': [
                create_rabbit_frame(ear_twitch=2),        # Frame 6: ears alert
                create_rabbit_frame(ear_twitch=3),        # Frame 7: ears more alert
                create_rabbit_frame(ear_twitch=2),        # Frame 8: ears settle
            ],
            # Jump: more dynamic poses
            'jump': [
                create_rabbit_frame(ear_twitch=1),        # Frame 9: prepare
                create_rabbit_frame(ear_twitch=2),        # Frame 10: crouch
                create_rabbit_frame(ear_twitch=3),        # Frame 11: mid-jump
                create_rabbit_frame(ear_twitch=2),        # Frame 12: landing
                create_rabbit_frame(),                    # Frame 13: settle
            ],
            # Hop: small movements
            'hop': [
                create_rabbit_frame(),                    # Frame 14: normal
                create_rabbit_frame(nose_twitch=1),       # Frame 15: slight movement
                create_rabbit_frame(),                    # Frame 16: normal
            ]
        }

        # Assign frames to sprite indices
        frame_index = 0
        for anim_name, frames in animations.items():
            for frame in frames:
                if frame_index < 17:
                    self.sprites[frame_index] = frame
                    frame_index += 1

        print("Created realistic fallback rabbit sprite with natural animations")
        self.play_animation('idle')

    def play_animation(self, animation_name):
        """Start playing an animation"""
        if animation_name in self.animations:
            self.current_animation = animation_name
            self.current_frame = 0
            self.frame_timer = 0.0
            self.animation_finished = False
            anim = self.animations[animation_name]
            self.frame_duration = anim['duration']
            self.loop = anim['loop']
            print(f"Rabbit playing animation: {animation_name}")
        else:
            print(f"Unknown rabbit animation: {animation_name}")

    def update(self, dt):
        """Update animation"""
        if self.current_animation is None:
            return

        self.frame_timer += dt

        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0.0
            anim = self.animations[self.current_animation]

            if self.current_frame < len(anim['frames']) - 1:
                self.current_frame += 1
            else:
                if self.loop:
                    self.current_frame = 0
                else:
                    self.animation_finished = True

    def get_current_frame(self):
        """Get the current frame surface"""
        if self.current_animation is None or not self.sprites:
            return None

        anim = self.animations[self.current_animation]
        sprite_index = anim['frames'][self.current_frame]
        return self.sprites.get(sprite_index)

    def is_animation_finished(self):
        """Check if current animation is finished (for non-looping animations)"""
        return self.animation_finished

def create_rabbit_animation_system():
    """Create and return a rabbit animation system"""
    return RabbitAnimation()