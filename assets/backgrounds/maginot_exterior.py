import pygame

def create_maginot_exterior_background(width, height):
    """Create a Final Fantasy IX style background of the exterior of a Maginot Line bunker"""
    surface = pygame.Surface((width, height))

    # Sky gradient (dawn/dusk colors for atmospheric feel)
    for y in range(height // 3):
        color_intensity = 255 - (y * 100 // (height // 3))
        color = (max(100, color_intensity), max(80, color_intensity - 20), max(120, color_intensity - 10))
        pygame.draw.line(surface, color, (0, y), (width, y))

    # Ground base color (earthy green-brown)
    ground_start_y = height // 3
    ground_color = (85, 107, 47)  # Dark olive green
    pygame.draw.rect(surface, ground_color, (0, ground_start_y, width, height - ground_start_y))

    # Rolling hills in background
    hill_points = []
    for x in range(0, width + 20, 20):
        hill_height = ground_start_y + (height // 6) + int(30 * (x / width))
        hill_points.append((x, hill_height))
    hill_points.append((width, height))
    hill_points.append((0, height))
    pygame.draw.polygon(surface, (70, 90, 40), hill_points)

    # Maginot bunker (concrete gray blockhouse)
    bunker_width = 180
    bunker_height = 80
    bunker_x = width // 2 - bunker_width // 2 + 50
    bunker_y = ground_start_y + 40

    # Main bunker structure
    bunker_color = (120, 120, 115)
    pygame.draw.rect(surface, bunker_color, (bunker_x, bunker_y, bunker_width, bunker_height))

    # Bunker entrance (dark opening)
    entrance_width = 25
    entrance_height = 35
    entrance_x = bunker_x + 30
    entrance_y = bunker_y + bunker_height - entrance_height
    pygame.draw.rect(surface, (30, 30, 30), (entrance_x, entrance_y, entrance_width, entrance_height))

    # Small viewing slit
    slit_width = 15
    slit_height = 4
    slit_x = bunker_x + bunker_width - 40
    slit_y = bunker_y + 25
    pygame.draw.rect(surface, (20, 20, 20), (slit_x, slit_y, slit_width, slit_height))

    # Add some weathering/texture to bunker
    for i in range(10):
        stain_x = bunker_x + (i * bunker_width // 10)
        stain_y = bunker_y + (i * 8)
        stain_color = (100, 100, 95)
        pygame.draw.circle(surface, stain_color, (stain_x, stain_y), 3)

    # Grass patches
    grass_color = (34, 139, 34)
    for i in range(20):
        grass_x = (i * width // 20) + (i * 10) % 30
        grass_y = ground_start_y + 60 + (i * 5) % 40
        # Simple grass tufts
        for j in range(3):
            pygame.draw.line(surface, grass_color,
                           (grass_x + j * 2, grass_y),
                           (grass_x + j * 2, grass_y - 8), 2)

    # Add some scattered rocks
    rock_color = (105, 105, 105)
    rock_positions = [(100, ground_start_y + 70), (300, ground_start_y + 85),
                     (500, ground_start_y + 75), (700, ground_start_y + 90)]
    for rock_x, rock_y in rock_positions:
        pygame.draw.ellipse(surface, rock_color, (rock_x, rock_y, 12, 8))

    # Trees in background (simple FF9-style)
    tree_positions = [(80, ground_start_y + 20), (width - 100, ground_start_y + 30)]
    for tree_x, tree_y in tree_positions:
        # Tree trunk
        trunk_color = (101, 67, 33)
        pygame.draw.rect(surface, trunk_color, (tree_x, tree_y, 8, 25))
        # Tree foliage
        foliage_color = (34, 100, 34)
        pygame.draw.circle(surface, foliage_color, (tree_x + 4, tree_y - 5), 15)
        pygame.draw.circle(surface, foliage_color, (tree_x - 3, tree_y + 5), 12)
        pygame.draw.circle(surface, foliage_color, (tree_x + 11, tree_y + 3), 10)

    return surface

def add_birds_to_scene(surface):
    """Add simple birds flying in the background"""
    bird_color = (50, 50, 50)
    bird_positions = [(150, 80), (400, 60), (600, 90), (800, 70)]

    for bird_x, bird_y in bird_positions:
        # Simple V-shaped birds
        pygame.draw.line(surface, bird_color, (bird_x, bird_y), (bird_x - 5, bird_y - 3), 2)
        pygame.draw.line(surface, bird_color, (bird_x, bird_y), (bird_x + 5, bird_y - 3), 2)

    return surface