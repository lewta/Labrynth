"""Puzzle challenge implementation."""

from typing import Dict, List, Optional, Any
from enum import Enum
from src.challenges.base import Challenge
from src.utils.data_models import Item, ChallengeResult
from src.utils.challenge_content import get_content_loader


class PuzzleType(Enum):
    """Types of logic puzzles available."""
    SEQUENCE = "sequence"
    LOGIC_GRID = "logic_grid"
    MATH_PUZZLE = "math_puzzle"
    PATTERN = "pattern"


class PuzzleChallenge(Challenge):
    """An interactive logic puzzle challenge with step-by-step solving."""
    
    def __init__(self, difficulty: int = 5, puzzle_type: PuzzleType = None,
                 reward_item: Item = None, **kwargs):
        """Initialize a puzzle challenge.
        
        Args:
            difficulty: Difficulty level (1-10)
            puzzle_type: Type of puzzle to generate
            reward_item: Item to give as reward for solving the puzzle
            **kwargs: Additional arguments
        """
        name = kwargs.get('name', 'Logic Puzzle')
        description = kwargs.get('description', 'A challenging logic puzzle that tests your reasoning')
        
        super().__init__(name, description, difficulty)
        
        # Set puzzle type
        if isinstance(puzzle_type, str):
            # Convert string to enum
            try:
                self.puzzle_type = PuzzleType(puzzle_type)
            except ValueError:
                self.puzzle_type = self._select_puzzle_type()
        else:
            self.puzzle_type = puzzle_type or self._select_puzzle_type()
        
        # Initialize puzzle state
        self.puzzle_data = self._generate_puzzle()
        self.current_step = 0
        self.max_steps = self.puzzle_data.get('max_steps', 3)
        self.player_progress = {}
        self.hints_used = 0
        self.max_hints = 2
        
        # Try to get randomized content if available
        self._apply_randomized_content()
        
        # Set reward
        self.reward_item = reward_item or self._get_default_reward()
    
    def _select_puzzle_type(self) -> PuzzleType:
        """Select puzzle type based on difficulty."""
        if self.difficulty <= 3:
            return PuzzleType.SEQUENCE
        elif self.difficulty <= 6:
            return PuzzleType.PATTERN
        elif self.difficulty <= 8:
            return PuzzleType.MATH_PUZZLE
        else:
            return PuzzleType.LOGIC_GRID
    
    def _generate_puzzle(self) -> Dict[str, Any]:
        """Generate puzzle data based on type and difficulty."""
        generators = {
            PuzzleType.SEQUENCE: self._generate_sequence_puzzle,
            PuzzleType.LOGIC_GRID: self._generate_logic_grid_puzzle,
            PuzzleType.MATH_PUZZLE: self._generate_math_puzzle,
            PuzzleType.PATTERN: self._generate_pattern_puzzle
        }
        
        return generators[self.puzzle_type]()
    
    def _apply_randomized_content(self) -> None:
        """Apply randomized content from content loader if available."""
        try:
            content_loader = get_content_loader()
            
            if self.puzzle_type == PuzzleType.SEQUENCE:
                # Try to get a randomized sequence puzzle
                puzzle_data = content_loader.get_puzzle(self.difficulty, 'sequence')
                if puzzle_data and puzzle_data.get('type') == 'sequence':
                    self.puzzle_data.update({
                        'sequence': puzzle_data.get('sequence', self.puzzle_data['sequence']),
                        'answer': puzzle_data.get('answer', self.puzzle_data['answer']),
                        'rule': puzzle_data.get('rule', self.puzzle_data['rule']),
                        'description': puzzle_data.get('description', self.puzzle_data['description'])
                    })
            
            elif self.puzzle_type == PuzzleType.LOGIC_GRID:
                # Try to get a randomized logic grid puzzle
                puzzle_data = content_loader.get_puzzle(self.difficulty, 'logic_grid')
                if puzzle_data and puzzle_data.get('type') == 'logic_grid':
                    self.puzzle_data.update({
                        'description': puzzle_data.get('description', self.puzzle_data['description']),
                        'clues': puzzle_data.get('clues', self.puzzle_data['clues']),
                        'questions': puzzle_data.get('questions', self.puzzle_data['questions']),
                        'answers': puzzle_data.get('answers', self.puzzle_data['answers'])
                    })
            
            elif self.puzzle_type == PuzzleType.MATH_PUZZLE:
                # Try to get a randomized math puzzle
                puzzle_data = content_loader.get_puzzle(self.difficulty, 'math_puzzle')
                if puzzle_data and puzzle_data.get('type') == 'math_puzzle':
                    self.puzzle_data.update({
                        'description': puzzle_data.get('description', self.puzzle_data['description']),
                        'answer': puzzle_data.get('answer', self.puzzle_data['answer']),
                        'explanation': puzzle_data.get('explanation', self.puzzle_data.get('explanation', ''))
                    })
            
            elif self.puzzle_type == PuzzleType.PATTERN:
                # Try to get a randomized pattern puzzle
                puzzle_data = content_loader.get_puzzle(self.difficulty, 'pattern')
                if puzzle_data and puzzle_data.get('type') == 'pattern':
                    self.puzzle_data.update({
                        'description': puzzle_data.get('description', self.puzzle_data['description']),
                        'pattern': puzzle_data.get('pattern', self.puzzle_data['pattern']),
                        'answer': puzzle_data.get('answer', self.puzzle_data['answer']),
                        'rule': puzzle_data.get('rule', self.puzzle_data['rule'])
                    })
                    
        except Exception:
            # If randomization fails, keep the default generated puzzle
            pass
    
    def _generate_sequence_puzzle(self) -> Dict[str, Any]:
        """Generate a number sequence puzzle."""
        sequences = {
            1: {"sequence": [2, 4, 6, 8, "?"], "answer": "10", "rule": "even numbers"},
            2: {"sequence": [1, 4, 9, 16, "?"], "answer": "25", "rule": "perfect squares"},
            3: {"sequence": [1, 1, 2, 3, 5, "?"], "answer": "8", "rule": "Fibonacci sequence"},
            4: {"sequence": [2, 6, 12, 20, "?"], "answer": "30", "rule": "n(n+1)"},
            5: {"sequence": [1, 4, 7, 10, "?"], "answer": "13", "rule": "add 3 each time"}
        }
        
        difficulty_key = min(max(self.difficulty, 1), 5)
        base_puzzle = sequences[difficulty_key]
        
        return {
            "type": "sequence",
            "sequence": base_puzzle["sequence"],
            "answer": base_puzzle["answer"],
            "rule": base_puzzle["rule"],
            "max_steps": 1,
            "description": f"Complete the sequence: {', '.join(map(str, base_puzzle['sequence']))}"
        }
    
    def _generate_logic_grid_puzzle(self) -> Dict[str, Any]:
        """Generate a logic grid puzzle."""
        return {
            "type": "logic_grid",
            "description": "Three friends (Alice, Bob, Carol) have different pets (cat, dog, bird) and live in different colored houses (red, blue, green).",
            "clues": [
                "Alice doesn't live in the red house",
                "The person with the cat lives in the blue house",
                "Bob has the dog",
                "Carol doesn't live in the green house"
            ],
            "questions": [
                "Who lives in the red house?",
                "What pet does Alice have?",
                "What color house does Bob live in?"
            ],
            "answers": ["Carol", "bird", "green"],
            "max_steps": 3,
            "current_question": 0
        }
    
    def _generate_math_puzzle(self) -> Dict[str, Any]:
        """Generate a math-based logic puzzle."""
        puzzles = {
            6: {
                "description": "If 2 cats catch 2 mice in 2 minutes, how many cats are needed to catch 100 mice in 50 minutes?",
                "answer": "4",
                "explanation": "Rate is 1 cat per 1 mouse per 2 minutes. In 50 minutes, 1 cat catches 25 mice. So 4 cats catch 100 mice."
            },
            7: {
                "description": "A farmer has chickens and rabbits. There are 35 heads and 94 feet total. How many chickens are there?",
                "answer": "23",
                "explanation": "Let c=chickens, r=rabbits. c+r=35, 2c+4r=94. Solving: r=12, c=23."
            },
            8: {
                "description": "In a race, you overtake the person in 2nd place. What position are you in now?",
                "answer": "2nd",
                "explanation": "If you overtake the person in 2nd place, you take their position."
            }
        }
        
        difficulty_key = min(max(self.difficulty, 6), 8)
        puzzle = puzzles.get(difficulty_key, puzzles[6])
        
        return {
            "type": "math_puzzle",
            "description": puzzle["description"],
            "answer": puzzle["answer"],
            "explanation": puzzle["explanation"],
            "max_steps": 1
        }
    
    def _generate_pattern_puzzle(self) -> Dict[str, Any]:
        """Generate a pattern recognition puzzle."""
        # Create different patterns based on difficulty
        patterns = {
            1: {
                "pattern": ["○", "○", "△", "○", "○", "?"],
                "answer": "△",
                "rule": "alternating pattern: two circles, one triangle"
            },
            2: {
                "pattern": ["△", "□", "△", "□", "△", "?"],
                "answer": "□",
                "rule": "alternating triangle and square"
            },
            3: {
                "pattern": ["△", "□", "○", "△", "□", "?"],
                "answer": "○",
                "rule": "repeating sequence of triangle, square, circle"
            },
            4: {
                "pattern": ["○", "△", "△", "○", "△", "?"],
                "answer": "△",
                "rule": "pattern: circle, two triangles, repeat"
            },
            5: {
                "pattern": ["□", "○", "△", "□", "○", "?"],
                "answer": "△",
                "rule": "repeating sequence of square, circle, triangle"
            }
        }
        
        # Select pattern based on difficulty, default to medium if out of range
        difficulty_key = min(max(self.difficulty, 1), 5)
        if difficulty_key not in patterns:
            difficulty_key = 3
        
        selected_pattern = patterns[difficulty_key]
        
        return {
            "type": "pattern",
            "description": "Look at this pattern and find what comes next:",
            "pattern": selected_pattern["pattern"],
            "answer": selected_pattern["answer"],
            "rule": selected_pattern["rule"],
            "max_steps": 1
        }
    
    def _get_default_reward(self) -> Item:
        """Get a default reward item."""
        reward_names = [
            "Logic Crystal", "Puzzle Box", "Mind Gem", "Wisdom Stone",
            "Clever Key", "Brain Teaser", "Smart Token", "Riddle Rune"
        ]
        
        reward_name = reward_names[self.difficulty % len(reward_names)]
        
        return Item(
            name=reward_name,
            description=f"A valuable {reward_name.lower()} earned by solving a challenging puzzle",
            item_type="treasure",
            value=self.difficulty * 15  # Slightly higher value than riddles
        )
    
    def present_challenge(self) -> str:
        """Present the current step of the puzzle to the player."""
        presentation = f"\n=== {self.name} ===\n"
        presentation += f"Difficulty: {self.difficulty}/10\n"
        presentation += f"Puzzle Type: {self.puzzle_type.value.replace('_', ' ').title()}\n\n"
        
        if self.puzzle_type == PuzzleType.SEQUENCE:
            presentation += f"{self.puzzle_data['description']}\n\n"
            presentation += "What number comes next? "
            
        elif self.puzzle_type == PuzzleType.LOGIC_GRID:
            presentation += f"{self.puzzle_data['description']}\n\n"
            presentation += "Clues:\n"
            for i, clue in enumerate(self.puzzle_data['clues'], 1):
                presentation += f"{i}. {clue}\n"
            
            current_q = self.puzzle_data['current_question']
            if current_q < len(self.puzzle_data['questions']):
                presentation += f"\nQuestion {current_q + 1}: {self.puzzle_data['questions'][current_q]}\n"
                presentation += "Your answer: "
            else:
                presentation += "\nAll questions answered!"
                
        elif self.puzzle_type == PuzzleType.MATH_PUZZLE:
            presentation += f"{self.puzzle_data['description']}\n\n"
            presentation += "Your answer: "
            
        elif self.puzzle_type == PuzzleType.PATTERN:
            pattern_str = " ".join(self.puzzle_data['pattern'])
            presentation += f"{self.puzzle_data['description']}\n"
            presentation += f"{pattern_str}\n\n"
            presentation += "What comes next? (You can type the symbol or shape name like 'circle', 'triangle', 'square') "
        
        # Add hint information
        if self.hints_used < self.max_hints:
            remaining_hints = self.max_hints - self.hints_used
            presentation += f"\n(Type 'hint' for a clue - {remaining_hints} hint(s) remaining)"
        
        return presentation
    
    def process_response(self, response: str) -> ChallengeResult:
        """Process the player's response to the current puzzle step.
        
        Args:
            response: The player's input/response
            
        Returns:
            ChallengeResult indicating success/failure and any rewards
        """
        response = response.strip().lower()
        
        # Handle hint requests
        if response == "hint" and self.hints_used < self.max_hints:
            return self._provide_hint()
        
        # Process answer based on puzzle type
        if self.puzzle_type == PuzzleType.SEQUENCE:
            return self._process_sequence_answer(response)
        elif self.puzzle_type == PuzzleType.LOGIC_GRID:
            return self._process_logic_grid_answer(response)
        elif self.puzzle_type == PuzzleType.MATH_PUZZLE:
            return self._process_math_answer(response)
        elif self.puzzle_type == PuzzleType.PATTERN:
            return self._process_pattern_answer(response)
        
        return ChallengeResult(
            success=False,
            message="Unable to process your response. Please try again."
        )
    
    def _provide_hint(self) -> ChallengeResult:
        """Provide a hint for the current puzzle."""
        self.hints_used += 1
        
        hints = {
            PuzzleType.SEQUENCE: f"Think about the rule: {self.puzzle_data.get('rule', 'look for a pattern')}",
            PuzzleType.LOGIC_GRID: "Try to eliminate possibilities using the clues systematically.",
            PuzzleType.MATH_PUZZLE: "Break the problem down into smaller parts and think step by step.",
            PuzzleType.PATTERN: f"The pattern follows: {self.puzzle_data.get('rule', 'a repeating sequence')}"
        }
        
        hint_message = hints.get(self.puzzle_type, "Look for patterns and relationships.")
        
        return ChallengeResult(
            success=False,
            message=f"Hint: {hint_message}",
            is_intermediate=True
        )
    
    def _process_sequence_answer(self, response: str) -> ChallengeResult:
        """Process answer for sequence puzzle."""
        correct_answer = self.puzzle_data['answer'].lower()
        
        if response == correct_answer:
            self.mark_completed()
            return ChallengeResult(
                success=True,
                message=f"Correct! The answer is {self.puzzle_data['answer']}. The rule was: {self.puzzle_data['rule']}.",
                reward=self.reward_item
            )
        else:
            return ChallengeResult(
                success=False,
                message=f"That's not correct. The sequence follows a specific mathematical rule."
            )
    
    def _process_logic_grid_answer(self, response: str) -> ChallengeResult:
        """Process answer for logic grid puzzle."""
        current_q = self.puzzle_data['current_question']
        correct_answer = self.puzzle_data['answers'][current_q].lower()
        
        if response == correct_answer:
            self.puzzle_data['current_question'] += 1
            
            if self.puzzle_data['current_question'] >= len(self.puzzle_data['questions']):
                # All questions answered
                self.mark_completed()
                return ChallengeResult(
                    success=True,
                    message="Excellent! You've solved the entire logic puzzle!",
                    reward=self.reward_item
                )
            else:
                return ChallengeResult(
                    success=False,  # Not fully complete yet
                    message=f"Correct! Moving to the next question...",
                    is_intermediate=True
                )
        else:
            return ChallengeResult(
                success=False,
                message="That's not correct. Use the clues to eliminate possibilities."
            )
    
    def _process_math_answer(self, response: str) -> ChallengeResult:
        """Process answer for math puzzle."""
        correct_answer = self.puzzle_data['answer'].lower()
        
        if response == correct_answer:
            self.mark_completed()
            return ChallengeResult(
                success=True,
                message=f"Correct! {self.puzzle_data['explanation']}",
                reward=self.reward_item
            )
        else:
            return ChallengeResult(
                success=False,
                message="That's not correct. Think about the problem step by step."
            )
    
    def _process_pattern_answer(self, response: str) -> ChallengeResult:
        """Process answer for pattern puzzle."""
        correct_answer = self.puzzle_data['answer'].lower()
        response_lower = response.lower().strip()
        
        # Create a mapping of symbols to word names
        symbol_to_word = {
            '○': 'circle',
            '△': 'triangle', 
            '□': 'square',
            '^': 'triangle',  # ASCII alternative
            'o': 'circle',    # ASCII alternative
            '#': 'square'     # ASCII alternative
        }
        
        # Create reverse mapping
        word_to_symbol = {word: symbol for symbol, word in symbol_to_word.items()}
        
        # Check if response matches the correct answer
        is_correct = False
        
        # Direct symbol match
        if response_lower == correct_answer:
            is_correct = True
        
        # ASCII symbol alternatives
        elif response_lower == correct_answer.replace('○', 'o').replace('△', '^').replace('□', '#'):
            is_correct = True
        
        # Word name match - check if the correct answer symbol corresponds to the response word
        elif correct_answer in symbol_to_word and response_lower == symbol_to_word[correct_answer]:
            is_correct = True
        
        # Word to symbol match - check if response word corresponds to correct symbol
        elif response_lower in word_to_symbol and word_to_symbol[response_lower] == correct_answer:
            is_correct = True
        
        if is_correct:
            self.mark_completed()
            return ChallengeResult(
                success=True,
                message=f"Correct! The pattern was: {self.puzzle_data['rule']}",
                reward=self.reward_item
            )
        else:
            return ChallengeResult(
                success=False,
                message="That's not correct. Look carefully at the repeating pattern. You can type the symbol or the name of the shape."
            )
    
    def get_reward(self) -> Optional[Item]:
        """Get the reward for completing this puzzle.
        
        Returns:
            The reward item if the puzzle is completed, None otherwise
        """
        return self.reward_item if self.completed else None
    
    def reset(self) -> None:
        """Reset the puzzle challenge for a new attempt."""
        self.current_step = 0
        self.player_progress = {}
        self.hints_used = 0
        self.completed = False
        
        # Reset puzzle-specific state
        if self.puzzle_type == PuzzleType.LOGIC_GRID:
            self.puzzle_data['current_question'] = 0
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress information.
        
        Returns:
            Dictionary containing progress information
        """
        progress = {
            "puzzle_type": self.puzzle_type.value,
            "current_step": self.current_step,
            "max_steps": self.max_steps,
            "hints_used": self.hints_used,
            "max_hints": self.max_hints,
            "completed": self.completed
        }
        
        if self.puzzle_type == PuzzleType.LOGIC_GRID:
            progress["questions_answered"] = self.puzzle_data['current_question']
            progress["total_questions"] = len(self.puzzle_data['questions'])
        
        return progress