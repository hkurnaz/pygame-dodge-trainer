"""Zilean's Time Bomb effect for Q ability."""

import pygame
import math
from game.config import ZILEAN_Q_DELAY, ZILEAN_Q_RADIUS


class TimeBomb:
    """Zilean's time bomb - thrown to a location and explodes after delay."""
    
    def __init__(self, x: float, y: float, target_x: float, target_y: float):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.radius = ZILEAN_Q_RADIUS
        self.active = True
        self.exploded = False
        
        # Travel animation
        self.travel_speed = 800  # pixels per second
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self.vx = (dx / dist) * self.travel_speed
            self.vy = (dy / dist) * self.travel_speed
            self.travel_time = dist / self.travel_speed
        else:
            self.vx = 0
            self.vy = 0
            self.travel_time = 0
        
        self.travel_timer = 0
        self.landed = False
        
        # Explosion countdown
        self.delay = ZILEAN_Q_DELAY
        self.timer = self.delay
        
        # Visual
        self.pulse = 0
        self.hit_enemies = set()  # Track enemies hit by explosion
    
    def update(self, dt: float):
        """Update bomb state."""
        if self.exploded:
            return
        
        if not self.landed:
            # Travel to target
            self.travel_timer += dt
            progress = min(1.0, self.travel_timer / self.travel_time) if self.travel_time > 0 else 1.0
            
            # Arc trajectory
            arc_height = 100
            self.x = self.start_x + (self.target_x - self.start_x) * progress
            self.y = self.start_y + (self.target_y - self.start_y) * progress - math.sin(progress * math.pi) * arc_height
            
            if progress >= 1.0:
                self.landed = True
                self.x = self.target_x
                self.y = self.target_y
        else:
            # Countdown to explosion
            self.timer -= dt
            self.pulse += dt * 5  # Pulsing effect
            
            if self.timer <= 0:
                self.explode()
    
    def explode(self):
        """Trigger explosion."""
        self.exploded = True
        self.active = False
    
    def check_explosion_collision(self, enemy) -> bool:
        """Check if enemy is within explosion radius."""
        if not self.exploded:
            return False
        dist = math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)
        return dist <= self.radius + enemy.size // 2
    
    def has_hit_enemy(self, enemy_id: int) -> bool:
        """Check if enemy has already been hit by this explosion."""
        return enemy_id in self.hit_enemies
    
    def mark_enemy_hit(self, enemy_id: int):
        """Mark enemy as hit."""
        self.hit_enemies.add(enemy_id)
    
    def draw(self, surface: pygame.Surface):
        """Draw the time bomb."""
        if self.exploded:
            return
        
        if not self.landed:
            # Draw traveling bomb
            bomb_size = 12
            pygame.draw.circle(surface, (100, 80, 60), (int(self.x), int(self.y)), bomb_size)
            pygame.draw.circle(surface, (150, 120, 80), (int(self.x), int(self.y)), bomb_size - 3)
            # Glow
            glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (200, 180, 100, 100), (20, 20), 15)
            surface.blit(glow_surface, (int(self.x - 20), int(self.y - 20)))
        else:
            # Draw landed bomb with countdown
            pulse_size = int(15 + math.sin(self.pulse) * 3)
            
            # Area indicator (growing as it gets closer to explosion)
            progress = 1 - (self.timer / self.delay)
            indicator_alpha = int(50 + progress * 100)
            indicator_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(indicator_surface, (200, 180, 100, indicator_alpha), 
                             (self.radius, self.radius), int(self.radius * progress))
            pygame.draw.circle(indicator_surface, (255, 200, 100, int(indicator_alpha * 1.5)), 
                             (self.radius, self.radius), int(self.radius * progress), 2)
            surface.blit(indicator_surface, (int(self.x - self.radius), int(self.y - self.radius)))
            
            # Bomb body
            pygame.draw.circle(surface, (80, 60, 40), (int(self.x), int(self.y)), pulse_size)
            pygame.draw.circle(surface, (150, 120, 80), (int(self.x), int(self.y)), pulse_size - 4)
            pygame.draw.circle(surface, (255, 200, 100), (int(self.x), int(self.y)), 8)
            
            # Countdown number
            countdown = int(self.timer) + 1
            if countdown > 0:
                font = pygame.font.Font(None, 24)
                text = font.render(str(countdown), True, (255, 255, 255))
                text_rect = text.get_rect(center=(int(self.x), int(self.y) - 25))
                surface.blit(text, text_rect)


class ExplosionEffect:
    """Visual effect for bomb explosion."""
    
    def __init__(self, x: float, y: float, radius: float):
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True
        self.duration = 0.5
        self.timer = self.duration
        self.expansion = 0
    
    def update(self, dt: float):
        """Update explosion animation."""
        self.timer -= dt
        progress = 1 - (self.timer / self.duration)
        self.expansion = progress
        
        if self.timer <= 0:
            self.active = False
    
    def draw(self, surface: pygame.Surface):
        """Draw explosion effect."""
        if not self.active:
            return
        
        progress = 1 - (self.timer / self.duration)
        current_radius = self.radius * progress
        alpha = int(255 * (1 - progress))
        
        # Outer ring
        ring_surface = pygame.Surface((self.radius * 2 + 40, self.radius * 2 + 40), pygame.SRCALPHA)
        pygame.draw.circle(ring_surface, (255, 200, 100, alpha), 
                         (self.radius + 20, self.radius + 20), int(current_radius))
        pygame.draw.circle(ring_surface, (255, 150, 50, int(alpha * 0.7)), 
                         (self.radius + 20, self.radius + 20), int(current_radius * 0.7))
        pygame.draw.circle(ring_surface, (255, 255, 200, int(alpha * 0.9)), 
                         (self.radius + 20, self.radius + 20), int(current_radius), 3)
        surface.blit(ring_surface, (int(self.x - self.radius - 20), int(self.y - self.radius - 20)))
