"""Game configuration and constants."""

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 220, 0)
LIGHT_YELLOW = (255, 255, 150)
DARK_YELLOW = (200, 180, 0)
BLUE = (100, 150, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
GRAY = (100, 100, 100)
SKIN_COLOR = (255, 220, 180)
ORANGE = (255, 165, 0)

# Player settings
PLAYER_SIZE = 40
PLAYER_SPEED = 300  # pixels per second
PLAYER_COLOR = BLUE

# Projectile settings
PROJECTILE_SIZE = 10
PROJECTILE_SPEED = 500
PROJECTILE_COLOR = RED

# Player Q skill settings
Q_SKILL_COOLDOWN = 1.3  # seconds
Q_PROJECTILE_WIDTH = 12  # thickness of the bar
Q_PROJECTILE_LENGTH = 40  # length of the bar
Q_PROJECTILE_SPEED = 600
Q_PROJECTILE_COLOR = YELLOW  # Yellow bar

# Teleport settings
TELEPORT_DISTANCE = 150
TELEPORT_COOLDOWN = 0.5  # seconds
TELEPORT_TRAIL_DURATION = 0.3  # seconds
TELEPORT_TRAIL_FADE_SPEED = 3  # fade speed multiplier

# Enemy settings
ENEMY_SIZE = 35
ENEMY_COLOR = (180, 50, 50)  # Dark red
ENEMY_OUTLINE_COLOR = (100, 30, 30)
ENEMY_SPAWN_INTERVAL = 3.0  # seconds (base, will decrease over time)
ENEMY_PROJECTILE_SIZE = 8
ENEMY_PROJECTILE_SPEED = 250
ENEMY_PROJECTILE_COLOR = (255, 50, 50)  # Bright red
ENEMY_SHOOT_INTERVAL = 2.0  # seconds between shots

# Spear enemy settings
SPEAR_ENEMY_SIZE = 38
SPEAR_ENEMY_COLOR = (100, 50, 150)  # Purple
SPEAR_ENEMY_OUTLINE_COLOR = (60, 30, 90)
SPEAR_ENEMY_SPEED = 100  # pixels per second
SPEAR_LENGTH = 50
SPEAR_ENEMY_SPAWN_INTERVAL = 5.0  # seconds (base, will decrease over time)

# Rogue enemy settings (fast, short-range knife)
ROGUE_ENEMY_SIZE = 32
ROGUE_ENEMY_COLOR = (50, 50, 50)  # Dark gray/black
ROGUE_ENEMY_OUTLINE_COLOR = (30, 30, 30)
ROGUE_ENEMY_SPEED = 180  # Faster than spear enemy (100)
ROGUE_CLOAK_COLOR = (40, 40, 60)  # Dark blue-gray cloak
KNIFE_LENGTH = 25  # Shorter than spear (50)
ROGUE_ENEMY_SPAWN_INTERVAL = 6.0  # seconds (base, will decrease over time)

# Difficulty scaling
DIFFICULTY_INCREASE_INTERVAL = 10.0  # seconds
SPAWN_RATE_MULTIPLIER = 0.85  # multiply spawn interval by this every 10 seconds

# Death effect settings
DEATH_EFFECT_DURATION = 0.4  # seconds
DEATH_EFFECT_PARTICLES = 12

# Map settings
WALL_COLOR = (60, 55, 50)
WALL_OUTLINE_COLOR = (40, 35, 30)
GRASS_COLOR = (45, 85, 45)
PATH_COLOR = (80, 75, 65)
RIVER_COLOR = (40, 80, 120)
BUSH_COLOR = (50, 100, 50)

# Zed character settings
ZED_Q_COOLDOWN = 1.5  # seconds
ZED_Q_RANGE = 350  # pixels - medium range
ZED_Q_SPEED = 550
ZED_Q_SIZE = 14

ZED_W_COOLDOWN = 8.0  # seconds
ZED_W_SHADOW_DISTANCE = 200  # pixels (about 4 blocks)
ZED_W_SHADOW_DURATION = 3.0  # seconds

ZED_E_COOLDOWN = 4.0  # seconds
ZED_E_RADIUS = 80  # Larger than spear length (50)

# Zilean character settings
ZILEAN_Q_COOLDOWN = 2.5  # seconds - bomb throw
ZILEAN_Q_DELAY = 1.5  # seconds - bomb explosion delay
ZILEAN_Q_RADIUS = 100  # explosion radius
ZILEAN_Q_DAMAGE = 1  # damage per enemy in radius

ZILEAN_E_COOLDOWN = 8.0  # seconds - time freeze
ZILEAN_E_RADIUS = 150  # freeze radius
ZILEAN_E_DURATION = 2.0  # seconds - freeze duration

# Game mode settings
GAME_MODE_LEGACY = "legacy"      # Classic survival - no upgrades, no hearts
GAME_MODE_SURVIVAL = "survival"  # Has XP, upgrades, and 3 hearts
GAME_MODE_STORY = "story"        # Story mode with stage-based challenges

# XP and leveling settings (for Survival mode)
XP_PER_KILL = 25
XP_LEVEL_BASE = 50  # XP needed for level 2 (easier)
XP_LEVEL_MULTIPLIER = 1.3  # Each level requires more XP (slower increase)

# Survival mode settings
SURVIVAL_MODE_HEARTS = 3  # Starting hearts in Survival mode

# Upgrade tier probabilities
TIER_COMMON_WEIGHT = 60
TIER_EPIC_WEIGHT = 30
TIER_LEGENDARY_WEIGHT = 10
