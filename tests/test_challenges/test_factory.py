"""Tests for the ChallengeFactory."""

import pytest
from src.challenges.factory import ChallengeFactory
from src.challenges.base import Challenge
from src.utils.data_models import Item, ChallengeResult


class MockChallenge(Challenge):
    """Mock challenge class for testing the factory."""
    
    def __init__(self, difficulty: int = 5, name: str = "Mock Challenge", **kwargs):
        super().__init__(name, "A mock challenge for testing", difficulty)
        self.extra_args = kwargs
    
    def present_challenge(self) -> str:
        return f"Mock challenge with difficulty {self.difficulty}"
    
    def process_response(self, response: str) -> ChallengeResult:
        return ChallengeResult(
            success=True,
            message="Mock response processed"
        )
    
    def get_reward(self) -> Item:
        return Item(
            name="Mock Reward",
            description="A mock reward",
            item_type="test",
            value=1
        )


class AnotherMockChallenge(Challenge):
    """Another mock challenge class for testing multiple registrations."""
    
    def __init__(self, difficulty: int = 5, special_param: str = "default", **kwargs):
        super().__init__("Another Mock", "Another mock challenge", difficulty)
        self.special_param = special_param
    
    def present_challenge(self) -> str:
        return f"Another mock challenge: {self.special_param}"
    
    def process_response(self, response: str) -> ChallengeResult:
        return ChallengeResult(success=False, message="Always fails")
    
    def get_reward(self) -> Item:
        return None


class TestChallengeFactory:
    """Test the ChallengeFactory class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Store original registry state
        self._original_types = ChallengeFactory._challenge_types.copy()
        # Clear registry before each test to ensure clean state
        ChallengeFactory.clear_registry()
    
    def teardown_method(self):
        """Clean up after each test."""
        # Restore original registry state
        ChallengeFactory._challenge_types = self._original_types
    
    def test_register_challenge_type(self):
        """Test registering a new challenge type."""
        ChallengeFactory.register_challenge_type("mock", MockChallenge)
        available_types = ChallengeFactory.get_available_types()
        assert "mock" in available_types
    
    def test_register_multiple_challenge_types(self):
        """Test registering multiple challenge types."""
        ChallengeFactory.register_challenge_type("mock", MockChallenge)
        ChallengeFactory.register_challenge_type("another", AnotherMockChallenge)
        
        available_types = ChallengeFactory.get_available_types()
        assert "mock" in available_types
        assert "another" in available_types
        assert len(available_types) == 2
    
    def test_create_challenge_success(self):
        """Test successful challenge creation."""
        ChallengeFactory.register_challenge_type("mock", MockChallenge)
        
        challenge = ChallengeFactory.create_challenge("mock", difficulty=7, randomize=False)
        
        assert isinstance(challenge, MockChallenge)
        assert challenge.difficulty == 7
        assert challenge.name == "Mock Challenge"
    
    def test_create_challenge_with_kwargs(self):
        """Test challenge creation with additional keyword arguments."""
        ChallengeFactory.register_challenge_type("another", AnotherMockChallenge)
        
        challenge = ChallengeFactory.create_challenge(
            "another", 
            difficulty=3, 
            special_param="custom_value",
            randomize=False
        )
        
        assert isinstance(challenge, AnotherMockChallenge)
        assert challenge.difficulty == 3
        assert challenge.special_param == "custom_value"
    
    def test_create_challenge_default_difficulty(self):
        """Test challenge creation with default difficulty."""
        ChallengeFactory.register_challenge_type("mock", MockChallenge)
        
        challenge = ChallengeFactory.create_challenge("mock", randomize=False)
        
        assert challenge.difficulty == 5  # Default difficulty
    
    def test_create_challenge_unknown_type(self):
        """Test creating a challenge with unknown type raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ChallengeFactory.create_challenge("unknown_type")
        
        assert "Unknown challenge type 'unknown_type'" in str(exc_info.value)
        assert "Available types: []" in str(exc_info.value)
    
    def test_create_challenge_unknown_type_with_registered_types(self):
        """Test error message includes available types when some are registered."""
        ChallengeFactory.register_challenge_type("mock", MockChallenge)
        
        with pytest.raises(ValueError) as exc_info:
            ChallengeFactory.create_challenge("unknown_type")
        
        assert "Unknown challenge type 'unknown_type'" in str(exc_info.value)
        assert "Available types: ['mock']" in str(exc_info.value)
    
    def test_get_available_types_empty(self):
        """Test getting available types when none are registered."""
        available_types = ChallengeFactory.get_available_types()
        assert available_types == []
    
    def test_get_available_types_with_registrations(self):
        """Test getting available types with registered challenges."""
        ChallengeFactory.register_challenge_type("mock", MockChallenge)
        ChallengeFactory.register_challenge_type("another", AnotherMockChallenge)
        
        available_types = ChallengeFactory.get_available_types()
        assert set(available_types) == {"mock", "another"}
    
    def test_clear_registry(self):
        """Test clearing the challenge registry."""
        ChallengeFactory.register_challenge_type("mock", MockChallenge)
        assert len(ChallengeFactory.get_available_types()) == 1
        
        ChallengeFactory.clear_registry()
        assert len(ChallengeFactory.get_available_types()) == 0
    
    def test_registry_persistence_across_instances(self):
        """Test that registry is shared across factory instances."""
        # The factory uses class methods, so this tests the class-level registry
        ChallengeFactory.register_challenge_type("mock", MockChallenge)
        
        # Create challenge using class method (disable randomization for predictable results)
        challenge1 = ChallengeFactory.create_challenge("mock", randomize=False)
        
        # Registry should still be available
        available_types = ChallengeFactory.get_available_types()
        assert "mock" in available_types
        
        # Should be able to create another challenge
        challenge2 = ChallengeFactory.create_challenge("mock", difficulty=8, randomize=False)
        
        assert isinstance(challenge1, MockChallenge)
        assert isinstance(challenge2, MockChallenge)
        assert challenge1.difficulty == 5  # Default
        assert challenge2.difficulty == 8  # Custom
    
    def test_overwrite_challenge_type(self):
        """Test that registering the same type twice overwrites the previous registration."""
        ChallengeFactory.register_challenge_type("test", MockChallenge)
        ChallengeFactory.register_challenge_type("test", AnotherMockChallenge)
        
        challenge = ChallengeFactory.create_challenge("test")
        assert isinstance(challenge, AnotherMockChallenge)
        assert not isinstance(challenge, MockChallenge)