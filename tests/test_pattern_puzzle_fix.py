"""Tests for pattern puzzle fix - ensuring shape names are accepted."""

import pytest
from unittest.mock import patch
from src.challenges.puzzle import PuzzleChallenge, PuzzleType


class TestPatternPuzzleFix:
    """Test that pattern puzzles accept both symbols and shape names."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock content loader to prevent randomized content from interfering
        self.content_loader_patcher = patch('src.challenges.puzzle.get_content_loader')
        mock_loader = self.content_loader_patcher.start()
        mock_loader.side_effect = Exception("No content loader")
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.content_loader_patcher.stop()
    
    def test_pattern_puzzle_accepts_symbol_answers(self):
        """Test that pattern puzzles accept exact symbol answers."""
        puzzle = PuzzleChallenge(difficulty=3, puzzle_type=PuzzleType.PATTERN)
        
        # Should be triangle, square, circle pattern with circle as answer
        assert puzzle.puzzle_data['answer'] == '○'
        
        result = puzzle.process_response('○')
        assert result.success is True
        assert "Correct!" in result.message
    
    def test_pattern_puzzle_accepts_ascii_symbol_answers(self):
        """Test that pattern puzzles accept ASCII symbol alternatives."""
        puzzle = PuzzleChallenge(difficulty=3, puzzle_type=PuzzleType.PATTERN)
        
        # Should accept 'o' as alternative to '○'
        result = puzzle.process_response('o')
        assert result.success is True
        assert "Correct!" in result.message
    
    def test_pattern_puzzle_accepts_word_answers(self):
        """Test that pattern puzzles accept word names for shapes."""
        puzzle = PuzzleChallenge(difficulty=3, puzzle_type=PuzzleType.PATTERN)
        
        # Should accept 'circle' for '○'
        result = puzzle.process_response('circle')
        assert result.success is True
        assert "Correct!" in result.message
    
    def test_pattern_puzzle_accepts_case_insensitive_words(self):
        """Test that pattern puzzles accept case-insensitive word names."""
        puzzle = PuzzleChallenge(difficulty=3, puzzle_type=PuzzleType.PATTERN)
        
        # Test various cases
        test_cases = ['circle', 'Circle', 'CIRCLE', 'CiRcLe']
        
        for word in test_cases:
            puzzle.reset()  # Reset for each test
            result = puzzle.process_response(word)
            assert result.success is True, f"Failed for word: {word}"
            assert "Correct!" in result.message
    
    def test_pattern_puzzle_rejects_wrong_answers(self):
        """Test that pattern puzzles reject incorrect answers."""
        puzzle = PuzzleChallenge(difficulty=3, puzzle_type=PuzzleType.PATTERN)
        
        # Wrong answers should be rejected
        wrong_answers = ['triangle', 'square', '△', '□', 'wrong', 'x']
        
        for answer in wrong_answers:
            result = puzzle.process_response(answer)
            assert result.success is False, f"Should have rejected: {answer}"
            assert "not correct" in result.message
    
    def test_pattern_puzzle_instructions_mention_shape_names(self):
        """Test that pattern puzzle instructions mention shape names."""
        puzzle = PuzzleChallenge(difficulty=3, puzzle_type=PuzzleType.PATTERN)
        
        presentation = puzzle.present_challenge()
        
        # Should mention that users can type shape names
        assert "shape name" in presentation.lower()
        assert "circle" in presentation.lower()
        assert "triangle" in presentation.lower()
        assert "square" in presentation.lower()
    
    def test_all_difficulty_patterns_work(self):
        """Test that all difficulty levels have working patterns."""
        for difficulty in range(1, 6):
            puzzle = PuzzleChallenge(difficulty=difficulty, puzzle_type=PuzzleType.PATTERN)
            
            # Each difficulty should have a valid pattern
            assert 'pattern' in puzzle.puzzle_data
            assert 'answer' in puzzle.puzzle_data
            assert 'rule' in puzzle.puzzle_data
            
            # Pattern should contain geometric shapes
            pattern = puzzle.puzzle_data['pattern']
            assert len(pattern) > 0
            assert '?' in pattern  # Should have placeholder
            
            # Answer should be a geometric shape
            answer = puzzle.puzzle_data['answer']
            assert answer in ['○', '△', '□']
            
            # Should accept the correct answer
            result = puzzle.process_response(answer)
            assert result.success is True
    
    def test_triangle_pattern_accepts_word_names(self):
        """Test that triangle answers work with word names."""
        puzzle = PuzzleChallenge(difficulty=1, puzzle_type=PuzzleType.PATTERN)
        
        # Difficulty 1 should have triangle as answer
        assert puzzle.puzzle_data['answer'] == '△'
        
        # Should accept both symbol and word
        puzzle_copy = PuzzleChallenge(difficulty=1, puzzle_type=PuzzleType.PATTERN)
        result1 = puzzle.process_response('△')
        result2 = puzzle_copy.process_response('triangle')
        
        assert result1.success is True
        assert result2.success is True
    
    def test_square_pattern_accepts_word_names(self):
        """Test that square answers work with word names."""
        puzzle = PuzzleChallenge(difficulty=2, puzzle_type=PuzzleType.PATTERN)
        
        # Difficulty 2 should have square as answer
        assert puzzle.puzzle_data['answer'] == '□'
        
        # Should accept both symbol and word
        puzzle_copy = PuzzleChallenge(difficulty=2, puzzle_type=PuzzleType.PATTERN)
        result1 = puzzle.process_response('□')
        result2 = puzzle_copy.process_response('square')
        
        assert result1.success is True
        assert result2.success is True
    
    def test_pattern_puzzle_error_message_mentions_shape_names(self):
        """Test that error messages mention shape names."""
        puzzle = PuzzleChallenge(difficulty=3, puzzle_type=PuzzleType.PATTERN)
        
        result = puzzle.process_response('wrong_answer')
        
        assert result.success is False
        assert "shape" in result.message.lower()
        assert "symbol" in result.message.lower()
    
    def test_pattern_puzzle_with_whitespace_handling(self):
        """Test that pattern puzzles handle whitespace in answers."""
        puzzle = PuzzleChallenge(difficulty=3, puzzle_type=PuzzleType.PATTERN)
        
        # Should handle whitespace
        test_cases = [' circle ', '  circle', 'circle  ', '\tcircle\n']
        
        for answer in test_cases:
            puzzle.reset()
            result = puzzle.process_response(answer)
            assert result.success is True, f"Failed for answer with whitespace: '{answer}'"