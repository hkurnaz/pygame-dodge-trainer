"""Main game entry point."""

import pygame
import sys

from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_MODE_LEGACY, GAME_MODE_SURVIVAL, XP_PER_KILL
from game.entities import Player
from game.systems import InputHandler, Renderer, EnemyManager, GameMap, Upgrade, PlayerStats


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
        self.in_game_mode_select = False
        self.paused = False
        self.show_pause_confirmation = False
        self.game_over = False
        self.selected_character = 0  # 0 = Ezreal (only unlocked character)
        self.game_mode = None  # Will be set when mode is selected
        
        # Survival mode specific (has XP, hearts, upgrades)
        self.player_stats = None
        self.upgrade_options = []
        self.showing_upgrade_selection = False
        
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
        
        # Create player stats for Survival mode (has XP, hearts, upgrades)
        if self.game_mode == GAME_MODE_SURVIVAL:
            self.player_stats = PlayerStats(character_type)
            # Apply initial speed from stats
            self.player.speed = self.player_stats.get_speed()
        else:
            # Legacy mode - no stats, one-hit death
            self.player_stats = None
        
        # Create systems
        self.input_handler = InputHandler(self.player, character_type, self.player_stats)
        self.enemy_manager = EnemyManager(self.game_map)
        
        # Reset timers
        self.survival_time = 0.0
        
        # Reset game over state
        self.game_over = False
        self.paused = False
        self.show_pause_confirmation = False
        self.showing_upgrade_selection = False
        self.upgrade_options = []
    
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
                        # Go to game mode selection
                        if self.selected_character in [0, 1]:  # Ezreal or Zed
                            self.in_character_select = False
                            self.in_game_mode_select = True
                    elif self.renderer.back_button.is_clicked(mouse_pos):
                        self.in_character_select = False
                        self.in_main_menu = True
                continue
            
            # Handle game mode selection events
            if self.in_game_mode_select:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Survival button - has XP, hearts, upgrades
                    if self.renderer.survival_button.is_clicked(mouse_pos):
                        self.game_mode = GAME_MODE_SURVIVAL
                        self.in_game_mode_select = False
                        self.reset_game()
                    # Legacy button - classic one-hit death
                    elif self.renderer.legacy_button.is_clicked(mouse_pos):
                        self.game_mode = GAME_MODE_LEGACY
                        self.in_game_mode_select = False
                        self.reset_game()
                    elif self.renderer.mode_back_button.is_clicked(mouse_pos):
                        self.in_game_mode_select = False
                        self.in_character_select = True
                continue
            
            # Handle upgrade selection events (Survival mode)
            if self.showing_upgrade_selection:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        idx = event.key - pygame.K_1
                        if idx < len(self.upgrade_options):
                            self._apply_upgrade(idx)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check if clicking on upgrade cards
                    card_width = 320
                    card_height = 400
                    card_spacing = 30
                    total_width = 3 * card_width + 2 * card_spacing
                    start_x = (SCREEN_WIDTH - total_width) // 2
                    card_y = 180
                    
                    for i in range(3):
                        card_x = start_x + i * (card_width + card_spacing)
                        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
                        if card_rect.collidepoint(mouse_pos):
                            self._apply_upgrade(i)
                            break
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
                            self.game_mode = None
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
                        self.game_mode = None
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
                # Hidden debug key: L to instantly level up (for testing)
                elif event.key == pygame.K_l:
                    if self.game_mode == GAME_MODE_SURVIVAL and self.player_stats:
                        # Force level up
                        self.upgrade_options = Upgrade.generate_three_options()
                        self.showing_upgrade_selection = True
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Right click
                self.input_handler._handle_right_click(event.pos)
    
    def _apply_upgrade(self, index: int):
        """Apply the selected upgrade and close the selection screen."""
        if index < len(self.upgrade_options):
            upgrade = self.upgrade_options[index]
            self.player_stats.apply_upgrade(upgrade)
            
            # Update player speed if speed upgrade
            self.player.speed = self.player_stats.get_speed()
            
            # Ensure input handler has latest stats
            self.input_handler.apply_survival_stats(self.player_stats)
        
        self.showing_upgrade_selection = False
        self.upgrade_options = []
    
    def update(self, dt: float):
        """Update game state."""
        # Don't update if in menu, paused, game over, or showing upgrades
        if (self.in_main_menu or self.in_character_select or self.in_game_mode_select or 
            self.game_over or self.paused or self.showing_upgrade_selection):
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
        
        # Handle XP for Survival mode
        if self.game_mode == GAME_MODE_SURVIVAL and killed:
            for _ in killed:
                if self.player_stats.add_xp(XP_PER_KILL):
                    # Level up! Show upgrade selection
                    self.upgrade_options = Upgrade.generate_three_options()
                    self.showing_upgrade_selection = True
                    # Ensure input handler has latest stats
                    self.input_handler.apply_survival_stats(self.player_stats)
                    return  # Stop updating until upgrade is selected
        
        # Check collision between enemy projectiles/spears and player
        if self.enemy_manager.check_collision(self.player.rect):
            if self.game_mode == GAME_MODE_SURVIVAL:
                # Survival mode - use hearts system
                if self.player_stats.take_damage():
                    # Player survives with hearts or extra life
                    self.enemy_manager.clear_nearby_enemies(self.player.x, self.player.y, 100)
                    self.input_handler.clear_all_projectiles()
                else:
                    # No hearts left - game over
                    self.game_over = True
                    if self.survival_time > self.best_time:
                        self.best_time = self.survival_time
            else:
                # Legacy mode - instant death
                self.game_over = True
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
        
        if self.in_game_mode_select:
            self.renderer.draw_game_mode_select(mouse_pos, self.selected_character)
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
        
        # Draw Survival mode UI (XP bar, hearts, stats)
        if self.game_mode == GAME_MODE_SURVIVAL and self.player_stats:
            self.renderer.draw_survival_ui(self.player_stats, self.player)
        
        # Draw upgrade selection screen if showing
        if self.showing_upgrade_selection:
            self.renderer.draw_upgrade_selection(mouse_pos, self.upgrade_options, self.player_stats)
        # Draw pause screen if paused
        elif self.paused:
            self.renderer.draw_pause_screen_with_stats(mouse_pos, self.show_pause_confirmation, 
                                                        self.player_stats if self.game_mode == GAME_MODE_SURVIVAL else None)
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
