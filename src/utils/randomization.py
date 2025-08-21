"""Challenge randomization utilities and configuration."""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class RandomizationLevel(Enum):
    """Levels of randomization for challenges."""
    NONE = "none"           # No randomization, use fixed content
    LIGHT = "light"         # Light randomization within same difficulty
    MODERATE = "moderate"   # Moderate randomization across difficulty ranges
    HEAVY = "heavy"         # Heavy randomization with significant variation


@dataclass
class RandomizationConfig:
    """Configuration for challenge randomization."""
    level: RandomizationLevel = RandomizationLevel.MODERATE
    seed: Optional[int] = None
    challenge_variety: bool = True
    difficulty_variance: int = 1  # How much difficulty can vary (+/-)
    content_pools: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.content_pools is None:
            self.content_pools = {}


class ChallengeRandomizer:
    """Handles randomization of challenge content and parameters."""
    
    def __init__(self, config: RandomizationConfig = None):
        """Initialize the randomizer.
        
        Args:
            config: Randomization configuration
        """
        self.config = config or RandomizationConfig()
        self._session_challenges = []  # Track challenges created this session
        
        # Create a separate random instance for this randomizer
        self._random = random.Random()
        if self.config.seed is not None:
            self._random.seed(self.config.seed)
    
    def randomize_difficulty(self, base_difficulty: int, challenge_type: str = None) -> int:
        """Randomize difficulty based on configuration.
        
        Args:
            base_difficulty: Base difficulty level
            challenge_type: Type of challenge (for type-specific adjustments)
            
        Returns:
            Randomized difficulty level (1-10)
        """
        if self.config.level == RandomizationLevel.NONE:
            return base_difficulty
        
        variance = self.config.difficulty_variance
        
        if self.config.level == RandomizationLevel.LIGHT:
            variance = max(1, variance // 2)
        elif self.config.level == RandomizationLevel.HEAVY:
            variance = min(3, variance * 2)
        
        # Apply randomization
        min_diff = max(1, base_difficulty - variance)
        max_diff = min(10, base_difficulty + variance)
        
        return self._random.randint(min_diff, max_diff)
    
    def should_randomize_content(self, challenge_type: str) -> bool:
        """Determine if content should be randomized for a challenge type.
        
        Args:
            challenge_type: Type of challenge
            
        Returns:
            True if content should be randomized
        """
        if self.config.level == RandomizationLevel.NONE:
            return False
        
        # Always randomize unless explicitly disabled
        return True
    
    def get_challenge_variation(self, challenge_type: str, difficulty: int) -> Dict[str, Any]:
        """Get variation parameters for a challenge.
        
        Args:
            challenge_type: Type of challenge
            difficulty: Difficulty level
            
        Returns:
            Dictionary of variation parameters
        """
        variations = {}
        
        if self.config.level == RandomizationLevel.NONE:
            return variations
        
        # Type-specific variations
        if challenge_type == 'riddle':
            variations.update(self._get_riddle_variations(difficulty))
        elif challenge_type == 'puzzle':
            variations.update(self._get_puzzle_variations(difficulty))
        elif challenge_type == 'combat':
            variations.update(self._get_combat_variations(difficulty))
        elif challenge_type == 'skill':
            variations.update(self._get_skill_variations(difficulty))
        elif challenge_type == 'memory':
            variations.update(self._get_memory_variations(difficulty))
        
        return variations
    
    def _get_riddle_variations(self, difficulty: int) -> Dict[str, Any]:
        """Get riddle-specific variations."""
        variations = {}
        
        # Category preferences based on randomization level
        if self.config.level in [RandomizationLevel.MODERATE, RandomizationLevel.HEAVY]:
            categories = ['wordplay', 'objects', 'abstract', 'mathematical', 'ancient']
            variations['preferred_category'] = self._random.choice(categories)
        
        # Hint availability
        if self.config.level == RandomizationLevel.HEAVY:
            variations['hints_enabled'] = self._random.choice([True, False])
        
        return variations
    
    def _get_puzzle_variations(self, difficulty: int) -> Dict[str, Any]:
        """Get puzzle-specific variations."""
        variations = {}
        
        # Puzzle type preferences
        if self.config.level in [RandomizationLevel.MODERATE, RandomizationLevel.HEAVY]:
            puzzle_types = ['sequence', 'logic_grid', 'math_puzzle', 'pattern', 'mechanical']
            variations['preferred_type'] = self._random.choice(puzzle_types)
        
        # Complexity variations
        if self.config.level == RandomizationLevel.HEAVY:
            variations['complexity_modifier'] = self._random.choice([-1, 0, 1])
        
        return variations
    
    def _get_combat_variations(self, difficulty: int) -> Dict[str, Any]:
        """Get combat-specific variations."""
        variations = {}
        
        # Enemy type preferences
        if self.config.level in [RandomizationLevel.MODERATE, RandomizationLevel.HEAVY]:
            enemy_types = ['easy', 'medium', 'hard', 'boss']
            # Filter by difficulty
            if difficulty <= 3:
                enemy_types = ['easy', 'medium']
            elif difficulty <= 7:
                enemy_types = ['medium', 'hard']
            else:
                enemy_types = ['hard', 'boss']
            
            variations['preferred_enemy_type'] = self._random.choice(enemy_types)
        
        # Combat scenario variations
        if self.config.level == RandomizationLevel.HEAVY:
            variations['scenario_modifier'] = self._random.choice(['ambush', 'duel', 'guard', 'hunt'])
        
        return variations
    
    def _get_skill_variations(self, difficulty: int) -> Dict[str, Any]:
        """Get skill-specific variations."""
        variations = {}
        
        # Skill type preferences
        if self.config.level in [RandomizationLevel.MODERATE, RandomizationLevel.HEAVY]:
            skill_types = ['strength', 'intelligence', 'dexterity', 'luck']
            variations['preferred_skill'] = self._random.choice(skill_types)
        
        # Success threshold variations
        if self.config.level == RandomizationLevel.HEAVY:
            variations['threshold_modifier'] = self._random.choice([-5, 0, 5])
        
        return variations
    
    def _get_memory_variations(self, difficulty: int) -> Dict[str, Any]:
        """Get memory-specific variations."""
        variations = {}
        
        # Memory type preferences
        if self.config.level in [RandomizationLevel.MODERATE, RandomizationLevel.HEAVY]:
            memory_types = ['sequence', 'pattern']
            variations['preferred_memory_type'] = self._random.choice(memory_types)
        
        # Sequence length variations
        if self.config.level == RandomizationLevel.HEAVY:
            variations['length_modifier'] = self._random.choice([-1, 0, 1])
        
        return variations
    
    def ensure_challenge_variety(self, challenges: List[Any]) -> List[Any]:
        """Ensure variety in a list of challenges.
        
        Args:
            challenges: List of challenge instances
            
        Returns:
            Potentially reordered or modified list for better variety
        """
        if not self.config.challenge_variety or len(challenges) <= 1:
            return challenges
        
        # Track challenge types
        challenge_types = []
        for challenge in challenges:
            challenge_type = type(challenge).__name__.lower().replace('challenge', '')
            challenge_types.append(challenge_type)
        
        # If we have too many consecutive challenges of the same type, shuffle
        consecutive_count = 1
        max_consecutive = 2
        
        for i in range(1, len(challenge_types)):
            if challenge_types[i] == challenge_types[i-1]:
                consecutive_count += 1
                if consecutive_count > max_consecutive:
                    # Find a different challenge to swap with
                    for j in range(i+1, len(challenges)):
                        if challenge_types[j] != challenge_types[i]:
                            # Swap challenges
                            challenges[i], challenges[j] = challenges[j], challenges[i]
                            challenge_types[i], challenge_types[j] = challenge_types[j], challenge_types[i]
                            consecutive_count = 1
                            break
            else:
                consecutive_count = 1
        
        return challenges
    
    def get_randomization_stats(self) -> Dict[str, Any]:
        """Get statistics about randomization applied.
        
        Returns:
            Dictionary with randomization statistics
        """
        return {
            'level': self.config.level.value,
            'seed': self.config.seed,
            'challenges_created': len(self._session_challenges),
            'variety_enabled': self.config.challenge_variety,
            'difficulty_variance': self.config.difficulty_variance
        }
    
    def reset_session(self) -> None:
        """Reset session tracking."""
        self._session_challenges.clear()


# Global randomizer instance
_global_randomizer = None


def get_randomizer() -> ChallengeRandomizer:
    """Get the global randomizer instance.
    
    Returns:
        ChallengeRandomizer instance
    """
    global _global_randomizer
    if _global_randomizer is None:
        _global_randomizer = ChallengeRandomizer()
    return _global_randomizer


def set_randomization_config(config: RandomizationConfig) -> None:
    """Set the global randomization configuration.
    
    Args:
        config: New randomization configuration
    """
    global _global_randomizer
    _global_randomizer = ChallengeRandomizer(config)


def create_randomization_config(level: str = "moderate", seed: int = None, 
                              variety: bool = True, variance: int = 1) -> RandomizationConfig:
    """Create a randomization configuration.
    
    Args:
        level: Randomization level ('none', 'light', 'moderate', 'heavy')
        seed: Random seed for reproducible randomization
        variety: Whether to ensure challenge variety
        variance: Difficulty variance (+/-)
        
    Returns:
        RandomizationConfig instance
    """
    level_enum = RandomizationLevel(level.lower())
    return RandomizationConfig(
        level=level_enum,
        seed=seed,
        challenge_variety=variety,
        difficulty_variance=variance
    )