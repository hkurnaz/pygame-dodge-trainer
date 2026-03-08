"""Input handling system."""

import pygame
from game.entities.player import Player
from game.entities.projectile import Projectile
from game.effects.teleport_trail import TeleportTrail
from game.effects.death_effect import DeathEffect
from game.config import TELEPORT_DISTANCE, TELEPORT_COOLDOWN, Q_SKILL_COOLDOWN


class InputHandler:
    """Handles player input for movement and skills."""
    
    def __init__(self, player: Player):
        self.player = player
        self.projectiles: list = []
        self.effects: list = []
        self.killed_enemies: list = []  # Enemies killed this frame
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Returns True if quit."""
        if event.type == pygame.QUIT:
            return True
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right click
                self._handle_right_click(event.pos)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self._handle_q_skill(pygame.mouse.get_pos())
            elif event.key == pygame.K_e:
                self._handle_e_skill(pygame.mouse.get_pos())
        
        return False
    
    def _handle_right_click(self, mouse_pos: tuple):
        """Handle right-click movement."""
        self.player.set_target(mouse_pos[0], mouse_pos[1])
    
    def _handle_q_skill(self, mouse_pos: tuple):
        """Handle Q skill - fire yellow bar projectile."""
        if self.player.q_cooldown <= 0:
            projectile = Projectile(
                self.player.x,
                self.player.y,
                mouse_pos[0],
                mouse_pos[1]
            )
            self.projectiles.append(projectile)
            self.player.q_cooldown = Q_SKILL_COOLDOWN
    
    def _handle_e_skill(self, mouse_pos: tuple):
        """Handle E skill - teleport."""
        if self.player.teleport_cooldown <= 0:
            old_x, old_y = self.player.x, self.player.y
            new_x, new_y = self.player.teleport(
                mouse_pos[0], mouse_pos[1], TELEPORT_DISTANCE
            )
            
            # Create teleport trail effect
            trail = TeleportTrail(old_x, old_y, new_x, new_y)
            self.effects.append(trail)
            
            # Update player position
            self.player.x = new_x
            self.player.y = new_y
            self.player.target_x = new_x
            self.player.target_y = new_y
            self.player.is_moving = False
            
            # Set cooldown
            self.player.teleport_cooldown = TELEPORT_COOLDOWN
    
    def check_projectile_enemy_collision(self, enemies: list, spear_enemies: list) -> list:
        """Check if any projectile hits an enemy. Returns list of killed enemies."""
        killed = []
        
        for projectile in self.projectiles:
            if not projectile.active:
                continue
            
            # Check shooting enemies
            for enemy in enemies:
                if enemy.active and projectile.check_collision_with_enemy(enemy):
                    enemy.active = False
                    projectile.active = False
                    # Create death effect
                    self.effects.append(DeathEffect(enemy.x, enemy.y))
                    killed.append(enemy)
                    break
            
            # Check spear enemies
            if projectile.active:
                for enemy in spear_enemies:
                    if enemy.active and projectile.check_collision_with_enemy(enemy):
                        enemy.active = False
                        projectile.active = False
                        # Create death effect
                        self.effects.append(DeathEffect(enemy.x, enemy.y))
                        killed.append(enemy)
                        break
        
        return killed
    
    def update(self, dt: float):
        """Update all projectiles and effects."""
        # Update projectiles
        for projectile in self.projectiles:
            projectile.update(dt)
        
        # Remove inactive projectiles
        self.projectiles = [p for p in self.projectiles if p.active]
        
        # Update effects
        for effect in self.effects:
            effect.update(dt)
        
        # Remove inactive effects
        self.effects = [e for e in self.effects if e.active]
    
    def draw(self, surface: pygame.Surface):
        """Draw all projectiles and effects."""
        # Draw effects first (behind everything)
        for effect in self.effects:
            effect.draw(surface)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(surface)
