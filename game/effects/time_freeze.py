"""Zilean's Time Freeze effect for E ability."""

import pygame
import math
from game.config import ZILEAN_E_RADIUS, ZILEAN_E_DURATION


class TimeFreeze:
    """Zilean's time freeze - freezes enemies in a circular area."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.radius = ZILEAN_E_RADIUS
        self.active = True
        self.duration = ZILEAN_E_DURATION
        self.timer = self.duration
        
        # Visual
        self.expansion = 0
        self.frozen_enemies = set()  # Track which enemies are frozen
    
    def update(self, dt: float):
        """Update freeze effect."""
        self.timer -= dt
        
        # Expand quickly at start
        if self.expansion < 1.0:
            self.expansion += dt * 4
            if self.expansion > 1.0:
                self.expansion = 1.0
        
        if self.timer <= 0:
            self.active = False
    
    def check_collision_with_enemy(self, enemy) -> bool:
        """Check if enemy is within freeze radius."""
        dist = math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)
        return dist <= self.radius + enemy.size // 2
    
    def freeze_enemy(self, enemy_id: int):
        """Mark enemy as frozen."""
        self.frozen_enemies.add(enemy_id)
    
    def is_enemy_frozen(self, enemy_id: int) -> bool:
        """Check if enemy is currently frozen."""
        return enemy_id in self.frozen_enemies and self.active
    
    def draw(self, surface: pygame.Surface):
        """Draw the time freeze effect."""
        if not self.active:
            return
        
        progress = 1 - (self.timer / self.duration)
        current_radius = self.radius * self.expansion
        
        # Outer ice ring
        alpha = int(150 * (1 - progress * 0.5))
        ring_surface = pygame.Surface((self.radius * 2 + 40, self.radius * 2 + 40), pygame.SRCALPHA)
        
        # Main ice circle
        pygame.draw.circle(ring_surface, (100, 180, 255, int(alpha * 0.4)), 
                         (self.radius + 20, self.radius + 20), int(current_radius))
        
        # Ice border
        pygame.draw.circle(ring_surface, (150, 220, 255, alpha), 
                         (self.radius + 20, self.radius + 20), int(current_radius), 4)
        
        # Inner glow
        pygame.draw.circle(ring_surface, (200, 240, 255, int(alpha * 0.6)), 
                         (self.radius + 20, self.radius + 20), int(current_radius * 0.6))
        
        # Ice crystal lines
        num_crystals = 8
        for i in range(num_crystals):
            angle = math.radians(i * (360 / num_crystals) + progress * 90)
            inner_r = current_radius * 0.3
            outer_r = current_radius * 0.9
            
            x1 = self.radius + 20 + math.cos(angle) * inner_r
            y1 = self.radius + 20 + math.sin(angle) * inner_r
            x2 = self.radius + 20 + math.cos(angle) * outer_r
            y2 = self.radius + 20 + math.sin(angle) * outer_r
            
            pygame.draw.line(ring_surface, (180, 230, 255, int(alpha * 0.8)), 
                           (x1, y1), (x2, y2), 3)
        
        surface.blit(ring_surface, (int(self.x - self.radius - 20), int(self.y - self.radius - 20)))
        
        # Center clock symbol
        clock_alpha = int(200 * (1 - progress))
        clock_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(clock_surface, (255, 255, 255, clock_alpha), (30, 30), 25, 3)
        # Clock hands
        hand_angle = math.radians(-90 + progress * 360)
        hand_x = 30 + math.cos(hand_angle) * 18
        hand_y = 30 + math.sin(hand_angle) * 18
        pygame.draw.line(clock_surface, (255, 255, 255, clock_alpha), (30, 30), (hand_x, hand_y), 3)
        pygame.draw.line(clock_surface, (255, 255, 255, clock_alpha), (30, 30), (30, 15), 2)
        surface.blit(clock_surface, (int(self.x - 30), int(self.y - 30)))


class FrozenEffect:
    """Visual effect applied to frozen enemies."""
    
    def __init__(self, enemy):
        self.enemy = enemy
        self.active = True
        self.pulse = 0
    
    def update(self, dt: float):
        """Update frozen visual effect."""
        self.pulse += dt * 4
    
    def draw(self, surface: pygame.Surface):
        """Draw frozen effect on enemy."""
        if not self.active:
            return
        
        # Ice overlay on enemy
        size = self.enemy.size // 2 + 5
        pulse_size = int(size + math.sin(self.pulse) * 3)
        
        ice_surface = pygame.Surface((pulse_size * 2 + 10, pulse_size * 2 + 10), pygame.SRCALPHA)
        
        # Ice glow
        pygame.draw.circle(ice_surface, (150, 220, 255, 150), 
                         (pulse_size + 5, pulse_size + 5), pulse_size)
        pygame.draw.circle(ice_surface, (200, 240, 255, 200), 
                         (pulse_size + 5, pulse_size + 5), pulse_size - 5)
        
        # Ice crystals
        for i in range(4):
            angle = math.radians(i * 90 + self.pulse * 30)
            x = pulse_size + 5 + math.cos(angle) * (pulse_size * 0.7)
            y = pulse_size + 5 + math.sin(angle) * (pulse_size * 0.7)
            pygame.draw.circle(ice_surface, (255, 255, 255, 180), (int(x), int(y)), 4)
        
        surface.blit(ice_surface, (int(self.enemy.x - pulse_size - 5), int(self.enemy.y - pulse_size - 5)))
