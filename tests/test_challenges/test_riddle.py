"""Tests for the RiddleChallenge class."""

import pytest
from src.challenges.riddle import RiddleChallenge
from src.challenges.factory import ChallengeFactory
from src.utils.data_models import Item, ChallengeResult


class TestRiddleChallenge:
    """Test the RiddleChallenge class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.custom_riddle = RiddleChallenge(
            difficulty=3,
            riddle_text="What has four legs but cannot walk?",
            answers=["table", "chair", "desk"],
            reward_item=Item(
                name="Test Key",
                description="A test key",
                item_type="key",
                value=50
            )
        )
    
    def test_riddle_initialization_with_custom_values(self):
        """Test riddle initialization with custom values."""
        assert self.custom_riddle.difficulty == 3
        assert self.custom_riddle.riddle_text == "What has four legs but cannot walk?"
        assert set(self.custom_riddle.answers) == {"table", "chair", "desk"}
        assert self.custom_riddle.reward_item.name == "Test Key"
        assert self.custom_riddle.attempts == 0
        assert self.custom_riddle.max_attempts == 3
        assert self.custom_riddle.completed is False
    
    def test_riddle_initialization_with_defaults(self):
        """Test riddle initialization with default values."""
        default_riddle = RiddleChallenge(difficulty=5)
        
        assert default_riddle.difficulty == 5
        assert default_riddle.riddle_text is not None
        assert len(default_riddle.answers) > 0
        assert default_riddle.reward_item is not None
        assert default_riddle.attempts == 0
    
    def test_present_challenge(self):
        """Test challenge presentation."""
        presentation = self.custom_riddle.present_challenge()
        
        assert "Riddle Challenge" in presentation
        assert "Difficulty: 3/10" in presentation
        assert "What has four legs but cannot walk?" in presentation
        assert "What is your answer?" in presentation
    
    def test_present_challenge_with_attempts(self):
        """Test challenge presentation after some attempts."""
        self.custom_riddle.attempts = 1
        presentation = self.custom_riddle.present_challenge()
        
        assert "Attempts remaining: 2" in presentation
    
    def test_process_response_correct_answer(self):
        """Test processing a correct answer."""
        result = self.custom_riddle.process_response("table")
        
        assert result.success is True
        assert "Correct!" in result.message
        assert result.reward is not None
        assert result.reward.name == "Test Key"
        assert self.custom_riddle.completed is True
        assert self.custom_riddle.attempts == 1
    
    def test_process_response_correct_answer_case_insensitive(self):
        """Test that answers are case insensitive."""
        result = self.custom_riddle.process_response("TABLE")
        
        assert result.success is True
        assert self.custom_riddle.completed is True
    
    def test_process_response_correct_answer_with_whitespace(self):
        """Test that answers handle whitespace correctly."""
        result = self.custom_riddle.process_response("  chair  ")
        
        assert result.success is True
        assert self.custom_riddle.completed is True
    
    def test_process_response_incorrect_answer(self):
        """Test processing an incorrect answer."""
        result = self.custom_riddle.process_response("wrong answer")
        
        assert result.success is False
        assert "not correct" in result.message
        assert "2 attempt(s) remaining" in result.message
        assert result.reward is None
        assert self.custom_riddle.completed is False
        assert self.custom_riddle.attempts == 1
    
    def test_process_response_multiple_incorrect_answers(self):
        """Test processing multiple incorrect answers."""
        # First incorrect answer
        result1 = self.custom_riddle.process_response("wrong1")
        assert result1.success is False
        assert "2 attempt(s) remaining" in result1.message
        
        # Second incorrect answer
        result2 = self.custom_riddle.process_response("wrong2")
        assert result2.success is False
        assert "1 attempt(s) remaining" in result2.message
        
        # Third incorrect answer (final attempt)
        result3 = self.custom_riddle.process_response("wrong3")
        assert result3.success is False
        assert "run out of attempts" in result3.message
        assert "table" in result3.message  # Should show correct answer
        assert result3.damage == 5  # Should have damage penalty
    
    def test_process_response_correct_after_incorrect(self):
        """Test getting correct answer after some incorrect attempts."""
        # First incorrect answer
        self.custom_riddle.process_response("wrong")
        assert self.custom_riddle.attempts == 1
        
        # Then correct answer
        result = self.custom_riddle.process_response("table")
        assert result.success is True
        assert "second attempt" in result.message
        assert self.custom_riddle.completed is True
    
    def test_get_reward_when_completed(self):
        """Test getting reward when riddle is completed."""
        self.custom_riddle.process_response("table")  # Complete the riddle
        reward = self.custom_riddle.get_reward()
        
        assert reward is not None
        assert reward.name == "Test Key"
    
    def test_get_reward_when_not_completed(self):
        """Test getting reward when riddle is not completed."""
        reward = self.custom_riddle.get_reward()
        assert reward is None
    
    def test_reset_riddle(self):
        """Test resetting the riddle."""
        # Make some attempts and complete
        self.custom_riddle.process_response("wrong")
        self.custom_riddle.process_response("table")
        
        assert self.custom_riddle.attempts == 2
        assert self.custom_riddle.completed is True
        
        # Reset
        self.custom_riddle.reset()
        
        assert self.custom_riddle.attempts == 0
        assert self.custom_riddle.completed is False
    
    def test_add_acceptable_answer(self):
        """Test adding new acceptable answers."""
        original_count = len(self.custom_riddle.answers)
        
        self.custom_riddle.add_acceptable_answer("stool")
        
        assert len(self.custom_riddle.answers) == original_count + 1
        assert "stool" in self.custom_riddle.answers
        
        # Test that answer works
        result = self.custom_riddle.process_response("stool")
        assert result.success is True
    
    def test_add_duplicate_acceptable_answer(self):
        """Test that duplicate answers are not added."""
        original_count = len(self.custom_riddle.answers)
        
        self.custom_riddle.add_acceptable_answer("table")  # Already exists
        
        assert len(self.custom_riddle.answers) == original_count
    
    def test_get_acceptable_answers(self):
        """Test getting acceptable answers."""
        answers = self.custom_riddle.get_acceptable_answers()
        
        assert isinstance(answers, list)
        assert set(answers) == {"table", "chair", "desk"}
        
        # Ensure it's a copy (modifying returned list doesn't affect original)
        answers.append("new_answer")
        assert "new_answer" not in self.custom_riddle.answers
    
    def test_default_riddles_for_different_difficulties(self):
        """Test that different difficulties get different default riddles."""
        easy_riddle = RiddleChallenge(difficulty=1)
        hard_riddle = RiddleChallenge(difficulty=10)
        
        assert easy_riddle.riddle_text != hard_riddle.riddle_text
        assert easy_riddle.answers != hard_riddle.answers
    
    def test_success_messages_vary_by_attempts(self):
        """Test that success messages vary based on number of attempts."""
        # First try success
        riddle1 = RiddleChallenge(difficulty=1)
        result1 = riddle1.process_response("keyboard")
        assert "first try" in result1.message
        
        # Second try success
        riddle2 = RiddleChallenge(difficulty=1)
        riddle2.process_response("wrong")
        result2 = riddle2.process_response("keyboard")
        assert "second attempt" in result2.message
        
        # Third try success
        riddle3 = RiddleChallenge(difficulty=1)
        riddle3.process_response("wrong1")
        riddle3.process_response("wrong2")
        result3 = riddle3.process_response("keyboard")
        assert "persevered" in result3.message
    
    def test_factory_integration(self):
        """Test that RiddleChallenge works with ChallengeFactory."""
        # Clear and re-register to ensure clean state
        ChallengeFactory.clear_registry()
        ChallengeFactory.register_challenge_type('riddle', RiddleChallenge)
        
        challenge = ChallengeFactory.create_challenge(
            'riddle',
            difficulty=7,
            riddle_text="Test riddle?",
            answers=["test"]
        )
        
        assert isinstance(challenge, RiddleChallenge)
        assert challenge.difficulty == 7
        assert challenge.riddle_text == "Test riddle?"
        assert "test" in challenge.answers
    
    def test_reward_value_scales_with_difficulty(self):
        """Test that default reward value scales with difficulty."""
        easy_riddle = RiddleChallenge(difficulty=1)
        hard_riddle = RiddleChallenge(difficulty=10)
        
        assert easy_riddle.reward_item.value < hard_riddle.reward_item.value
        assert easy_riddle.reward_item.value == 10  # 1 * 10
        assert hard_riddle.reward_item.value == 100  # 10 * 10
    
    def test_hint_messages_provided(self):
        """Test that hint messages are provided for incorrect answers."""
        result = self.custom_riddle.process_response("wrong answer")
        
        assert result.success is False
        # Should contain some kind of hint or guidance
        assert len(result.message) > 20  # Should be more than just "incorrect"