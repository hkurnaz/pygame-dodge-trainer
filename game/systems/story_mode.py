"""Story Mode system for stage-based challenges."""

import pygame
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW, GREEN, RED, GRAY


class StageChallenge:
    """Represents a single stage challenge."""
    
    def __init__(self, stage_id: int, name: str, description: str, 
                 target_kills: int = 0, time_limit: float = 0, 
                 survive_time: float = 0, max_deaths: int = -1):
        self.stage_id = stage_id
        self.name = name
        self.description = description
        self.target_kills = target_kills
        self.time_limit = time_limit  # Time limit in seconds (0 = no limit)
        self.survive_time = survive_time  # Must survive for this many seconds
        self.max_deaths = max_deaths  # Maximum allowed deaths (-1 = unlimited)
        
        # Runtime state
        self.kills = 0
        self.elapsed_time = 0.0
        self.deaths = 0
        self.completed = False
        self.failed = False
    
    def update(self, dt: float, kills: int = 0, deaths: int = 0):
        """Update challenge state."""
        self.elapsed_time += dt
        self.kills = kills
        self.deaths = deaths
        
        # Check failure conditions
        if self.time_limit > 0 and self.elapsed_time >= self.time_limit:
            if self.target_kills > 0 and self.kills < self.target_kills:
                self.failed = True
        
        if self.max_deaths >= 0 and self.deaths > self.max_deaths:
            self.failed = True
        
        # Check completion conditions
        if self.target_kills > 0 and self.kills >= self.target_kills:
            if self.time_limit == 0 or self.elapsed_time <= self.time_limit:
                self.completed = True
        
        if self.survive_time > 0 and self.elapsed_time >= self.survive_time:
            self.completed = True
    
    def reset(self):
        """Reset challenge state."""
        self.kills = 0
        self.elapsed_time = 0.0
        self.deaths = 0
        self.completed = False
        self.failed = False
    
    def get_status_text(self) -> str:
        """Get current status text for display."""
        lines = []
        
        # Challenge description
        lines.append(self.description)
        
        # Progress
        if self.target_kills > 0:
            lines.append(f"Kills: {self.kills}/{self.target_kills}")
        
        if self.time_limit > 0:
            remaining = max(0, self.time_limit - self.elapsed_time)
            lines.append(f"Time: {remaining:.1f}s")
        
        if self.survive_time > 0:
            remaining = max(0, self.survive_time - self.elapsed_time)
            lines.append(f"Survive: {remaining:.1f}s")
        
        return "\n".join(lines)


class StoryStage:
    """Represents a stage in the story mode."""
    
    def __init__(self, stage_id: int, name: str, x: int, y: int, 
                 challenge: StageChallenge, unlocked: bool = False, is_boss: bool = False,
                 skills_locked: bool = False):
        self.stage_id = stage_id
        self.name = name
        self.x = x  # Position on the roadmap
        self.y = y
        self.challenge = challenge
        self.unlocked = unlocked
        self.completed = False
        self.radius = 35
        self.is_boss = is_boss
        self.skills_locked = skills_locked  # If True, player cannot use skills
    
    def is_hovered(self, mouse_pos: tuple) -> bool:
        """Check if mouse is hovering over this stage."""
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        return (dx * dx + dy * dy) <= (self.radius * self.radius)
    
    def complete(self):
        """Mark stage as completed."""
        self.completed = True
        self.challenge.completed = True


class StoryMode:
    """Manages the story mode with stages and challenges."""
    
    def __init__(self):
        self.stages: list[StoryStage] = []
        self.current_stage_index = 0
        self.stage_kill_count = 0
        self.stage_start_time = 0.0
        self.stage_death_count = 0
        
        # Initialize stages
        self._create_stages()
    
    def _create_stages(self):
        """Create the story mode stages."""
        # Stage 1: Kill 5 enemies in 30 seconds
        stage1_challenge = StageChallenge(
            stage_id=1,
            name="First Blood",
            description="Kill 5 enemies in 30 seconds",
            target_kills=5,
            time_limit=30.0
        )
        
        stage1 = StoryStage(
            stage_id=1,
            name="Stage 1: First Blood",
            x=SCREEN_WIDTH // 2,
            y=200,
            challenge=stage1_challenge,
            unlocked=True  # First stage is always unlocked
        )
        
        # Stage 2: Survive for 25 seconds while enemies chase
        stage2_challenge = StageChallenge(
            stage_id=2,
            name="Hold the Line",
            description="Survive for 25 seconds",
            survive_time=25.0
        )
        
        stage2 = StoryStage(
            stage_id=2,
            name="Stage 2: Hold the Line",
            x=SCREEN_WIDTH // 2,
            y=360,
            challenge=stage2_challenge,
            unlocked=False
        )
        
        # Stage 3: Boss battle
        stage3_challenge = StageChallenge(
            stage_id=3,
            name="Doctor's Wrath",
            description="Defeat Dr. Ogre",
        )
        
        stage3 = StoryStage(
            stage_id=3,
            name="Stage 3: Doctor's Wrath",
            x=SCREEN_WIDTH // 2,
            y=420,
            challenge=stage3_challenge,
            unlocked=False,
            is_boss=True
        )
        
        # Stage 4: Movement Only Challenge
        stage4_challenge = StageChallenge(
            stage_id=4,
            name="Pure Evasion",
            description="Survive 15s using only movement",
            survive_time=15.0,
        )
        
        stage4 = StoryStage(
            stage_id=4,
            name="Stage 4: Pure Evasion",
            x=SCREEN_WIDTH // 2,
            y=520,
            challenge=stage4_challenge,
            unlocked=False,
            is_boss=False,
            skills_locked=True  # New flag to disable skills
        )
        
        self.stages.extend([stage1, stage2, stage3, stage4])
    
    def get_current_stage(self) -> StoryStage | None:
        """Get the current active stage."""
        if 0 <= self.current_stage_index < len(self.stages):
            return self.stages[self.current_stage_index]
        return None
    
    def set_stage(self, stage_index: int):
        """Set the current stage."""
        if 0 <= stage_index < len(self.stages):
            self.current_stage_index = stage_index
            self.reset_stage_progress()
    
    def reset_stage_progress(self):
        """Reset progress for the current stage."""
        self.stage_kill_count = 0
        self.stage_start_time = 0.0
        self.stage_death_count = 0
        stage = self.get_current_stage()
        if stage:
            stage.challenge.reset()
    
    def start_stage(self):
        """Start the current stage."""
        self.reset_stage_progress()
        stage = self.get_current_stage()
        if stage:
            stage.challenge.reset()
    
    def update(self, dt: float, kills: int = 0, deaths: int = 0):
        """Update the current stage challenge."""
        self.stage_kill_count = kills
        self.stage_death_count = deaths
        
        stage = self.get_current_stage()
        if stage and not stage.challenge.completed and not stage.challenge.failed:
            stage.challenge.update(dt, kills, deaths)
            
            if stage.challenge.completed:
                stage.complete()
                self.unlock_next_stage()
    
    def is_stage_complete(self) -> bool:
        """Check if current stage is complete."""
        stage = self.get_current_stage()
        if stage:
            return stage.challenge.completed
        return False
    
    def is_stage_failed(self) -> bool:
        """Check if current stage is failed."""
        stage = self.get_current_stage()
        if stage:
            return stage.challenge.failed
        return False
    
    def get_challenge_display_text(self) -> str:
        """Get text to display during gameplay."""
        stage = self.get_current_stage()
        if stage:
            return stage.challenge.get_status_text()
        return ""
    
    def get_completed_stages_count(self) -> int:
        """Get number of completed stages."""
        return sum(1 for s in self.stages if s.completed)
    
    def unlock_next_stage(self):
        """Unlock the next stage if current is completed."""
        next_index = self.current_stage_index + 1
        if next_index < len(self.stages):
            self.stages[next_index].unlocked = True
    
    def reset_all_progress(self):
        """Reset all story mode progress."""
        for i, stage in enumerate(self.stages):
            stage.completed = False
            stage.challenge.reset()
            # Only first stage is unlocked initially
            stage.unlocked = (i == 0)
        self.current_stage_index = 0
        self.reset_stage_progress()
