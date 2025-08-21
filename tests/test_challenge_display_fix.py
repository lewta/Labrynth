"""Tests for challenge display fixes - ensuring proper SUCCESS/FAILED display."""

import pytest
from src.challenges.skill import SkillChallenge
from src.challenges.riddle import RiddleChallenge
from src.challenges.puzzle import PuzzleChallenge
from src.challenges.combat import CombatChallenge
from src.challenges.memory import MemoryChallenge
from src.utils.data_models import PlayerStats
from src.game.display import DisplayManager


class TestChallengeDisplayFix:
    """Test that challenges properly display SUCCESS/FAILED only for actual attempts."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.display_manager = DisplayManager(use_colors=False)
        self.player_stats = PlayerStats(strength=15, intelligence=15, dexterity=15, luck=15)
    
    def test_skill_challenge_examine_is_intermediate(self):
        """Test that skill challenge 'examine' action is intermediate (no SUCCESS/FAILED)."""
        challenge = SkillChallenge(difficulty=3, skill_type='strength')
        
        result = challenge.process_response("examine", self.player_stats)
        
        assert result.is_intermediate is True
        assert result.success is False
        
        # Display should not contain SUCCESS or FAILED
        display = self.display_manager.display_challenge_result(result)
        assert "SUCCESS!" not in display
        assert "FAILED!" not in display
    
    def test_skill_challenge_invalid_action_is_intermediate(self):
        """Test that skill challenge invalid actions are intermediate."""
        challenge = SkillChallenge(difficulty=3, skill_type='strength')
        
        result = challenge.process_response("invalid_action", self.player_stats)
        
        assert result.is_intermediate is True
        assert result.success is False
        
        # Display should not contain SUCCESS or FAILED
        display = self.display_manager.display_challenge_result(result)
        assert "SUCCESS!" not in display
        assert "FAILED!" not in display
    
    def test_skill_challenge_attempt_shows_result(self):
        """Test that skill challenge actual attempts show SUCCESS/FAILED."""
        challenge = SkillChallenge(difficulty=1, skill_type='strength')  # Easy challenge
        
        # Get the correct action for this challenge
        action = challenge.challenge_scenario['action']
        result = challenge.process_response(action, self.player_stats)
        
        assert result.is_intermediate is False
        
        # Display should contain either SUCCESS or FAILED
        display = self.display_manager.display_challenge_result(result)
        assert "SUCCESS!" in display or "FAILED!" in display
    
    def test_puzzle_challenge_hint_is_intermediate(self):
        """Test that puzzle challenge 'hint' action is intermediate."""
        challenge = PuzzleChallenge(difficulty=3)
        
        result = challenge.process_response("hint")
        
        assert result.is_intermediate is True
        assert result.success is False
        
        # Display should not contain SUCCESS or FAILED
        display = self.display_manager.display_challenge_result(result)
        assert "SUCCESS!" not in display
        assert "FAILED!" not in display
    
    def test_puzzle_challenge_answer_shows_result(self):
        """Test that puzzle challenge answers show SUCCESS/FAILED."""
        challenge = PuzzleChallenge(difficulty=3)
        
        result = challenge.process_response("wrong_answer")
        
        assert result.is_intermediate is False
        
        # Display should contain FAILED for wrong answer
        display = self.display_manager.display_challenge_result(result)
        assert "FAILED!" in display
    
    def test_memory_challenge_ready_is_intermediate(self):
        """Test that memory challenge 'ready' action is intermediate."""
        challenge = MemoryChallenge(difficulty=3, memory_type='sequence')
        
        result = challenge.process_response("ready")
        
        assert result.is_intermediate is True
        assert result.success is False
        
        # Display should not contain SUCCESS or FAILED
        display = self.display_manager.display_challenge_result(result)
        assert "SUCCESS!" not in display
        assert "FAILED!" not in display
    
    def test_memory_challenge_invalid_ready_is_intermediate(self):
        """Test that memory challenge invalid 'ready' responses are intermediate."""
        challenge = MemoryChallenge(difficulty=3, memory_type='sequence')
        
        result = challenge.process_response("not_ready")
        
        assert result.is_intermediate is True
        assert result.success is False
        
        # Display should not contain SUCCESS or FAILED
        display = self.display_manager.display_challenge_result(result)
        assert "SUCCESS!" not in display
        assert "FAILED!" not in display
    
    def test_combat_challenge_invalid_action_is_intermediate(self):
        """Test that combat challenge invalid actions are intermediate."""
        challenge = CombatChallenge(difficulty=3)
        
        result = challenge.process_response("examine", self.player_stats)
        
        assert result.is_intermediate is True
        assert result.success is False
        
        # Display should not contain SUCCESS or FAILED
        display = self.display_manager.display_challenge_result(result)
        assert "SUCCESS!" not in display
        assert "FAILED!" not in display
    
    def test_combat_challenge_combat_continues_is_intermediate(self):
        """Test that combat challenge 'combat continues' results are intermediate."""
        challenge = CombatChallenge(difficulty=3)
        
        result = challenge.process_response("attack", self.player_stats)
        
        # Combat continues should be intermediate (unless enemy dies immediately)
        if "Combat continues" in result.message or "defended against" in result.message:
            assert result.is_intermediate is True
            
            # Display should not contain SUCCESS or FAILED
            display = self.display_manager.display_challenge_result(result)
            assert "SUCCESS!" not in display
            assert "FAILED!" not in display
    
    def test_riddle_challenge_wrong_answer_shows_failed(self):
        """Test that riddle challenge wrong answers show FAILED."""
        challenge = RiddleChallenge(difficulty=3)
        
        result = challenge.process_response("definitely_wrong_answer")
        
        assert result.is_intermediate is False
        assert result.success is False
        
        # Display should contain FAILED
        display = self.display_manager.display_challenge_result(result)
        assert "FAILED!" in display
    
    def test_riddle_challenge_correct_answer_shows_success(self):
        """Test that riddle challenge correct answers show SUCCESS."""
        challenge = RiddleChallenge(difficulty=3)
        
        # Get the correct answer
        correct_answer = challenge.answers[0] if challenge.answers else "footsteps"
        result = challenge.process_response(correct_answer)
        
        assert result.is_intermediate is False
        assert result.success is True
        
        # Display should contain SUCCESS
        display = self.display_manager.display_challenge_result(result)
        assert "SUCCESS!" in display
    
    def test_all_challenge_types_have_proper_intermediate_flags(self):
        """Test that all challenge types properly use is_intermediate flag."""
        test_cases = [
            (SkillChallenge(difficulty=3, skill_type='strength'), "examine", True, True),  # (challenge, input, needs_stats, should_be_intermediate)
            (PuzzleChallenge(difficulty=3), "hint", False, True),
            (MemoryChallenge(difficulty=3, memory_type='sequence'), "ready", False, True),
            (CombatChallenge(difficulty=3), "invalid_action", True, True),
            (RiddleChallenge(difficulty=3), "wrong_answer", False, False)  # This should NOT be intermediate
        ]
        
        for challenge, test_input, needs_stats, should_be_intermediate in test_cases:
            if needs_stats:
                result = challenge.process_response(test_input, self.player_stats)
            else:
                result = challenge.process_response(test_input)
            
            assert result.is_intermediate == should_be_intermediate, \
                f"Challenge {type(challenge).__name__} with input '{test_input}' should {'be' if should_be_intermediate else 'not be'} intermediate"
    
    def test_display_manager_respects_intermediate_flag(self):
        """Test that DisplayManager properly handles is_intermediate flag."""
        from src.utils.data_models import ChallengeResult
        
        # Test intermediate result (should not show SUCCESS/FAILED)
        intermediate_result = ChallengeResult(
            success=False,
            message="This is an intermediate action",
            is_intermediate=True
        )
        
        display = self.display_manager.display_challenge_result(intermediate_result)
        assert "SUCCESS!" not in display
        assert "FAILED!" not in display
        assert "This is an intermediate action" in display
        
        # Test non-intermediate success result (should show SUCCESS)
        success_result = ChallengeResult(
            success=True,
            message="You succeeded!",
            is_intermediate=False
        )
        
        display = self.display_manager.display_challenge_result(success_result)
        assert "SUCCESS!" in display
        assert "You succeeded!" in display
        
        # Test non-intermediate failure result (should show FAILED)
        failure_result = ChallengeResult(
            success=False,
            message="You failed!",
            is_intermediate=False
        )
        
        display = self.display_manager.display_challenge_result(failure_result)
        assert "FAILED!" in display
        assert "You failed!" in display