"""Test for riddle hint functionality fix."""

import pytest
from src.challenges.riddle import RiddleChallenge
from src.utils.data_models import Item


class TestRiddleHintFix:
    """Test that riddle challenges handle hint requests properly."""
    
    def test_hint_request_does_not_show_failed(self):
        """Test that asking for a hint doesn't show 'FAILED!' message."""
        riddle = RiddleChallenge(
            difficulty=3,
            riddle_text="What has keys but no locks?",
            answers=["keyboard", "piano"],
            reward_item=Item("Test Key", "A test key", "key", 10)
        )
        
        # Test various hint request formats
        hint_requests = ["hint", "help", "clue", "tip", "HINT", "Help", "CLUE"]
        
        for hint_request in hint_requests:
            result = riddle.process_response(hint_request)
            
            # Should not be successful (it's not the answer)
            assert not result.success
            
            # Should be marked as intermediate to prevent "FAILED!" display
            assert result.is_intermediate
            
            # Should contain hint information
            assert "hint" in result.message.lower() or "think" in result.message.lower()
            
            # Should not increment attempts counter
            assert riddle.attempts == 0
    
    def test_wrong_answer_still_shows_failed(self):
        """Test that wrong answers still show failure properly."""
        riddle = RiddleChallenge(
            difficulty=3,
            riddle_text="What has keys but no locks?",
            answers=["keyboard", "piano"],
            reward_item=Item("Test Key", "A test key", "key", 10)
        )
        
        result = riddle.process_response("wrong answer")
        
        # Should not be successful
        assert not result.success
        
        # Should NOT be marked as intermediate (so "FAILED!" will show)
        assert not result.is_intermediate
        
        # Should increment attempts counter
        assert riddle.attempts == 1
        
        # Should contain failure message
        assert "not correct" in result.message.lower()
    
    def test_correct_answer_after_hint(self):
        """Test that correct answers work normally after asking for hints."""
        riddle = RiddleChallenge(
            difficulty=3,
            riddle_text="What has keys but no locks?",
            answers=["keyboard", "piano"],
            reward_item=Item("Test Key", "A test key", "key", 10)
        )
        
        # Ask for hint first
        hint_result = riddle.process_response("hint")
        assert hint_result.is_intermediate
        assert riddle.attempts == 0
        
        # Then give correct answer
        correct_result = riddle.process_response("keyboard")
        assert correct_result.success
        assert not correct_result.is_intermediate
        assert riddle.attempts == 1
        assert riddle.completed
    
    def test_hint_after_wrong_answer(self):
        """Test that hints work after giving wrong answers."""
        riddle = RiddleChallenge(
            difficulty=3,
            riddle_text="What has keys but no locks?",
            answers=["keyboard", "piano"],
            reward_item=Item("Test Key", "A test key", "key", 10)
        )
        
        # Give wrong answer first
        wrong_result = riddle.process_response("mouse")
        assert not wrong_result.success
        assert not wrong_result.is_intermediate
        assert riddle.attempts == 1
        
        # Then ask for hint
        hint_result = riddle.process_response("hint")
        assert not hint_result.success
        assert hint_result.is_intermediate
        assert riddle.attempts == 1  # Should not increment for hint
    
    def test_multiple_hints_allowed(self):
        """Test that multiple hint requests are allowed."""
        riddle = RiddleChallenge(
            difficulty=3,
            riddle_text="What has keys but no locks?",
            answers=["keyboard", "piano"],
            reward_item=Item("Test Key", "A test key", "key", 10)
        )
        
        # Ask for multiple hints
        for _ in range(3):
            hint_result = riddle.process_response("hint")
            assert hint_result.is_intermediate
            assert riddle.attempts == 0
        
        # Should still be able to answer correctly
        correct_result = riddle.process_response("keyboard")
        assert correct_result.success
        assert riddle.attempts == 1
    
    def test_hint_message_content(self):
        """Test that hint messages contain helpful information."""
        riddle = RiddleChallenge(
            difficulty=1,  # Use difficulty 1 for predictable hint
            riddle_text="What has keys but no locks, space but no room?",
            answers=["keyboard"],
            reward_item=Item("Test Key", "A test key", "key", 10)
        )
        
        hint_result = riddle.process_response("hint")
        
        # Should contain "Hint:" prefix
        assert hint_result.message.startswith("Hint:")
        
        # Should contain some helpful text
        assert len(hint_result.message) > 10
        
        # Should not reveal the answer directly
        assert "keyboard" not in hint_result.message.lower()