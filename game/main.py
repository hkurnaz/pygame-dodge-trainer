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
        self.game_over = False
        
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
        
        # Create systems
        self.input_handler = InputHandler(self.player)
        self.enemy_manager = EnemyManager(self.game_map)
        
        # Reset timers
        self.survival_time = 0.0
        
        # Reset game over state
        self.game_over = False
    
    def handle_events(self):
        """Process all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.in_main_menu:
                        self.running = False
                    elif self.game_over:
                        self.running = False
                    else:
                        self.running = False
                
                elif event.key == pygame.K_SPACE:
                    if self.in_main_menu:
                        # Start game
                        self.in_main_menu = False
                        self.reset_game()
                    elif self.game_over:
                        # Retry - reset game
                        self.reset_game()
                    else:
                        # Handle Q skill if in game (space also fires)
                        self.input_handler._handle_q_skill(pygame.mouse.get_pos())
            
            # Only handle game events if in game (not in menu or game over)
            if not self.in_main_menu and not self.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Right click
                    self.input_handler._handle_right_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.input_handler._handle_q_skill(pygame.mouse.get_pos())
                    elif event.key == pygame.K_e:
                        self.input_handler._handle_e_skill(pygame.mouse.get_pos())
    
    def update(self, dt: float):
        """Update game state."""
        if self.in_main_menu or self.game_over:
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
            self.enemy_manager.spear_enemies
        )
        
        # Check collision between enemy projectiles/spears and player
        if self.enemy_manager.check_collision(self.player.rect):
            self.game_over = True
            # Update best time
            if self.survival_time > self.best_time:
                self.best_time = self.survival_time
    
    def render(self):
        """Render the game."""
        if self.in_main_menu:
            self.renderer.draw_main_menu()
            self.renderer.present()
            return
        
        # Draw map first (background)
        self.renderer.draw_map(self.game_map)
        
        # Draw mouse indicator
        mouse_pos = pygame.mouse.get_pos()
        self.renderer.draw_mouse_indicator(mouse_pos, self.player.position)
        
        # Draw game objects
        self.renderer.draw_projectiles(self.input_handler)
        self.renderer.draw_enemies(self.enemy_manager, self.player.x, self.player.y)
        self.renderer.draw_player(self.player)
        
        # Draw UI
        self.renderer.draw_ui(self.player, self.survival_time)
        
        # Draw game over screen if needed
        if self.game_over:
            self.renderer.draw_game_over(self.survival_time, self.best_time)
        
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
