"""Integration test for riddle hint functionality with display system."""

import pytest
from src.challenges.riddle import RiddleChallenge
from src.game.display import DisplayManager
from src.utils.data_models import Item, ChallengeResult


class TestRiddleHintIntegration:
    """Test that riddle hints integrate properly with the display system."""
    
    def test_hint_display_does_not_show_failed(self):
        """Test that hint requests don't show 'FAILED!' in the display output."""
        riddle = RiddleChallenge(
            difficulty=3,
            riddle_text="What has keys but no locks?",
            answers=["keyboard", "piano"],
            reward_item=Item("Test Key", "A test key", "key", 10)
        )
        
        display_manager = DisplayManager(use_colors=False)
        
        # Test hint request
        hint_result = riddle.process_response("hint")
        display_output = display_manager.display_challenge_result(hint_result)
        
        # Should not contain "FAILED!"
        assert "FAILED!" not in display_output
        
        # Should contain hint information
        assert "Hint:" in display_output
        
        # Should be a clean hint message without status prefix
        assert display_output.strip().startswith("Hint:")
    
    def test_wrong_answer_still_shows_failed_in_display(self):
        """Test that wrong answers still show 'FAILED!' in display output."""
        riddle = RiddleChallenge(
            difficulty=3,
            riddle_text="What has keys but no locks?",
            answers=["keyboard", "piano"],
            reward_item=Item("Test Key", "A test key", "key", 10)
        )
        
        display_manager = DisplayManager(use_colors=False)
        
        # Test wrong answer
        wrong_result = riddle.process_response("wrong answer")
        display_output = display_manager.display_challenge_result(wrong_result)
        
        # Should contain "FAILED!"
        assert "FAILED!" in display_output
        
        # Should contain failure message
        assert "not correct" in display_output.lower()
    
    def test_correct_answer_shows_success_in_display(self):
        """Test that correct answers show 'SUCCESS!' in display output."""
        riddle = RiddleChallenge(
            difficulty=3,
            riddle_text="What has keys but no locks?",
            answers=["keyboard", "piano"],
            reward_item=Item("Test Key", "A test key", "key", 10)
        )
        
        display_manager = DisplayManager(use_colors=False)
        
        # Test correct answer
        correct_result = riddle.process_response("keyboard")
        display_output = display_manager.display_challenge_result(correct_result)
        
        # Should contain "SUCCESS!"
        assert "SUCCESS!" in display_output
        
        # Should contain success message
        assert "Correct!" in display_output
    
    def test_multiple_hint_types_work(self):
        """Test that different hint request formats work properly."""
        riddle = RiddleChallenge(
            difficulty=3,
            riddle_text="What has keys but no locks?",
            answers=["keyboard", "piano"],
            reward_item=Item("Test Key", "A test key", "key", 10)
        )
        
        display_manager = DisplayManager(use_colors=False)
        
        hint_words = ["hint", "help", "clue", "tip", "HINT", "Help"]
        
        for hint_word in hint_words:
            # Reset riddle for each test
            riddle.reset()
            
            hint_result = riddle.process_response(hint_word)
            display_output = display_manager.display_challenge_result(hint_result)
            
            # Should not contain "FAILED!" for any hint format
            assert "FAILED!" not in display_output, f"FAILED! appeared for hint word: {hint_word}"
            
            # Should contain hint information
            assert "Hint:" in display_output, f"Hint not found for hint word: {hint_word}"
    
    def test_hint_after_wrong_answer_display(self):
        """Test display behavior when asking for hint after wrong answer."""
        riddle = RiddleChallenge(
            difficulty=3,
            riddle_text="What has keys but no locks?",
            answers=["keyboard", "piano"],
            reward_item=Item("Test Key", "A test key", "key", 10)
        )
        
        display_manager = DisplayManager(use_colors=False)
        
        # Give wrong answer first
        wrong_result = riddle.process_response("mouse")
        wrong_display = display_manager.display_challenge_result(wrong_result)
        assert "FAILED!" in wrong_display
        
        # Then ask for hint
        hint_result = riddle.process_response("hint")
        hint_display = display_manager.display_challenge_result(hint_result)
        
        # Hint should not show FAILED!
        assert "FAILED!" not in hint_display
        assert "Hint:" in hint_display