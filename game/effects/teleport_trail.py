"""Teleport trail effect."""

import pygame
from game.config import YELLOW, LIGHT_YELLOW, TELEPORT_TRAIL_DURATION


class TeleportTrail:
    """Visual effect for teleport skill."""
    
    def __init__(self, start_x: float, start_y: float, end_x: float, end_y: float):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.duration = TELEPORT_TRAIL_DURATION
        self.timer = self.duration
        self.active = True
    
    def update(self, dt: float):
        """Update trail effect."""
        self.timer -= dt
        if self.timer <= 0:
            self.active = False
    
    def draw(self, surface: pygame.Surface):
        """Draw the teleport trail effect."""
        if not self.active:
            return
        
        # Calculate alpha based on remaining time
        alpha = int(255 * (self.timer / self.duration))
        
        # Draw trail line
        trail_surface = pygame.Surface((abs(self.end_x - self.start_x) + 40, 
                                        abs(self.end_y - self.start_y) + 40), pygame.SRCALPHA)
        
        # Calculate offset for the surface
        offset_x = min(self.start_x, self.end_x) - 20
        offset_y = min(self.start_y, self.end_y) - 20
        
        # Draw multiple lines for glow effect
        for i in range(5, 0, -1):
            line_alpha = int(alpha * (i / 5) * 0.5)
            color = (*LIGHT_YELLOW, line_alpha)
            pygame.draw.line(
                trail_surface,
                color,
                (self.start_x - offset_x, self.start_y - offset_y),
                (self.end_x - offset_x, self.end_y - offset_y),
                i * 3
            )
        
        # Draw sparkles along the trail
        import math
        num_sparkles = 8
        for i in range(num_sparkles):
            t = i / num_sparkles
            sparkle_x = self.start_x + (self.end_x - self.start_x) * t
            sparkle_y = self.start_y + (self.end_y - self.start_y) * t
            
            sparkle_size = int(5 * (self.timer / self.duration))
            sparkle_alpha = int(alpha * 0.8)
            
            # Draw sparkle
            pygame.draw.circle(
                trail_surface,
                (*YELLOW, sparkle_alpha),
                (int(sparkle_x - offset_x), int(sparkle_y - offset_y)),
                sparkle_size
            )
        
        surface.blit(trail_surface, (int(offset_x), int(offset_y)))
        
        # Draw afterimage circles at start and end
        afterimage_alpha = int(alpha * 0.6)
        
        # Start position afterimage
        start_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(start_surface, (*YELLOW, afterimage_alpha), (30, 30), 25)
        pygame.draw.circle(start_surface, (*LIGHT_YELLOW, afterimage_alpha // 2), (30, 30), 15)
        surface.blit(start_surface, (int(self.start_x - 30), int(self.start_y - 30)))
        
        # End position flash
        end_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(end_surface, (*YELLOW, afterimage_alpha), (30, 30), 20)
        pygame.draw.circle(end_surface, (*LIGHT_YELLOW, afterimage_alpha), (30, 30), 10)
        surface.blit(end_surface, (int(self.end_x - 30), int(self.end_y - 30)))
