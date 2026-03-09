"""Zed's Shadow effect for W ability."""

import pygame
import math
from game.config import ZED_W_SHADOW_DURATION, SCREEN_WIDTH, SCREEN_HEIGHT


class Shadow:
    """Zed's living shadow that can be teleported to."""
    
    def __init__(self, x: float, y: float, direction_x: float, direction_y: float, distance: float):
        self.x = x
        self.y = y
        self.active = True
        self.duration = ZED_W_SHADOW_DURATION
        self.timer = self.duration
        self.pulse = 0  # For visual pulsing effect
        
        # Calculate shadow position
        if direction_x == 0 and direction_y == 0:
            direction_x = 1
        
        # Normalize direction
        dist = math.sqrt(direction_x ** 2 + direction_y ** 2)
        self.dir_x = direction_x / dist
        self.dir_y = direction_y / dist
        
        # Set shadow position
        self.shadow_x = x + self.dir_x * distance
        self.shadow_y = y + self.dir_y * distance
        
        # Keep within bounds
        self.shadow_x = max(20, min(SCREEN_WIDTH - 20, self.shadow_x))
        self.shadow_y = max(20, min(SCREEN_HEIGHT - 20, self.shadow_y))
        
        # Trail effect
        self.trail_points = []
        self.generate_trail()
    
    def generate_trail(self):
        """Generate trail points from player to shadow."""
        num_points = 10
        for i in range(num_points + 1):
            t = i / num_points
            px = self.x + (self.shadow_x - self.x) * t
            py = self.y + (self.shadow_y - self.y) * t
            self.trail_points.append((px, py))
    
    def update(self, dt: float):
        """Update shadow timer."""
        self.timer -= dt
        self.pulse += dt * 5  # Pulse speed
        
        if self.timer <= 0:
            self.active = False
    
    def get_position(self) -> tuple:
        """Get shadow position for teleport."""
        return (self.shadow_x, self.shadow_y)
    
    def draw(self, surface: pygame.Surface):
        """Draw the shadow and its trail."""
        if not self.active:
            return
        
        # Calculate alpha based on remaining time
        alpha = int(200 * (self.timer / self.duration))
        pulse_alpha = int(alpha * (0.7 + 0.3 * math.sin(self.pulse)))
        
        # Draw trail
        if len(self.trail_points) > 1:
            for i in range(len(self.trail_points) - 1):
                t = i / len(self.trail_points)
                point_alpha = int(alpha * (1 - t) * 0.5)
                
                trail_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(
                    trail_surface,
                    (100, 0, 150, point_alpha),
                    self.trail_points[i],
                    self.trail_points[i + 1],
                    3
                )
                surface.blit(trail_surface, (0, 0))
        
        # Draw shadow body (dark figure)
        shadow_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        
        # Shadow body - dark silhouette
        body_color = (30, 30, 40, pulse_alpha)
        outline_color = (150, 0, 200, alpha)
        
        # Draw shadow figure (similar to Zed but darker)
        center = (25, 25)
        
        # Body
        pygame.draw.ellipse(shadow_surface, body_color, (10, 15, 30, 35))
        pygame.draw.ellipse(shadow_surface, outline_color, (10, 15, 30, 35), 2)
        
        # Head
        pygame.draw.circle(shadow_surface, body_color, center, 12)
        pygame.draw.circle(shadow_surface, outline_color, center, 12, 2)
        
        # Glowing eyes
        eye_color = (200, 0, 255, alpha)
        pygame.draw.circle(shadow_surface, eye_color, (21, 23), 3)
        pygame.draw.circle(shadow_surface, eye_color, (29, 23), 3)
        
        surface.blit(shadow_surface, (int(self.shadow_x - 25), int(self.shadow_y - 25)))
        
        # Draw pulsing ring around shadow
        ring_radius = 20 + int(5 * math.sin(self.pulse))
        ring_surface = pygame.Surface((ring_radius * 2 + 10, ring_radius * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(
            ring_surface,
            (150, 0, 200, int(alpha * 0.5)),
            (ring_radius + 5, ring_radius + 5),
            ring_radius,
            2
        )
        surface.blit(
            ring_surface,
            (int(self.shadow_x - ring_radius - 5), int(self.shadow_y - ring_radius - 5))
        )