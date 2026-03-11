"""Input handling system."""

import pygame
import math
from game.entities.player import Player
from game.entities.projectile import Projectile, Shuriken
from game.effects.teleport_trail import TeleportTrail
from game.effects.death_effect import DeathEffect
from game.effects.shadow import Shadow
from game.effects.spin_attack import SpinAttack
from game.config import (
    TELEPORT_DISTANCE, TELEPORT_COOLDOWN, Q_SKILL_COOLDOWN,
    ZED_Q_COOLDOWN, ZED_W_COOLDOWN, ZED_E_COOLDOWN, ZED_W_SHADOW_DISTANCE
)


class InputHandler:
    """Handles player input for movement and skills."""
    
    def __init__(self, player: Player, character_type: str = "ezreal", player_stats=None):
        self.player = player
        self.character_type = character_type
        self.player_stats = player_stats
        self.projectiles: list = []
        self.effects: list = []
        self.killed_enemies: list = []  # Enemies killed this frame
        
        # Zed-specific
        self.shadow = None
        self.spin_attacks: list = []
        self.shurikens: list = []
    
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
            elif event.key == pygame.K_w:
                self._handle_w_skill(pygame.mouse.get_pos())
            elif event.key == pygame.K_e:
                self._handle_e_skill(pygame.mouse.get_pos())
        
        return False
    
    def _handle_right_click(self, mouse_pos: tuple):
        """Handle right-click movement."""
        self.player.set_target(mouse_pos[0], mouse_pos[1])
    
    def _handle_q_skill(self, mouse_pos: tuple):
        """Handle Q skill based on character type."""
        if self.character_type == "zed":
            self._handle_zed_q(mouse_pos)
        else:
            self._handle_ezreal_q(mouse_pos)
    
    def _handle_ezreal_q(self, mouse_pos: tuple):
        """Handle Ezreal's Q skill - fire yellow bar projectile."""
        if self.player.q_cooldown <= 0:
            projectile = Projectile(
                self.player.x,
                self.player.y,
                mouse_pos[0],
                mouse_pos[1]
            )
            
            # Apply Survival mode stat multipliers
            if self.player_stats:
                size_mult = self.player_stats.attack_size_multiplier
                projectile.width = int(projectile.width * size_mult)
                projectile.length = int(projectile.length * size_mult)
            
            self.projectiles.append(projectile)
            
            # Apply cooldown multiplier
            if self.player_stats:
                self.player.q_cooldown = self.player_stats.get_q_cooldown()
            else:
                self.player.q_cooldown = Q_SKILL_COOLDOWN
            

    
    def _handle_zed_q(self, mouse_pos: tuple):
        """Handle Zed's Q skill - throw shuriken."""
        if self.player.q_cooldown <= 0:
            shuriken = Shuriken(
                self.player.x,
                self.player.y,
                mouse_pos[0],
                mouse_pos[1]
            )
            
            # Apply Survival mode stat multipliers
            if self.player_stats:
                size_mult = self.player_stats.attack_size_multiplier
                shuriken.size = int(shuriken.size * size_mult)
            
            self.shurikens.append(shuriken)
            
            # Apply cooldown multiplier
            if self.player_stats:
                self.player.q_cooldown = self.player_stats.get_q_cooldown()
            else:
                self.player.q_cooldown = ZED_Q_COOLDOWN
            
            # Shadow also casts Q toward cursor
            self._cast_shadow_q(mouse_pos)
    
    def _handle_w_skill(self, mouse_pos: tuple):
        """Handle W skill based on character type."""
        if self.character_type == "zed":
            self._handle_zed_w(mouse_pos)
        # Ezreal doesn't have a W skill
    
    def _cast_shadow_q(self, mouse_pos: tuple):
        """Cast Zed's Q from shadow toward cursor."""
        if self.shadow and self.shadow.active:
            shadow_x, shadow_y = self.shadow.get_position()
            shadow_shuriken = Shuriken(
                shadow_x,
                shadow_y,
                mouse_pos[0],
                mouse_pos[1]
            )
            if self.player_stats:
                shadow_shuriken.size = int(shadow_shuriken.size * self.player_stats.attack_size_multiplier)
            self.shurikens.append(shadow_shuriken)
    
    def _cast_shadow_e(self):
        """Cast Zed's E from shadow's position."""
        if self.shadow and self.shadow.active:
            shadow_x, shadow_y = self.shadow.get_position()
            shadow_spin = SpinAttack(shadow_x, shadow_y)
            if self.player_stats:
                shadow_spin.radius = shadow_spin.radius * self.player_stats.attack_size_multiplier
            self.spin_attacks.append(shadow_spin)
    
    def _handle_zed_w(self, mouse_pos: tuple):
        """Handle Zed's W skill - send shadow or teleport to it."""
        # Check if there's an active shadow to teleport to (can teleport even during cooldown)
        if self.shadow and self.shadow.active:
            # Teleport to shadow
            old_x, old_y = self.player.x, self.player.y
            new_x, new_y = self.shadow.get_position()
            
            # Create teleport trail
            trail = TeleportTrail(old_x, old_y, new_x, new_y)
            self.effects.append(trail)
            
            # Update player position
            self.player.x = new_x
            self.player.y = new_y
            self.player.target_x = new_x
            self.player.target_y = new_y
            self.player.is_moving = False
            
            # Remove shadow
            self.shadow.active = False
            self.shadow = None
            
            # Set cooldown after teleport
            self.player.w_cooldown = ZED_W_COOLDOWN
        elif self.player.w_cooldown <= 0:
            # Send shadow (only if cooldown is ready and no active shadow)
            dx = mouse_pos[0] - self.player.x
            dy = mouse_pos[1] - self.player.y
            
            self.shadow = Shadow(
                self.player.x,
                self.player.y,
                dx,
                dy,
                ZED_W_SHADOW_DISTANCE
            )
            self.effects.append(self.shadow)
            
            # Set cooldown after sending shadow
            self.player.w_cooldown = ZED_W_COOLDOWN
    
    def _handle_e_skill(self, mouse_pos: tuple):
        """Handle E skill based on character type."""
        if self.character_type == "zed":
            self._handle_zed_e()
        else:
            self._handle_ezreal_e(mouse_pos)
    
    def _handle_ezreal_e(self, mouse_pos: tuple):
        """Handle Ezreal's E skill - teleport."""
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
            if self.player_stats:
                self.player.teleport_cooldown = self.player_stats.get_e_cooldown()
            else:
                self.player.teleport_cooldown = TELEPORT_COOLDOWN
    
    def _handle_zed_e(self):
        """Handle Zed's E skill - spin attack with hidden blades."""
        if self.player.e_cooldown <= 0:
            spin = SpinAttack(self.player.x, self.player.y)
            
            # Apply Survival mode stat multipliers
            if self.player_stats:
                size_mult = self.player_stats.attack_size_multiplier
                spin.radius = spin.radius * size_mult
            
            self.spin_attacks.append(spin)
            
            # Apply cooldown multiplier
            if self.player_stats:
                self.player.e_cooldown = self.player_stats.get_e_cooldown()
            else:
                self.player.e_cooldown = ZED_E_COOLDOWN
            
            # Shadow also casts E at its position
            self._cast_shadow_e()
    
    def check_projectile_enemy_collision(self, enemies: list, spear_enemies: list, rogue_enemies: list) -> list:
        """Check if any projectile hits an enemy. Returns list of killed enemies."""
        killed = []
        
        # Check regular projectiles (Ezreal)
        for projectile in self.projectiles:
            if not projectile.active:
                continue
            
            # Check shooting enemies
            for enemy in enemies:
                if enemy.active and projectile.check_collision_with_enemy(enemy):
                    if self._apply_damage(enemy):
                        enemy.active = False
                        self.effects.append(DeathEffect(enemy.x, enemy.y))
                        killed.append(enemy)
                    projectile.active = False
                    break
            
            # Check spear enemies
            if projectile.active:
                for enemy in spear_enemies:
                    if enemy.active and projectile.check_collision_with_enemy(enemy):
                        if self._apply_damage(enemy):
                            enemy.active = False
                            self.effects.append(DeathEffect(enemy.x, enemy.y))
                            killed.append(enemy)
                        projectile.active = False
                        break
            
            # Check rogue enemies
            if projectile.active:
                for enemy in rogue_enemies:
                    if enemy.active and projectile.check_collision_with_enemy(enemy):
                        if self._apply_damage(enemy):
                            enemy.active = False
                            self.effects.append(DeathEffect(enemy.x, enemy.y))
                            killed.append(enemy)
                        projectile.active = False
                        break
        
        # Check shurikens (Zed)
        for shuriken in self.shurikens:
            if not shuriken.active:
                continue
            
            # Check shooting enemies
            for enemy in enemies:
                if enemy.active and shuriken.check_collision_with_enemy(enemy):
                    if self._apply_damage(enemy):
                        enemy.active = False
                        self.effects.append(DeathEffect(enemy.x, enemy.y))
                        killed.append(enemy)
                    shuriken.active = False
                    break
            
            # Check spear enemies
            if shuriken.active:
                for enemy in spear_enemies:
                    if enemy.active and shuriken.check_collision_with_enemy(enemy):
                        if self._apply_damage(enemy):
                            enemy.active = False
                            self.effects.append(DeathEffect(enemy.x, enemy.y))
                            killed.append(enemy)
                        shuriken.active = False
                        break
            
            # Check rogue enemies
            if shuriken.active:
                for enemy in rogue_enemies:
                    if enemy.active and shuriken.check_collision_with_enemy(enemy):
                        if self._apply_damage(enemy):
                            enemy.active = False
                            self.effects.append(DeathEffect(enemy.x, enemy.y))
                            killed.append(enemy)
                        shuriken.active = False
                        break
        
        # Check spin attacks (Zed's E)
        for spin in self.spin_attacks:
            if not spin.active:
                continue
            
            # Get enemy id for tracking
            enemy_id = 0
            
            # Check shooting enemies
            for enemy in enemies:
                if enemy.active and spin.check_collision_with_enemy(enemy):
                    if not spin.has_hit_enemy(id(enemy)):
                        if self._apply_damage(enemy):
                            enemy.active = False
                            self.effects.append(DeathEffect(enemy.x, enemy.y))
                            killed.append(enemy)
                        spin.mark_enemy_hit(id(enemy))
            
            # Check spear enemies
            for enemy in spear_enemies:
                if enemy.active and spin.check_collision_with_enemy(enemy):
                    if not spin.has_hit_enemy(id(enemy)):
                        if self._apply_damage(enemy):
                            enemy.active = False
                            self.effects.append(DeathEffect(enemy.x, enemy.y))
                            killed.append(enemy)
                        spin.mark_enemy_hit(id(enemy))
            
            # Check rogue enemies
            for enemy in rogue_enemies:
                if enemy.active and spin.check_collision_with_enemy(enemy):
                    if not spin.has_hit_enemy(id(enemy)):
                        if self._apply_damage(enemy):
                            enemy.active = False
                            self.effects.append(DeathEffect(enemy.x, enemy.y))
                            killed.append(enemy)
                        spin.mark_enemy_hit(id(enemy))
        
        return killed
    
    def _apply_damage(self, enemy) -> bool:
        """Apply damage to enemy. Returns True if enemy should be killed."""
        # In Survival mode, enemies have health that requires multiple hits
        if self.player_stats:
            # Initialize enemy health if not set (2 hits to kill base)
            if not hasattr(enemy, "health"):
                enemy.health = 2.0  # 2 hits to kill at base damage (1.0)
            
            damage = self.player_stats.damage_multiplier
            enemy.health -= damage
            return enemy.health <= 0
        else:
            # Legacy mode - one hit kill
            return True
    
    def apply_survival_stats(self, player_stats):
        """Update Survival mode stats reference."""
        self.player_stats = player_stats
    
    def update(self, dt: float):
        """Update all projectiles and effects."""
        # Update projectiles
        for projectile in self.projectiles:
            projectile.update(dt)
        
        # Remove inactive projectiles
        self.projectiles = [p for p in self.projectiles if p.active]
        
        # Update shurikens
        for shuriken in self.shurikens:
            shuriken.update(dt)
        
        # Remove inactive shurikens
        self.shurikens = [s for s in self.shurikens if s.active]
        
        # Update spin attacks
        for spin in self.spin_attacks:
            spin.update(dt)
        
        # Remove inactive spin attacks
        self.spin_attacks = [s for s in self.spin_attacks if s.active]
        
        # Update effects
        for effect in self.effects:
            effect.update(dt)
        
        # Remove inactive effects
        self.effects = [e for e in self.effects if e.active]
        
        # Update shadow reference if it became inactive
        if self.shadow and not self.shadow.active:
            self.shadow = None
    
    def clear_all_projectiles(self):
        """Clear all player projectiles (for extra life effect)."""
        self.projectiles.clear()
        self.shurikens.clear()
        self.spin_attacks.clear()
    
    def draw(self, surface: pygame.Surface):
        """Draw all projectiles and effects."""
        # Draw effects first (behind everything)
        for effect in self.effects:
            effect.draw(surface)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(surface)
        
        # Draw shurikens
        for shuriken in self.shurikens:
            shuriken.draw(surface)
        
        # Draw spin attacks
        for spin in self.spin_attacks:
            spin.draw(surface)
