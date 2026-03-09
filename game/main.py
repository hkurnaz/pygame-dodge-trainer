"""Main game entry point."""

import pygame
import sys

from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game.entities import Player
from game.systems import InputHandler, Renderer, EnemyManager, GameMap


class Game:
    """Main game class."""
    
    def __init__(self):
        pygame.init()
        
        # Setup display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dodge Training - LoL Style")
        
        # Setup clock
        self.clock = pygame.time.Clock()
        
        # Create systems
        self.renderer = Renderer(self.screen)
        
        # Create game map
        self.game_map = GameMap()
        
        # Game states
        self.running = True
        self.in_main_menu = True
        self.in_character_select = False
        self.paused = False
        self.show_pause_confirmation = False
        self.game_over = False
        self.selected_character = 0  # 0 = Ezreal (only unlocked character)
        
        # Timer and score
        self.survival_time = 0.0
        self.best_time = 0.0
        
        # Initialize game (will be reset when starting from menu)
        self.player = None
        self.input_handler = None
        self.enemy_manager = None
    
    def reset_game(self):
        """Reset game state for a new game."""
        # Create player at center of screen (in a valid position)
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.player.set_map(self.game_map)
        
        # Determine character type based on selection
        character_type = "ezreal" if self.selected_character == 0 else "zed"
        
        # Create systems
        self.input_handler = InputHandler(self.player, character_type)
        self.enemy_manager = EnemyManager(self.game_map)
        
        # Reset timers
        self.survival_time = 0.0
        
        # Reset game over state
        self.game_over = False
        self.paused = False
        self.show_pause_confirmation = False
    
    def handle_events(self):
        """Process all pygame events."""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # Handle main menu events
            if self.in_main_menu:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.renderer.start_button.is_clicked(mouse_pos):
                        self.in_main_menu = False
                        self.in_character_select = True
                    elif self.renderer.quit_button.is_clicked(mouse_pos):
                        self.running = False
                continue
            
            # Handle character selection events
            if self.in_character_select:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check if clicking on character slots
                    slot_width = 280
                    slot_spacing = 40
                    total_width = 3 * slot_width + 2 * slot_spacing
                    start_x = (SCREEN_WIDTH - total_width) // 2
                    slot_y = 150
                    
                    for i in range(3):
                        slot_x = start_x + i * (slot_width + slot_spacing)
                        slot_rect = pygame.Rect(slot_x, slot_y, slot_width, 400)
                        if slot_rect.collidepoint(mouse_pos):
                            if i < 2:  # Only first two are selectable (Ezreal and Zed)
                                self.selected_character = i
                    
                    if self.renderer.select_button.is_clicked(mouse_pos):
                        # Start game with selected character
                        if self.selected_character in [0, 1]:  # Ezreal or Zed
                            self.in_character_select = False
                            self.reset_game()
                    elif self.renderer.back_button.is_clicked(mouse_pos):
                        self.in_character_select = False
                        self.in_main_menu = True
                continue
            
            # Handle pause menu events
            if self.paused:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.show_pause_confirmation:
                        self.show_pause_confirmation = False
                    else:
                        self.paused = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.show_pause_confirmation:
                        if self.renderer.yes_button.is_clicked(mouse_pos):
                            # Return to main menu
                            self.in_main_menu = True
                            self.paused = False
                            self.show_pause_confirmation = False
                        elif self.renderer.no_button.is_clicked(mouse_pos):
                            self.show_pause_confirmation = False
                    else:
                        if self.renderer.resume_button.is_clicked(mouse_pos):
                            self.paused = False
                        elif self.renderer.menu_button.is_clicked(mouse_pos):
                            self.show_pause_confirmation = True
                continue
            
            # Handle game over events
            if self.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.renderer.retry_button.is_clicked(mouse_pos):
                        self.reset_game()
                    elif self.renderer.game_over_quit_button.is_clicked(mouse_pos):
                        self.in_main_menu = True
                        self.game_over = False
                continue
            
            # Handle in-game events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = True
                elif event.key == pygame.K_q:
                    self.input_handler._handle_q_skill(mouse_pos)
                elif event.key == pygame.K_w:
                    self.input_handler._handle_w_skill(mouse_pos)
                elif event.key == pygame.K_e:
                    self.input_handler._handle_e_skill(mouse_pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Right click
                self.input_handler._handle_right_click(event.pos)
    
    def update(self, dt: float):
        """Update game state."""
        if self.in_main_menu or self.in_character_select or self.game_over or self.paused:
            return
        
        # Update survival time
        self.survival_time += dt
        
        # Update player
        self.player.update(dt)
        self.input_handler.update(dt)
        
        # Update enemies
        self.enemy_manager.update(dt, self.player.x, self.player.y)
        
        # Check projectile-enemy collisions
        killed = self.input_handler.check_projectile_enemy_collision(
            self.enemy_manager.enemies,
            self.enemy_manager.spear_enemies,
            self.enemy_manager.rogue_enemies
        )
        
        # Check collision between enemy projectiles/spears and player
        if self.enemy_manager.check_collision(self.player.rect):
            self.game_over = True
            # Update best time
            if self.survival_time > self.best_time:
                self.best_time = self.survival_time
    
    def render(self):
        """Render the game."""
        mouse_pos = pygame.mouse.get_pos()
        
        if self.in_main_menu:
            self.renderer.draw_main_menu(mouse_pos)
            self.renderer.present()
            return
        
        if self.in_character_select:
            self.renderer.draw_character_select(mouse_pos, self.selected_character)
            self.renderer.present()
            return
        
        # Draw map first (background)
        self.renderer.draw_map(self.game_map)
        
        # Draw mouse indicator
        self.renderer.draw_mouse_indicator(mouse_pos, self.player.position)
        
        # Determine character type
        character_type = "ezreal" if self.selected_character == 0 else "zed"
        
        # Draw game objects
        self.renderer.draw_projectiles(self.input_handler)
        self.renderer.draw_enemies(self.enemy_manager, self.player.x, self.player.y)
        self.renderer.draw_player(self.player, character_type)
        
        # Draw UI
        self.renderer.draw_ui(self.player, self.survival_time, character_type)
        
        # Draw pause screen if paused
        if self.paused:
            self.renderer.draw_pause_screen(mouse_pos, self.show_pause_confirmation)
        # Draw game over screen if needed
        elif self.game_over:
            self.renderer.draw_game_over(self.survival_time, self.best_time, mouse_pos)
        
        self.renderer.present()
    
    def run(self):
        """Main game loop."""
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.render()
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
