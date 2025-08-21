"""Tests for the PuzzleChallenge class."""

import pytest
from src.challenges.puzzle import PuzzleChallenge, PuzzleType
from src.challenges.factory import ChallengeFactory
from src.utils.data_models import Item, ChallengeResult


class TestPuzzleChallenge:
    """Test the PuzzleChallenge class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sequence_puzzle = PuzzleChallenge(
            difficulty=2,
            puzzle_type=PuzzleType.SEQUENCE
        )
        
        self.logic_puzzle = PuzzleChallenge(
            difficulty=8,
            puzzle_type=PuzzleType.LOGIC_GRID
        )
    
    def test_puzzle_initialization_with_sequence_type(self):
        """Test puzzle initialization with sequence type."""
        assert self.sequence_puzzle.difficulty == 2
        assert self.sequence_puzzle.puzzle_type == PuzzleType.SEQUENCE
        assert self.sequence_puzzle.current_step == 0
        assert self.sequence_puzzle.hints_used == 0
        assert self.sequence_puzzle.max_hints == 2
        assert self.sequence_puzzle.completed is False
        assert self.sequence_puzzle.puzzle_data['type'] == 'sequence'
    
    def test_puzzle_initialization_with_logic_grid_type(self):
        """Test puzzle initialization with logic grid type."""
        assert self.logic_puzzle.difficulty == 8
        assert self.logic_puzzle.puzzle_type == PuzzleType.LOGIC_GRID
        assert self.logic_puzzle.puzzle_data['type'] == 'logic_grid'
        assert 'clues' in self.logic_puzzle.puzzle_data
        assert 'questions' in self.logic_puzzle.puzzle_data
    
    def test_puzzle_initialization_with_defaults(self):
        """Test puzzle initialization with default values."""
        default_puzzle = PuzzleChallenge(difficulty=5)
        
        assert default_puzzle.difficulty == 5
        assert default_puzzle.puzzle_type is not None
        assert default_puzzle.reward_item is not None
    
    def test_puzzle_type_selection_by_difficulty(self):
        """Test that puzzle type is selected based on difficulty."""
        easy_puzzle = PuzzleChallenge(difficulty=1)
        medium_puzzle = PuzzleChallenge(difficulty=5)
        hard_puzzle = PuzzleChallenge(difficulty=9)
        
        assert easy_puzzle.puzzle_type == PuzzleType.SEQUENCE
        assert medium_puzzle.puzzle_type == PuzzleType.PATTERN
        assert hard_puzzle.puzzle_type == PuzzleType.LOGIC_GRID
    
    def test_present_sequence_challenge(self):
        """Test presenting a sequence challenge."""
        presentation = self.sequence_puzzle.present_challenge()
        
        assert "Logic Puzzle" in presentation
        assert "Difficulty: 2/10" in presentation
        assert "Sequence" in presentation
        assert "Complete the sequence" in presentation
        assert "What number comes next?" in presentation
        assert "hint" in presentation.lower()
    
    def test_present_logic_grid_challenge(self):
        """Test presenting a logic grid challenge."""
        presentation = self.logic_puzzle.present_challenge()
        
        assert "Logic Puzzle" in presentation
        assert "Logic Grid" in presentation
        assert "Clues:" in presentation
        assert "Question 1:" in presentation
        assert len([line for line in presentation.split('\n') if line.strip().startswith(('1.', '2.', '3.', '4.'))]) > 0
    
    def test_process_sequence_correct_answer(self):
        """Test processing correct answer for sequence puzzle."""
        # The sequence puzzle should have a known answer
        correct_answer = self.sequence_puzzle.puzzle_data['answer']
        result = self.sequence_puzzle.process_response(correct_answer)
        
        assert result.success is True
        assert "Correct!" in result.message
        assert result.reward is not None
        assert self.sequence_puzzle.completed is True
    
    def test_process_sequence_incorrect_answer(self):
        """Test processing incorrect answer for sequence puzzle."""
        result = self.sequence_puzzle.process_response("wrong_answer")
        
        assert result.success is False
        assert "not correct" in result.message
        assert result.reward is None
        assert self.sequence_puzzle.completed is False
    
    def test_process_logic_grid_partial_completion(self):
        """Test processing logic grid answers step by step."""
        # Get the first correct answer
        first_answer = self.logic_puzzle.puzzle_data['answers'][0]
        result = self.logic_puzzle.process_response(first_answer)
        
        # Should be correct but not complete yet
        assert "Correct!" in result.message
        assert self.logic_puzzle.puzzle_data['current_question'] == 1
        assert self.logic_puzzle.completed is False
    
    def test_process_logic_grid_full_completion(self):
        """Test completing entire logic grid puzzle."""
        # Answer all questions correctly
        for answer in self.logic_puzzle.puzzle_data['answers']:
            result = self.logic_puzzle.process_response(answer)
        
        # Last result should indicate completion
        assert result.success is True
        assert "solved the entire" in result.message
        assert result.reward is not None
        assert self.logic_puzzle.completed is True
    
    def test_hint_system(self):
        """Test the hint system."""
        # Request first hint
        result1 = self.sequence_puzzle.process_response("hint")
        assert result1.success is False  # Hint doesn't solve puzzle
        assert "Hint:" in result1.message
        assert self.sequence_puzzle.hints_used == 1
        
        # Request second hint
        result2 = self.sequence_puzzle.process_response("hint")
        assert "Hint:" in result2.message
        assert self.sequence_puzzle.hints_used == 2
        
        # Try to request third hint (should not work)
        result3 = self.sequence_puzzle.process_response("hint")
        assert "Hint:" not in result3.message  # Should process as regular answer
    
    def test_hint_affects_presentation(self):
        """Test that hint usage affects challenge presentation."""
        initial_presentation = self.sequence_puzzle.present_challenge()
        assert "2 hint(s) remaining" in initial_presentation
        
        # Use one hint
        self.sequence_puzzle.process_response("hint")
        
        updated_presentation = self.sequence_puzzle.present_challenge()
        assert "1 hint(s) remaining" in updated_presentation
    
    def test_get_reward_when_completed(self):
        """Test getting reward when puzzle is completed."""
        # Complete the puzzle
        correct_answer = self.sequence_puzzle.puzzle_data['answer']
        self.sequence_puzzle.process_response(correct_answer)
        
        reward = self.sequence_puzzle.get_reward()
        assert reward is not None
        assert reward.value > 0
    
    def test_get_reward_when_not_completed(self):
        """Test getting reward when puzzle is not completed."""
        reward = self.sequence_puzzle.get_reward()
        assert reward is None
    
    def test_reset_puzzle(self):
        """Test resetting the puzzle."""
        # Make some progress
        self.sequence_puzzle.process_response("hint")
        self.sequence_puzzle.process_response("wrong_answer")
        
        assert self.sequence_puzzle.hints_used == 1
        
        # Reset
        self.sequence_puzzle.reset()
        
        assert self.sequence_puzzle.current_step == 0
        assert self.sequence_puzzle.hints_used == 0
        assert self.sequence_puzzle.completed is False
    
    def test_reset_logic_grid_puzzle(self):
        """Test resetting logic grid puzzle resets question progress."""
        # Answer first question
        first_answer = self.logic_puzzle.puzzle_data['answers'][0]
        self.logic_puzzle.process_response(first_answer)
        
        assert self.logic_puzzle.puzzle_data['current_question'] == 1
        
        # Reset
        self.logic_puzzle.reset()
        
        assert self.logic_puzzle.puzzle_data['current_question'] == 0
    
    def test_get_progress_information(self):
        """Test getting progress information."""
        progress = self.sequence_puzzle.get_progress()
        
        assert 'puzzle_type' in progress
        assert 'current_step' in progress
        assert 'hints_used' in progress
        assert 'completed' in progress
        assert progress['puzzle_type'] == 'sequence'
        assert progress['hints_used'] == 0
        assert progress['completed'] is False
    
    def test_get_progress_logic_grid(self):
        """Test getting progress information for logic grid."""
        progress = self.logic_puzzle.get_progress()
        
        assert 'questions_answered' in progress
        assert 'total_questions' in progress
        assert progress['questions_answered'] == 0
        assert progress['total_questions'] == len(self.logic_puzzle.puzzle_data['questions'])
    
    def test_math_puzzle_type(self):
        """Test math puzzle type functionality."""
        math_puzzle = PuzzleChallenge(difficulty=7, puzzle_type=PuzzleType.MATH_PUZZLE)
        
        assert math_puzzle.puzzle_type == PuzzleType.MATH_PUZZLE
        assert math_puzzle.puzzle_data['type'] == 'math_puzzle'
        
        presentation = math_puzzle.present_challenge()
        assert "Math Puzzle" in presentation
        assert "Your answer:" in presentation
    
    def test_pattern_puzzle_type(self):
        """Test pattern puzzle type functionality."""
        pattern_puzzle = PuzzleChallenge(difficulty=4, puzzle_type=PuzzleType.PATTERN)
        
        assert pattern_puzzle.puzzle_type == PuzzleType.PATTERN
        assert pattern_puzzle.puzzle_data['type'] == 'pattern'
        
        presentation = pattern_puzzle.present_challenge()
        assert "Pattern" in presentation
        assert "What symbol comes next?" in presentation
    
    def test_factory_integration(self):
        """Test that PuzzleChallenge works with ChallengeFactory."""
        # Clear and re-register to ensure clean state
        ChallengeFactory.clear_registry()
        ChallengeFactory.register_challenge_type('puzzle', PuzzleChallenge)
        
        challenge = ChallengeFactory.create_challenge(
            'puzzle',
            difficulty=6,
            puzzle_type=PuzzleType.SEQUENCE,
            randomize=False
        )
        
        assert isinstance(challenge, PuzzleChallenge)
        assert challenge.difficulty == 6
        assert challenge.puzzle_type == PuzzleType.SEQUENCE
    
    def test_reward_value_scales_with_difficulty(self):
        """Test that reward value scales with difficulty."""
        easy_puzzle = PuzzleChallenge(difficulty=1)
        hard_puzzle = PuzzleChallenge(difficulty=10)
        
        assert easy_puzzle.reward_item.value < hard_puzzle.reward_item.value
        assert easy_puzzle.reward_item.value == 15  # 1 * 15
        assert hard_puzzle.reward_item.value == 150  # 10 * 15
    
    def test_case_insensitive_answers(self):
        """Test that answers are processed case-insensitively."""
        correct_answer = self.sequence_puzzle.puzzle_data['answer']
        
        # Test uppercase
        result = self.sequence_puzzle.process_response(correct_answer.upper())
        assert result.success is True
    
    def test_whitespace_handling(self):
        """Test that whitespace in answers is handled correctly."""
        correct_answer = self.sequence_puzzle.puzzle_data['answer']
        
        # Test with extra whitespace
        result = self.sequence_puzzle.process_response(f"  {correct_answer}  ")
        assert result.success is True
    
    def test_different_puzzle_types_have_different_data(self):
        """Test that different puzzle types generate different data structures."""
        sequence = PuzzleChallenge(difficulty=3, puzzle_type=PuzzleType.SEQUENCE)
        logic_grid = PuzzleChallenge(difficulty=3, puzzle_type=PuzzleType.LOGIC_GRID)
        math_puzzle = PuzzleChallenge(difficulty=3, puzzle_type=PuzzleType.MATH_PUZZLE)
        pattern = PuzzleChallenge(difficulty=3, puzzle_type=PuzzleType.PATTERN)
        
        # Each should have different required fields
        assert 'sequence' in sequence.puzzle_data
        assert 'clues' in logic_grid.puzzle_data
        assert 'explanation' in math_puzzle.puzzle_data
        assert 'pattern' in pattern.puzzle_data
    
    def test_puzzle_data_consistency(self):
        """Test that puzzle data is consistent and complete."""
        puzzle = PuzzleChallenge(difficulty=5)
        
        # All puzzles should have these basic fields
        assert 'type' in puzzle.puzzle_data
        assert 'max_steps' in puzzle.puzzle_data
        assert puzzle.puzzle_data['max_steps'] > 0