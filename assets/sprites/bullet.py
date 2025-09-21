import pygame
import math

class Bullet:
    def __init__(self, x, y, direction_x, direction_y, speed=300):
        self.x = x
        self.y = y
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.speed = speed
        self.sprite = self.create_bullet_sprite()
        self.active = True

    def create_bullet_sprite(self):
        """Create a small yellow bullet sprite"""
        sprite = pygame.Surface((4, 4), pygame.SRCALPHA)
        # Yellow bullet with slight orange center
        pygame.draw.circle(sprite, (255, 255, 0), (2, 2), 2)
        pygame.draw.circle(sprite, (255, 200, 0), (2, 2), 1)
        return sprite

    def update(self, dt):
        """Update bullet position"""
        if self.active:
            self.x += self.direction_x * self.speed * dt
            self.y += self.direction_y * self.speed * dt

    def render(self, screen):
        """Render the bullet"""
        if self.active:
            screen.blit(self.sprite, (int(self.x), int(self.y)))

    def is_off_screen(self, screen_width, screen_height):
        """Check if bullet has left the screen"""
        return (self.x < -10 or self.x > screen_width + 10 or
                self.y < -10 or self.y > screen_height + 10)

def get_direction_from_keys(keys):
    """Get shooting direction based on arrow keys or WASD"""
    direction_x = 0
    direction_y = 0

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        direction_x = -1
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        direction_x = 1
    elif keys[pygame.K_UP] or keys[pygame.K_w]:
        direction_y = -1
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        direction_y = 1
    else:
        # Default to shooting right if no direction keys are pressed
        direction_x = 1

    # Normalize diagonal directions
    if direction_x != 0 and direction_y != 0:
        length = math.sqrt(direction_x * direction_x + direction_y * direction_y)
        direction_x /= length
        direction_y /= length

    return direction_x, direction_y