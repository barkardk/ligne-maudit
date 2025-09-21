import pygame
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("NumPy not available, falling back to basic collision detection")

from .collision_map import CollisionMap

class ImageCollisionDetector:
    def __init__(self):
        self.walkable_colors = []
        self.obstacle_colors = []
        self.color_tolerance = 30  # How similar colors need to be

    def analyze_background_image(self, image_surface):
        """
        Analyze a background image to detect walkable vs non-walkable areas
        """
        # Convert pygame surface to numpy array for analysis
        width, height = image_surface.get_size()
        pixels = pygame.surfarray.array3d(image_surface)

        # Analyze the image to identify different terrain types
        terrain_map = self.classify_terrain(pixels, width, height)

        # Generate collision areas from terrain analysis
        collision_map = self.generate_collision_map_from_terrain(terrain_map, width, height)

        return collision_map

    def classify_terrain(self, pixels, width, height):
        """
        Classify each pixel as walkable or obstacle based on color analysis
        """
        terrain_map = np.zeros((width, height), dtype=int)

        for x in range(width):
            for y in range(height):
                pixel_color = pixels[x, y]
                terrain_type = self.classify_pixel_color(pixel_color)
                terrain_map[x, y] = terrain_type

        return terrain_map

    def classify_pixel_color(self, color):
        """
        Classify a pixel color as:
        0 = walkable (grass, dirt paths)
        1 = obstacle (bunker, trees, rocks)
        2 = special (water, etc.)
        """
        r, g, b = color

        # Grass colors (green tones) - walkable
        if self.is_grass_color(r, g, b):
            return 0

        # Concrete/bunker colors (gray tones) - obstacle
        if self.is_concrete_color(r, g, b):
            return 1

        # Tree colors (brown/dark green) - obstacle
        if self.is_tree_color(r, g, b):
            return 1

        # Rock colors (gray/brown) - obstacle
        if self.is_rock_color(r, g, b):
            return 1

        # Sky colors - walkable (for now)
        if self.is_sky_color(r, g, b):
            return 0

        # Default to walkable
        return 0

    def is_grass_color(self, r, g, b):
        """Detect grass-like colors"""
        # Green dominant, with some variation
        return (g > r + 20 and g > b + 10 and
                30 < g < 200 and r < 150 and b < 150)

    def is_concrete_color(self, r, g, b):
        """Detect concrete/bunker colors"""
        # Gray tones - similar R, G, B values
        avg = (r + g + b) / 3
        variance = max(abs(r - avg), abs(g - avg), abs(b - avg))
        return (80 < avg < 180 and variance < 30)

    def is_tree_color(self, r, g, b):
        """Detect tree colors (bark and leaves)"""
        # Brown bark colors
        if (60 < r < 140 and 40 < g < 90 and 20 < b < 60):
            return True
        # Dark green leaf colors
        if (r < 80 and 50 < g < 150 and b < 80 and g > r + 20):
            return True
        return False

    def is_rock_color(self, r, g, b):
        """Detect rock colors"""
        # Grayish-brown rocks
        return (70 < r < 120 and 70 < g < 120 and 60 < b < 110 and
                abs(r - g) < 20 and abs(g - b) < 20)

    def is_sky_color(self, r, g, b):
        """Detect sky colors"""
        # Light blue/purple sky tones
        return (b > r and b > g and b > 100 and r + g < 400)

    def generate_collision_map_from_terrain(self, terrain_map, width, height):
        """
        Convert terrain classification into collision rectangles
        """
        collision_map = CollisionMap(width, height)

        # Group adjacent obstacle pixels into larger rectangles for efficiency
        processed = np.zeros((width, height), dtype=bool)

        for x in range(width):
            for y in range(height):
                if terrain_map[x, y] == 1 and not processed[x, y]:  # Obstacle
                    # Find the largest rectangle starting from this point
                    rect_width, rect_height = self.find_obstacle_rectangle(
                        terrain_map, processed, x, y, width, height
                    )

                    if rect_width > 0 and rect_height > 0:
                        collision_map.add_collision_rect(x, y, rect_width, rect_height)

        return collision_map

    def find_obstacle_rectangle(self, terrain_map, processed, start_x, start_y, width, height):
        """
        Find the largest rectangle of obstacles starting from a point
        """
        if terrain_map[start_x, start_y] != 1:
            return 0, 0

        # Find maximum width
        max_width = 0
        for w in range(start_x, width):
            if terrain_map[w, start_y] == 1 and not processed[w, start_y]:
                max_width += 1
            else:
                break

        # Find maximum height for this width
        max_height = 0
        for h in range(start_y, height):
            valid_row = True
            for w in range(start_x, start_x + max_width):
                if w >= width or terrain_map[w, h] != 1 or processed[w, h]:
                    valid_row = False
                    break

            if valid_row:
                max_height += 1
            else:
                break

        # Mark these pixels as processed
        for w in range(start_x, start_x + max_width):
            for h in range(start_y, start_y + max_height):
                if w < width and h < height:
                    processed[w, h] = True

        return max_width, max_height

def create_smart_collision_map(background_surface, screen_width, screen_height):
    """
    Create a collision map by analyzing the background image
    """
    if not NUMPY_AVAILABLE:
        print("NumPy not available, using manual collision map")
        from .collision_map import create_maginot_collision_map
        return create_maginot_collision_map(screen_width, screen_height)

    detector = ImageCollisionDetector()

    try:
        # Analyze the background image
        collision_map = detector.analyze_background_image(background_surface)
        print("Successfully generated collision map from background image analysis")
        return collision_map

    except Exception as e:
        print(f"Error analyzing background image: {e}")
        # Fall back to manual collision map
        from .collision_map import create_maginot_collision_map
        return create_maginot_collision_map(screen_width, screen_height)