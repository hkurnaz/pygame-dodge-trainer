"""Death effect for enemies."""

import pygame
import math
import random
from game.config import DEATH_EFFECT_DURATION, DEATH_EFFECT_PARTICLES


class DeathParticle:
    """A single particle in the death effect."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.active = True
        
        # Random velocity
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 150)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        # Random size
        self.size = random.randint(3, 8)
        
        # Color variation (red blood)
        self.color = (
            random.randint(180, 255),
            random.randint(20, 60),
            random.randint(20, 60)
        )
        
        # Lifetime
        self.lifetime = DEATH_EFFECT_DURATION
        self.timer = self.lifetime
    
    def update(self, dt: float):
        """Update particle position and state."""
        self.timer -= dt
        
        if self.timer <= 0:
            self.active = False
            return
        
        # Move
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Slow down
        self.vx *= 0.95
        self.vy *= 0.95
    
    def draw(self, surface: pygame.Surface):
        """Draw the particle."""
        if not self.active:
            return
        
        # Calculate alpha based on remaining lifetime
        alpha = int(255 * (self.timer / self.lifetime))
        
        # Draw particle with alpha
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (*self.color, alpha), (self.size, self.size), self.size)
        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))


class DeathEffect:
    """Blood explosion effect when enemy dies."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.particles = []
        self.active = True
        self.timer = DEATH_EFFECT_DURATION
        
        # Create particles
        for _ in range(DEATH_EFFECT_PARTICLES):
            self.particles.append(DeathParticle(x, y))
        
        # Add some larger "splatter" particles
        for _ in range(4):
            particle = DeathParticle(x, y)
            particle.size = random.randint(10, 15)
            particle.vx *= 0.5
            particle.vy *= 0.5
            self.particles.append(particle)
    
    def update(self, dt: float):
        """Update all particles."""
        self.timer -= dt
        
        for particle in self.particles:
            particle.update(dt)
        
        # Remove inactive particles
        self.particles = [p for p in self.particles if p.active]
        
        if not self.particles:
            self.active = False
    
    def draw(self, surface: pygame.Surface):
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(surface)
