"""Challenge content management and loading utilities."""

import json
import os
import random
from typing import Dict, List, Any, Optional
from src.utils.exceptions import GameException


class ChallengeContentLoader:
    """Loads and manages challenge content from configuration files."""
    
    def __init__(self, content_dir: str = "config/challenges"):
        """Initialize the content loader.
        
        Args:
            content_dir: Directory containing challenge content files
        """
        self.content_dir = content_dir
        self._content_cache = {}
        self._load_all_content()
    
    def _load_all_content(self) -> None:
        """Load all challenge content files into cache."""
        content_files = {
            'riddles': 'riddles.json',
            'puzzles': 'puzzles.json',
            'combat': 'combat.json',
            'skills': 'skills.json',
            'memory': 'memory.json'
        }
        
        for content_type, filename in content_files.items():
            file_path = os.path.join(self.content_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self._content_cache[content_type] = json.load(f)
            except FileNotFoundError:
                raise GameException(f"Challenge content file not found: {file_path}")
            except json.JSONDecodeError as e:
                raise GameException(f"Invalid JSON in challenge content file {file_path}: {e}")
    
    def get_riddle(self, difficulty: int = None, category: str = None) -> Dict[str, Any]:
        """Get a riddle based on difficulty and category.
        
        Args:
            difficulty: Desired difficulty level (1-10)
            category: Desired category (optional)
            
        Returns:
            Dictionary containing riddle data
        """
        riddles_data = self._content_cache.get('riddles', {}).get('riddles', {})
        
        # Collect all riddles that match criteria
        matching_riddles = []
        
        for difficulty_group, riddles in riddles_data.items():
            for riddle in riddles:
                # Check difficulty match
                if difficulty is not None and riddle.get('difficulty') != difficulty:
                    continue
                
                # Check category match
                if category is not None and riddle.get('category') != category:
                    continue
                
                matching_riddles.append(riddle)
        
        if not matching_riddles:
            # Fallback to any riddle if no matches
            all_riddles = []
            for riddles in riddles_data.values():
                all_riddles.extend(riddles)
            
            if not all_riddles:
                raise GameException("No riddles available in content database")
            
            matching_riddles = all_riddles
        
        return random.choice(matching_riddles)
    
    def get_puzzle(self, difficulty: int = None, puzzle_type: str = None) -> Dict[str, Any]:
        """Get a puzzle based on difficulty and type.
        
        Args:
            difficulty: Desired difficulty level (1-10)
            puzzle_type: Type of puzzle ('sequence', 'logic_grid', 'math_puzzle', 'pattern', 'mechanical')
            
        Returns:
            Dictionary containing puzzle data
        """
        puzzles_data = self._content_cache.get('puzzles', {}).get('puzzles', {})
        
        # If specific type requested, get from that category
        if puzzle_type and puzzle_type in puzzles_data:
            puzzles = puzzles_data[puzzle_type]
            
            if difficulty is not None:
                # Filter by difficulty
                matching_puzzles = [p for p in puzzles if p.get('difficulty') == difficulty]
                if matching_puzzles:
                    puzzle = random.choice(matching_puzzles)
                    puzzle['type'] = puzzle_type
                    return puzzle
            
            # Return random puzzle from the type
            puzzle = random.choice(puzzles)
            puzzle['type'] = puzzle_type
            return puzzle
        
        # Collect all puzzles that match difficulty
        matching_puzzles = []
        
        for puzzle_category, puzzles in puzzles_data.items():
            for puzzle in puzzles:
                if difficulty is None or puzzle.get('difficulty') == difficulty:
                    puzzle_copy = puzzle.copy()
                    puzzle_copy['type'] = puzzle_category
                    matching_puzzles.append(puzzle_copy)
        
        if not matching_puzzles:
            # Fallback to any puzzle
            all_puzzles = []
            for puzzle_category, puzzles in puzzles_data.items():
                for puzzle in puzzles:
                    puzzle_copy = puzzle.copy()
                    puzzle_copy['type'] = puzzle_category
                    all_puzzles.append(puzzle_copy)
            
            if not all_puzzles:
                raise GameException("No puzzles available in content database")
            
            matching_puzzles = all_puzzles
        
        return random.choice(matching_puzzles)
    
    def get_enemy(self, difficulty: int = None, enemy_type: str = None) -> Dict[str, Any]:
        """Get an enemy based on difficulty and type.
        
        Args:
            difficulty: Desired difficulty level (1-10)
            enemy_type: Type of enemy ('easy', 'medium', 'hard', 'boss')
            
        Returns:
            Dictionary containing enemy data
        """
        enemies_data = self._content_cache.get('combat', {}).get('enemies', {})
        
        # If specific type requested, get from that category
        if enemy_type and enemy_type in enemies_data:
            enemies = enemies_data[enemy_type]
            
            if difficulty is not None:
                # Filter by difficulty
                matching_enemies = [e for e in enemies if e.get('difficulty') == difficulty]
                if matching_enemies:
                    enemy = random.choice(matching_enemies)
                    enemy['category'] = enemy_type
                    return enemy
            
            # Return random enemy from the type
            enemy = random.choice(enemies)
            enemy['category'] = enemy_type
            return enemy
        
        # Collect all enemies that match difficulty
        matching_enemies = []
        
        for enemy_category, enemies in enemies_data.items():
            for enemy in enemies:
                if difficulty is None or enemy.get('difficulty') == difficulty:
                    enemy_copy = enemy.copy()
                    enemy_copy['category'] = enemy_category
                    matching_enemies.append(enemy_copy)
        
        if not matching_enemies:
            # Fallback to any enemy
            all_enemies = []
            for enemy_category, enemies in enemies_data.items():
                for enemy in enemies:
                    enemy_copy = enemy.copy()
                    enemy_copy['category'] = enemy_category
                    all_enemies.append(enemy_copy)
            
            if not all_enemies:
                raise GameException("No enemies available in content database")
            
            matching_enemies = all_enemies
        
        return random.choice(matching_enemies)
    
    def get_skill_challenge(self, difficulty: int = None, skill_type: str = None) -> Dict[str, Any]:
        """Get a skill challenge based on difficulty and skill type.
        
        Args:
            difficulty: Desired difficulty level (1-10)
            skill_type: Type of skill ('strength', 'intelligence', 'dexterity', 'luck')
            
        Returns:
            Dictionary containing skill challenge data
        """
        skills_data = self._content_cache.get('skills', {}).get('skill_challenges', {})
        
        # If specific skill type requested, get from that category
        if skill_type and skill_type in skills_data:
            challenges = skills_data[skill_type]
            
            if difficulty is not None:
                # Filter by difficulty
                matching_challenges = [c for c in challenges if c.get('difficulty') == difficulty]
                if matching_challenges:
                    challenge = random.choice(matching_challenges)
                    challenge['skill_type'] = skill_type
                    return challenge
            
            # Return random challenge from the skill type
            challenge = random.choice(challenges)
            challenge['skill_type'] = skill_type
            return challenge
        
        # Collect all challenges that match difficulty
        matching_challenges = []
        
        for skill_category, challenges in skills_data.items():
            for challenge in challenges:
                if difficulty is None or challenge.get('difficulty') == difficulty:
                    challenge_copy = challenge.copy()
                    challenge_copy['skill_type'] = skill_category
                    matching_challenges.append(challenge_copy)
        
        if not matching_challenges:
            # Fallback to any challenge
            all_challenges = []
            for skill_category, challenges in skills_data.items():
                for challenge in challenges:
                    challenge_copy = challenge.copy()
                    challenge_copy['skill_type'] = skill_category
                    all_challenges.append(challenge_copy)
            
            if not all_challenges:
                raise GameException("No skill challenges available in content database")
            
            matching_challenges = all_challenges
        
        return random.choice(matching_challenges)
    
    def get_memory_challenge_config(self, difficulty: int = None, memory_type: str = None) -> Dict[str, Any]:
        """Get memory challenge configuration.
        
        Args:
            difficulty: Desired difficulty level (1-10)
            memory_type: Type of memory challenge ('sequence', 'pattern')
            
        Returns:
            Dictionary containing memory challenge configuration
        """
        memory_data = self._content_cache.get('memory', {}).get('memory_challenges', {})
        
        # Default to sequence if no type specified
        if memory_type is None:
            memory_type = random.choice(['sequence', 'pattern'])
        
        if memory_type not in memory_data:
            memory_type = 'sequence'  # Fallback
        
        config = memory_data[memory_type].copy()
        
        # Add difficulty-specific settings
        if difficulty is not None:
            difficulty_settings = config.get('difficulty_settings', {})
            if str(difficulty) in difficulty_settings:
                config.update(difficulty_settings[str(difficulty)])
        
        # Add a random scenario
        scenarios = self._content_cache.get('memory', {}).get('memory_challenges', {}).get('scenarios', [])
        if scenarios:
            config['scenario'] = random.choice(scenarios)
        
        config['memory_type'] = memory_type
        return config
    
    def get_reward_for_challenge_type(self, challenge_type: str, difficulty: int = 5) -> Dict[str, Any]:
        """Get an appropriate reward for a challenge type.
        
        Args:
            challenge_type: Type of challenge ('riddle', 'puzzle', 'combat', 'skill', 'memory')
            difficulty: Difficulty level for value scaling
            
        Returns:
            Dictionary containing reward data
        """
        if challenge_type == 'combat':
            enemy_data = self.get_enemy(difficulty)
            loot = enemy_data.get('loot', [])
            if loot:
                reward_name = random.choice(loot)
                return {
                    'name': reward_name,
                    'description': f"A {reward_name.lower()} taken from a defeated enemy",
                    'item_type': 'weapon' if 'weapon' in reward_name.lower() or 'sword' in reward_name.lower() or 'axe' in reward_name.lower() else 'treasure',
                    'value': difficulty * 15
                }
        
        elif challenge_type == 'skill':
            skills_data = self._content_cache.get('skills', {}).get('skill_rewards', {})
            skill_type = random.choice(['strength', 'intelligence', 'dexterity', 'luck'])
            
            if skill_type in skills_data:
                rewards = skills_data[skill_type]
                reward = random.choice(rewards)
                reward['value'] = reward.get('value', 40) + (difficulty * 5)
                return reward
        
        elif challenge_type == 'memory':
            memory_rewards = self._content_cache.get('memory', {}).get('memory_rewards', [])
            if memory_rewards:
                reward = random.choice(memory_rewards)
                reward['value'] = reward.get('value', 40) + (difficulty * 5)
                return reward
        
        # Default rewards for riddle and puzzle
        default_rewards = [
            {'name': 'Ancient Key', 'description': 'A key to unlock hidden secrets', 'item_type': 'key', 'value': difficulty * 10},
            {'name': 'Wisdom Scroll', 'description': 'A scroll containing ancient knowledge', 'item_type': 'scroll', 'value': difficulty * 12},
            {'name': 'Crystal Shard', 'description': 'A magical crystal fragment', 'item_type': 'crystal', 'value': difficulty * 8},
            {'name': 'Golden Coin', 'description': 'A valuable gold coin', 'item_type': 'treasure', 'value': difficulty * 15},
            {'name': 'Magic Rune', 'description': 'A rune inscribed with magical power', 'item_type': 'rune', 'value': difficulty * 11}
        ]
        
        return random.choice(default_rewards)
    
    def get_combat_scenario(self) -> Dict[str, Any]:
        """Get a random combat scenario.
        
        Returns:
            Dictionary containing combat scenario data
        """
        scenarios = self._content_cache.get('combat', {}).get('combat_scenarios', [])
        
        if not scenarios:
            # Default scenario
            return {
                'type': 'guard',
                'description': '{enemy_name} blocks your path forward.',
                'initiative_bonus': 0
            }
        
        return random.choice(scenarios)
    
    def validate_content(self) -> List[str]:
        """Validate all loaded content for completeness and correctness.
        
        Returns:
            List of validation warnings/errors
        """
        warnings = []
        
        # Check riddles
        riddles_data = self._content_cache.get('riddles', {}).get('riddles', {})
        if not riddles_data:
            warnings.append("No riddles found in content database")
        else:
            for category, riddles in riddles_data.items():
                for i, riddle in enumerate(riddles):
                    if not riddle.get('riddle'):
                        warnings.append(f"Riddle {i} in category {category} missing riddle text")
                    if not riddle.get('answers'):
                        warnings.append(f"Riddle {i} in category {category} missing answers")
        
        # Check puzzles
        puzzles_data = self._content_cache.get('puzzles', {}).get('puzzles', {})
        if not puzzles_data:
            warnings.append("No puzzles found in content database")
        
        # Check combat
        enemies_data = self._content_cache.get('combat', {}).get('enemies', {})
        if not enemies_data:
            warnings.append("No enemies found in content database")
        
        # Check skills
        skills_data = self._content_cache.get('skills', {}).get('skill_challenges', {})
        if not skills_data:
            warnings.append("No skill challenges found in content database")
        
        # Check memory
        memory_data = self._content_cache.get('memory', {}).get('memory_challenges', {})
        if not memory_data:
            warnings.append("No memory challenges found in content database")
        
        return warnings
    
    def get_content_stats(self) -> Dict[str, int]:
        """Get statistics about loaded content.
        
        Returns:
            Dictionary with content counts
        """
        stats = {}
        
        # Count riddles
        riddles_data = self._content_cache.get('riddles', {}).get('riddles', {})
        riddle_count = sum(len(riddles) for riddles in riddles_data.values())
        stats['riddles'] = riddle_count
        
        # Count puzzles
        puzzles_data = self._content_cache.get('puzzles', {}).get('puzzles', {})
        puzzle_count = sum(len(puzzles) for puzzles in puzzles_data.values())
        stats['puzzles'] = puzzle_count
        
        # Count enemies
        enemies_data = self._content_cache.get('combat', {}).get('enemies', {})
        enemy_count = sum(len(enemies) for enemies in enemies_data.values())
        stats['enemies'] = enemy_count
        
        # Count skill challenges
        skills_data = self._content_cache.get('skills', {}).get('skill_challenges', {})
        skill_count = sum(len(challenges) for challenges in skills_data.values())
        stats['skill_challenges'] = skill_count
        
        # Count memory challenge types
        memory_data = self._content_cache.get('memory', {}).get('memory_challenges', {})
        stats['memory_types'] = len(memory_data)
        
        return stats
    
    def get_challenge_content(self, challenge_type: str) -> List[Dict[str, Any]]:
        """Get all content for a specific challenge type.
        
        Args:
            challenge_type: Type of challenge ('riddle', 'puzzle', 'combat', 'skill', 'memory')
            
        Returns:
            List of challenge content dictionaries
        """
        if challenge_type == 'riddle':
            riddles_data = self._content_cache.get('riddles', {}).get('riddles', {})
            all_riddles = []
            for category, riddles in riddles_data.items():
                if isinstance(riddles, list):
                    all_riddles.extend(riddles)
            return all_riddles
        
        elif challenge_type == 'puzzle':
            puzzles_data = self._content_cache.get('puzzles', {}).get('puzzles', {})
            all_puzzles = []
            for puzzle_type, puzzles in puzzles_data.items():
                if isinstance(puzzles, list):
                    all_puzzles.extend(puzzles)
            return all_puzzles
        
        elif challenge_type == 'combat':
            combat_data = self._content_cache.get('combat', {})
            all_combat = []
            
            # Handle enemies (dict structure)
            enemies_data = combat_data.get('enemies', {})
            for category, enemies in enemies_data.items():
                if isinstance(enemies, list):
                    all_combat.extend(enemies)
            
            # Handle scenarios (list structure)
            scenarios = combat_data.get('combat_scenarios', [])
            if isinstance(scenarios, list):
                all_combat.extend(scenarios)
            
            return all_combat
        
        elif challenge_type == 'skill':
            skills_data = self._content_cache.get('skills', {}).get('skill_challenges', {})
            all_skills = []
            for skill_type, challenges in skills_data.items():
                if isinstance(challenges, list):
                    all_skills.extend(challenges)
            return all_skills
        
        elif challenge_type == 'memory':
            memory_data = self._content_cache.get('memory', {}).get('memory_challenges', {})
            all_memory = []
            for memory_type, challenges in memory_data.items():
                if isinstance(challenges, list):
                    all_memory.extend(challenges)
            return all_memory
        
        else:
            return []


# Global content loader instance
_content_loader = None


def get_content_loader() -> ChallengeContentLoader:
    """Get the global content loader instance.
    
    Returns:
        ChallengeContentLoader instance
    """
    global _content_loader
    if _content_loader is None:
        _content_loader = ChallengeContentLoader()
    return _content_loader