"""Rendering system."""

import pygame
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, RED, YELLOW


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
    
    def present(self):
        """Flip the display buffer."""
        pygame.display.flip()
