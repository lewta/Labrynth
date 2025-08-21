"""Unit tests for challenge content management."""

import pytest
import tempfile
import os
import json
from src.utils.challenge_content import ChallengeContentLoader, get_content_loader
from src.utils.exceptions import GameException


class TestChallengeContentLoader:
    """Test cases for ChallengeContentLoader class."""
    
    def test_load_content_success(self):
        """Test successful loading of challenge content."""
        loader = ChallengeContentLoader()
        
        # Should load without errors
        assert loader._content_cache is not None
        assert 'riddles' in loader._content_cache
        assert 'puzzles' in loader._content_cache
        assert 'combat' in loader._content_cache
        assert 'skills' in loader._content_cache
        assert 'memory' in loader._content_cache
    
    def test_load_content_missing_file(self):
        """Test loading with missing content file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create empty directory
            with pytest.raises(GameException, match="Challenge content file not found"):
                ChallengeContentLoader(temp_dir)
    
    def test_load_content_invalid_json(self):
        """Test loading with invalid JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid JSON file
            invalid_file = os.path.join(temp_dir, "riddles.json")
            with open(invalid_file, 'w') as f:
                f.write("invalid json content")
            
            with pytest.raises(GameException, match="Invalid JSON in challenge content file"):
                ChallengeContentLoader(temp_dir)
    
    def test_get_riddle_by_difficulty(self):
        """Test getting riddle by difficulty level."""
        loader = ChallengeContentLoader()
        
        # Get riddle with specific difficulty
        riddle = loader.get_riddle(difficulty=1)
        assert riddle is not None
        assert 'riddle' in riddle
        assert 'answers' in riddle
        assert riddle['difficulty'] == 1
    
    def test_get_riddle_by_category(self):
        """Test getting riddle by category."""
        loader = ChallengeContentLoader()
        
        # Get riddle with specific category
        riddle = loader.get_riddle(category='wordplay')
        assert riddle is not None
        assert riddle['category'] == 'wordplay'
    
    def test_get_riddle_random(self):
        """Test getting random riddle."""
        loader = ChallengeContentLoader()
        
        # Get random riddle
        riddle = loader.get_riddle()
        assert riddle is not None
        assert 'riddle' in riddle
        assert 'answers' in riddle
        assert 'difficulty' in riddle
    
    def test_get_puzzle_by_difficulty(self):
        """Test getting puzzle by difficulty level."""
        loader = ChallengeContentLoader()
        
        # Get puzzle with specific difficulty
        puzzle = loader.get_puzzle(difficulty=5)
        assert puzzle is not None
        assert puzzle['difficulty'] == 5
    
    def test_get_puzzle_by_type(self):
        """Test getting puzzle by type."""
        loader = ChallengeContentLoader()
        
        # Get sequence puzzle
        puzzle = loader.get_puzzle(puzzle_type='sequence')
        assert puzzle is not None
        assert puzzle['type'] == 'sequence'
        assert 'sequence' in puzzle
        assert 'answer' in puzzle
    
    def test_get_puzzle_random(self):
        """Test getting random puzzle."""
        loader = ChallengeContentLoader()
        
        # Get random puzzle
        puzzle = loader.get_puzzle()
        assert puzzle is not None
        assert 'type' in puzzle
        assert 'difficulty' in puzzle
    
    def test_get_enemy_by_difficulty(self):
        """Test getting enemy by difficulty level."""
        loader = ChallengeContentLoader()
        
        # Get enemy with specific difficulty
        enemy = loader.get_enemy(difficulty=5)
        assert enemy is not None
        assert enemy['difficulty'] == 5
        assert 'name' in enemy
        assert 'health' in enemy
        assert 'attack' in enemy
        assert 'defense' in enemy
    
    def test_get_enemy_by_type(self):
        """Test getting enemy by type."""
        loader = ChallengeContentLoader()
        
        # Get easy enemy
        enemy = loader.get_enemy(enemy_type='easy')
        assert enemy is not None
        assert enemy['category'] == 'easy'
        assert enemy['difficulty'] <= 3
    
    def test_get_enemy_random(self):
        """Test getting random enemy."""
        loader = ChallengeContentLoader()
        
        # Get random enemy
        enemy = loader.get_enemy()
        assert enemy is not None
        assert 'name' in enemy
        assert 'health' in enemy
        assert 'attack' in enemy
        assert 'defense' in enemy
    
    def test_get_skill_challenge_by_difficulty(self):
        """Test getting skill challenge by difficulty."""
        loader = ChallengeContentLoader()
        
        # Get skill challenge with specific difficulty
        challenge = loader.get_skill_challenge(difficulty=3)
        assert challenge is not None
        assert challenge['difficulty'] == 3
        assert 'scenario' in challenge
        assert 'action' in challenge
        assert 'skill_type' in challenge
    
    def test_get_skill_challenge_by_type(self):
        """Test getting skill challenge by skill type."""
        loader = ChallengeContentLoader()
        
        # Get strength challenge
        challenge = loader.get_skill_challenge(skill_type='strength')
        assert challenge is not None
        assert challenge['skill_type'] == 'strength'
        assert 'scenario' in challenge
        assert 'action' in challenge
    
    def test_get_skill_challenge_random(self):
        """Test getting random skill challenge."""
        loader = ChallengeContentLoader()
        
        # Get random skill challenge
        challenge = loader.get_skill_challenge()
        assert challenge is not None
        assert 'skill_type' in challenge
        assert 'scenario' in challenge
        assert 'action' in challenge
    
    def test_get_memory_challenge_config(self):
        """Test getting memory challenge configuration."""
        loader = ChallengeContentLoader()
        
        # Get memory challenge config
        config = loader.get_memory_challenge_config(difficulty=5, memory_type='sequence')
        assert config is not None
        assert config['memory_type'] == 'sequence'
        assert 'symbols' in config
        assert 'difficulty_settings' in config
    
    def test_get_memory_challenge_config_random(self):
        """Test getting random memory challenge configuration."""
        loader = ChallengeContentLoader()
        
        # Get random memory challenge config
        config = loader.get_memory_challenge_config()
        assert config is not None
        assert 'memory_type' in config
    
    def test_get_reward_for_challenge_type(self):
        """Test getting rewards for different challenge types."""
        loader = ChallengeContentLoader()
        
        # Test different challenge types
        challenge_types = ['riddle', 'puzzle', 'combat', 'skill', 'memory']
        
        for challenge_type in challenge_types:
            reward = loader.get_reward_for_challenge_type(challenge_type, difficulty=5)
            assert reward is not None
            assert 'name' in reward
            assert 'description' in reward
            assert 'value' in reward
            assert reward['value'] > 0
    
    def test_get_combat_scenario(self):
        """Test getting combat scenario."""
        loader = ChallengeContentLoader()
        
        # Get combat scenario
        scenario = loader.get_combat_scenario()
        assert scenario is not None
        assert 'type' in scenario
        assert 'description' in scenario
        assert 'initiative_bonus' in scenario
    
    def test_validate_content(self):
        """Test content validation."""
        loader = ChallengeContentLoader()
        
        # Validate content
        warnings = loader.validate_content()
        assert isinstance(warnings, list)
        # Should have no warnings with proper content
        assert len(warnings) == 0
    
    def test_get_content_stats(self):
        """Test getting content statistics."""
        loader = ChallengeContentLoader()
        
        # Get content stats
        stats = loader.get_content_stats()
        assert isinstance(stats, dict)
        assert 'riddles' in stats
        assert 'puzzles' in stats
        assert 'enemies' in stats
        assert 'skill_challenges' in stats
        assert 'memory_types' in stats
        
        # All counts should be positive
        for count in stats.values():
            assert count > 0
    
    def test_content_variety(self):
        """Test that content provides good variety."""
        loader = ChallengeContentLoader()
        
        # Test riddle variety
        riddles = [loader.get_riddle() for _ in range(10)]
        riddle_texts = [r['riddle'] for r in riddles]
        assert len(set(riddle_texts)) > 5  # Should have variety
        
        # Test puzzle variety
        puzzles = [loader.get_puzzle() for _ in range(10)]
        puzzle_types = [p['type'] for p in puzzles]
        assert len(set(puzzle_types)) > 1  # Should have different types
        
        # Test enemy variety
        enemies = [loader.get_enemy() for _ in range(10)]
        enemy_names = [e['name'] for e in enemies]
        assert len(set(enemy_names)) > 3  # Should have variety
    
    def test_difficulty_scaling(self):
        """Test that difficulty affects content appropriately."""
        loader = ChallengeContentLoader()
        
        # Test riddle difficulty scaling
        easy_riddle = loader.get_riddle(difficulty=1)
        hard_riddle = loader.get_riddle(difficulty=9)
        
        assert easy_riddle['difficulty'] < hard_riddle['difficulty']
        
        # Test enemy difficulty scaling
        easy_enemy = loader.get_enemy(difficulty=1)
        hard_enemy = loader.get_enemy(difficulty=9)
        
        assert easy_enemy['difficulty'] < hard_enemy['difficulty']
        assert easy_enemy['health'] < hard_enemy['health']
        assert easy_enemy['attack'] < hard_enemy['attack']
    
    def test_reward_value_scaling(self):
        """Test that reward values scale with difficulty."""
        loader = ChallengeContentLoader()
        
        # Test reward scaling
        easy_reward = loader.get_reward_for_challenge_type('riddle', difficulty=1)
        hard_reward = loader.get_reward_for_challenge_type('riddle', difficulty=10)
        
        assert easy_reward['value'] < hard_reward['value']


class TestGlobalContentLoader:
    """Test cases for global content loader function."""
    
    def test_get_content_loader_singleton(self):
        """Test that get_content_loader returns singleton instance."""
        loader1 = get_content_loader()
        loader2 = get_content_loader()
        
        # Should be the same instance
        assert loader1 is loader2
    
    def test_get_content_loader_functionality(self):
        """Test that global content loader works correctly."""
        loader = get_content_loader()
        
        # Should be able to get content
        riddle = loader.get_riddle()
        assert riddle is not None
        
        puzzle = loader.get_puzzle()
        assert puzzle is not None
        
        enemy = loader.get_enemy()
        assert enemy is not None


class TestContentIntegration:
    """Integration tests for challenge content system."""
    
    def test_all_challenge_types_have_content(self):
        """Test that all challenge types have sufficient content."""
        loader = ChallengeContentLoader()
        
        # Test each challenge type
        challenge_types = ['riddle', 'puzzle', 'combat', 'skill', 'memory']
        
        for challenge_type in challenge_types:
            if challenge_type == 'riddle':
                content = loader.get_riddle()
            elif challenge_type == 'puzzle':
                content = loader.get_puzzle()
            elif challenge_type == 'combat':
                content = loader.get_enemy()
            elif challenge_type == 'skill':
                content = loader.get_skill_challenge()
            elif challenge_type == 'memory':
                content = loader.get_memory_challenge_config()
            
            assert content is not None, f"No content available for {challenge_type}"
    
    def test_difficulty_range_coverage(self):
        """Test that content covers the full difficulty range."""
        loader = ChallengeContentLoader()
        
        # Test difficulty range 1-10 for different content types
        for difficulty in range(1, 11):
            # Should be able to get content for each difficulty
            riddle = loader.get_riddle(difficulty=difficulty)
            enemy = loader.get_enemy(difficulty=difficulty)
            
            # May not have exact difficulty matches, but should get something
            assert riddle is not None
            assert enemy is not None
    
    def test_content_completeness(self):
        """Test that content has all required fields."""
        loader = ChallengeContentLoader()
        
        # Test riddle completeness
        riddle = loader.get_riddle()
        required_riddle_fields = ['riddle', 'answers', 'difficulty']
        for field in required_riddle_fields:
            assert field in riddle, f"Riddle missing required field: {field}"
        
        # Test enemy completeness
        enemy = loader.get_enemy()
        required_enemy_fields = ['name', 'health', 'attack', 'defense', 'difficulty']
        for field in required_enemy_fields:
            assert field in enemy, f"Enemy missing required field: {field}"
        
        # Test skill challenge completeness
        skill = loader.get_skill_challenge()
        required_skill_fields = ['scenario', 'action', 'difficulty', 'skill_type']
        for field in required_skill_fields:
            assert field in skill, f"Skill challenge missing required field: {field}"
    
    def test_content_balance(self):
        """Test that content provides balanced gameplay."""
        loader = ChallengeContentLoader()
        
        # Test that we have content across all skill types
        skill_types = ['strength', 'intelligence', 'dexterity', 'luck']
        for skill_type in skill_types:
            challenge = loader.get_skill_challenge(skill_type=skill_type)
            assert challenge is not None
            assert challenge['skill_type'] == skill_type
        
        # Test that we have different puzzle types
        puzzle_types = ['sequence', 'logic_grid', 'math_puzzle', 'pattern']
        found_types = set()
        
        for _ in range(20):  # Try multiple times to find different types
            puzzle = loader.get_puzzle()
            found_types.add(puzzle['type'])
        
        assert len(found_types) > 1, "Should have multiple puzzle types available"