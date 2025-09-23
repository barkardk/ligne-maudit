import pygame
import os

def load_background_image(filename, target_width=1024, target_height=768, scene_folder=None):
    """Load and scale a background image to fit the screen"""
    try:
        # Get the path to the images directory
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(os.path.dirname(current_dir))

        if scene_folder:
            image_path = os.path.join(project_root, "assets", "images", "backgrounds", scene_folder, filename)
        else:
            image_path = os.path.join(project_root, "assets", "images", "backgrounds", filename)

        # Debug: print the path being tried
        print(f"Trying to load image from: {image_path}")
        print(f"File exists: {os.path.exists(image_path)}")

        # Load the image
        background = pygame.image.load(image_path)

        # Scale to target resolution
        background = pygame.transform.scale(background, (target_width, target_height))

        print(f"Successfully loaded background: {filename}")
        return background

    except pygame.error as e:
        print(f"Could not load image {filename}: {e}")
        return None
    except FileNotFoundError:
        print(f"Image file not found: {filename}")
        return None

def load_concept_art_background(screen_width, screen_height, fallback_function=None):
    """
    Try to load concept art, fall back to generated background if not available
    """
    # Try to load your concept art files from scene2 folder (for field state)
    concept_files = [
        "bunker.png",
        "maginot_concept.jpg",
        "ff9_style_bunker.png"
    ]

    for filename in concept_files:
        background = load_background_image(filename, screen_width, screen_height, scene_folder="scene2")
        if background:
            return background

    # Fall back to procedural generation if no concept art found
    print("No concept art found, using procedural background")
    if fallback_function:
        return fallback_function(screen_width, screen_height)
    else:
        # Create a simple placeholder
        surface = pygame.Surface((screen_width, screen_height))
        surface.fill((100, 150, 100))  # Green placeholder
        font = pygame.font.Font(None, 36)
        text = font.render("Add your concept art to assets/images/backgrounds/", True, (255, 255, 255))
        surface.blit(text, (50, screen_height // 2))
        return surface

def blend_concept_with_generated(concept_art, generated_bg, blend_ratio=0.7):
    """
    Blend concept art with generated elements
    blend_ratio: 0.0 = all generated, 1.0 = all concept art
    """
    if concept_art and generated_bg:
        # Create a new surface
        result = pygame.Surface(concept_art.get_size())

        # Blend the two images
        concept_art.set_alpha(int(255 * blend_ratio))
        generated_bg.set_alpha(int(255 * (1 - blend_ratio)))

        result.blit(generated_bg, (0, 0))
        result.blit(concept_art, (0, 0))

        return result
    elif concept_art:
        return concept_art
    else:
        return generated_bg