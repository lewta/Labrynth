"""Tests for the Challenge abstract base class."""

import pytest
from abc import ABC
from src.challenges.base import Challenge
from src.utils.data_models import Item, ChallengeResult


class TestChallengeABC:
    """Test the Challenge abstract base class."""
    
    def test_challenge_is_abstract(self):
        """Test that Challenge cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Challenge("test", "test description", 5)
    
    def test_challenge_abstract_methods(self):
        """Test that Challenge has the required abstract methods."""
        abstract_methods = Challenge.__abstractmethods__
        expected_methods = {'present_challenge', 'process_response', 'get_reward'}
        assert abstract_methods == expected_methods


class ConcreteChallenge(Challenge):
    """Concrete implementation of Challenge for testing."""
    
    def __init__(self, name: str, description: str, difficulty: int):
        super().__init__(name, description, difficulty)
        self.reward_item = Item(
            name="Test Reward",
            description="A test reward item",
            item_type="key",
            value=10
        )
    
    def present_challenge(self) -> str:
        return f"Test challenge: {self.description}"
    
    def process_response(self, response: str) -> ChallengeResult:
        success = response.lower() == "correct"
        return ChallengeResult(
            success=success,
            message="Correct!" if success else "Incorrect!",
            reward=self.reward_item if success else None
        )
    
    def get_reward(self) -> Item:
        return self.reward_item


class TestConcreteChallenge:
    """Test the concrete Challenge implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.challenge = ConcreteChallenge(
            name="Test Challenge",
            description="A test challenge for unit testing",
            difficulty=5
        )
    
    def test_challenge_initialization(self):
        """Test challenge initialization."""
        assert self.challenge.name == "Test Challenge"
        assert self.challenge.description == "A test challenge for unit testing"
        assert self.challenge.difficulty == 5
        assert self.challenge.completed is False
    
    def test_present_challenge(self):
        """Test challenge presentation."""
        result = self.challenge.present_challenge()
        assert "Test challenge: A test challenge for unit testing" in result
    
    def test_process_response_success(self):
        """Test successful response processing."""
        result = self.challenge.process_response("correct")
        assert result.success is True
        assert result.message == "Correct!"
        assert result.reward is not None
        assert result.reward.name == "Test Reward"
    
    def test_process_response_failure(self):
        """Test failed response processing."""
        result = self.challenge.process_response("wrong")
        assert result.success is False
        assert result.message == "Incorrect!"
        assert result.reward is None
    
    def test_process_response_case_insensitive(self):
        """Test that response processing is case insensitive."""
        result = self.challenge.process_response("CORRECT")
        assert result.success is True
    
    def test_get_reward(self):
        """Test reward retrieval."""
        reward = self.challenge.get_reward()
        assert reward.name == "Test Reward"
        assert reward.item_type == "key"
        assert reward.value == 10
    
    def test_mark_completed(self):
        """Test marking challenge as completed."""
        assert self.challenge.completed is False
        self.challenge.mark_completed()
        assert self.challenge.completed is True
    
    def test_difficulty_range(self):
        """Test challenges with different difficulty levels."""
        easy_challenge = ConcreteChallenge("Easy", "Easy test", 1)
        hard_challenge = ConcreteChallenge("Hard", "Hard test", 10)
        
        assert easy_challenge.difficulty == 1
        assert hard_challenge.difficulty == 10