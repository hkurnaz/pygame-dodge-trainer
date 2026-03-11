"""Upgrade system for Survival game mode."""

import random
from game.config import (
    TIER_COMMON_WEIGHT, TIER_EPIC_WEIGHT, TIER_LEGENDARY_WEIGHT,
    PLAYER_SPEED, Q_SKILL_COOLDOWN, ZED_Q_COOLDOWN, ZED_W_COOLDOWN, ZED_E_COOLDOWN,
    TELEPORT_COOLDOWN, XP_LEVEL_BASE, XP_LEVEL_MULTIPLIER, SURVIVAL_MODE_HEARTS
)


class Upgrade:
    """Represents a single upgrade option."""
    
    TIER_COMMON = "common"
    TIER_EPIC = "epic"
    TIER_LEGENDARY = "legendary"
    
    # Upgrade types
    TYPE_SPEED = "speed"
    TYPE_COOLDOWN = "cooldown"
    TYPE_EXTRA_LIFE = "extra_life"
    TYPE_ATTACK_SPEED = "attack_speed"
    TYPE_ATTACK_SIZE = "attack_size"
    TYPE_DAMAGE = "damage"
    
    # Tier colors
    TIER_COLORS = {
        TIER_COMMON: (150, 150, 150),      # Gray
        TIER_EPIC: (160, 50, 200),          # Purple
        TIER_LEGENDARY: (255, 165, 0),      # Orange/Gold
    }
    
    # Upgrade definitions by tier
    UPGRADES = {
        TIER_COMMON: [
            {"type": TYPE_SPEED, "name": "Swift Feet", "description": "+5% Movement Speed", "value": 0.05},
            {"type": TYPE_COOLDOWN, "name": "Quick Hands", "description": "-3% All Cooldowns", "value": 0.03},
            {"type": TYPE_ATTACK_SPEED, "name": "Rapid Fire", "description": "-5% Q Cooldown", "value": 0.05},
            {"type": TYPE_ATTACK_SIZE, "name": "Expanding Shot", "description": "+8% Attack Size", "value": 0.08},
            {"type": TYPE_DAMAGE, "name": "Sharp Edge", "description": "+5% Damage", "value": 0.05},
        ],
        TIER_EPIC: [
            {"type": TYPE_SPEED, "name": "Wind Walker", "description": "+10% Movement Speed", "value": 0.10},
            {"type": TYPE_COOLDOWN, "name": "Master Caster", "description": "-8% All Cooldowns", "value": 0.08},
            {"type": TYPE_ATTACK_SIZE, "name": "Power Shot", "description": "+15% Attack Size", "value": 0.15},
            {"type": TYPE_ATTACK_SPEED, "name": "Haste", "description": "-10% Q Cooldown", "value": 0.10},
            {"type": TYPE_DAMAGE, "name": "Deadly Strike", "description": "+12% Damage", "value": 0.12},
        ],
        TIER_LEGENDARY: [
            {"type": TYPE_EXTRA_LIFE, "name": "Second Chance", "description": "+1 Extra Life", "value": 1},
            {"type": TYPE_SPEED, "name": "Lightning Reflexes", "description": "+20% Movement Speed", "value": 0.20},
            {"type": TYPE_COOLDOWN, "name": "Arcane Mastery", "description": "-15% All Cooldowns", "value": 0.15},
            {"type": TYPE_ATTACK_SIZE, "name": "Giant Projectile", "description": "+30% Attack Size", "value": 0.30},
            {"type": TYPE_DAMAGE, "name": "Annihilator", "description": "+25% Damage", "value": 0.25},
        ],
    }
    
    def __init__(self, tier: str, upgrade_type: str, name: str, description: str, value: float):
        self.tier = tier
        self.type = upgrade_type
        self.name = name
        self.description = description
        self.value = value
    
    @property
    def color(self) -> tuple:
        """Get the color for this upgrade's tier."""
        return self.TIER_COLORS.get(self.tier, (150, 150, 150))
    
    @classmethod
    def generate_random(cls, tier: str = None) -> 'Upgrade':
        """Generate a random upgrade, optionally specifying tier."""
        if tier is None:
            tier = cls._roll_tier()
        
        upgrades = cls.UPGRADES.get(tier, cls.UPGRADES[cls.TIER_COMMON])
        upgrade_data = random.choice(upgrades)
        
        return cls(
            tier=tier,
            upgrade_type=upgrade_data["type"],
            name=upgrade_data["name"],
            description=upgrade_data["description"],
            value=upgrade_data["value"]
        )
    
    @classmethod
    def _roll_tier(cls) -> str:
        """Roll for a random tier based on weights."""
        total_weight = TIER_COMMON_WEIGHT + TIER_EPIC_WEIGHT + TIER_LEGENDARY_WEIGHT
        roll = random.randint(1, total_weight)
        
        if roll <= TIER_LEGENDARY_WEIGHT:
            return cls.TIER_LEGENDARY
        elif roll <= TIER_LEGENDARY_WEIGHT + TIER_EPIC_WEIGHT:
            return cls.TIER_EPIC
        else:
            return cls.TIER_COMMON
    
    @classmethod
    def generate_three_options(cls) -> list:
        """Generate three upgrade options for level up."""
        # Better distribution for more interesting choices
        options = []
        
        # First slot: common or better
        roll1 = random.random()
        if roll1 < 0.15:
            tier1 = cls.TIER_EPIC
        else:
            tier1 = cls.TIER_COMMON
        options.append(cls.generate_random(tier1))
        
        # Second slot: chance for epic
        roll2 = random.random()
        if roll2 < 0.35:
            tier2 = cls.TIER_EPIC
        elif roll2 < 0.45:
            tier2 = cls.TIER_LEGENDARY
        else:
            tier2 = cls.TIER_COMMON
        options.append(cls.generate_random(tier2))
        
        # Third slot: chance for legendary
        roll3 = random.random()
        if roll3 < 0.15:
            tier3 = cls.TIER_LEGENDARY
        elif roll3 < 0.50:
            tier3 = cls.TIER_EPIC
        else:
            tier3 = cls.TIER_COMMON
        options.append(cls.generate_random(tier3))
        
        return options


class PlayerStats:
    """Tracks player stats and upgrades for Survival mode."""
    
    def __init__(self, character_type: str = "ezreal"):
        self.character_type = character_type
        
        # Base stats
        self.base_speed = PLAYER_SPEED
        self.base_q_cooldown = Q_SKILL_COOLDOWN if character_type == "ezreal" else ZED_Q_COOLDOWN
        self.base_w_cooldown = ZED_W_COOLDOWN if character_type == "zed" else 0
        self.base_e_cooldown = ZED_E_COOLDOWN if character_type == "zed" else TELEPORT_COOLDOWN
        
        # Multipliers (stack multiplicatively)
        self.speed_multiplier = 1.0
        self.cooldown_multiplier = 1.0
        self.q_cooldown_multiplier = 1.0
        self.attack_size_multiplier = 1.0
        self.damage_multiplier = 1.0
        
        # Hearts (for Survival mode)
        self.hearts = SURVIVAL_MODE_HEARTS
        self.max_hearts = SURVIVAL_MODE_HEARTS
        
        # Extra lives (from upgrades)
        self.extra_lives = 0
        
        # XP and level
        self.xp = 0
        self.level = 1
        self.xp_to_next_level = XP_LEVEL_BASE  # Use config value
        
        # Kill count
        self.kills = 0
    
    def get_speed(self) -> float:
        """Get current speed with multipliers."""
        return self.base_speed * self.speed_multiplier
    
    def get_q_cooldown(self) -> float:
        """Get Q cooldown with multipliers."""
        return self.base_q_cooldown * self.cooldown_multiplier * self.q_cooldown_multiplier
    
    def get_w_cooldown(self) -> float:
        """Get W cooldown with multipliers."""
        return self.base_w_cooldown * self.cooldown_multiplier
    
    def get_e_cooldown(self) -> float:
        """Get E cooldown with multipliers."""
        return self.base_e_cooldown * self.cooldown_multiplier
    
    def add_xp(self, amount: int) -> bool:
        """Add XP and return True if leveled up."""
        self.xp += amount
        
        if self.xp >= self.xp_to_next_level:
            self.level_up()
            return True
        return False
    
    def level_up(self):
        """Level up the player."""
        self.xp -= self.xp_to_next_level
        self.level += 1
        # XP needed increases each level
        self.xp_to_next_level = int(XP_LEVEL_BASE * (XP_LEVEL_MULTIPLIER ** (self.level - 1)))
    
    def apply_upgrade(self, upgrade: Upgrade):
        """Apply an upgrade to player stats."""
        if upgrade.type == Upgrade.TYPE_SPEED:
            self.speed_multiplier += upgrade.value
        elif upgrade.type == Upgrade.TYPE_COOLDOWN:
            self.cooldown_multiplier *= (1 - upgrade.value)
        elif upgrade.type == Upgrade.TYPE_ATTACK_SPEED:
            self.q_cooldown_multiplier *= (1 - upgrade.value)
        elif upgrade.type == Upgrade.TYPE_ATTACK_SIZE:
            self.attack_size_multiplier += upgrade.value
        elif upgrade.type == Upgrade.TYPE_DAMAGE:
            self.damage_multiplier += upgrade.value
        elif upgrade.type == Upgrade.TYPE_EXTRA_LIFE:
            self.extra_lives += int(upgrade.value)
            # Extra lives add to max hearts and current hearts
            self.max_hearts += int(upgrade.value)
            self.hearts += int(upgrade.value)
    
    def take_damage(self) -> bool:
        """Take damage. Returns True if player survives, False if game over."""
        if self.hearts > 0:
            self.hearts -= 1
            # Return True if still alive (hearts > 0), False if dead (hearts == 0)
            return self.hearts > 0
        return False
    
    def get_xp_progress(self) -> float:
        """Get XP progress as a percentage (0.0 to 1.0)."""
        return self.xp / self.xp_to_next_level if self.xp_to_next_level > 0 else 0
