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
        self.w_cooldown = 0.0  # For Zed's shadow
        self.e_cooldown = 0.0  # For Zed's spin
        
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
        if self.w_cooldown > 0:
            self.w_cooldown -= dt
        if self.e_cooldown > 0:
            self.e_cooldown -= dt
        
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
    
    def draw(self, surface: pygame.Surface, character_type: str = "ezreal"):
        """Draw the player character based on type."""
        if character_type == "zed":
            self._draw_zed(surface)
        else:
            self._draw_ezreal(surface)
    
    def _draw_ezreal(self, surface: pygame.Surface):
        """Draw Ezreal style blond adventurer."""
        center_x = int(self.x)
        center_y = int(self.y)
        
        # Draw shadow
        shadow_surface = pygame.Surface((self.size + 10, self.size // 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 50), (0, 0, self.size + 10, self.size // 2))
        surface.blit(shadow_surface, (center_x - (self.size + 10) // 2, center_y + self.size // 3))
        
        # Draw body (blue adventurer outfit)
        body_color = (70, 130, 180)  # Steel blue
        body_outline = (50, 100, 140)
        body_rect = pygame.Rect(
            center_x - self.size // 2 + 5,
            center_y - self.size // 4,
            self.size - 10,
            self.size // 2 + self.size // 4
        )
        pygame.draw.ellipse(surface, body_color, body_rect)
        pygame.draw.ellipse(surface, body_outline, body_rect, 2)
        
        # Draw head (skin-colored circle)
        head_radius = self.size // 3
        head_y = center_y - self.size // 4
        pygame.draw.circle(surface, (255, 220, 180), (center_x, head_y), head_radius)  # Skin color
        pygame.draw.circle(surface, (220, 190, 150), (center_x, head_y), head_radius, 2)  # Outline
        
        # Draw blond hair (spiky adventurer style like Ezreal)
        hair_color = (255, 215, 0)  # Golden blond
        hair_highlight = (255, 240, 150)  # Lighter blond for highlights
        hair_outline = (200, 170, 0)  # Darker blond for outline
        
        # Main hair shape with spikes
        hair_points = [
            (center_x - head_radius - 2, head_y + 3),
            (center_x - head_radius + 2, head_y - head_radius // 2),
            (center_x - head_radius // 2, head_y - head_radius - 5),
            (center_x - head_radius // 3, head_y - head_radius),
            (center_x, head_y - head_radius - 10),  # Top spike
            (center_x + head_radius // 3, head_y - head_radius),
            (center_x + head_radius // 2, head_y - head_radius - 8),
            (center_x + head_radius - 2, head_y - head_radius // 2),
            (center_x + head_radius + 2, head_y + 3),
        ]
        pygame.draw.polygon(surface, hair_color, hair_points)
        pygame.draw.polygon(surface, hair_outline, hair_points, 2)
        
        # Hair highlight
        highlight_points = [
            (center_x - head_radius // 2, head_y - head_radius - 3),
            (center_x - head_radius // 3, head_y - head_radius - 8),
            (center_x, head_y - head_radius - 5),
        ]
        pygame.draw.polygon(surface, hair_highlight, highlight_points)
        
        # Draw face - handsome features
        # Eyes (blue like Ezreal)
        eye_offset = head_radius // 3
        eye_y = head_y - 2
        
        # Eye whites
        pygame.draw.circle(surface, WHITE, (center_x - eye_offset, eye_y), 4)
        pygame.draw.circle(surface, WHITE, (center_x + eye_offset, eye_y), 4)
        
        # Blue irises
        pygame.draw.circle(surface, (70, 130, 180), (center_x - eye_offset, eye_y), 3)
        pygame.draw.circle(surface, (70, 130, 180), (center_x + eye_offset, eye_y), 3)
        
        # Pupils
        pygame.draw.circle(surface, BLACK, (center_x - eye_offset, eye_y), 1)
        pygame.draw.circle(surface, BLACK, (center_x + eye_offset, eye_y), 1)
        
        # Eye shine
        pygame.draw.circle(surface, WHITE, (center_x - eye_offset - 1, eye_y - 1), 1)
        pygame.draw.circle(surface, WHITE, (center_x + eye_offset - 1, eye_y - 1), 1)
        
        # Confident smile
        pygame.draw.arc(surface, (150, 100, 80),
                       (center_x - 6, head_y + 2, 12, 8),
                       3.14, 0, 2)
        
        # Draw gauntlet on right side (Ezreal's signature golden gauntlet)
        gauntlet_x = center_x + self.size // 3
        gauntlet_y = center_y + 5
        pygame.draw.circle(surface, (255, 215, 0), (gauntlet_x, gauntlet_y), 8)
        pygame.draw.circle(surface, (200, 170, 0), (gauntlet_x, gauntlet_y), 8, 2)
        
        # Gauntlet glow effect
        glow_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 215, 0, 80), (15, 15), 12)
        surface.blit(glow_surface, (gauntlet_x - 15, gauntlet_y - 15))
        
        # Draw feet
        foot_y = center_y + self.size // 2
        pygame.draw.ellipse(surface, (60, 60, 70), 
                          (center_x - self.size // 3, foot_y - 5, self.size // 4, 10))
        pygame.draw.ellipse(surface, (60, 60, 70), 
                          (center_x + self.size // 10, foot_y - 5, self.size // 4, 10))
    
    def _draw_zed(self, surface: pygame.Surface):
        """Draw Zed style shinobi with black/red theme."""
        center_x = int(self.x)
        center_y = int(self.y)
        
        # Draw shadow
        shadow_surface = pygame.Surface((self.size + 10, self.size // 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 50), (0, 0, self.size + 10, self.size // 2))
        surface.blit(shadow_surface, (center_x - (self.size + 10) // 2, center_y + self.size // 3))
        
        # Draw body (dark shinobi outfit)
        body_color = (30, 30, 35)  # Very dark
        body_outline = (80, 0, 0)  # Dark red outline
        body_rect = pygame.Rect(
            center_x - self.size // 2 + 5,
            center_y - self.size // 4,
            self.size - 10,
            self.size // 2 + self.size // 4
        )
        pygame.draw.ellipse(surface, body_color, body_rect)
        pygame.draw.ellipse(surface, body_outline, body_rect, 2)
        
        # Draw head (masked face)
        head_radius = self.size // 3
        head_y = center_y - self.size // 4
        pygame.draw.circle(surface, (20, 20, 25), (center_x, head_y), head_radius)  # Dark mask
        pygame.draw.circle(surface, (100, 0, 0), (center_x, head_y), head_radius, 2)  # Red outline
        
        # Draw mask details - horizontal line
        pygame.draw.line(surface, (120, 0, 0), 
                        (center_x - head_radius + 5, head_y),
                        (center_x + head_radius - 5, head_y), 3)
        
        # Draw glowing red eyes (Zed's signature)
        eye_offset = head_radius // 3
        eye_y = head_y - 2
        
        # Eye glow
        pygame.draw.circle(surface, (200, 0, 0), (center_x - eye_offset, eye_y), 5)
        pygame.draw.circle(surface, (255, 50, 50), (center_x - eye_offset, eye_y), 3)
        pygame.draw.circle(surface, (200, 0, 0), (center_x + eye_offset, eye_y), 5)
        pygame.draw.circle(surface, (255, 50, 50), (center_x + eye_offset, eye_y), 3)
        
        # Draw shadowy hair/spikes
        hair_color = (40, 40, 45)
        hair_points = [
            (center_x - head_radius - 2, head_y + 5),
            (center_x - head_radius + 5, head_y - 20),
            (center_x - head_radius // 2, head_y - 30),
            (center_x, head_y - 25),
            (center_x + head_radius // 2, head_y - 30),
            (center_x + head_radius - 5, head_y - 20),
            (center_x + head_radius + 2, head_y + 5),
        ]
        pygame.draw.polygon(surface, hair_color, hair_points)
        pygame.draw.polygon(surface, (80, 0, 0), hair_points, 2)
        
        # Draw arm blades (hidden blades on both arms)
        for side in [-1, 1]:
            blade_x = center_x + side * (self.size // 2 - 5)
            blade_y = center_y + 10
            blade_points = [
                (blade_x, blade_y),
                (blade_x + side * 15, blade_y - 5),
                (blade_x + side * 15, blade_y + 5),
            ]
            pygame.draw.polygon(surface, (150, 150, 160), blade_points)
            pygame.draw.polygon(surface, (200, 200, 210), blade_points, 1)
            
            # Blade glow
            glow_surface = pygame.Surface((25, 25), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (150, 0, 0, 60), (12, 12), 10)
            surface.blit(glow_surface, (int(blade_x + side * 5 - 12), int(blade_y - 12)))
        
        # Draw feet
        foot_y = center_y + self.size // 2
        pygame.draw.ellipse(surface, (40, 40, 45), 
                          (center_x - self.size // 3, foot_y - 5, self.size // 4, 10))
        pygame.draw.ellipse(surface, (40, 40, 45), 
                          (center_x + self.size // 10, foot_y - 5, self.size // 4, 10))
