"""Rendering system."""

import pygame
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, RED, YELLOW


class Renderer:
    """Handles all game rendering."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.menu_font = pygame.font.Font(None, 48)
    
    def clear(self):
        """Clear the screen with background color."""
        self.screen.fill((30, 30, 40))
        
        # Draw grid for visual reference
        grid_color = (40, 40, 50)
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(self.screen, grid_color, (0, y), (SCREEN_WIDTH, y))
    
    def draw_player(self, player):
        """Draw the player character."""
        player.draw(self.screen)
    
    def draw_projectiles(self, input_handler):
        """Draw all projectiles and effects."""
        input_handler.draw(self.screen)
    
    def draw_enemies(self, enemy_manager, player_x: float, player_y: float):
        """Draw all enemies and their projectiles."""
        enemy_manager.draw(self.screen, player_x, player_y)
    
    def draw_map(self, game_map):
        """Draw the game map."""
        game_map.draw(self.screen)
    
    def draw_ui(self, player, survival_time: float):
        """Draw UI elements."""
        # Draw survival timer at top center
        minutes = int(survival_time // 60)
        seconds = int(survival_time % 60)
        milliseconds = int((survival_time % 1) * 100)
        time_text = f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
        
        timer_surface = self.subtitle_font.render(time_text, True, WHITE)
        timer_rect = timer_surface.get_rect(center=(SCREEN_WIDTH // 2, 25))
        
        # Draw timer background
        bg_rect = timer_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (40, 45, 55), bg_rect, border_radius=5)
        pygame.draw.rect(self.screen, (80, 90, 110), bg_rect, 2, border_radius=5)
        self.screen.blit(timer_surface, timer_rect)
        
        # Draw skill cooldowns on left side
        y_offset = 60
        
        # Q skill cooldown
        if player.q_cooldown > 0:
            cd_text = f"Q: {player.q_cooldown:.1f}s"
            text_surface = self.font.render(cd_text, True, GRAY)
        else:
            text_surface = self.font.render("Q: Ready", True, YELLOW)
        self.screen.blit(text_surface, (10, y_offset))
        
        # E skill cooldown
        y_offset += 25
        if player.teleport_cooldown > 0:
            cd_text = f"E Teleport: {player.teleport_cooldown:.1f}s"
            text_surface = self.font.render(cd_text, True, GRAY)
        else:
            text_surface = self.font.render("E Teleport: Ready", True, WHITE)
        self.screen.blit(text_surface, (10, y_offset))
        
        # Draw controls info at bottom
        controls = [
            "Right-Click: Move",
            "Q: Fire Projectile",
            "E: Teleport"
        ]
        
        for i, control in enumerate(controls):
            text_surface = self.font.render(control, True, (150, 150, 150))
            self.screen.blit(text_surface, (10, SCREEN_HEIGHT - 80 + i * 25))
    
    def draw_mouse_indicator(self, mouse_pos: tuple, player_pos: tuple):
        """Draw mouse position indicator."""
        # Draw small crosshair at mouse position only (no line to player)
        crosshair_size = 10
        pygame.draw.line(self.screen, (100, 100, 100), 
                        (mouse_pos[0] - crosshair_size, mouse_pos[1]),
                        (mouse_pos[0] + crosshair_size, mouse_pos[1]), 1)
        pygame.draw.line(self.screen, (100, 100, 100),
                        (mouse_pos[0], mouse_pos[1] - crosshair_size),
                        (mouse_pos[0], mouse_pos[1] + crosshair_size), 1)
    
    def draw_main_menu(self):
        """Draw the main menu screen."""
        # Fill with dark background
        self.screen.fill((20, 25, 35))
        
        # Draw decorative lines
        for i in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (30, 35, 45), (0, i), (SCREEN_WIDTH, i))
        
        # Draw title box
        title_box = pygame.Rect(SCREEN_WIDTH // 2 - 300, 100, 600, 120)
        pygame.draw.rect(self.screen, (40, 50, 70), title_box, border_radius=15)
        pygame.draw.rect(self.screen, YELLOW, title_box, 3, border_radius=15)
        
        # Title text
        title_text = self.title_font.render("DODGE TRAINING", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.subtitle_font.render("League of Legends Style", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 190))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw character preview (simplified)
        preview_x = SCREEN_WIDTH // 2
        preview_y = 320
        
        # Draw a simple character silhouette
        pygame.draw.circle(self.screen, (100, 150, 255), (preview_x, preview_y), 30)
        pygame.draw.circle(self.screen, (50, 100, 200), (preview_x, preview_y), 30, 3)
        
        # Yellow hair on preview
        hair_points = [
            (preview_x - 20, preview_y - 25),
            (preview_x - 15, preview_y - 45),
            (preview_x, preview_y - 35),
            (preview_x + 10, preview_y - 50),
            (preview_x + 20, preview_y - 30),
        ]
        pygame.draw.polygon(self.screen, YELLOW, hair_points)
        
        # Instructions box
        instructions_box = pygame.Rect(SCREEN_WIDTH // 2 - 250, 420, 500, 200)
        pygame.draw.rect(self.screen, (35, 40, 55), instructions_box, border_radius=10)
        pygame.draw.rect(self.screen, (80, 90, 110), instructions_box, 2, border_radius=10)
        
        # Instructions
        instructions = [
            "CONTROLS:",
            "",
            "Right-Click: Move character",
            "Q: Fire projectile at cursor",
            "E: Teleport toward cursor",
            "",
            "Avoid enemy projectiles and spears!"
        ]
        
        y_start = 440
        for i, line in enumerate(instructions):
            if i == 0:
                text_surface = self.subtitle_font.render(line, True, YELLOW)
            else:
                text_surface = self.font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 25))
            self.screen.blit(text_surface, text_rect)
        
        # Start prompt
        start_text = self.menu_font.render("Press SPACE to Start", True, (100, 255, 100))
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, 680))
        
        # Pulsing effect
        import time
        alpha = int(128 + 127 * (1 + (time.time() % 2 - 1)))
        start_surface = pygame.Surface(start_text.get_size(), pygame.SRCALPHA)
        start_surface.blit(start_text, (0, 0))
        start_surface.set_alpha(alpha)
        self.screen.blit(start_surface, start_rect)
        
        # Quit prompt
        quit_text = self.font.render("Press ESC to Quit", True, GRAY)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, 730))
        self.screen.blit(quit_text, quit_rect)
    
    def draw_game_over(self, survival_time: float, best_time: float):
        """Draw game over screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.title_font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(game_over_text, text_rect)
        
        # Draw a box around "GAME OVER"
        box_rect = text_rect.inflate(40, 20)
        pygame.draw.rect(self.screen, RED, box_rect, 3, border_radius=10)
        
        # Survival time
        minutes = int(survival_time // 60)
        seconds = int(survival_time % 60)
        milliseconds = int((survival_time % 1) * 100)
        time_text = f"Time: {minutes:02d}:{seconds:02d}.{milliseconds:02d}"
        
        time_surface = self.subtitle_font.render(time_text, True, WHITE)
        time_rect = time_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(time_surface, time_rect)
        
        # Best time (smaller, below current time)
        best_minutes = int(best_time // 60)
        best_seconds = int(best_time % 60)
        best_milliseconds = int((best_time % 1) * 100)
        best_text = f"Best: {best_minutes:02d}:{best_seconds:02d}.{best_milliseconds:02d}"
        
        best_surface = self.font.render(best_text, True, YELLOW)
        best_rect = best_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(best_surface, best_rect)
        
        # Decorative line
        pygame.draw.line(self.screen, YELLOW, 
                        (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 35),
                        (SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2 + 35), 2)
        
        # Retry instruction
        retry_text = self.subtitle_font.render("Press SPACE to Retry", True, WHITE)
        retry_rect = retry_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        self.screen.blit(retry_text, retry_rect)
        
        # Quit instruction
        quit_text = self.subtitle_font.render("Press ESC to Quit", True, GRAY)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110))
        self.screen.blit(quit_text, quit_rect)
    
    def present(self):
        """Flip the display buffer."""
        pygame.display.flip()
