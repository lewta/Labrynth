"""Factory for creating different types of challenges."""

import random
from typing import Dict, Type, Optional, Any
from src.challenges.base import Challenge
from src.utils.challenge_content import get_content_loader
from src.utils.randomization import get_randomizer


class ChallengeFactory:
    """Factory class for creating different types of challenges."""
    
    # Registry of challenge types - will be populated as challenge classes are implemented
    _challenge_types: Dict[str, Type[Challenge]] = {}
    
    @classmethod
    def register_challenge_type(cls, challenge_type: str, challenge_class: Type[Challenge]) -> None:
        """Register a new challenge type.
        
        Args:
            challenge_type: String identifier for the challenge type
            challenge_class: The Challenge class to register
        """
        cls._challenge_types[challenge_type] = challenge_class
    
    @classmethod
    def create_challenge(cls, challenge_type: str, difficulty: int = 5, randomize: bool = True, **kwargs) -> Challenge:
        """Create a challenge of the specified type.
        
        Args:
            challenge_type: The type of challenge to create
            difficulty: Difficulty level (1-10)
            randomize: Whether to randomize challenge content
            **kwargs: Additional arguments specific to the challenge type
            
        Returns:
            A Challenge instance of the requested type
            
        Raises:
            ValueError: If the challenge type is not registered
        """
        if challenge_type not in cls._challenge_types:
            available_types = list(cls._challenge_types.keys())
            raise ValueError(f"Unknown challenge type '{challenge_type}'. Available types: {available_types}")
        
        challenge_class = cls._challenge_types[challenge_type]
        
        # Store original difficulty for comparison
        original_difficulty = difficulty
        
        # Add randomized content if requested
        if randomize:
            try:
                randomizer = get_randomizer()
                
                # Apply difficulty randomization only if content should be randomized
                if randomizer.should_randomize_content(challenge_type):
                    difficulty = randomizer.randomize_difficulty(difficulty, challenge_type)
                
                # Get randomized content
                randomized_kwargs = cls._get_randomized_content(challenge_type, difficulty, **kwargs)
                
                # Apply challenge variations
                variations = randomizer.get_challenge_variation(challenge_type, difficulty)
                randomized_kwargs.update(variations)
                
                kwargs.update(randomized_kwargs)
            except Exception:
                # If randomization fails, use original difficulty and continue without randomization
                difficulty = original_difficulty
        
        return challenge_class(difficulty=difficulty, **kwargs)
    
    @classmethod
    def get_available_types(cls) -> list[str]:
        """Get a list of all available challenge types.
        
        Returns:
            List of registered challenge type names
        """
        return list(cls._challenge_types.keys())
    
    @classmethod
    def clear_registry(cls) -> None:
        """Clear the challenge type registry. Mainly for testing purposes."""
        cls._challenge_types.clear()
    
    @classmethod
    def _get_randomized_content(cls, challenge_type: str, difficulty: int, **existing_kwargs) -> Dict[str, Any]:
        """Get randomized content for a challenge type.
        
        Args:
            challenge_type: Type of challenge
            difficulty: Difficulty level
            existing_kwargs: Existing keyword arguments (won't be overridden)
            
        Returns:
            Dictionary of randomized content parameters
        """
        content_loader = get_content_loader()
        randomized_content = {}
        
        try:
            if challenge_type == 'riddle' and 'riddle_text' not in existing_kwargs:
                riddle_data = content_loader.get_riddle(difficulty)
                randomized_content.update({
                    'riddle_text': riddle_data.get('riddle'),
                    'answers': riddle_data.get('answers', []),
                    'name': f"Riddle Challenge ({riddle_data.get('category', 'mystery').title()})",
                    'description': f"A {riddle_data.get('category', 'mysterious')} riddle that tests your wit"
                })
                
            elif challenge_type == 'puzzle' and 'puzzle_type' not in existing_kwargs:
                puzzle_data = content_loader.get_puzzle(difficulty)
                puzzle_type = puzzle_data.get('type', 'sequence')
                randomized_content.update({
                    'puzzle_type': puzzle_type,
                    'name': f"Logic Puzzle ({puzzle_type.replace('_', ' ').title()})",
                    'description': f"A challenging {puzzle_type.replace('_', ' ')} puzzle"
                })
                
            elif challenge_type == 'combat' and 'enemy_name' not in existing_kwargs:
                enemy_data = content_loader.get_enemy(difficulty)
                randomized_content.update({
                    'enemy_name': enemy_data.get('name'),
                    'name': f"Combat Challenge ({enemy_data.get('category', 'enemy').title()})",
                    'description': f"A dangerous {enemy_data.get('name', 'enemy')} blocks your path"
                })
                
            elif challenge_type == 'skill' and 'skill_type' not in existing_kwargs:
                skill_data = content_loader.get_skill_challenge(difficulty)
                skill_type = skill_data.get('skill_type', 'strength')
                randomized_content.update({
                    'skill_type': skill_type,
                    'name': f"Skill Challenge ({skill_type.title()})",
                    'description': f"A challenge that tests your {skill_type}"
                })
                
            elif challenge_type == 'memory' and 'memory_type' not in existing_kwargs:
                memory_data = content_loader.get_memory_challenge_config(difficulty)
                memory_type = memory_data.get('memory_type', 'sequence')
                randomized_content.update({
                    'memory_type': memory_type,
                    'name': f"Memory Challenge ({memory_type.title()})",
                    'description': f"A {memory_type} memory challenge that tests your recall"
                })
                
        except Exception:
            # If randomization fails, continue without it
            pass
        
        return randomized_content
    
    @classmethod
    def create_random_challenge(cls, difficulty: int = None, challenge_types: Optional[list] = None) -> Challenge:
        """Create a completely random challenge.
        
        Args:
            difficulty: Difficulty level (1-10). If None, will be randomized
            challenge_types: List of challenge types to choose from. If None, uses all available
            
        Returns:
            A randomly generated Challenge instance
        """
        # Randomize difficulty if not provided
        if difficulty is None:
            randomizer = get_randomizer()
            difficulty = randomizer._random.randint(1, 10)
        
        # Get available challenge types
        available_types = challenge_types or cls.get_available_types()
        if not available_types:
            raise ValueError("No challenge types are registered")
        
        # Select random challenge type
        randomizer = get_randomizer()
        challenge_type = randomizer._random.choice(available_types)
        
        # Create challenge with randomization
        challenge = cls.create_challenge(challenge_type, difficulty, randomize=True)
        
        # Track challenge creation in randomizer
        randomizer = get_randomizer()
        randomizer._session_challenges.append(challenge)
        
        return challenge
    
    @classmethod
    def create_challenge_set(cls, count: int, difficulty_range: tuple = (1, 10), 
                           challenge_types: Optional[list] = None, ensure_variety: bool = True) -> list:
        """Create a set of randomized challenges.
        
        Args:
            count: Number of challenges to create
            difficulty_range: Tuple of (min_difficulty, max_difficulty)
            challenge_types: List of challenge types to use. If None, uses all available
            ensure_variety: If True, tries to ensure different challenge types
            
        Returns:
            List of Challenge instances
        """
        challenges = []
        available_types = challenge_types or cls.get_available_types()
        
        if not available_types:
            raise ValueError("No challenge types are registered")
        
        min_diff, max_diff = difficulty_range
        
        for i in range(count):
            # Get randomizer for consistent random state
            randomizer = get_randomizer()
            
            # Select challenge type
            if ensure_variety and len(available_types) > 1:
                # Try to avoid repeating the same type consecutively
                if challenges and len(available_types) > 1:
                    last_type = type(challenges[-1]).__name__.lower().replace('challenge', '')
                    filtered_types = [t for t in available_types if t != last_type]
                    challenge_type = randomizer._random.choice(filtered_types if filtered_types else available_types)
                else:
                    challenge_type = randomizer._random.choice(available_types)
            else:
                challenge_type = randomizer._random.choice(available_types)
            
            # Randomize difficulty within range
            difficulty = randomizer._random.randint(min_diff, max_diff)
            
            # Create challenge
            challenge = cls.create_challenge(challenge_type, difficulty, randomize=True)
            challenges.append(challenge)
        
        # Ensure variety if requested
        randomizer = get_randomizer()
        if ensure_variety:
            challenges = randomizer.ensure_challenge_variety(challenges)
        
        return challenges