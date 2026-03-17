"""Enemy management system."""

import pygame
from game.entities.enemy import Enemy, EnemyProjectile, SpearEnemy, RogueEnemy
from game.config import (
    ENEMY_SPAWN_INTERVAL, SPEAR_ENEMY_SPAWN_INTERVAL, ROGUE_ENEMY_SPAWN_INTERVAL,
    DIFFICULTY_INCREASE_INTERVAL, SPAWN_RATE_MULTIPLIER
)


class EnemyManager:
    """Manages enemy spawning and projectile updates."""
    
    def __init__(self, game_map=None):
        self.enemies: list = []
        self.spear_enemies: list = []
        self.rogue_enemies: list = []
        self.enemy_projectiles: list = []
        
        # Base spawn intervals
        self.base_enemy_spawn_interval = ENEMY_SPAWN_INTERVAL
        self.base_spear_spawn_interval = SPEAR_ENEMY_SPAWN_INTERVAL
        self.base_rogue_spawn_interval = ROGUE_ENEMY_SPAWN_INTERVAL
        
        # Current spawn intervals (decrease over time)
        self.current_enemy_spawn_interval = ENEMY_SPAWN_INTERVAL
        self.current_spear_spawn_interval = SPEAR_ENEMY_SPAWN_INTERVAL
        self.current_rogue_spawn_interval = ROGUE_ENEMY_SPAWN_INTERVAL
        
        self.spawn_timer = ENEMY_SPAWN_INTERVAL
        self.spear_spawn_timer = SPEAR_ENEMY_SPAWN_INTERVAL
        self.rogue_spawn_timer = ROGUE_ENEMY_SPAWN_INTERVAL
        self.game_map = game_map
        
        # Difficulty scaling
        self.difficulty_timer = 0.0
        self.difficulty_level = 0
    
    def set_map(self, game_map):
        """Set the map reference for collision detection."""
        self.game_map = game_map
    
    def spawn_enemy(self):
        """Spawn a new shooting enemy at random position."""
        enemy = Enemy.spawn_random()
        self.enemies.append(enemy)
    
    def spawn_spear_enemy(self):
        """Spawn a new spear enemy at random position."""
        enemy = SpearEnemy.spawn_random(self.game_map)
        self.spear_enemies.append(enemy)
    
    def spawn_rogue_enemy(self):
        """Spawn a new rogue enemy at random position."""
        enemy = RogueEnemy.spawn_random(self.game_map)
        self.rogue_enemies.append(enemy)
    
    def update(self, dt: float, player_x: float, player_y: float):
        """Update all enemies and their projectiles."""
        # Update difficulty timer
        self.difficulty_timer += dt
        if self.difficulty_timer >= DIFFICULTY_INCREASE_INTERVAL:
            self.difficulty_timer = 0
            self.difficulty_level += 1
            # Decrease spawn intervals (faster spawning)
            self.current_enemy_spawn_interval = max(
                0.5,  # Minimum spawn interval
                self.current_enemy_spawn_interval * SPAWN_RATE_MULTIPLIER
            )
            self.current_spear_spawn_interval = max(
                1.5,  # Minimum spawn interval
                self.current_spear_spawn_interval * SPAWN_RATE_MULTIPLIER
            )
            self.current_rogue_spawn_interval = max(
                2.0,  # Minimum spawn interval
                self.current_rogue_spawn_interval * SPAWN_RATE_MULTIPLIER
            )
        
        # Update spawn timer for shooting enemies
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            self.spawn_timer = self.current_enemy_spawn_interval
        
        # Update spawn timer for spear enemies
        self.spear_spawn_timer -= dt
        if self.spear_spawn_timer <= 0:
            self.spawn_spear_enemy()
            self.spear_spawn_timer = self.current_spear_spawn_interval
        
        # Update spawn timer for rogue enemies
        self.rogue_spawn_timer -= dt
        if self.rogue_spawn_timer <= 0:
            self.spawn_rogue_enemy()
            self.rogue_spawn_timer = self.current_rogue_spawn_interval
        
        # Update shooting enemies and collect new projectiles
        for enemy in self.enemies:
            if not getattr(enemy, 'frozen', False):
                new_projectiles = enemy.update(dt, player_x, player_y)
                self.enemy_projectiles.extend(new_projectiles)
        
        # Update spear enemies (follow player)
        for spear_enemy in self.spear_enemies:
            if not getattr(spear_enemy, 'frozen', False):
                spear_enemy.update(dt, player_x, player_y)
        
        # Update rogue enemies (follow player fast)
        for rogue_enemy in self.rogue_enemies:
            if not getattr(rogue_enemy, 'frozen', False):
                rogue_enemy.update(dt, player_x, player_y)
        
        # Update all enemy projectiles
        for projectile in self.enemy_projectiles:
            projectile.update(dt)
        
        # Remove inactive enemies and projectiles
        self.enemies = [e for e in self.enemies if e.active]
        self.spear_enemies = [e for e in self.spear_enemies if e.active]
        self.rogue_enemies = [e for e in self.rogue_enemies if e.active]
        self.enemy_projectiles = [p for p in self.enemy_projectiles if p.active]
    
    def check_collision(self, player_rect: pygame.Rect) -> bool:
        """Check if any enemy projectile or spear collides with player."""
        # Check projectile collisions
        for projectile in self.enemy_projectiles:
            if projectile.rect.colliderect(player_rect):
                return True
        
        # Check spear collisions
        for spear_enemy in self.spear_enemies:
            if spear_enemy.check_spear_collision(player_rect):
                return True
        
        # Check knife collisions
        for rogue_enemy in self.rogue_enemies:
            if rogue_enemy.check_knife_collision(player_rect):
                return True
        
        return False
    
    def clear_nearby_enemies(self, x: float, y: float, radius: float):
        """Clear enemies and projectiles near a position (for extra life effect)."""
        # Clear nearby enemy projectiles
        for projectile in self.enemy_projectiles:
            dist = ((projectile.x - x) ** 2 + (projectile.y - y) ** 2) ** 0.5
            if dist <= radius:
                projectile.active = False
        
        # Clear nearby shooting enemies
        for enemy in self.enemies:
            dist = ((enemy.x - x) ** 2 + (enemy.y - y) ** 2) ** 0.5
            if dist <= radius:
                enemy.active = False
        
        # Clear nearby spear enemies
        for enemy in self.spear_enemies:
            dist = ((enemy.x - x) ** 2 + (enemy.y - y) ** 2) ** 0.5
            if dist <= radius:
                enemy.active = False
        
        # Clear nearby rogue enemies
        for enemy in self.rogue_enemies:
            dist = ((enemy.x - x) ** 2 + (enemy.y - y) ** 2) ** 0.5
            if dist <= radius:
                enemy.active = False
    
    def draw(self, surface: pygame.Surface, player_x: float, player_y: float):
        """Draw all enemies and their projectiles."""
        # Draw shooting enemies
        for enemy in self.enemies:
            enemy.draw(surface)
        
        # Draw spear enemies (body first, then spear)
        for spear_enemy in self.spear_enemies:
            spear_enemy.draw(surface)
        
        # Draw spears (after bodies so they appear on top)
        for spear_enemy in self.spear_enemies:
            spear_enemy.draw_spear(surface, player_x, player_y)
        
        # Draw rogue enemies (body first, then knife)
        for rogue_enemy in self.rogue_enemies:
            rogue_enemy.draw(surface)
        
        # Draw knives (after bodies so they appear on top)
        for rogue_enemy in self.rogue_enemies:
            rogue_enemy.draw_knife(surface, player_x, player_y)
        
        # Draw projectiles
        for projectile in self.enemy_projectiles:
            projectile.draw(surface)
    
    def reset(self):
        """Reset enemy manager state."""
        self.enemies.clear()
        self.spear_enemies.clear()
        self.rogue_enemies.clear()
        self.enemy_projectiles.clear()
        
        # Reset spawn intervals
        self.current_enemy_spawn_interval = self.base_enemy_spawn_interval
        self.current_spear_spawn_interval = self.base_spear_spawn_interval
        self.current_rogue_spawn_interval = self.base_rogue_spawn_interval
        self.spawn_timer = self.base_enemy_spawn_interval
        self.spear_spawn_timer = self.base_spear_spawn_interval
        self.rogue_spawn_timer = self.base_rogue_spawn_interval
        
        # Reset difficulty
        self.difficulty_timer = 0.0
        self.difficulty_level = 0
