"""Projectile entity."""

import pygame
import math
from game.config import (
    Q_PROJECTILE_WIDTH, Q_PROJECTILE_LENGTH, Q_PROJECTILE_SPEED, Q_PROJECTILE_COLOR,
    SCREEN_WIDTH, SCREEN_HEIGHT
)


class Projectile:
    """Yellow bar projectile fired by the player's Q skill."""
    
    def __init__(self, x: float, y: float, target_x: float, target_y: float):
        self.x = x
        self.y = y
        self.width = Q_PROJECTILE_WIDTH
        self.length = Q_PROJECTILE_LENGTH
        self.speed = Q_PROJECTILE_SPEED
        self.color = Q_PROJECTILE_COLOR
        self.active = True
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
            # Store normalized direction for drawing
            self.dir_x = dx / distance
            self.dir_y = dy / distance
        else:
            self.vx = 0
            self.vy = 0
            self.dir_x = 1
            self.dir_y = 0
    
    @property
    def rect(self) -> pygame.Rect:
        """Get projectile bounding rectangle."""
        # Return a rect that covers the bar
        return pygame.Rect(
            self.x - self.length // 2,
            self.y - self.width // 2,
            self.length,
            self.width
        )
    
    def check_collision_with_enemy(self, enemy) -> bool:
        """Check if projectile collides with an enemy."""
        # Create a line segment from the projectile
        half_length = self.length // 2
        start_x = self.x - self.dir_x * half_length
        start_y = self.y - self.dir_y * half_length
        end_x = self.x + self.dir_x * half_length
        end_y = self.y + self.dir_y * half_length
        
        # Check if line intersects enemy circle
        enemy_radius = enemy.size // 2
        
        # Check multiple points along the projectile
        for t in range(0, 11):
            check_x = start_x + (end_x - start_x) * (t / 10)
            check_y = start_y + (end_y - start_y) * (t / 10)
            
            dist = math.sqrt((check_x - enemy.x) ** 2 + (check_y - enemy.y) ** 2)
            if dist < enemy_radius + self.width // 2:
                return True
        
        return False
    
    def update(self, dt: float):
        """Update projectile position."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Deactivate if out of bounds
        margin = self.length
        if (self.x < -margin or self.x > SCREEN_WIDTH + margin or
            self.y < -margin or self.y > SCREEN_HEIGHT + margin):
            self.active = False
    
    def draw(self, surface: pygame.Surface):
        """Draw the yellow bar projectile."""
        # Calculate the perpendicular direction for width
        perp_x = -self.dir_y
        perp_y = self.dir_x
        
        half_length = self.length // 2
        half_width = self.width // 2
        
        # Calculate the four corners of the bar
        points = [
            (self.x - self.dir_x * half_length - perp_x * half_width,
             self.y - self.dir_y * half_length - perp_y * half_width),
            (self.x + self.dir_x * half_length - perp_x * half_width,
             self.y + self.dir_y * half_length - perp_y * half_width),
            (self.x + self.dir_x * half_length + perp_x * half_width,
             self.y + self.dir_y * half_length + perp_y * half_width),
            (self.x - self.dir_x * half_length + perp_x * half_width,
             self.y - self.dir_y * half_length + perp_y * half_width),
        ]
        
        # Draw glow effect
        glow_points = [
            (self.x - self.dir_x * (half_length + 4) - perp_x * (half_width + 4),
             self.y - self.dir_y * (half_length + 4) - perp_y * (half_width + 4)),
            (self.x + self.dir_x * (half_length + 4) - perp_x * (half_width + 4),
             self.y + self.dir_y * (half_length + 4) - perp_y * (half_width + 4)),
            (self.x + self.dir_x * (half_length + 4) + perp_x * (half_width + 4),
             self.y + self.dir_y * (half_length + 4) + perp_y * (half_width + 4)),
            (self.x - self.dir_x * (half_length + 4) + perp_x * (half_width + 4),
             self.y - self.dir_y * (half_length + 4) + perp_y * (half_width + 4)),
        ]
        
        glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(glow_surface, (*self.color, 60), [(int(p[0]), int(p[1])) for p in glow_points])
        surface.blit(glow_surface, (0, 0))
        
        # Draw main bar
        pygame.draw.polygon(surface, self.color, [(int(p[0]), int(p[1])) for p in points])
        
        # Draw outline
        pygame.draw.polygon(surface, (200, 180, 0), [(int(p[0]), int(p[1])) for p in points], 2)
        
        # Draw bright center line
        center_points = [
            (self.x - self.dir_x * half_length,
             self.y - self.dir_y * half_length),
            (self.x + self.dir_x * half_length,
             self.y + self.dir_y * half_length),
        ]
        pygame.draw.line(surface, (255, 255, 200), 
                        (int(center_points[0][0]), int(center_points[0][1])),
                        (int(center_points[1][0]), int(center_points[1][1])), 3)
