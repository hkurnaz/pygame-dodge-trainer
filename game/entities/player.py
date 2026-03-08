"""Player character entity."""

import pygame
import math
from game.config import (
    PLAYER_SIZE, PLAYER_SPEED, PLAYER_COLOR, 
    YELLOW, SKIN_COLOR, DARK_YELLOW, LIGHT_YELLOW,
    BLACK, WHITE, Q_SKILL_COOLDOWN
)


class Player:
    """Main player character with yellow hair."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.color = PLAYER_COLOR
        
        # Movement
        self.target_x = x
        self.target_y = y
        self.is_moving = False
        
        # Cooldowns
        self.teleport_cooldown = 0.0
        self.q_cooldown = 0.0
        
        # Map reference for collision
        self.game_map = None
    
    def set_map(self, game_map):
        """Set the map reference for collision detection."""
        self.game_map = game_map
    
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
        
    @property
    def position(self) -> tuple:
        """Get current position as tuple."""
        return (self.x, self.y)
    
    @property
    def rect(self) -> pygame.Rect:
        """Get player bounding rectangle."""
        return pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size
        )
    
    def set_target(self, target_x: float, target_y: float):
        """Set movement target position."""
        self.target_x = target_x
        self.target_y = target_y
        self.is_moving = True
    
    def teleport(self, target_x: float, target_y: float, max_distance: float) -> tuple:
        """Teleport towards target position, returns new position."""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return self.x, self.y
        
        # Normalize and apply max distance
        dx = dx / distance * max_distance
        dy = dy / distance * max_distance
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Keep within screen bounds
        from game.config import SCREEN_WIDTH, SCREEN_HEIGHT
        new_x = max(self.size // 2, min(SCREEN_WIDTH - self.size // 2, new_x))
        new_y = max(self.size // 2, min(SCREEN_HEIGHT - self.size // 2, new_y))
        
        # Check wall collision - if colliding, try to find valid position along the path
        if self._check_wall_collision(new_x, new_y):
            # Try shorter distances until we find a valid spot
            for factor in [0.8, 0.6, 0.4, 0.2, 0.1]:
                test_x = self.x + dx * factor
                test_y = self.y + dy * factor
                test_x = max(self.size // 2, min(SCREEN_WIDTH - self.size // 2, test_x))
                test_y = max(self.size // 2, min(SCREEN_HEIGHT - self.size // 2, test_y))
                if not self._check_wall_collision(test_x, test_y):
                    return test_x, test_y
            return self.x, self.y  # Can't teleport, stay in place
        
        return new_x, new_y
    
    def update(self, dt: float):
        """Update player position and state."""
        # Update cooldowns
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= dt
        if self.q_cooldown > 0:
            self.q_cooldown -= dt
        
        # Move towards target
        if self.is_moving:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < 5:  # Close enough to target
                self.x = self.target_x
                self.y = self.target_y
                self.is_moving = False
            else:
                # Move at constant speed
                move_distance = self.speed * dt
                if move_distance >= distance:
                    new_x = self.target_x
                    new_y = self.target_y
                else:
                    new_x = self.x + (dx / distance) * move_distance
                    new_y = self.y + (dy / distance) * move_distance
                
                # Check wall collision
                if not self._check_wall_collision(new_x, new_y):
                    self.x = new_x
                    self.y = new_y
                else:
                    # Try sliding along walls
                    # Try moving only in X
                    if not self._check_wall_collision(new_x, self.y):
                        self.x = new_x
                    # Try moving only in Y
                    elif not self._check_wall_collision(self.x, new_y):
                        self.y = new_y
                    else:
                        # Can't move, stop
                        self.is_moving = False
    
    def draw(self, surface: pygame.Surface):
        """Draw the player character with yellow hair."""
        center_x = int(self.x)
        center_y = int(self.y)
        
        # Draw body (blue rectangle)
        body_rect = pygame.Rect(
            center_x - self.size // 2,
            center_y - self.size // 4,
            self.size,
            self.size // 2 + self.size // 4
        )
        pygame.draw.rect(surface, self.color, body_rect, border_radius=5)
        pygame.draw.rect(surface, (50, 100, 200), body_rect, 2, border_radius=5)
        
        # Draw head (skin-colored circle)
        head_radius = self.size // 3
        pygame.draw.circle(surface, SKIN_COLOR, (center_x, center_y - self.size // 4), head_radius)
        pygame.draw.circle(surface, (200, 180, 140), (center_x, center_y - self.size // 4), head_radius, 2)
        
        # Draw yellow hair (spiky style)
        hair_y = center_y - self.size // 4 - head_radius // 2
        
        # Main hair shape
        hair_points = [
            (center_x - head_radius, center_y - self.size // 4 + 2),
            (center_x - head_radius + 5, center_y - self.size // 4 - head_radius),
            (center_x - head_radius // 2, center_y - self.size // 4 - head_radius - 5),
            (center_x, center_y - self.size // 4 - head_radius + 3),
            (center_x + head_radius // 3, center_y - self.size // 4 - head_radius - 8),
            (center_x + head_radius // 2, center_y - self.size // 4 - head_radius - 2),
            (center_x + head_radius - 3, center_y - self.size // 4 - head_radius + 2),
            (center_x + head_radius, center_y - self.size // 4 + 2),
        ]
        pygame.draw.polygon(surface, YELLOW, hair_points)
        pygame.draw.polygon(surface, DARK_YELLOW, hair_points, 2)
        
        # Additional hair spikes
        spike_points = [
            (center_x - head_radius // 2, center_y - self.size // 4 - head_radius - 3),
            (center_x - head_radius // 3, center_y - self.size // 4 - head_radius - 12),
            (center_x, center_y - self.size // 4 - head_radius - 5),
        ]
        pygame.draw.polygon(surface, LIGHT_YELLOW, spike_points)
        
        # Draw eyes
        eye_offset = head_radius // 3
        eye_y = center_y - self.size // 4 - 2
        pygame.draw.circle(surface, BLACK, (center_x - eye_offset, eye_y), 3)
        pygame.draw.circle(surface, BLACK, (center_x + eye_offset, eye_y), 3)
        pygame.draw.circle(surface, WHITE, (center_x - eye_offset - 1, eye_y - 1), 1)
        pygame.draw.circle(surface, WHITE, (center_x + eye_offset - 1, eye_y - 1), 1)
        
        # Draw feet
        foot_y = center_y + self.size // 2
        pygame.draw.ellipse(surface, (80, 80, 80), 
                          (center_x - self.size // 3, foot_y - 5, self.size // 4, 10))
        pygame.draw.ellipse(surface, (80, 80, 80), 
                          (center_x + self.size // 8, foot_y - 5, self.size // 4, 10))
