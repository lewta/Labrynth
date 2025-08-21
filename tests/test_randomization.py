"""Tests for challenge randomization system."""

import pytest
import random
from unittest.mock import patch, MagicMock

from src.utils.randomization import (
    ChallengeRandomizer, RandomizationConfig, RandomizationLevel,
    get_randomizer, set_randomization_config, create_randomization_config
)
from src.challenges.factory import ChallengeFactory
from src.challenges.base import Challenge


class MockChallenge(Challenge):
    """Mock challenge for testing."""
    
    def __init__(self, name="Mock", description="Test", difficulty=5):
        super().__init__(name, description, difficulty)
    
    def present_challenge(self):
        return "Mock challenge"
    
    def process_response(self, response):
        from src.utils.data_models import ChallengeResult
        return ChallengeResult(success=True, message="Mock success")
    
    def get_reward(self):
        return None


class TestRandomizationConfig:
    """Test randomization configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = RandomizationConfig()
        
        assert config.level == RandomizationLevel.MODERATE
        assert config.seed is None
        assert config.challenge_variety is True
        assert config.difficulty_variance == 1
        assert config.content_pools == {}
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = RandomizationConfig(
            level=RandomizationLevel.HEAVY,
            seed=12345,
            challenge_variety=False,
            difficulty_variance=2
        )
        
        assert config.level == RandomizationLevel.HEAVY
        assert config.seed == 12345
        assert config.challenge_variety is False
        assert config.difficulty_variance == 2
    
    def test_seed_setting(self):
        """Test that seed is stored in config."""
        config = RandomizationConfig(seed=42)
        assert config.seed == 42


class TestChallengeRandomizer:
    """Test challenge randomizer functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RandomizationConfig(level=RandomizationLevel.MODERATE, seed=42)
        self.randomizer = ChallengeRandomizer(self.config)
    
    def test_initialization(self):
        """Test randomizer initialization."""
        assert self.randomizer.config == self.config
        assert self.randomizer._session_challenges == []
    
    def test_randomize_difficulty_none_level(self):
        """Test difficulty randomization with NONE level."""
        config = RandomizationConfig(level=RandomizationLevel.NONE)
        randomizer = ChallengeRandomizer(config)
        
        # Should return original difficulty
        assert randomizer.randomize_difficulty(5) == 5
        assert randomizer.randomize_difficulty(1) == 1
        assert randomizer.randomize_difficulty(10) == 10
    
    def test_randomize_difficulty_light_level(self):
        """Test difficulty randomization with LIGHT level."""
        config = RandomizationConfig(level=RandomizationLevel.LIGHT, difficulty_variance=2, seed=42)
        randomizer = ChallengeRandomizer(config)
        
        # Should have minimal variance
        results = [randomizer.randomize_difficulty(5) for _ in range(10)]
        
        # All results should be within reasonable range
        assert all(3 <= r <= 7 for r in results)
        # Should have some variation
        assert len(set(results)) > 1
    
    def test_randomize_difficulty_heavy_level(self):
        """Test difficulty randomization with HEAVY level."""
        config = RandomizationConfig(level=RandomizationLevel.HEAVY, difficulty_variance=1, seed=42)
        randomizer = ChallengeRandomizer(config)
        
        # Should have more variance
        results = [randomizer.randomize_difficulty(5) for _ in range(20)]
        
        # Should have good variation
        assert len(set(results)) > 3
        # Should stay within bounds
        assert all(1 <= r <= 10 for r in results)
    
    def test_randomize_difficulty_bounds(self):
        """Test difficulty randomization respects bounds."""
        config = RandomizationConfig(level=RandomizationLevel.HEAVY, difficulty_variance=5, seed=42)
        randomizer = ChallengeRandomizer(config)
        
        # Test lower bound
        results = [randomizer.randomize_difficulty(1) for _ in range(10)]
        assert all(r >= 1 for r in results)
        
        # Test upper bound
        results = [randomizer.randomize_difficulty(10) for _ in range(10)]
        assert all(r <= 10 for r in results)
    
    def test_should_randomize_content(self):
        """Test content randomization decision."""
        # NONE level should not randomize
        config = RandomizationConfig(level=RandomizationLevel.NONE)
        randomizer = ChallengeRandomizer(config)
        assert not randomizer.should_randomize_content('riddle')
        
        # Other levels should randomize
        config = RandomizationConfig(level=RandomizationLevel.MODERATE)
        randomizer = ChallengeRandomizer(config)
        assert randomizer.should_randomize_content('riddle')
    
    def test_get_challenge_variation_riddle(self):
        """Test riddle challenge variations."""
        variations = self.randomizer.get_challenge_variation('riddle', 5)
        
        # Should have some variation parameters
        assert isinstance(variations, dict)
        # Moderate level should include category preferences
        if 'preferred_category' in variations:
            assert variations['preferred_category'] in ['wordplay', 'objects', 'abstract', 'mathematical', 'ancient']
    
    def test_get_challenge_variation_combat(self):
        """Test combat challenge variations."""
        variations = self.randomizer.get_challenge_variation('combat', 5)
        
        assert isinstance(variations, dict)
        # Should have enemy type preferences for moderate level
        if 'preferred_enemy_type' in variations:
            assert variations['preferred_enemy_type'] in ['easy', 'medium', 'hard', 'boss']
    
    def test_ensure_challenge_variety(self):
        """Test challenge variety enforcement."""
        # Create mock challenges of same type
        challenges = [MockChallenge(f"Challenge {i}") for i in range(5)]
        
        # Should return same challenges if variety disabled
        config = RandomizationConfig(challenge_variety=False)
        randomizer = ChallengeRandomizer(config)
        result = randomizer.ensure_challenge_variety(challenges)
        assert result == challenges
        
        # Should potentially reorder if variety enabled
        config = RandomizationConfig(challenge_variety=True)
        randomizer = ChallengeRandomizer(config)
        result = randomizer.ensure_challenge_variety(challenges)
        assert len(result) == len(challenges)
        assert set(result) == set(challenges)
    
    def test_get_randomization_stats(self):
        """Test randomization statistics."""
        stats = self.randomizer.get_randomization_stats()
        
        assert 'level' in stats
        assert 'seed' in stats
        assert 'challenges_created' in stats
        assert 'variety_enabled' in stats
        assert 'difficulty_variance' in stats
        
        assert stats['level'] == 'moderate'
        assert stats['seed'] == 42
        assert stats['challenges_created'] == 0
        assert stats['variety_enabled'] is True
        assert stats['difficulty_variance'] == 1
    
    def test_reset_session(self):
        """Test session reset."""
        # Add some mock challenges
        self.randomizer._session_challenges = [MockChallenge(), MockChallenge()]
        
        self.randomizer.reset_session()
        assert self.randomizer._session_challenges == []


class TestRandomizationIntegration:
    """Test integration with challenge factory."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Register mock challenge type
        ChallengeFactory.register_challenge_type('mock', MockChallenge)
        
        # Set up randomization
        config = RandomizationConfig(level=RandomizationLevel.MODERATE, seed=42)
        set_randomization_config(config)
    
    def teardown_method(self):
        """Clean up after tests."""
        ChallengeFactory.clear_registry()
    
    @patch('src.utils.challenge_content.get_content_loader')
    def test_factory_randomization(self, mock_content_loader):
        """Test factory integration with randomization."""
        # Mock content loader
        mock_loader = MagicMock()
        mock_content_loader.return_value = mock_loader
        
        # Create challenge with randomization
        challenge = ChallengeFactory.create_challenge('mock', difficulty=5, randomize=True)
        
        assert isinstance(challenge, MockChallenge)
        # Difficulty might be randomized
        assert 1 <= challenge.difficulty <= 10
    
    @patch('src.utils.challenge_content.get_content_loader')
    def test_factory_no_randomization(self, mock_content_loader):
        """Test factory without randomization."""
        challenge = ChallengeFactory.create_challenge('mock', difficulty=5, randomize=False)
        
        assert isinstance(challenge, MockChallenge)
        assert challenge.difficulty == 5
    
    @patch('src.utils.challenge_content.get_content_loader')
    def test_create_random_challenge(self, mock_content_loader):
        """Test creating completely random challenge."""
        # Mock content loader
        mock_loader = MagicMock()
        mock_content_loader.return_value = mock_loader
        
        challenge = ChallengeFactory.create_random_challenge()
        
        assert isinstance(challenge, MockChallenge)
        assert 1 <= challenge.difficulty <= 10
    
    @patch('src.utils.challenge_content.get_content_loader')
    def test_create_challenge_set(self, mock_content_loader):
        """Test creating set of challenges."""
        # Mock content loader
        mock_loader = MagicMock()
        mock_content_loader.return_value = mock_loader
        
        challenges = ChallengeFactory.create_challenge_set(
            count=3,
            difficulty_range=(3, 7),
            challenge_types=['mock']
        )
        
        assert len(challenges) == 3
        assert all(isinstance(c, MockChallenge) for c in challenges)
        assert all(3 <= c.difficulty <= 7 for c in challenges)


class TestRandomizationUtilities:
    """Test utility functions."""
    
    def test_create_randomization_config(self):
        """Test config creation utility."""
        config = create_randomization_config(
            level='heavy',
            seed=123,
            variety=False,
            variance=3
        )
        
        assert config.level == RandomizationLevel.HEAVY
        assert config.seed == 123
        assert config.challenge_variety is False
        assert config.difficulty_variance == 3
    
    def test_global_randomizer(self):
        """Test global randomizer management."""
        # Get default randomizer
        randomizer1 = get_randomizer()
        assert isinstance(randomizer1, ChallengeRandomizer)
        
        # Should return same instance
        randomizer2 = get_randomizer()
        assert randomizer1 is randomizer2
        
        # Set new config
        config = RandomizationConfig(level=RandomizationLevel.HEAVY)
        set_randomization_config(config)
        
        # Should get new randomizer
        randomizer3 = get_randomizer()
        assert randomizer3 is not randomizer1
        assert randomizer3.config.level == RandomizationLevel.HEAVY


class TestRandomizationLevels:
    """Test different randomization levels."""
    
    @pytest.mark.parametrize("level", [
        RandomizationLevel.NONE,
        RandomizationLevel.LIGHT,
        RandomizationLevel.MODERATE,
        RandomizationLevel.HEAVY
    ])
    def test_all_randomization_levels(self, level):
        """Test all randomization levels work."""
        config = RandomizationConfig(level=level, seed=42)
        randomizer = ChallengeRandomizer(config)
        
        # Should not raise exceptions
        difficulty = randomizer.randomize_difficulty(5)
        assert 1 <= difficulty <= 10
        
        should_randomize = randomizer.should_randomize_content('riddle')
        assert isinstance(should_randomize, bool)
        
        variations = randomizer.get_challenge_variation('riddle', 5)
        assert isinstance(variations, dict)
    
    def test_randomization_consistency_with_seed(self):
        """Test that same seed produces consistent results."""
        config1 = RandomizationConfig(level=RandomizationLevel.MODERATE, seed=12345)
        randomizer1 = ChallengeRandomizer(config1)
        
        config2 = RandomizationConfig(level=RandomizationLevel.MODERATE, seed=12345)
        randomizer2 = ChallengeRandomizer(config2)
        
        # Should produce same results with same seed
        results1 = [randomizer1.randomize_difficulty(5) for _ in range(10)]
        results2 = [randomizer2.randomize_difficulty(5) for _ in range(10)]
        
        assert results1 == results2