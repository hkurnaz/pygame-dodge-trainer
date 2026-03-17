"""Boss entity for Story Mode Stage 3."""

import math
import random
import pygame
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, RED, WHITE, GREEN, YELLOW


class BossOgre:
    """Giant purple ogre boss with multiple attacks."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.size = 140
        self.color = (120, 70, 180)  # Purple ogre
        self.outline_color = (70, 40, 120)
        
        # Freeze state (for Zilean's E)
        self.frozen = False
        self.frozen_timer = 0.0
        
        self.max_health = 30
        self.health = self.max_health
        
        # Movement
        self.speed = 120
        self.charge_speed = 420
        self.state = "idle"
        self.state_timer = 0.0
        self.attack_cooldown = 2.0
        self.direction = (1.0, 0.0)
        self.charge_direction_set = False
        
        # Attack ranges
        self.punch_range = 200  # Increased for larger swing radius
        self.grab_range = 90
        self.charge_range = 380
        
        # Grab minigame
        self.escape_sequence = []
        self.escape_index = 0
        self.escape_timer = 0.0
        self.escape_time_limit = 1.4
        self.escape_success_required = 5
        self.escape_active = False
        
        # Status flags
        self.player_hit = False
        self.player_killed = False
        self.stunned = False
        self.stun_duration = 2.5
        
        # Bite effect timer
        self.bite_timer = 0.0
    
    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size
        )
    
    def reset_flags(self):
        """Reset transient combat flags."""
        self.player_hit = False
        self.player_killed = False
    
    def take_damage(self, amount: float):
        """Apply damage to the boss."""
        self.health = max(0, self.health - amount)
    
    def is_defeated(self) -> bool:
        """Check if boss is defeated."""
        return self.health <= 0
    
    def handle_escape_input(self, key: int) -> bool:
        """Handle directional input during grab escape mini game."""
        if not self.escape_active or not self.escape_sequence:
            return False
        
        expected = self.escape_sequence[self.escape_index]
        if key == expected:
            self.escape_index += 1
            self.escape_timer = 0.0
            if self.escape_index >= self.escape_success_required:
                # Escape successful -> stun boss
                self.escape_active = False
                self.escape_sequence = []
                self.escape_index = 0
                self._enter_stunned()
            return True
        
        # Wrong input -> fail
        self._trigger_bite_kill()
        return False
    
    def get_current_escape_prompt(self) -> int | None:
        """Return current escape key prompt if active."""
        if self.escape_active and self.escape_sequence:
            return self.escape_sequence[self.escape_index]
        return None
    
    def update(self, dt: float, player, game_map):
        """Update boss logic and attacks."""
        self.reset_flags()
        
        # Timers
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Frozen timer (Zilean E)
        if self.frozen:
            self.frozen_timer -= dt
            if self.frozen_timer <= 0:
                self.frozen = False
        
        if self.escape_active:
            self.escape_timer += dt
            if self.escape_timer >= self.escape_time_limit:
                # Timeout -> fail
                self._trigger_bite_kill()
        
        if self.state == "bite":
            self.bite_timer -= dt
            if self.bite_timer <= 0:
                self.player_killed = True
            return
        
        if self.state == "stunned":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = "idle"
                self.attack_cooldown = 1.5
            return
        
        if self.frozen:
            # Boss frozen - no movement or attacks
            return
        
        if self.escape_active:
            # Boss holds player while escape sequence happens
            return
        
        # Update based on state
        if self.state == "idle":
            self._update_idle(dt, player)
        elif self.state == "punch":
            self._update_punch(dt, player)
        elif self.state == "grab":
            self._update_grab(dt, player)
        elif self.state == "charge":
            self._update_charge(dt, player, game_map)
    
    def _update_idle(self, dt: float, player):
        # Move slightly toward player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy)
        if distance > 0:
            self.direction = (dx / distance, dy / distance)
        
        if distance > 80:
            move_distance = self.speed * dt
            self.x += self.direction[0] * move_distance
            self.y += self.direction[1] * move_distance
        
        # Choose attack
        if self.attack_cooldown <= 0:
            if distance <= self.grab_range:
                self._enter_grab()
            elif distance <= self.punch_range:
                self._enter_punch()
            elif distance >= self.charge_range:
                self._enter_charge()
            else:
                # Random between punch/charge to mix
                if random.random() < 0.5:
                    self._enter_punch()
                else:
                    self._enter_charge()
    
    def _enter_punch(self):
        self.state = "punch"
        self.state_timer = 0.5
    
    def _update_punch(self, dt: float, player):
        self.state_timer -= dt
        if self.state_timer <= 0:
            # Punch swing hit check
            distance = math.hypot(player.x - self.x, player.y - self.y)
            if distance <= self.punch_range:
                self.player_hit = True
            self.state = "idle"
            self.attack_cooldown = 1.8
    
    def _enter_grab(self):
        self.state = "grab"
        self.state_timer = 0.45
    
    def _update_grab(self, dt: float, player):
        self.state_timer -= dt
        if self.state_timer <= 0:
            distance = math.hypot(player.x - self.x, player.y - self.y)
            if distance <= self.grab_range:
                self._start_escape_minigame()
            else:
                self.state = "idle"
                self.attack_cooldown = 1.2
    
    def _start_escape_minigame(self):
        self.escape_active = True
        self.escape_timer = 0.0
        self.escape_index = 0
        self.escape_sequence = [
            random.choice([pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN])
            for _ in range(self.escape_success_required)
        ]
        self.state = "grab"
    
    def _enter_charge(self):
        self.state = "charge"
        self.state_timer = 1.0
        self.charge_direction_set = False
    
    def _update_charge(self, dt: float, player, game_map):
        # Direction locked at charge start
        if not self.charge_direction_set:
            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.hypot(dx, dy)
            if distance > 0:
                self.direction = (dx / distance, dy / distance)
            self.charge_direction_set = True
        
        self.state_timer -= dt
        move_distance = self.charge_speed * dt
        new_x = self.x + self.direction[0] * move_distance
        new_y = self.y + self.direction[1] * move_distance
        
        boss_rect = pygame.Rect(new_x - self.size // 2, new_y - self.size // 2, self.size, self.size)
        if game_map and game_map.check_collision(boss_rect):
            self._enter_stunned()
            return
        
        self.x = new_x
        self.y = new_y
        
        # Check collision with player
        if boss_rect.colliderect(player.rect):
            self.player_hit = True
            self.state = "idle"
            self.attack_cooldown = 2.0
            return
        
        if self.state_timer <= 0:
            self.state = "idle"
            self.attack_cooldown = 2.0
    
    def _enter_stunned(self):
        self.state = "stunned"
        self.state_timer = self.stun_duration
        self.stunned = True
    
    def _trigger_bite_kill(self):
        self.escape_active = False
        self.state = "bite"
        self.bite_timer = 0.6
    
    def draw(self, surface: pygame.Surface):
        """Draw the boss."""
        center_x = int(self.x)
        center_y = int(self.y)
        
        # Shadow
        shadow_surface = pygame.Surface((self.size + 30, self.size // 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 80), (0, 0, self.size + 30, self.size // 2))
        surface.blit(shadow_surface, (center_x - (self.size + 30) // 2, center_y + self.size // 3))
        
        # Body
        pygame.draw.circle(surface, self.color, (center_x, center_y), self.size // 2)
        pygame.draw.circle(surface, self.outline_color, (center_x, center_y), self.size // 2, 4)
        
        # Doctor coat
        coat_rect = pygame.Rect(center_x - self.size // 3, center_y - 10, self.size // 1.5, self.size // 2)
        pygame.draw.rect(surface, (220, 220, 230), coat_rect, border_radius=8)
        pygame.draw.rect(surface, (170, 170, 180), coat_rect, 2, border_radius=8)
        
        # Red cross
        cross_center = (center_x, center_y + 15)
        pygame.draw.rect(surface, (200, 40, 40), (cross_center[0] - 6, cross_center[1] - 18, 12, 36))
        pygame.draw.rect(surface, (200, 40, 40), (cross_center[0] - 18, cross_center[1] - 6, 36, 12))
        
        # Head
        head_radius = self.size // 3
        head_y = center_y - self.size // 3
        pygame.draw.circle(surface, (140, 90, 200), (center_x, head_y), head_radius)
        pygame.draw.circle(surface, self.outline_color, (center_x, head_y), head_radius, 3)
        
        # Angry eyes
        eye_offset = head_radius // 2
        eye_y = head_y - 5
        pygame.draw.circle(surface, WHITE, (center_x - eye_offset, eye_y), 8)
        pygame.draw.circle(surface, WHITE, (center_x + eye_offset, eye_y), 8)
        pygame.draw.circle(surface, (60, 20, 80), (center_x - eye_offset, eye_y), 4)
        pygame.draw.circle(surface, (60, 20, 80), (center_x + eye_offset, eye_y), 4)
        
        # Mouth
        mouth_rect = pygame.Rect(center_x - 18, head_y + 10, 36, 16)
        pygame.draw.arc(surface, (70, 20, 90), mouth_rect, 0, 3.14, 3)
        
        # Stethoscope
        pygame.draw.circle(surface, (80, 80, 90), (center_x - 25, center_y - 5), 6)
        pygame.draw.circle(surface, (80, 80, 90), (center_x + 25, center_y - 5), 6)
        pygame.draw.line(surface, (80, 80, 90), (center_x - 25, center_y - 5), (center_x - 10, center_y + 10), 3)
        pygame.draw.line(surface, (80, 80, 90), (center_x + 25, center_y - 5), (center_x + 10, center_y + 10), 3)
        
        # Stun effect
        if self.state == "stunned":
            stun_text = pygame.font.Font(None, 32).render("STUNNED", True, YELLOW)
            surface.blit(stun_text, (center_x - stun_text.get_width() // 2, center_y - self.size // 2 - 30))
        
        if self.frozen:
            freeze_text = pygame.font.Font(None, 32).render("FROZEN", True, (120, 200, 255))
            surface.blit(freeze_text, (center_x - freeze_text.get_width() // 2, center_y - self.size // 2 - 60))
            # Blue freeze overlay
            freeze_surface = pygame.Surface((self.size + 20, self.size + 20), pygame.SRCALPHA)
            pygame.draw.circle(freeze_surface, (120, 200, 255, 90), (self.size // 2 + 10, self.size // 2 + 10), self.size // 2 + 5)
            surface.blit(freeze_surface, (center_x - self.size // 2 - 10, center_y - self.size // 2 - 10))
        
        # Punch attack visualization
        if self.state == "punch":
            # Draw punch swing arc
            punch_progress = 1.0 - (self.state_timer / 0.5)  # 0 to 1 during punch
            if punch_progress < 1.0:
                # Swing arc effect
                arc_color = (255, 200, 100, 150)
                arc_surface = pygame.Surface((self.punch_range * 2, self.punch_range * 2), pygame.SRCALPHA)
                start_angle = -2.5 + punch_progress * 2.0  # Swing arc
                end_angle = start_angle + 1.5
                pygame.draw.arc(arc_surface, arc_color, 
                               (0, 0, self.punch_range * 2, self.punch_range * 2),
                               start_angle, end_angle, 8)
                surface.blit(arc_surface, (center_x - self.punch_range, center_y - self.punch_range))
                
                # Draw fist
                fist_offset = self.punch_range * 0.7
                fist_x = center_x + math.cos(start_angle + 0.75) * fist_offset
                fist_y = center_y + math.sin(start_angle + 0.75) * fist_offset
                pygame.draw.circle(surface, (200, 160, 120), (int(fist_x), int(fist_y)), 25)
                pygame.draw.circle(surface, (150, 110, 80), (int(fist_x), int(fist_y)), 25, 3)
        
        # Charge attack visualization
        if self.state == "charge":
            # Draw charge direction indicator
            charge_color = (255, 100, 100, 100)
            line_end_x = center_x + self.direction[0] * 100
            line_end_y = center_y + self.direction[1] * 100
            pygame.draw.line(surface, (255, 100, 100), (center_x, center_y), 
                           (int(line_end_x), int(line_end_y)), 6)
            # Draw bull horns effect
            horn_offset = 20
            pygame.draw.polygon(surface, (200, 80, 80), [
                (center_x - horn_offset, center_y - self.size // 2 - 10),
                (center_x - horn_offset - 15, center_y - self.size // 2 - 25),
                (center_x - horn_offset + 5, center_y - self.size // 2 - 15),
            ])
            pygame.draw.polygon(surface, (200, 80, 80), [
                (center_x + horn_offset, center_y - self.size // 2 - 10),
                (center_x + horn_offset + 15, center_y - self.size // 2 - 25),
                (center_x + horn_offset - 5, center_y - self.size // 2 - 15),
            ])
        
        # Grab attack visualization
        if self.state == "grab" and self.escape_active:
            # Draw grab hands
            hand_y = center_y + 20
            pygame.draw.ellipse(surface, (180, 140, 100), 
                              (center_x - 60, hand_y, 40, 50))
            pygame.draw.ellipse(surface, (180, 140, 100), 
                              (center_x + 20, hand_y, 40, 50))
    
    def draw_health_bar(self, surface: pygame.Surface):
        """Draw boss health bar at top of screen."""
        bar_width = 500
        bar_height = 18
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = 20
        
        pygame.draw.rect(surface, (40, 40, 50), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), border_radius=8)
        pygame.draw.rect(surface, (120, 120, 140), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=6)
        
        health_ratio = max(0, self.health / self.max_health)
        fill_width = int(bar_width * health_ratio)
        if fill_width > 0:
            pygame.draw.rect(surface, (160, 80, 220), (bar_x, bar_y, fill_width, bar_height), border_radius=6)
        
        label = pygame.font.Font(None, 28).render("DR. OGRE", True, WHITE)
        surface.blit(label, (bar_x, bar_y - 24))
