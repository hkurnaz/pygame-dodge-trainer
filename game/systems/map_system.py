"""Map system for LoL-style mid lane."""

import pygame
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WALL_COLOR, WALL_OUTLINE_COLOR,
    GRASS_COLOR, PATH_COLOR, RIVER_COLOR, BUSH_COLOR
)


class Wall:
    """Represents a wall that blocks movement."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, surface: pygame.Surface):
        """Draw the wall."""
        pygame.draw.rect(surface, WALL_COLOR, self.rect)
        pygame.draw.rect(surface, WALL_OUTLINE_COLOR, self.rect, 2)


class GameMap:
    """LoL-style mid lane map with walls."""
    
    def __init__(self):
        self.walls = []
        self.decorations = []  # Non-collision decorative elements
        self._create_mid_lane_map()
    
    def _create_mid_lane_map(self):
        """Create a mid lane style map with walls on sides - open and spacious."""
        wall_thickness = 35
        
        # Border walls with large gaps for entry/exit
        # Top border - two segments with large center gap
        self.walls.append(Wall(0, 0, 250, wall_thickness))
        self.walls.append(Wall(SCREEN_WIDTH - 250, 0, 250, wall_thickness))
        
        # Bottom border - two segments with large center gap
        self.walls.append(Wall(0, SCREEN_HEIGHT - wall_thickness, 250, wall_thickness))
        self.walls.append(Wall(SCREEN_WIDTH - 250, SCREEN_HEIGHT - wall_thickness, 250, wall_thickness))
        
        # Left border - two segments with large center gap
        self.walls.append(Wall(0, 0, wall_thickness, 250))
        self.walls.append(Wall(0, SCREEN_HEIGHT - 250, wall_thickness, 250))
        
        # Right border - two segments with large center gap
        self.walls.append(Wall(SCREEN_WIDTH - wall_thickness, 0, wall_thickness, 250))
        self.walls.append(Wall(SCREEN_WIDTH - wall_thickness, SCREEN_HEIGHT - 250, wall_thickness, 250))
        
        # Corner structures (turret-like areas) - smaller and less intrusive
        corner_size = 70
        corner_offset = 180
        
        # Top-left corner structure
        self.walls.append(Wall(corner_offset, corner_offset, corner_size, wall_thickness))
        self.walls.append(Wall(corner_offset, corner_offset, wall_thickness, corner_size))
        
        # Top-right corner structure
        self.walls.append(Wall(SCREEN_WIDTH - corner_offset - corner_size, corner_offset, corner_size, wall_thickness))
        self.walls.append(Wall(SCREEN_WIDTH - corner_offset - wall_thickness, corner_offset, wall_thickness, corner_size))
        
        # Bottom-left corner structure
        self.walls.append(Wall(corner_offset, SCREEN_HEIGHT - corner_offset - wall_thickness, corner_size, wall_thickness))
        self.walls.append(Wall(corner_offset, SCREEN_HEIGHT - corner_offset - corner_size, wall_thickness, corner_size))
        
        # Bottom-right corner structure
        self.walls.append(Wall(SCREEN_WIDTH - corner_offset - corner_size, SCREEN_HEIGHT - corner_offset - wall_thickness, corner_size, wall_thickness))
        self.walls.append(Wall(SCREEN_WIDTH - corner_offset - wall_thickness, SCREEN_HEIGHT - corner_offset - corner_size, wall_thickness, corner_size))
        
        # Center area - small pillars for cover (not blocking movement much)
        pillar_size = 40
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Four small pillars around center
        pillar_offset = 120
        self.walls.append(Wall(center_x - pillar_offset - pillar_size // 2, center_y - pillar_offset - pillar_size // 2, pillar_size, pillar_size))
        self.walls.append(Wall(center_x + pillar_offset - pillar_size // 2, center_y - pillar_offset - pillar_size // 2, pillar_size, pillar_size))
        self.walls.append(Wall(center_x - pillar_offset - pillar_size // 2, center_y + pillar_offset - pillar_size // 2, pillar_size, pillar_size))
        self.walls.append(Wall(center_x + pillar_offset - pillar_size // 2, center_y + pillar_offset - pillar_size // 2, pillar_size, pillar_size))
    
    def check_collision(self, rect: pygame.Rect) -> bool:
        """Check if a rectangle collides with any wall."""
        for wall in self.walls:
            if rect.colliderect(wall.rect):
                return True
        return False
    
    def get_valid_spawn_position(self, entity_size: int, avoid_walls: bool = True) -> tuple:
        """Get a valid spawn position that doesn't collide with walls."""
        import random
        margin = entity_size + 50
        
        for _ in range(100):  # Try 100 times
            x = random.randint(margin, SCREEN_WIDTH - margin)
            y = random.randint(margin, SCREEN_HEIGHT - margin)
            
            test_rect = pygame.Rect(x - entity_size // 2, y - entity_size // 2, entity_size, entity_size)
            
            if not avoid_walls or not self.check_collision(test_rect):
                return x, y
        
        # Fallback to center
        return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    
    def draw(self, surface: pygame.Surface):
        """Draw the map background and walls."""
        # Draw grass background
        surface.fill(GRASS_COLOR)
        
        # Draw path (mid lane)
        path_width = 200
        path_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - path_width // 2,
            0,
            path_width,
            SCREEN_HEIGHT
        )
        pygame.draw.rect(surface, PATH_COLOR, path_rect)
        
        # Draw horizontal path sections
        h_path_height = 150
        pygame.draw.rect(surface, PATH_COLOR, 
                        pygame.Rect(0, SCREEN_HEIGHT // 2 - h_path_height // 2, 
                                   SCREEN_WIDTH, h_path_height))
        
        # Draw river (diagonal area in center)
        river_points = [
            (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50),
            (SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2 - 50),
            (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 + 50),
            (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 50),
        ]
        pygame.draw.polygon(surface, RIVER_COLOR, river_points)
        
        # Draw bushes
        bush_positions = [
            (100, 350), (100, 420),  # Left bushes
            (SCREEN_WIDTH - 150, 350), (SCREEN_WIDTH - 150, 420),  # Right bushes
            (SCREEN_WIDTH // 2 - 120, 180), (SCREEN_WIDTH // 2 + 70, 180),  # Top bushes
            (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 220), (SCREEN_WIDTH // 2 + 70, SCREEN_HEIGHT - 220),  # Bottom bushes
        ]
        
        for bx, by in bush_positions:
            bush_rect = pygame.Rect(bx, by, 50, 30)
            pygame.draw.rect(surface, BUSH_COLOR, bush_rect, border_radius=5)
            pygame.draw.rect(surface, (30, 70, 30), bush_rect, 2, border_radius=5)
        
        # Draw all walls
        for wall in self.walls:
            wall.draw(surface)
        
        # Draw wall details (stone texture lines)
        for wall in self.walls:
            # Add some texture lines
            for i in range(0, wall.rect.width, 20):
                if i > 0 and i < wall.rect.width - 5:
                    pygame.draw.line(surface, WALL_OUTLINE_COLOR,
                                   (wall.rect.x + i, wall.rect.y),
                                   (wall.rect.x + i, wall.rect.y + wall.rect.height), 1)
            for j in range(0, wall.rect.height, 15):
                if j > 0 and j < wall.rect.height - 5:
                    pygame.draw.line(surface, WALL_OUTLINE_COLOR,
                                   (wall.rect.x, wall.rect.y + j),
                                   (wall.rect.x + wall.rect.width, wall.rect.y + j), 1)
