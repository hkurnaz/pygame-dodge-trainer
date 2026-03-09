"""Projectile entity."""

import pygame
import math
from game.config import (
    Q_PROJECTILE_WIDTH, Q_PROJECTILE_LENGTH, Q_PROJECTILE_SPEED, Q_PROJECTILE_COLOR,
    SCREEN_WIDTH, SCREEN_HEIGHT, ZED_Q_SPEED, ZED_Q_SIZE
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


class Shuriken:
    """Zed's shuriken projectile - star-shaped with rotation."""
    
    def __init__(self, x: float, y: float, target_x: float, target_y: float, max_range: float = 350):
        self.x = x
        self.y = y
        self.size = ZED_Q_SIZE
        self.speed = ZED_Q_SPEED
        self.max_range = max_range
        self.active = True
        self.rotation = 0
        self.rotation_speed = 720  # degrees per second
        
        # Starting position for range calculation
        self.start_x = x
        self.start_y = y
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
            self.dir_x = dx / distance
            self.dir_y = dy / distance
        else:
            self.vx = self.speed
            self.vy = 0
            self.dir_x = 1
            self.dir_y = 0
    
    @property
    def rect(self) -> pygame.Rect:
        """Get shuriken bounding rectangle."""
        return pygame.Rect(
            self.x - self.size,
            self.y - self.size,
            self.size * 2,
            self.size * 2
        )
    
    def check_collision_with_enemy(self, enemy) -> bool:
        """Check if shuriken collides with an enemy."""
        enemy_radius = enemy.size // 2
        dist = math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)
        return dist < enemy_radius + self.size // 2
    
    def update(self, dt: float):
        """Update shuriken position and rotation."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rotation += self.rotation_speed * dt
        
        # Check max range
        traveled = math.sqrt((self.x - self.start_x) ** 2 + (self.y - self.start_y) ** 2)
        if traveled >= self.max_range:
            self.active = False
        
        # Deactivate if out of bounds
        margin = self.size * 2
        if (self.x < -margin or self.x > SCREEN_WIDTH + margin or
            self.y < -margin or self.y > SCREEN_HEIGHT + margin):
            self.active = False
    
    def draw(self, surface: pygame.Surface):
        """Draw the rotating shuriken."""
        # Calculate star points
        points = []
        num_points = 4
        outer_radius = self.size
        inner_radius = self.size // 3
        
        for i in range(num_points * 2):
            angle = math.radians(self.rotation + i * (360 / (num_points * 2)))
            if i % 2 == 0:
                r = outer_radius
            else:
                r = inner_radius
            px = self.x + math.cos(angle) * r
            py = self.y + math.sin(angle) * r
            points.append((px, py))
        
        # Draw shadow/glow
        glow_surface = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        glow_points = [(p[0] - self.x + self.size * 2, p[1] - self.y + self.size * 2) for p in points]
        pygame.draw.polygon(glow_surface, (150, 0, 0, 60), glow_points)
        surface.blit(glow_surface, (int(self.x - self.size * 2), int(self.y - self.size * 2)))
        
        # Draw main shuriken
        pygame.draw.polygon(surface, (180, 20, 20), points)  # Dark red
        pygame.draw.polygon(surface, (220, 50, 50), points, 2)  # Lighter red outline
        
        # Draw center
        pygame.draw.circle(surface, (50, 50, 50), (int(self.x), int(self.y)), 4)
        pygame.draw.circle(surface, (150, 0, 0), (int(self.x), int(self.y)), 4, 1)
