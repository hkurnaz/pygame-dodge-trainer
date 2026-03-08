"""Enemy entity."""

import pygame
import math
import random
from game.config import (
    ENEMY_SIZE, ENEMY_COLOR, ENEMY_OUTLINE_COLOR,
    ENEMY_PROJECTILE_SIZE, ENEMY_PROJECTILE_SPEED, ENEMY_PROJECTILE_COLOR,
    ENEMY_SHOOT_INTERVAL, SCREEN_WIDTH, SCREEN_HEIGHT,
    SPEAR_ENEMY_SIZE, SPEAR_ENEMY_COLOR, SPEAR_ENEMY_OUTLINE_COLOR,
    SPEAR_ENEMY_SPEED, SPEAR_LENGTH
)


class EnemyProjectile:
    """Projectile fired by enemy towards player."""
    
    def __init__(self, x: float, y: float, target_x: float, target_y: float):
        self.x = x
        self.y = y
        self.size = ENEMY_PROJECTILE_SIZE
        self.speed = ENEMY_PROJECTILE_SPEED
        self.color = ENEMY_PROJECTILE_COLOR
        self.active = True
        
        # Calculate direction towards target
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
        else:
            self.vx = 0
            self.vy = 0
    
    @property
    def rect(self) -> pygame.Rect:
        """Get projectile bounding rectangle."""
        return pygame.Rect(
            self.x - self.size,
            self.y - self.size,
            self.size * 2,
            self.size * 2
        )
    
    def update(self, dt: float):
        """Update projectile position."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Deactivate if out of bounds
        if (self.x < -self.size * 2 or self.x > SCREEN_WIDTH + self.size * 2 or
            self.y < -self.size * 2 or self.y > SCREEN_HEIGHT + self.size * 2):
            self.active = False
    
    def draw(self, surface: pygame.Surface):
        """Draw the enemy projectile."""
        # Draw glow effect
        glow_radius = self.size + 6
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.color, 80), (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surface, (int(self.x - glow_radius), int(self.y - glow_radius)))
        
        # Draw main projectile (red)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, (255, 150, 150), (int(self.x), int(self.y)), self.size // 2)


class Enemy:
    """Enemy that spawns and shoots projectiles at player."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.size = ENEMY_SIZE
        self.color = ENEMY_COLOR
        self.outline_color = ENEMY_OUTLINE_COLOR
        self.shoot_timer = random.uniform(0.5, ENEMY_SHOOT_INTERVAL)  # Random initial delay
        self.projectiles: list = []
        self.active = True
    
    @property
    def rect(self) -> pygame.Rect:
        """Get enemy bounding rectangle."""
        return pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size
        )
    
    def shoot(self, target_x: float, target_y: float) -> EnemyProjectile:
        """Shoot a projectile towards target position."""
        projectile = EnemyProjectile(self.x, self.y, target_x, target_y)
        return projectile
    
    def update(self, dt: float, player_x: float, player_y: float) -> list:
        """Update enemy and return any new projectiles."""
        new_projectiles = []
        
        # Update shoot timer
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            # Shoot at player's current position
            new_projectiles.append(self.shoot(player_x, player_y))
            self.shoot_timer = ENEMY_SHOOT_INTERVAL
        
        # Update existing projectiles
        for projectile in self.projectiles:
            projectile.update(dt)
        
        # Remove inactive projectiles
        self.projectiles = [p for p in self.projectiles if p.active]
        
        return new_projectiles
    
    def draw(self, surface: pygame.Surface):
        """Draw the enemy as a red circle with angry eyes."""
        center_x = int(self.x)
        center_y = int(self.y)
        
        # Draw shadow
        shadow_surface = pygame.Surface((self.size + 10, self.size // 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 50), (0, 0, self.size + 10, self.size // 2))
        surface.blit(shadow_surface, (center_x - (self.size + 10) // 2, center_y + self.size // 3))
        
        # Draw main body (red circle)
        pygame.draw.circle(surface, self.color, (center_x, center_y), self.size // 2)
        pygame.draw.circle(surface, self.outline_color, (center_x, center_y), self.size // 2, 3)
        
        # Draw angry eyes
        eye_offset = self.size // 5
        eye_y = center_y - 2
        
        # Left eye (angry - slanted)
        pygame.draw.circle(surface, (255, 255, 255), (center_x - eye_offset, eye_y), 5)
        pygame.draw.circle(surface, (0, 0, 0), (center_x - eye_offset, eye_y), 3)
        
        # Right eye (angry - slanted)
        pygame.draw.circle(surface, (255, 255, 255), (center_x + eye_offset, eye_y), 5)
        pygame.draw.circle(surface, (0, 0, 0), (center_x + eye_offset, eye_y), 3)
        
        # Angry eyebrows
        pygame.draw.line(surface, (0, 0, 0), 
                        (center_x - eye_offset - 6, eye_y - 6),
                        (center_x - eye_offset + 4, eye_y - 4), 2)
        pygame.draw.line(surface, (0, 0, 0),
                        (center_x + eye_offset - 4, eye_y - 4),
                        (center_x + eye_offset + 6, eye_y - 6), 2)
        
        # Draw mouth (angry)
        pygame.draw.arc(surface, (0, 0, 0),
                       (center_x - 6, center_y, 12, 8),
                       3.14, 0, 2)  # Frown
        
        # Draw all projectiles
        for projectile in self.projectiles:
            projectile.draw(surface)
    
    @staticmethod
    def spawn_random() -> 'Enemy':
        """Spawn enemy at random position on screen edge."""
        side = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left
        
        margin = ENEMY_SIZE
        
        if side == 0:  # Top
            x = random.randint(margin, SCREEN_WIDTH - margin)
            y = margin
        elif side == 1:  # Right
            x = SCREEN_WIDTH - margin
            y = random.randint(margin, SCREEN_HEIGHT - margin)
        elif side == 2:  # Bottom
            x = random.randint(margin, SCREEN_WIDTH - margin)
            y = SCREEN_HEIGHT - margin
        else:  # Left
            x = margin
            y = random.randint(margin, SCREEN_HEIGHT - margin)
        
        return Enemy(x, y)


class SpearEnemy:
    """Enemy that follows player with a spear. Spear collision = game over."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.size = SPEAR_ENEMY_SIZE
        self.speed = SPEAR_ENEMY_SPEED
        self.color = SPEAR_ENEMY_COLOR
        self.outline_color = SPEAR_ENEMY_OUTLINE_COLOR
        self.spear_length = SPEAR_LENGTH
        self.active = True
        self.game_map = None
    
    def set_map(self, game_map):
        """Set the map reference for collision detection."""
        self.game_map = game_map
    
    @property
    def rect(self) -> pygame.Rect:
        """Get enemy bounding rectangle."""
        return pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size
        )
    
    @property
    def spear_rect(self) -> pygame.Rect:
        """Get spear bounding rectangle for collision."""
        # Spear extends in front of the enemy
        # Calculate direction based on where enemy is facing (towards player)
        return pygame.Rect(
            self.x - self.spear_length // 2,
            self.y - self.spear_length // 2,
            self.spear_length,
            self.spear_length
        )
    
    def _check_wall_collision(self, new_x: float, new_y: float) -> bool:
        """Check if position would collide with a wall."""
        if self.game_map is None:
            return False
        
        test_rect = pygame.Rect(
            new_x - self.size // 2,
            new_y - self.size // 2,
            self.size,
            self.size
        )
        return self.game_map.check_collision(test_rect)
    
    def update(self, dt: float, player_x: float, player_y: float):
        """Update enemy position to follow player."""
        # Calculate direction to player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normalize direction
            dx = dx / distance
            dy = dy / distance
            
            # Move towards player
            move_distance = self.speed * dt
            
            new_x = self.x + dx * move_distance
            new_y = self.y + dy * move_distance
            
            # Check wall collision with sliding
            if not self._check_wall_collision(new_x, new_y):
                self.x = new_x
                self.y = new_y
            else:
                # Try moving only in X
                if not self._check_wall_collision(new_x, self.y):
                    self.x = new_x
                # Try moving only in Y
                elif not self._check_wall_collision(self.x, new_y):
                    self.y = new_y
    
    def check_spear_collision(self, player_rect: pygame.Rect) -> bool:
        """Check if spear collides with player."""
        # Calculate angle to player for spear direction
        dx = player_rect.centerx - self.x
        dy = player_rect.centery - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return False
        
        # Normalize direction
        dx = dx / distance
        dy = dy / distance
        
        # Spear tip position
        spear_tip_x = self.x + dx * (self.size // 2 + self.spear_length)
        spear_tip_y = self.y + dy * (self.size // 2 + self.spear_length)
        
        # Check if spear tip is inside player rect
        if player_rect.collidepoint(spear_tip_x, spear_tip_y):
            return True
        
        # Also check along the spear shaft
        for i in range(1, int(self.spear_length)):
            check_x = self.x + dx * (self.size // 2 + i)
            check_y = self.y + dy * (self.size // 2 + i)
            if player_rect.collidepoint(check_x, check_y):
                return True
        
        return False
    
    def draw(self, surface: pygame.Surface):
        """Draw the spear enemy."""
        center_x = int(self.x)
        center_y = int(self.y)
        
        # Calculate angle to draw spear in correct direction
        # (we'll use player position passed separately, but for now draw to the right)
        
        # Draw shadow
        shadow_surface = pygame.Surface((self.size + 10, self.size // 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 50), (0, 0, self.size + 10, self.size // 2))
        surface.blit(shadow_surface, (center_x - (self.size + 10) // 2, center_y + self.size // 3))
        
        # Draw main body (purple circle)
        pygame.draw.circle(surface, self.color, (center_x, center_y), self.size // 2)
        pygame.draw.circle(surface, self.outline_color, (center_x, center_y), self.size // 2, 3)
        
        # Draw angry eyes
        eye_offset = self.size // 5
        eye_y = center_y - 2
        
        # Eyes with red pupils (aggressive)
        pygame.draw.circle(surface, (255, 255, 255), (center_x - eye_offset, eye_y), 5)
        pygame.draw.circle(surface, (200, 0, 0), (center_x - eye_offset, eye_y), 3)
        
        pygame.draw.circle(surface, (255, 255, 255), (center_x + eye_offset, eye_y), 5)
        pygame.draw.circle(surface, (200, 0, 0), (center_x + eye_offset, eye_y), 3)
        
        # Angry eyebrows
        pygame.draw.line(surface, (50, 30, 70), 
                        (center_x - eye_offset - 6, eye_y - 6),
                        (center_x - eye_offset + 4, eye_y - 4), 2)
        pygame.draw.line(surface, (50, 30, 70),
                        (center_x + eye_offset - 4, eye_y - 4),
                        (center_x + eye_offset + 6, eye_y - 6), 2)
        
        # Draw mouth (determined expression)
        pygame.draw.line(surface, (50, 30, 70),
                        (center_x - 5, center_y + 5),
                        (center_x + 5, center_y + 5), 2)
    
    def draw_spear(self, surface: pygame.Surface, player_x: float, player_y: float):
        """Draw the spear pointing towards player."""
        # Calculate direction to player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return
        
        # Normalize direction
        dx = dx / distance
        dy = dy / distance
        
        # Spear starts from enemy edge
        start_x = self.x + dx * (self.size // 2)
        start_y = self.y + dy * (self.size // 2)
        
        # Spear tip
        tip_x = self.x + dx * (self.size // 2 + self.spear_length)
        tip_y = self.y + dy * (self.size // 2 + self.spear_length)
        
        # Draw spear shaft (wooden brown)
        pygame.draw.line(surface, (139, 90, 43), 
                        (int(start_x), int(start_y)),
                        (int(tip_x), int(tip_y)), 4)
        
        # Draw spear tip (metallic silver)
        tip_length = 15
        tip_end_x = self.x + dx * (self.size // 2 + self.spear_length + tip_length)
        tip_end_y = self.y + dy * (self.size // 2 + self.spear_length + tip_length)
        
        # Spearhead (triangle)
        perp_x = -dy  # Perpendicular to direction
        perp_y = dx
        
        spear_head_width = 8
        head_points = [
            (int(tip_end_x), int(tip_end_y)),  # Tip
            (int(tip_x + perp_x * spear_head_width), int(tip_y + perp_y * spear_head_width)),
            (int(tip_x - perp_x * spear_head_width), int(tip_y - perp_y * spear_head_width)),
        ]
        pygame.draw.polygon(surface, (180, 180, 190), head_points)
        pygame.draw.polygon(surface, (120, 120, 130), head_points, 2)
    
    @staticmethod
    def spawn_random(game_map=None) -> 'SpearEnemy':
        """Spawn spear enemy at random position on screen edge."""
        side = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left
        
        margin = SPEAR_ENEMY_SIZE * 2
        
        if side == 0:  # Top
            x = random.randint(margin, SCREEN_WIDTH - margin)
            y = margin
        elif side == 1:  # Right
            x = SCREEN_WIDTH - margin
            y = random.randint(margin, SCREEN_HEIGHT - margin)
        elif side == 2:  # Bottom
            x = random.randint(margin, SCREEN_WIDTH - margin)
            y = SCREEN_HEIGHT - margin
        else:  # Left
            x = margin
            y = random.randint(margin, SCREEN_HEIGHT - margin)
        
        enemy = SpearEnemy(x, y)
        if game_map:
            enemy.set_map(game_map)
        
        return enemy
