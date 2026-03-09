"""Zed's Spin Attack effect for E ability."""

import pygame
import math
from game.config import ZED_E_RADIUS


class SpinAttack:
    """Zed's spin attack with hidden blades - area damage effect."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.radius = ZED_E_RADIUS
        self.active = True
        self.duration = 0.4  # seconds - quick spin
        self.timer = self.duration
        self.rotation = 0
        self.hit_enemies = set()  # Track which enemies have been hit
        
        # Blade positions
        self.num_blades = 3
    
    def update(self, dt: float):
        """Update spin animation."""
        self.timer -= dt
        self.rotation += 720 * dt  # Fast rotation
        
        if self.timer <= 0:
            self.active = False
    
    def check_collision_with_enemy(self, enemy) -> bool:
        """Check if enemy is within spin attack radius."""
        dist = math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)
        return dist <= self.radius + enemy.size // 2
    
    def has_hit_enemy(self, enemy_id: int) -> bool:
        """Check if enemy has already been hit."""
        return enemy_id in self.hit_enemies
    
    def mark_enemy_hit(self, enemy_id: int):
        """Mark enemy as hit."""
        self.hit_enemies.add(enemy_id)
    
    def draw(self, surface: pygame.Surface):
        """Draw the spin attack effect."""
        if not self.active:
            return
        
        # Calculate alpha based on remaining time
        progress = 1 - (self.timer / self.duration)
        alpha = int(255 * (1 - progress))
        
        # Draw area indicator (fading)
        area_surface = pygame.Surface((self.radius * 2 + 20, self.radius * 2 + 20), pygame.SRCALPHA)
        pygame.draw.circle(
            area_surface,
            (150, 0, 0, int(alpha * 0.3)),
            (self.radius + 10, self.radius + 10),
            self.radius
        )
        pygame.draw.circle(
            area_surface,
            (200, 50, 50, int(alpha * 0.6)),
            (self.radius + 10, self.radius + 10),
            self.radius,
            2
        )
        surface.blit(area_surface, (int(self.x - self.radius - 10), int(self.y - self.radius - 10)))
        
        # Draw spinning blades
        for i in range(self.num_blades):
            angle = math.radians(self.rotation + i * (360 / self.num_blades))
            
            # Blade position
            blade_dist = self.radius * 0.7
            blade_x = self.x + math.cos(angle) * blade_dist
            blade_y = self.y + math.sin(angle) * blade_dist
            
            # Draw blade (elongated shape)
            blade_length = 30
            blade_width = 8
            
            # Calculate blade points
            perp_x = -math.sin(angle)
            perp_y = math.cos(angle)
            
            blade_points = [
                (blade_x + math.cos(angle) * blade_length,
                 blade_y + math.sin(angle) * blade_length),
                (blade_x + perp_x * blade_width,
                 blade_y + perp_y * blade_width),
                (blade_x - perp_x * blade_width,
                 blade_y - perp_y * blade_width),
            ]
            
            # Draw blade glow
            glow_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
            glow_points = [
                (p[0] - blade_x + 30, p[1] - blade_y + 30) for p in blade_points
            ]
            pygame.draw.polygon(glow_surface, (200, 50, 50, int(alpha * 0.5)), glow_points)
            surface.blit(glow_surface, (int(blade_x - 30), int(blade_y - 30)))
            
            # Draw blade
            pygame.draw.polygon(surface, (150, 20, 20), blade_points)
            pygame.draw.polygon(surface, (220, 80, 80), blade_points, 2)
        
        # Draw center slash effect
        slash_alpha = int(200 * math.sin(progress * math.pi))
        slash_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(slash_surface, (100, 0, 0, slash_alpha), (30, 30), 20)
        pygame.draw.circle(slash_surface, (150, 50, 50, slash_alpha), (30, 30), 15)
        surface.blit(slash_surface, (int(self.x - 30), int(self.y - 30)))