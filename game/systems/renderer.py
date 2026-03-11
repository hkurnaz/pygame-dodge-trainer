"""Rendering system."""

import pygame
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, RED, YELLOW, GREEN, ORANGE, SURVIVAL_MODE_HEARTS


class Button:
    """Interactive button for menus."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: tuple, hover_color: tuple, text_color: tuple = WHITE):
        self.rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
    
    def update(self, mouse_pos: tuple):
        """Update hover state based on mouse position."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos: tuple) -> bool:
        """Check if button is clicked."""
        return self.rect.collidepoint(mouse_pos)
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw the button."""
        color = self.hover_color if self.is_hovered else self.color
        
        # Draw button background
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE if self.is_hovered else GRAY, self.rect, 2, border_radius=8)
        
        # Draw text
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class Renderer:
    """Handles all game rendering."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.menu_font = pygame.font.Font(None, 48)
        self.button_font = pygame.font.Font(None, 36)
        
        # Main menu buttons
        self.start_button = Button(
            SCREEN_WIDTH // 2, 650, 200, 50,
            "START", (40, 100, 40), (60, 150, 60)
        )
        self.quit_button = Button(
            SCREEN_WIDTH // 2, 720, 200, 50,
            "QUIT", (100, 40, 40), (150, 60, 60)
        )
        
        # Character selection buttons
        self.select_button = Button(
            SCREEN_WIDTH // 2, 700, 200, 50,
            "SELECT", (40, 100, 40), (60, 150, 60)
        )
        self.back_button = Button(
            SCREEN_WIDTH // 2, 760, 200, 50,
            "BACK", (80, 80, 80), (120, 120, 120)
        )
        
        # Pause menu buttons
        self.resume_button = Button(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, 250, 50,
            "RESUME", (40, 100, 40), (60, 150, 60)
        )
        self.menu_button = Button(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, 250, 50,
            "RETURN TO MENU", (100, 80, 40), (150, 120, 60)
        )
        
        # Confirmation dialog buttons
        self.yes_button = Button(
            SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 60, 120, 45,
            "YES", (100, 40, 40), (150, 60, 60)
        )
        self.no_button = Button(
            SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT // 2 + 60, 120, 45,
            "NO", (40, 100, 40), (60, 150, 60)
        )
        
        # Game over buttons
        self.retry_button = Button(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70, 200, 50,
            "RETRY", (40, 100, 40), (60, 150, 60)
        )
        self.game_over_quit_button = Button(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130, 200, 50,
            "QUIT", (100, 40, 40), (150, 60, 60)
        )
        
        # Game mode selection buttons
        self.legacy_button = Button(
            SCREEN_WIDTH // 2, 450, 280, 60,
            "LEGACY", (60, 80, 120), (80, 100, 150)
        )
        self.survival_button = Button(
            SCREEN_WIDTH // 2, 530, 280, 60,
            "SURVIVAL", (80, 60, 100), (110, 80, 130)
        )
        self.mode_back_button = Button(
            SCREEN_WIDTH // 2, 620, 200, 50,
            "BACK", (80, 80, 80), (120, 120, 120)
        )
    
    def clear(self):
        """Clear the screen with background color."""
        self.screen.fill((30, 30, 40))
        
        # Draw grid for visual reference
        grid_color = (40, 40, 50)
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(self.screen, grid_color, (0, y), (SCREEN_WIDTH, y))
    
    def draw_player(self, player, character_type: str = "ezreal"):
        """Draw the player character."""
        player.draw(self.screen, character_type)
    
    def draw_projectiles(self, input_handler):
        """Draw all projectiles and effects."""
        input_handler.draw(self.screen)
    
    def draw_enemies(self, enemy_manager, player_x: float, player_y: float):
        """Draw all enemies and their projectiles."""
        enemy_manager.draw(self.screen, player_x, player_y)
    
    def draw_map(self, game_map):
        """Draw the game map."""
        game_map.draw(self.screen)
    
    def draw_ui(self, player, survival_time: float, character_type: str = "ezreal"):
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
        
        # W skill cooldown (Zed only)
        y_offset += 25
        if character_type == "zed":
            if player.w_cooldown > 0:
                cd_text = f"W: {player.w_cooldown:.1f}s"
                text_surface = self.font.render(cd_text, True, GRAY)
            else:
                text_surface = self.font.render("W: Ready", True, (150, 100, 255))
            self.screen.blit(text_surface, (10, y_offset))
        
        # E skill cooldown
        y_offset += 25
        if character_type == "zed":
            if player.e_cooldown > 0:
                cd_text = f"E: {player.e_cooldown:.1f}s"
                text_surface = self.font.render(cd_text, True, GRAY)
            else:
                text_surface = self.font.render("E: Ready", True, (255, 100, 100))
        else:
            if player.teleport_cooldown > 0:
                cd_text = f"E Teleport: {player.teleport_cooldown:.1f}s"
                text_surface = self.font.render(cd_text, True, GRAY)
            else:
                text_surface = self.font.render("E Teleport: Ready", True, WHITE)
        self.screen.blit(text_surface, (10, y_offset))
        
        # Draw controls info at bottom
        controls = [
            "Right-Click: Move",
            "Q: Attack",
        ]
        
        if character_type == "zed":
            controls.append("W: Living Shadow")
            controls.append("E: Spin Attack")
        else:
            controls.append("E: Teleport")
        
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
    
    def draw_main_menu(self, mouse_pos: tuple):
        """Draw the main menu screen with interactive buttons."""
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
        instructions_box = pygame.Rect(SCREEN_WIDTH // 2 - 250, 400, 500, 200)
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
            "Avoid projectiles, spears, and knives!"
        ]
        
        y_start = 420
        for i, line in enumerate(instructions):
            if i == 0:
                text_surface = self.subtitle_font.render(line, True, YELLOW)
            else:
                text_surface = self.font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 25))
            self.screen.blit(text_surface, text_rect)
        
        # Update and draw buttons
        self.start_button.update(mouse_pos)
        self.quit_button.update(mouse_pos)
        
        self.start_button.draw(self.screen, self.button_font)
        self.quit_button.draw(self.screen, self.button_font)
    
    def draw_character_select(self, mouse_pos: tuple, selected_character: int = 0):
        """Draw the character selection screen."""
        # Fill with dark background
        self.screen.fill((20, 25, 35))
        
        # Draw decorative lines
        for i in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (30, 35, 45), (0, i), (SCREEN_WIDTH, i))
        
        # Title
        title_text = self.title_font.render("SELECT CHARACTER", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title_text, title_rect)
        
        # Draw title box
        title_box = title_rect.inflate(40, 20)
        pygame.draw.rect(self.screen, (40, 50, 70), title_box, border_radius=10)
        pygame.draw.rect(self.screen, YELLOW, title_box, 3, border_radius=10)
        self.screen.blit(title_text, title_rect)
        
        # Character slots configuration
        slot_width = 280
        slot_height = 400
        slot_spacing = 40
        total_width = 3 * slot_width + 2 * slot_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        slot_y = 150
        
        characters = [
            {"name": "Ezreal", "unlocked": True, "type": "ezreal"},
            {"name": "Zed", "unlocked": True, "type": "zed"},
            {"name": "Coming Soon", "unlocked": False, "type": "locked"}
        ]
        
        for i, char in enumerate(characters):
            slot_x = start_x + i * (slot_width + slot_spacing)
            
            # Draw slot background
            slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)
            
            if char["unlocked"]:
                # Unlocked character slot
                pygame.draw.rect(self.screen, (40, 50, 70), slot_rect, border_radius=15)
                
                # Highlight border for selected
                if i == selected_character:
                    pygame.draw.rect(self.screen, YELLOW, slot_rect, 4, border_radius=15)
                else:
                    pygame.draw.rect(self.screen, (80, 90, 110), slot_rect, 2, border_radius=15)
                
                # Draw character preview
                preview_x = slot_x + slot_width // 2
                preview_y = slot_y + 150
                
                if char["type"] == "ezreal":
                    self._draw_ezreal_preview(preview_x, preview_y)
                elif char["type"] == "zed":
                    self._draw_zed_preview(preview_x, preview_y)
                
                # Character name
                name_text = self.subtitle_font.render(char["name"], True, YELLOW)
                name_rect = name_text.get_rect(center=(slot_x + slot_width // 2, slot_y + slot_height - 60))
                self.screen.blit(name_text, name_rect)
                
                # "Available" label
                avail_text = self.font.render("Available", True, (100, 255, 100))
                avail_rect = avail_text.get_rect(center=(slot_x + slot_width // 2, slot_y + slot_height - 30))
                self.screen.blit(avail_text, avail_rect)
            else:
                # Locked character slot
                pygame.draw.rect(self.screen, (30, 35, 45), slot_rect, border_radius=15)
                pygame.draw.rect(self.screen, (50, 55, 65), slot_rect, 2, border_radius=15)
                
                # Draw shadow/locked character
                preview_x = slot_x + slot_width // 2
                preview_y = slot_y + 150
                
                # Draw black shadow ball
                pygame.draw.circle(self.screen, (20, 20, 25), (preview_x, preview_y), 60)
                pygame.draw.circle(self.screen, (40, 40, 50), (preview_x, preview_y), 60, 3)
                
                # Draw question marks
                for j in range(3):
                    qm_text = self.subtitle_font.render("?", True, (60, 60, 70))
                    qm_rect = qm_text.get_rect(center=(preview_x + (j - 1) * 30, preview_y))
                    self.screen.blit(qm_text, qm_rect)
                
                # "Coming Soon" text
                name_text = self.subtitle_font.render(char["name"], True, (80, 80, 90))
                name_rect = name_text.get_rect(center=(slot_x + slot_width // 2, slot_y + slot_height - 60))
                self.screen.blit(name_text, name_rect)
                
                # "Locked" label
                locked_text = self.font.render("Locked", True, (100, 100, 110))
                locked_rect = locked_text.get_rect(center=(slot_x + slot_width // 2, slot_y + slot_height - 30))
                self.screen.blit(locked_text, locked_rect)
        
        # Update and draw buttons
        self.select_button.update(mouse_pos)
        self.back_button.update(mouse_pos)
        
        self.select_button.draw(self.screen, self.button_font)
        self.back_button.draw(self.screen, self.button_font)
    
    def _draw_ezreal_preview(self, x: int, y: int):
        """Draw Ezreal character preview at the given position."""
        # Body color - blue adventurer outfit
        body_color = (70, 130, 180)
        body_outline = (50, 100, 140)
        
        # Draw body (oval shape)
        body_rect = pygame.Rect(x - 25, y - 10, 50, 70)
        pygame.draw.ellipse(self.screen, body_color, body_rect)
        pygame.draw.ellipse(self.screen, body_outline, body_rect, 2)
        
        # Draw head
        head_y = y - 50
        pygame.draw.circle(self.screen, (255, 220, 180), (x, head_y), 28)  # Skin color
        pygame.draw.circle(self.screen, (220, 190, 150), (x, head_y), 28, 2)  # Outline
        
        # Draw blond hair (spiky adventurer style)
        hair_color = (255, 215, 0)  # Golden blond
        hair_points = [
            (x - 25, head_y + 5),    # Left side
            (x - 20, head_y - 25),   # Left spike
            (x - 10, head_y - 15),   # Left middle
            (x, head_y - 35),        # Top spike
            (x + 10, head_y - 15),   # Right middle
            (x + 20, head_y - 25),   # Right spike
            (x + 25, head_y + 5),    # Right side
        ]
        pygame.draw.polygon(self.screen, hair_color, hair_points)
        pygame.draw.polygon(self.screen, (200, 170, 0), hair_points, 2)
        
        # Draw face - handsome features
        # Eyes
        eye_y = head_y - 5
        pygame.draw.circle(self.screen, (255, 255, 255), (x - 10, eye_y), 6)
        pygame.draw.circle(self.screen, (255, 255, 255), (x + 10, eye_y), 6)
        pygame.draw.circle(self.screen, (70, 130, 180), (x - 10, eye_y), 4)  # Blue eyes
        pygame.draw.circle(self.screen, (70, 130, 180), (x + 10, eye_y), 4)
        pygame.draw.circle(self.screen, (30, 30, 30), (x - 10, eye_y), 2)  # Pupils
        pygame.draw.circle(self.screen, (30, 30, 30), (x + 10, eye_y), 2)
        
        # Confident smile
        pygame.draw.arc(self.screen, (150, 100, 80),
                       (x - 10, head_y + 5, 20, 12),
                       3.14, 0, 2)
        
        # Draw gauntlet on right hand (Ezreal's signature)
        gauntlet_x = x + 30
        gauntlet_y = y + 20
        pygame.draw.circle(self.screen, (255, 215, 0), (gauntlet_x, gauntlet_y), 15)
        pygame.draw.circle(self.screen, (200, 170, 0), (gauntlet_x, gauntlet_y), 15, 2)
        # Gauntlet glow
        glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 215, 0, 50), (20, 20), 20)
        self.screen.blit(glow_surface, (gauntlet_x - 20, gauntlet_y - 20))
    
    def _draw_zed_preview(self, x: int, y: int):
        """Draw Zed character preview at the given position."""
        # Body color - dark shinobi outfit
        body_color = (30, 30, 35)
        body_outline = (60, 0, 0)
        
        # Draw body (oval shape)
        body_rect = pygame.Rect(x - 25, y - 10, 50, 70)
        pygame.draw.ellipse(self.screen, body_color, body_rect)
        pygame.draw.ellipse(self.screen, body_outline, body_rect, 2)
        
        # Draw head (masked face)
        head_y = y - 50
        pygame.draw.circle(self.screen, (20, 20, 25), (x, head_y), 28)  # Dark mask
        pygame.draw.circle(self.screen, (80, 0, 0), (x, head_y), 28, 2)  # Red outline
        
        # Draw mask details
        # Horizontal mask line
        pygame.draw.line(self.screen, (100, 0, 0), 
                        (x - 20, head_y), (x + 20, head_y), 3)
        
        # Glowing red eyes (Zed's signature)
        eye_y = head_y - 2
        # Left eye glow
        pygame.draw.circle(self.screen, (200, 0, 0), (x - 12, eye_y), 5)
        pygame.draw.circle(self.screen, (255, 50, 50), (x - 12, eye_y), 3)
        # Right eye glow
        pygame.draw.circle(self.screen, (200, 0, 0), (x + 12, eye_y), 5)
        pygame.draw.circle(self.screen, (255, 50, 50), (x + 12, eye_y), 3)
        
        # Draw shadowy hair/spikes
        hair_color = (40, 40, 45)
        hair_points = [
            (x - 25, head_y + 5),
            (x - 20, head_y - 20),
            (x - 10, head_y - 30),
            (x, head_y - 25),
            (x + 10, head_y - 30),
            (x + 20, head_y - 20),
            (x + 25, head_y + 5),
        ]
        pygame.draw.polygon(self.screen, hair_color, hair_points)
        pygame.draw.polygon(self.screen, (80, 0, 0), hair_points, 2)
        
        # Draw arm blades (hidden blades)
        blade_x = x + 28
        blade_y = y + 10
        blade_points = [
            (blade_x, blade_y),
            (blade_x + 15, blade_y - 5),
            (blade_x + 15, blade_y + 5),
        ]
        pygame.draw.polygon(self.screen, (150, 150, 160), blade_points)
        pygame.draw.polygon(self.screen, (200, 200, 210), blade_points, 1)
        
        # Blade glow
        glow_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (150, 0, 0, 60), (15, 15), 12)
        self.screen.blit(glow_surface, (blade_x - 5, blade_y - 15))
    
    def draw_game_over(self, survival_time: float, best_time: float, mouse_pos: tuple):
        """Draw game over screen with interactive buttons."""
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
        
        # Update and draw buttons
        self.retry_button.update(mouse_pos)
        self.game_over_quit_button.update(mouse_pos)
        
        self.retry_button.draw(self.screen, self.button_font)
        self.game_over_quit_button.draw(self.screen, self.button_font)
    
    def draw_pause_screen(self, mouse_pos: tuple, show_confirmation: bool = False):
        """Draw pause screen with resume and menu buttons."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        if show_confirmation:
            # Draw confirmation dialog
            dialog_box = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 60, 400, 150)
            pygame.draw.rect(self.screen, (40, 45, 55), dialog_box, border_radius=10)
            pygame.draw.rect(self.screen, YELLOW, dialog_box, 3, border_radius=10)
            
            # Confirmation text
            confirm_text = self.subtitle_font.render("Are you sure?", True, WHITE)
            confirm_rect = confirm_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(confirm_text, confirm_rect)
            
            # Warning text
            warning_text = self.font.render("Progress will be lost!", True, (255, 150, 150))
            warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 15))
            self.screen.blit(warning_text, warning_rect)
            
            # Update and draw confirmation buttons
            self.yes_button.update(mouse_pos)
            self.no_button.update(mouse_pos)
            
            self.yes_button.draw(self.screen, self.button_font)
            self.no_button.draw(self.screen, self.button_font)
        else:
            # Pause text
            pause_text = self.title_font.render("PAUSED", True, WHITE)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(pause_text, pause_rect)
            
            # Draw a box around "PAUSED"
            box_rect = pause_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, WHITE, box_rect, 3, border_radius=10)
            
            # Update and draw buttons
            self.resume_button.update(mouse_pos)
            self.menu_button.update(mouse_pos)
            
            self.resume_button.draw(self.screen, self.button_font)
            self.menu_button.draw(self.screen, self.button_font)
    
    def draw_game_mode_select(self, mouse_pos: tuple, selected_character: int = 0):
        """Draw the game mode selection screen."""
        # Fill with dark background
        self.screen.fill((20, 25, 35))
        
        # Draw decorative lines
        for i in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (30, 35, 45), (0, i), (SCREEN_WIDTH, i))
        
        # Title
        title_text = self.title_font.render("SELECT GAME MODE", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        
        # Draw title box
        title_box = title_rect.inflate(40, 20)
        pygame.draw.rect(self.screen, (40, 50, 70), title_box, border_radius=10)
        pygame.draw.rect(self.screen, YELLOW, title_box, 3, border_radius=10)
        self.screen.blit(title_text, title_rect)
        
        # Character indicator
        char_name = "Ezreal" if selected_character == 0 else "Zed"
        char_text = self.subtitle_font.render(f"Character: {char_name}", True, WHITE)
        char_rect = char_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(char_text, char_rect)
        
        # Mode cards - side by side
        card_width = 500
        card_height = 380
        card_spacing = 40
        total_width = 2 * card_width + card_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        card_y = 160
        
        # Survival Mode Card (left) - has XP, upgrades, hearts
        survival_rect = pygame.Rect(start_x, card_y, card_width, card_height)
        is_survival_hovered = survival_rect.collidepoint(mouse_pos)
        
        # Card background with gradient effect
        survival_bg = (50, 40, 70) if is_survival_hovered else (40, 35, 55)
        pygame.draw.rect(self.screen, survival_bg, survival_rect, border_radius=15)
        pygame.draw.rect(self.screen, (180, 100, 220), survival_rect, 3 if is_survival_hovered else 2, border_radius=15)
        
        # Survival title
        survival_title = self.subtitle_font.render("SURVIVAL MODE", True, (200, 120, 255))
        self.screen.blit(survival_title, (start_x + 20, card_y + 20))
        
        # Survival description
        survival_desc = [
            "• Start with 3 hearts (lives)",
            "• Gain XP by killing enemies",
            "• Level up and choose upgrades",
            "• Upgrade tiers: Common, Epic, Legendary",
            "• Improve speed, cooldowns, damage",
            "• Enemies don't one-hit kill you",
            "• Best for longer gameplay sessions"
        ]
        for i, line in enumerate(survival_desc):
            text = self.font.render(line, True, WHITE)
            self.screen.blit(text, (start_x + 20, card_y + 60 + i * 28))
        
        # Survival badge
        pygame.draw.rect(self.screen, (100, 50, 150), (start_x + card_width - 100, card_y + 10, 90, 25), border_radius=5)
        badge_text = self.font.render("FEATURED", True, WHITE)
        self.screen.blit(badge_text, (start_x + card_width - 95, card_y + 15))
        
        # Legacy Mode Card (right) - classic, no upgrades
        legacy_x = start_x + card_width + card_spacing
        legacy_rect = pygame.Rect(legacy_x, card_y, card_width, card_height)
        is_legacy_hovered = legacy_rect.collidepoint(mouse_pos)
        
        # Card background
        legacy_bg = (60, 50, 40) if is_legacy_hovered else (45, 40, 35)
        pygame.draw.rect(self.screen, legacy_bg, legacy_rect, border_radius=15)
        pygame.draw.rect(self.screen, (200, 150, 100), legacy_rect, 3 if is_legacy_hovered else 2, border_radius=15)
        
        # Legacy title
        legacy_title = self.subtitle_font.render("LEGACY MODE", True, (255, 200, 100))
        self.screen.blit(legacy_title, (legacy_x + 20, card_y + 20))
        
        # Legacy description
        legacy_desc = [
            "• Classic survival experience",
            "• No XP or upgrades",
            "• No extra lives",
            "• One hit = instant death",
            "• Pure skill-based gameplay",
            "• Test your dodging abilities",
            "• How long can you survive?"
        ]
        for i, line in enumerate(legacy_desc):
            text = self.font.render(line, True, WHITE)
            self.screen.blit(text, (legacy_x + 20, card_y + 60 + i * 28))
        
        # Legacy badge
        pygame.draw.rect(self.screen, (150, 100, 50), (legacy_x + card_width - 100, card_y + 10, 90, 25), border_radius=5)
        badge_text = self.font.render("CLASSIC", True, WHITE)
        self.screen.blit(badge_text, (legacy_x + card_width - 90, card_y + 15))
        
        # Update buttons to match card positions
        self.survival_button.rect.center = (start_x + card_width // 2, card_y + card_height + 40)
        self.legacy_button.rect.center = (legacy_x + card_width // 2, card_y + card_height + 40)
        self.mode_back_button.rect.center = (SCREEN_WIDTH // 2, card_y + card_height + 100)
        
        # Update and draw buttons
        self.survival_button.update(mouse_pos)
        self.legacy_button.update(mouse_pos)
        self.mode_back_button.update(mouse_pos)
        
        self.survival_button.draw(self.screen, self.button_font)
        self.legacy_button.draw(self.screen, self.button_font)
        self.mode_back_button.draw(self.screen, self.button_font)
    
    def draw_upgrade_selection(self, mouse_pos: tuple, upgrades: list, player_stats, selected_index: int = -1):
        """Draw the upgrade selection screen during level up."""
        # Semi-transparent overlay with gradient
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        
        # Title with glow effect
        title_text = self.title_font.render("LEVEL UP!", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        # Glow
        glow_surf = pygame.Surface((title_rect.width + 40, title_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (255, 220, 0, 50), glow_surf.get_rect(), border_radius=10)
        self.screen.blit(glow_surf, (title_rect.x - 20, title_rect.y - 10))
        self.screen.blit(title_text, title_rect)
        
        # Level indicator
        level_text = self.subtitle_font.render(f"Level {player_stats.level}", True, WHITE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, 110))
        self.screen.blit(level_text, level_rect)
        
        # Instruction
        inst_text = self.font.render("Choose an upgrade (click or press 1, 2, 3)", True, (180, 180, 180))
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, 145))
        self.screen.blit(inst_text, inst_rect)
        
        # Draw current stats panel on the right
        self._draw_stats_panel(player_stats)
        
        # Draw upgrade cards
        card_width = 320
        card_height = 400
        card_spacing = 30
        total_width = 3 * card_width + 2 * card_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        card_y = 180
        
        tier_names = {
            "common": "COMMON",
            "epic": "EPIC",
            "legendary": "LEGENDARY"
        }
        
        tier_colors = {
            "common": (180, 180, 190),
            "epic": (200, 100, 255),
            "legendary": (255, 200, 50)
        }
        
        tier_bg_colors = {
            "common": (50, 50, 60),
            "epic": (60, 40, 80),
            "legendary": (70, 55, 30)
        }
        
        for i, upgrade in enumerate(upgrades):
            card_x = start_x + i * (card_width + card_spacing)
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            
            # Highlight if selected/hovered
            is_hovered = card_rect.collidepoint(mouse_pos)
            is_selected = i == selected_index
            tier_color = tier_colors.get(upgrade.tier, (180, 180, 190))
            tier_bg = tier_bg_colors.get(upgrade.tier, (50, 50, 60))
            
            # Card shadow
            shadow_rect = card_rect.copy()
            shadow_rect.x += 5
            shadow_rect.y += 5
            pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=20)
            
            # Card background with tier color
            pygame.draw.rect(self.screen, tier_bg, card_rect, border_radius=20)
            
            # Inner card area
            inner_rect = card_rect.inflate(-10, -10)
            inner_color = (40, 45, 55) if not is_hovered else (50, 55, 70)
            pygame.draw.rect(self.screen, inner_color, inner_rect, border_radius=15)
            
            # Tier-colored border with glow effect for legendary
            border_width = 4 if is_hovered or is_selected else 3
            if upgrade.tier == "legendary":
                # Glow effect
                glow_rect = card_rect.inflate(6, 6)
                pygame.draw.rect(self.screen, (255, 200, 50, 100), glow_rect, border_radius=22)
            pygame.draw.rect(self.screen, tier_color, card_rect, border_width, border_radius=20)
            
            # Tier label with background
            tier_bg_rect = pygame.Rect(card_x + card_width // 2 - 60, card_y + 15, 120, 28)
            pygame.draw.rect(self.screen, tier_color, tier_bg_rect, border_radius=5)
            tier_text = self.font.render(tier_names.get(upgrade.tier, "COMMON"), True, (30, 30, 30))
            tier_text_rect = tier_text.get_rect(center=tier_bg_rect.center)
            self.screen.blit(tier_text, tier_text_rect)
            
            # Upgrade name with underline
            name_text = self.subtitle_font.render(upgrade.name, True, WHITE)
            name_rect = name_text.get_rect(center=(card_x + card_width // 2, card_y + 75))
            self.screen.blit(name_text, name_rect)
            # Underline
            pygame.draw.line(self.screen, tier_color, 
                           (name_rect.left, name_rect.bottom + 5),
                           (name_rect.right, name_rect.bottom + 5), 2)
            
            # Description with background
            desc_bg_rect = pygame.Rect(card_x + 20, card_y + 110, card_width - 40, 50)
            pygame.draw.rect(self.screen, (30, 35, 45), desc_bg_rect, border_radius=8)
            desc_text = self.font.render(upgrade.description, True, (220, 220, 220))
            desc_rect = desc_text.get_rect(center=desc_bg_rect.center)
            self.screen.blit(desc_text, desc_rect)
            
            # Draw icon based on type
            icon_y = card_y + 220
            self._draw_upgrade_icon(card_x + card_width // 2, icon_y, upgrade.type, tier_color)
            
            # Key hint with background
            key_bg_rect = pygame.Rect(card_x + card_width // 2 - 25, card_y + card_height - 55, 50, 35)
            pygame.draw.rect(self.screen, tier_color, key_bg_rect, border_radius=8)
            key_text = self.subtitle_font.render(f"{i + 1}", True, (30, 30, 30))
            key_rect = key_text.get_rect(center=key_bg_rect.center)
            self.screen.blit(key_text, key_rect)
    
    def _draw_stats_panel(self, player_stats):
        """Draw the stats panel on the right side during upgrade selection."""
        panel_x = SCREEN_WIDTH - 220
        panel_y = 180
        panel_width = 200
        panel_height = 300
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (30, 35, 50), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100, 120, 150), panel_rect, 2, border_radius=15)
        
        # Title
        title = self.font.render("CURRENT STATS", True, (200, 200, 220))
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, panel_y + 25))
        self.screen.blit(title, title_rect)
        
        # Stats
        y_offset = panel_y + 60
        spacing = 40
        
        # Speed
        speed_mult = player_stats.speed_multiplier
        self._draw_stat_line(panel_x + 15, y_offset, "Speed", f"x{speed_mult:.2f}", speed_mult)
        y_offset += spacing
        
        # Cooldown
        cd_mult = player_stats.cooldown_multiplier
        cd_display = f"x{cd_mult:.2f}"
        self._draw_stat_line(panel_x + 15, y_offset, "Cooldown", cd_display, 1/cd_mult if cd_mult > 0 else 1)
        y_offset += spacing
        
        # Q Cooldown
        q_mult = player_stats.q_cooldown_multiplier
        self._draw_stat_line(panel_x + 15, y_offset, "Q Speed", f"x{q_mult:.2f}", 1/q_mult if q_mult > 0 else 1)
        y_offset += spacing
        
        # Attack Size
        size_mult = player_stats.attack_size_multiplier
        self._draw_stat_line(panel_x + 15, y_offset, "Attack Size", f"x{size_mult:.2f}", size_mult)
        y_offset += spacing
        
        # Extra Lives
        lives = player_stats.extra_lives
        lives_color = (255, 100, 100) if lives > 0 else (150, 150, 150)
        lives_text = self.font.render(f"Extra Lives: {lives}", True, lives_color)
        self.screen.blit(lives_text, (panel_x + 15, y_offset))
        y_offset += spacing
        
        # Level
        level_text = self.font.render(f"Level: {player_stats.level}", True, YELLOW)
        self.screen.blit(level_text, (panel_x + 15, y_offset))
    
    def _draw_stat_line(self, x: int, y: int, name: str, value: str, multiplier: float):
        """Draw a single stat line with color based on multiplier."""
        # Name
        name_text = self.font.render(f"{name}:", True, (180, 180, 200))
        self.screen.blit(name_text, (x, y))
        
        # Value with color (green if buffed, white if neutral)
        if multiplier > 1.05:
            value_color = (100, 255, 100)
        elif multiplier < 0.95:
            value_color = (100, 255, 100)  # Lower cooldown is good
        else:
            value_color = (200, 200, 200)
        
        value_text = self.font.render(value, True, value_color)
        self.screen.blit(value_text, (x + 100, y))
    
    def _draw_upgrade_icon(self, x: int, y: int, upgrade_type: str, color: tuple):
        """Draw an icon representing the upgrade type."""
        if upgrade_type == "speed":
            # Draw a lightning bolt / arrow
            points = [
                (x - 15, y - 25),
                (x + 10, y - 25),
                (x, y - 5),
                (x + 15, y - 5),
                (x - 5, y + 25),
                (x + 5, y),
                (x - 15, y)
            ]
            pygame.draw.polygon(self.screen, color, points)
        elif upgrade_type == "cooldown":
            # Draw a clock
            pygame.draw.circle(self.screen, color, (x, y), 25, 3)
            pygame.draw.line(self.screen, color, (x, y), (x, y - 15), 3)
            pygame.draw.line(self.screen, color, (x, y), (x + 10, y + 5), 3)
        elif upgrade_type == "extra_life":
            # Draw a heart
            pygame.draw.circle(self.screen, color, (x - 10, y - 5), 15)
            pygame.draw.circle(self.screen, color, (x + 10, y - 5), 15)
            pygame.draw.polygon(self.screen, color, [
                (x - 25, y),
                (x, y + 25),
                (x + 25, y)
            ])
        elif upgrade_type == "attack_speed":
            # Draw multiple arrows
            for i in range(3):
                offset_x = (i - 1) * 20
                pygame.draw.polygon(self.screen, color, [
                    (x + offset_x - 8, y - 15),
                    (x + offset_x + 8, y - 15),
                    (x + offset_x, y + 15)
                ])
        elif upgrade_type == "attack_size":
            # Draw expanding circles
            pygame.draw.circle(self.screen, color, (x, y), 15, 2)
            pygame.draw.circle(self.screen, color, (x, y), 25, 2)
            pygame.draw.circle(self.screen, color, (x, y), 35, 2)
        else:
            # Default star
            pygame.draw.polygon(self.screen, color, [
                (x, y - 25),
                (x + 8, y - 8),
                (x + 25, y - 8),
                (x + 12, y + 5),
                (x + 18, y + 25),
                (x, y + 12),
                (x - 18, y + 25),
                (x - 12, y + 5),
                (x - 25, y - 8),
                (x - 8, y - 8)
            ])
    
    def draw_survival_ui(self, player_stats, player):
        """Draw additional UI for Survival mode (XP bar, level, hearts, stats)."""
        # XP bar at bottom center
        bar_width = 400
        bar_height = 20
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = SCREEN_HEIGHT - 35
        
        # Background
        pygame.draw.rect(self.screen, (40, 40, 50), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), border_radius=5)
        
        # XP progress
        progress = player_stats.get_xp_progress()
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            pygame.draw.rect(self.screen, (50, 150, 200), (bar_x, bar_y, fill_width, bar_height), border_radius=3)
        
        # Border
        pygame.draw.rect(self.screen, (100, 100, 120), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=3)
        
        # Level text
        level_text = self.font.render(f"Lv.{player_stats.level}", True, YELLOW)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height // 2))
        self.screen.blit(level_text, level_rect)
        
        # XP text
        xp_text = self.font.render(f"{player_stats.xp}/{player_stats.xp_to_next_level} XP", True, WHITE)
        xp_rect = xp_text.get_rect(midleft=(bar_x + bar_width + 10, bar_y + bar_height // 2))
        self.screen.blit(xp_text, xp_rect)
        
        # Hearts indicator (top right)
        hearts_text = self.font.render("Hearts:", True, (255, 150, 150))
        self.screen.blit(hearts_text, (SCREEN_WIDTH - 260, 10))
        
        # Total hearts is just max_hearts (extra lives upgrade adds to max_hearts directly)
        total_hearts = player_stats.max_hearts
        base_hearts = SURVIVAL_MODE_HEARTS  # The original 3 hearts
        
        # Draw hearts (full, empty, and extra) with wrapping
        hearts_per_row = 6
        for i in range(total_hearts):
            row = i // hearts_per_row
            col = i % hearts_per_row
            heart_x = SCREEN_WIDTH - 260 + col * 22
            heart_y = 35 + row * 20
            
            # Determine heart color
            if i < player_stats.hearts:
                # Full heart - red for base, green for extra
                if i < base_hearts:
                    heart_color = (255, 80, 80)  # Red for base hearts
                else:
                    heart_color = (80, 200, 120)  # Green for extra hearts
            else:
                # Empty heart
                if i < base_hearts:
                    heart_color = (80, 80, 80)  # Gray for empty base hearts
                else:
                    heart_color = (40, 100, 60)  # Darker green for empty extra hearts
                    
            pygame.draw.circle(self.screen, heart_color, (heart_x - 5, heart_y), 6)
            pygame.draw.circle(self.screen, heart_color, (heart_x + 5, heart_y), 6)
            pygame.draw.polygon(self.screen, heart_color, [
                (heart_x - 11, heart_y + 2),
                (heart_x, heart_y + 13),
                (heart_x + 11, heart_y + 2)
            ])
        
        # Hearts count text
        count_text = self.font.render(f"{player_stats.hearts}/{total_hearts}", True, (200, 200, 200))
        self.screen.blit(count_text, (SCREEN_WIDTH - 260, 55 + ((total_hearts - 1) // hearts_per_row + 1) * 20))
    
    def draw_pause_screen_with_stats(self, mouse_pos: tuple, show_confirmation: bool = False, player_stats = None):
        """Draw pause screen with optional stats panel for Survival mode."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        if show_confirmation:
            # Draw confirmation dialog
            dialog_box = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 60, 400, 150)
            pygame.draw.rect(self.screen, (40, 45, 55), dialog_box, border_radius=10)
            pygame.draw.rect(self.screen, YELLOW, dialog_box, 3, border_radius=10)
            
            # Confirmation text
            confirm_text = self.subtitle_font.render("Are you sure?", True, WHITE)
            confirm_rect = confirm_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(confirm_text, confirm_rect)
            
            # Warning text
            warning_text = self.font.render("Progress will be lost!", True, (255, 150, 150))
            warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 15))
            self.screen.blit(warning_text, warning_rect)
            
            # Update and draw confirmation buttons
            self.yes_button.update(mouse_pos)
            self.no_button.update(mouse_pos)
            
            self.yes_button.draw(self.screen, self.button_font)
            self.no_button.draw(self.screen, self.button_font)
        else:
            # Pause text
            pause_text = self.title_font.render("PAUSED", True, WHITE)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
            self.screen.blit(pause_text, pause_rect)
            
            # Draw a box around "PAUSED"
            box_rect = pause_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, WHITE, box_rect, 3, border_radius=10)
            
            # Draw stats panel if in Survival mode
            if player_stats:
                self._draw_pause_stats_panel(player_stats)
            
            # Update and draw buttons
            self.resume_button.update(mouse_pos)
            self.menu_button.update(mouse_pos)
            
            self.resume_button.draw(self.screen, self.button_font)
            self.menu_button.draw(self.screen, self.button_font)
    
    def _draw_pause_stats_panel(self, player_stats):
        """Draw a detailed stats panel during pause in Survival mode."""
        panel_x = SCREEN_WIDTH - 280
        panel_y = 150
        panel_width = 250
        panel_height = 350
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (30, 35, 50), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100, 120, 150), panel_rect, 2, border_radius=15)
        
        # Title
        title = self.subtitle_font.render("CHARACTER STATS", True, (200, 200, 220))
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, panel_y + 25))
        self.screen.blit(title, title_rect)
        
        # Divider line
        pygame.draw.line(self.screen, (80, 90, 110), 
                        (panel_x + 20, panel_y + 50), 
                        (panel_x + panel_width - 20, panel_y + 50), 2)
        
        # Stats
        y_offset = panel_y + 70
        spacing = 35
        
        # Level
        level_text = self.font.render(f"Level: {player_stats.level}", True, YELLOW)
        self.screen.blit(level_text, (panel_x + 20, y_offset))
        y_offset += spacing
        
        # Speed
        speed_mult = player_stats.speed_multiplier
        self._draw_stat_line(panel_x + 20, y_offset, "Speed", f"x{speed_mult:.2f}", speed_mult)
        y_offset += spacing
        
        # Cooldown
        cd_mult = player_stats.cooldown_multiplier
        self._draw_stat_line(panel_x + 20, y_offset, "Cooldown", f"x{cd_mult:.2f}", 1/cd_mult if cd_mult > 0 else 1)
        y_offset += spacing
        
        # Q Speed
        q_mult = player_stats.q_cooldown_multiplier
        self._draw_stat_line(panel_x + 20, y_offset, "Q Speed", f"x{q_mult:.2f}", 1/q_mult if q_mult > 0 else 1)
        y_offset += spacing
        
        # Attack Size
        size_mult = player_stats.attack_size_multiplier
        self._draw_stat_line(panel_x + 20, y_offset, "Attack Size", f"x{size_mult:.2f}", size_mult)
        y_offset += spacing
        
        # Damage
        dmg_mult = player_stats.damage_multiplier
        self._draw_stat_line(panel_x + 20, y_offset, "Damage", f"x{dmg_mult:.2f}", dmg_mult)
        y_offset += spacing
        
        # Hearts
        hearts_text = self.font.render(f"Hearts: {player_stats.hearts}/{player_stats.max_hearts}", True, (255, 100, 100))
        self.screen.blit(hearts_text, (panel_x + 20, y_offset))
        y_offset += spacing
        
        # Extra Lives
        lives = player_stats.extra_lives
        lives_color = (100, 255, 100) if lives > 0 else (150, 150, 150)
        lives_text = self.font.render(f"Extra Lives: {lives}", True, lives_color)
        self.screen.blit(lives_text, (panel_x + 20, y_offset))
    
    def present(self):
        """Flip the display buffer."""
        pygame.display.flip()
