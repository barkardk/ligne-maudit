#!/usr/bin/env python3
"""
Simple door detection in the background image
"""
import pygame
import sys
import os

def main():
    pygame.init()
    pygame.display.set_mode((100, 100))  # Minimal display

    # Load the concept art background
    try:
        bg_path = "assets/images/backgrounds/maginot_concept.png"
        background = pygame.image.load(bg_path).convert_alpha()
        width, height = background.get_size()

        print(f"Analyzing background: {width}x{height}")

        # Look for very dark areas (likely doors/entrances)
        dark_areas = []

        # Sample every 10 pixels to find dark regions
        for y in range(0, height, 10):
            for x in range(0, width, 10):
                pixel = background.get_at((x, y))
                r, g, b = pixel[:3]

                # Very dark pixels (likely entrances)
                if r < 50 and g < 50 and b < 50:
                    dark_areas.append((x, y, r + g + b))

        # Sort by darkness (lowest RGB sum = darkest)
        dark_areas.sort(key=lambda x: x[2])

        print(f"Found {len(dark_areas)} dark areas")

        if dark_areas:
            print("\nDarkest areas (likely doors/entrances):")
            for i, (x, y, darkness) in enumerate(dark_areas[:10]):
                print(f"  {i+1}. Position ({x}, {y}) - darkness: {darkness}")

            # Find clusters of dark areas (actual doors)
            clusters = find_clusters(dark_areas[:50])  # Use top 50 darkest

            print(f"\nFound {len(clusters)} potential door locations:")
            for i, (center_x, center_y, count) in enumerate(clusters):
                print(f"  Door {i+1}: Center at ({center_x}, {center_y}) - {count} dark pixels")

        # Save a marked version
        marked_bg = background.copy()
        for center_x, center_y, count in clusters[:3]:  # Mark top 3 candidates
            # Draw a yellow rectangle around potential door
            pygame.draw.rect(marked_bg, (255, 255, 0), (center_x-15, center_y-20, 30, 40), 2)

        pygame.image.save(marked_bg, "door_detection.png")
        print(f"\nSaved marked background to door_detection.png")

    except Exception as e:
        print(f"Error: {e}")

    pygame.quit()

def find_clusters(dark_points, cluster_radius=50):
    """Group nearby dark points into clusters (potential doors)"""
    clusters = []

    for x, y, darkness in dark_points:
        # Find if this point belongs to an existing cluster
        added_to_cluster = False

        for i, (cluster_x, cluster_y, count) in enumerate(clusters):
            distance = ((x - cluster_x) ** 2 + (y - cluster_y) ** 2) ** 0.5
            if distance < cluster_radius:
                # Add to existing cluster
                new_x = (cluster_x * count + x) / (count + 1)
                new_y = (cluster_y * count + y) / (count + 1)
                clusters[i] = (int(new_x), int(new_y), count + 1)
                added_to_cluster = True
                break

        if not added_to_cluster:
            # Create new cluster
            clusters.append((x, y, 1))

    # Sort by cluster size (more dark pixels = more likely to be a door)
    clusters.sort(key=lambda x: x[2], reverse=True)
    return clusters

if __name__ == "__main__":
    main()