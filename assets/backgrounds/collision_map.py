import pygame

class CollisionMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.collision_rects = []
        self.debug_mode = False

    def add_collision_rect(self, x, y, width, height):
        """Add a rectangular collision area"""
        rect = pygame.Rect(x, y, width, height)
        self.collision_rects.append(rect)

    def add_collision_circle(self, center_x, center_y, radius):
        """Add a circular collision area (converted to rect for simplicity)"""
        rect = pygame.Rect(center_x - radius, center_y - radius, radius * 2, radius * 2)
        self.collision_rects.append(rect)

    def check_collision(self, x, y, width, height):
        """Check if a rectangle collides with any collision areas"""
        player_rect = pygame.Rect(x, y, width, height)
        for collision_rect in self.collision_rects:
            if player_rect.colliderect(collision_rect):
                return True
        return False

    def get_valid_position(self, old_x, old_y, new_x, new_y, width, height):
        """
        Return a valid position, trying to slide along walls if possible
        """
        # Try the new position
        if not self.check_collision(new_x, new_y, width, height):
            return new_x, new_y

        # Try moving only horizontally
        if not self.check_collision(new_x, old_y, width, height):
            return new_x, old_y

        # Try moving only vertically
        if not self.check_collision(old_x, new_y, width, height):
            return old_x, new_y

        # Can't move, return old position
        return old_x, old_y

    def render_debug(self, screen):
        """Render collision areas for debugging"""
        if self.debug_mode:
            for rect in self.collision_rects:
                # Draw collision areas in semi-transparent red
                debug_surface = pygame.Surface((rect.width, rect.height))
                debug_surface.set_alpha(128)
                debug_surface.fill((255, 0, 0))
                screen.blit(debug_surface, (rect.x, rect.y))
                # Draw outline
                pygame.draw.rect(screen, (255, 255, 0), rect, 2)

    def toggle_debug(self):
        """Toggle debug visualization"""
        self.debug_mode = not self.debug_mode
        print(f"Collision debug mode: {'ON' if self.debug_mode else 'OFF'}")

def create_maginot_collision_map(screen_width, screen_height):
    """Create collision map for the Maginot Line scene"""
    collision_map = CollisionMap(screen_width, screen_height)

    # Scale factor if background is different size than screen
    bg_width, bg_height = 1536, 1024  # Actual concept art size
    scale_x = screen_width / bg_width
    scale_y = screen_height / bg_height

    # Door location - lower third center
    door_x = 467  # 25 pixels to the right
    door_y = 575  # 25 pixels up
    door_width = int(30 * scale_x)  # Reasonable door width
    door_height = int(40 * scale_y)  # Reasonable door height

    print(f"Door location (scaled): ({door_x}, {door_y}) size: {door_width}x{door_height}")

    # Minimal collision areas to avoid blocking door access at (467, 575)
    # Only add essential collision areas that don't interfere with door approach
    bunker_areas = [
        # Small collision area to the left of door (if needed)
        (door_x - 60, door_y - 20, 40, 60),
        # Small collision area to the right of door (if needed)
        (door_x + door_width + 20, door_y - 20, 40, 60),
    ]

    # Only add collision areas that are well away from the door
    for bx, by, bw, bh in bunker_areas:
        if bx >= 0 and by >= 0 and bx + bw <= screen_width and by + bh <= screen_height:
            # Only add if it doesn't block approach to door
            if not (abs(bx + bw/2 - door_x) < 100 and abs(by + bh/2 - door_y) < 100):
                collision_map.add_collision_rect(bx, by, bw, bh)

    # Trees (approximate positions from background)
    tree_positions = [(80, screen_height // 3 + 20), (screen_width - 100, screen_height // 3 + 30)]
    for tree_x, tree_y in tree_positions:
        # Tree collision area (smaller than visual for gameplay)
        collision_map.add_collision_circle(tree_x + 4, tree_y + 10, 12)

    # Optional: Add invisible walls at screen edges to prevent going too far off-screen
    edge_margin = 10
    # Left wall
    collision_map.add_collision_rect(-edge_margin, 0, edge_margin, screen_height)
    # Right wall
    collision_map.add_collision_rect(screen_width, 0, edge_margin, screen_height)
    # Top wall
    collision_map.add_collision_rect(0, -edge_margin, screen_width, edge_margin)
    # Bottom wall
    collision_map.add_collision_rect(0, screen_height, screen_width, edge_margin)

    # Optional: Add some rocks as obstacles
    rock_positions = [(100, screen_height // 3 + 70), (300, screen_height // 3 + 85),
                     (500, screen_height // 3 + 75), (700, screen_height // 3 + 90)]
    for rock_x, rock_y in rock_positions:
        collision_map.add_collision_rect(rock_x - 6, rock_y - 4, 12, 8)

    return collision_map