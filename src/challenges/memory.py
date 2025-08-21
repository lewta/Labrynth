"""Memory challenge implementation."""

import random
import time
from typing import Optional, List, Dict, Any
from src.challenges.base import Challenge
from src.utils.data_models import Item, ChallengeResult


class MemoryChallenge(Challenge):
    """A memory-based challenge with pattern or sequence memorization."""
    
    # Different types of memory challenges
    MEMORY_TYPES = {
        'sequence': {
            'name': 'Sequence Memory',
            'description': 'Remember and repeat a sequence of symbols',
            'symbols': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        },
        'pattern': {
            'name': 'Pattern Memory',
            'description': 'Remember the positions of symbols in a grid',
            'symbols': ['*', '#', '@', '%', '&', '+', '=', '~']
        },
        'color': {
            'name': 'Color Memory',
            'description': 'Remember a sequence of colors',
            'symbols': ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Orange', 'Pink', 'Cyan']
        },
        'number': {
            'name': 'Number Memory',
            'description': 'Remember a sequence of numbers',
            'symbols': ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        }
    }
    
    def __init__(self, difficulty: int = 5, memory_type: str = None, 
                 reward_item: Item = None, **kwargs):
        """Initialize a memory challenge.
        
        Args:
            difficulty: Difficulty level (1-10)
            memory_type: Type of memory challenge ('sequence', 'pattern', 'color', 'number')
            reward_item: Item to give as reward for success
            **kwargs: Additional arguments
        """
        # Choose random memory type if not specified
        if memory_type is None:
            memory_type = random.choice(list(self.MEMORY_TYPES.keys()))
        
        if memory_type not in self.MEMORY_TYPES:
            raise ValueError(f"Invalid memory type: {memory_type}. Must be one of {list(self.MEMORY_TYPES.keys())}")
        
        self.memory_type = memory_type
        memory_info = self.MEMORY_TYPES[memory_type]
        
        name = kwargs.get('name', memory_info['name'])
        description = kwargs.get('description', memory_info['description'])
        
        super().__init__(name, description, difficulty)
        
        # Challenge state
        self.attempts = 0
        self.max_attempts = 3
        self.sequence_length = self._calculate_sequence_length()
        self.current_sequence = []
        self.player_response = []
        self.phase = 'presentation'  # 'presentation', 'input', 'complete'
        self.show_time = self._calculate_show_time()
        
        # Generate the challenge
        self._generate_challenge()
        
        # Reward
        self.reward_item = reward_item or self._get_default_reward()
    
    def _calculate_sequence_length(self) -> int:
        """Calculate sequence length based on difficulty.
        
        Returns:
            Length of sequence to memorize
        """
        # Start with 3 items for difficulty 1, add 1 per difficulty level
        base_length = 2 + self.difficulty
        return min(base_length, 12)  # Cap at 12 items
    
    def _calculate_show_time(self) -> float:
        """Calculate how long to show the sequence.
        
        Returns:
            Time in seconds to display the sequence
        """
        # Base time of 1 second per item, reduced by difficulty
        base_time_per_item = max(0.5, 1.5 - (self.difficulty * 0.1))
        return self.sequence_length * base_time_per_item
    
    def _generate_challenge(self) -> None:
        """Generate the memory challenge sequence or pattern."""
        memory_info = self.MEMORY_TYPES[self.memory_type]
        symbols = memory_info['symbols']
        
        if self.memory_type == 'pattern':
            # For pattern memory, create a grid with symbols
            self._generate_pattern_challenge(symbols)
        else:
            # For sequence-based challenges
            self._generate_sequence_challenge(symbols)
    
    def _generate_sequence_challenge(self, symbols: List[str]) -> None:
        """Generate a sequence memory challenge.
        
        Args:
            symbols: Available symbols to use
        """
        # Create a random sequence
        self.current_sequence = []
        for _ in range(self.sequence_length):
            symbol = random.choice(symbols)
            self.current_sequence.append(symbol)
        
        # For higher difficulties, allow repeated symbols
        if self.difficulty <= 3:
            # Easy: no repeats
            self.current_sequence = list(dict.fromkeys(self.current_sequence))
            # Pad if needed
            while len(self.current_sequence) < self.sequence_length:
                available = [s for s in symbols if s not in self.current_sequence]
                if available:
                    self.current_sequence.append(random.choice(available))
                else:
                    break
    
    def _generate_pattern_challenge(self, symbols: List[str]) -> None:
        """Generate a pattern memory challenge.
        
        Args:
            symbols: Available symbols to use
        """
        # Create a 3x3 or 4x4 grid based on difficulty
        grid_size = 3 if self.difficulty <= 5 else 4
        total_positions = grid_size * grid_size
        
        # Number of symbols to place
        num_symbols = min(self.sequence_length, total_positions)
        
        # Create grid
        self.grid_size = grid_size
        self.pattern_grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Place symbols randomly
        positions = [(r, c) for r in range(grid_size) for c in range(grid_size)]
        selected_positions = random.sample(positions, num_symbols)
        
        self.current_sequence = []  # Store as (row, col, symbol) tuples
        for i, (row, col) in enumerate(selected_positions):
            symbol = symbols[i % len(symbols)]
            self.pattern_grid[row][col] = symbol
            self.current_sequence.append((row, col, symbol))
    
    def _get_default_reward(self) -> Item:
        """Get a default reward item based on memory type and difficulty."""
        reward_names = [
            "Memory Crystal", "Mind Enhancer", "Recall Potion", "Focus Amulet",
            "Concentration Ring", "Mental Clarity Gem", "Wisdom Stone", "Thought Amplifier"
        ]
        
        reward_name = reward_names[min(self.difficulty - 1, len(reward_names) - 1)]
        
        return Item(
            name=reward_name,
            description=f"A {reward_name.lower()} that sharpens your memory and focus",
            item_type="mental_enhancement",
            value=self.difficulty * 10
        )
    
    def present_challenge(self) -> str:
        """Present the memory challenge to the player."""
        if self.phase == 'presentation':
            presentation = f"\n=== {self.name} ===\n"
            presentation += f"Difficulty: {self.difficulty}/10\n"
            presentation += f"Sequence Length: {len(self.current_sequence)}\n\n"
            presentation += f"{self.description}\n\n"
            
            if self.attempts > 0:
                remaining = self.max_attempts - self.attempts
                presentation += f"Attempts remaining: {remaining}\n\n"
            
            presentation += "The sequence will be shown for a limited time. Pay close attention!\n"
            presentation += f"You will have {self.show_time:.1f} seconds to memorize it.\n\n"
            presentation += "Type 'ready' when you're prepared to see the sequence.\n\n"
            presentation += "What do you do? "
            
            return presentation
        
        elif self.phase == 'showing':
            return self._show_sequence()
        
        elif self.phase == 'input':
            presentation = "\nNow enter what you remember!\n\n"
            
            if self.memory_type == 'pattern':
                presentation += "Enter the positions and symbols you saw.\n"
                presentation += "Format: row,col,symbol (e.g., '1,2,*' for symbol * at row 1, column 2)\n"
                presentation += "Enter one per line, or separate multiple with semicolons.\n"
                presentation += "Rows and columns are numbered starting from 1.\n\n"
            else:
                presentation += "Enter the sequence you saw.\n"
                presentation += "Separate items with spaces or commas.\n\n"
            
            presentation += "Your answer: "
            return presentation
        
        else:
            return "Challenge completed!"
    
    def _show_sequence(self) -> str:
        """Show the sequence to memorize.
        
        Returns:
            String representation of the sequence
        """
        if self.memory_type == 'pattern':
            display = "\n" + "="*20 + "\n"
            display += "MEMORIZE THIS PATTERN:\n\n"
            
            # Show grid with row/column numbers
            display += "   "
            for c in range(self.grid_size):
                display += f" {c+1} "
            display += "\n"
            
            for r in range(self.grid_size):
                display += f"{r+1}: "
                for c in range(self.grid_size):
                    display += f"[{self.pattern_grid[r][c]}]"
                display += "\n"
            
            display += "\n" + "="*20 + "\n"
            display += f"Study this for {self.show_time:.1f} seconds...\n"
        else:
            display = "\n" + "="*30 + "\n"
            display += "MEMORIZE THIS SEQUENCE:\n\n"
            display += " -> ".join(self.current_sequence) + "\n\n"
            display += "="*30 + "\n"
            display += f"Study this for {self.show_time:.1f} seconds...\n"
        
        return display
    
    def process_response(self, response: str) -> ChallengeResult:
        """Process the player's response to the memory challenge.
        
        Args:
            response: The player's input
            
        Returns:
            ChallengeResult indicating the outcome
        """
        action = response.lower().strip()
        
        if self.phase == 'presentation':
            if action == 'ready':
                self.phase = 'input'  # Go directly to input phase after showing sequence
                sequence_display = self._show_sequence()
                # Add clear instructions
                instructions = "\n\n" + "="*50 + "\n"
                instructions += "SEQUENCE SHOWN ABOVE - NOW ENTER YOUR ANSWER\n"
                instructions += "="*50 + "\n\n"
                
                if self.memory_type == 'pattern':
                    instructions += "Enter the positions and symbols you saw.\n"
                    instructions += "Format: row,col,symbol (e.g., '1,2,*' for symbol * at row 1, column 2)\n"
                    instructions += "Enter one per line, or separate multiple with semicolons.\n"
                    instructions += "Rows and columns are numbered starting from 1.\n\n"
                else:
                    instructions += "Enter the sequence you saw.\n"
                    instructions += "Separate items with spaces or commas.\n\n"
                
                instructions += "Your answer: "
                
                return ChallengeResult(
                    success=False,
                    message=f"{sequence_display}{instructions}",
                    is_intermediate=True
                )
            else:
                return ChallengeResult(
                    success=False,
                    message="Type 'ready' when you're prepared to see the sequence.",
                    is_intermediate=True
                )
        
        elif self.phase == 'showing':
            # This phase is now skipped, but keep for compatibility
            if action == 'continue':
                self.phase = 'input'
                return ChallengeResult(
                    success=False,
                    message=self.present_challenge(),
                    is_intermediate=True
                )
            else:
                return ChallengeResult(
                    success=False,
                    message="Type 'continue' when you've finished studying the sequence.",
                    is_intermediate=True
                )
        
        elif self.phase == 'input':
            return self._process_memory_input(response)
        
        else:
            return ChallengeResult(
                success=False,
                message="Challenge is already complete!"
            )
    
    def _process_memory_input(self, response: str) -> ChallengeResult:
        """Process the player's memory input.
        
        Args:
            response: Player's memory response
            
        Returns:
            ChallengeResult with outcome
        """
        self.attempts += 1
        
        if self.memory_type == 'pattern':
            return self._check_pattern_answer(response)
        else:
            return self._check_sequence_answer(response)
    
    def _check_sequence_answer(self, response: str) -> ChallengeResult:
        """Check sequence memory answer.
        
        Args:
            response: Player's sequence answer
            
        Returns:
            ChallengeResult with outcome
        """
        # Parse player response
        player_sequence = []
        
        # Try different separators
        if ' -> ' in response:
            # Handle the format shown in the display (A -> B -> C)
            player_sequence = [item.strip() for item in response.split(' -> ')]
        elif ',' in response:
            player_sequence = [item.strip() for item in response.split(',')]
        else:
            player_sequence = response.split()
        
        # Clean up the response
        player_sequence = [item.strip() for item in player_sequence if item.strip()]
        
        # Check accuracy
        correct_count = 0
        total_items = len(self.current_sequence)
        
        # Check each position
        for i in range(min(len(player_sequence), len(self.current_sequence))):
            if i < len(player_sequence) and player_sequence[i] == self.current_sequence[i]:
                correct_count += 1
        
        # Calculate accuracy percentage
        accuracy = (correct_count / total_items) * 100 if total_items > 0 else 0
        
        # Determine success threshold based on difficulty
        success_threshold = max(60, 100 - (self.difficulty * 5))  # 95% for easy, 60% for hard
        
        if accuracy >= success_threshold:
            # Success!
            self.mark_completed()
            self.phase = 'complete'
            return ChallengeResult(
                success=True,
                message=f"Excellent memory! You got {correct_count}/{total_items} correct ({accuracy:.1f}%).",
                reward=self.reward_item
            )
        else:
            # Failure
            remaining_attempts = self.max_attempts - self.attempts
            
            if remaining_attempts > 0:
                self.phase = 'presentation'  # Reset to try again
                return ChallengeResult(
                    success=False,
                    message=f"Not quite right. You got {correct_count}/{total_items} correct ({accuracy:.1f}%). "
                           f"You need at least {success_threshold:.0f}% accuracy. {remaining_attempts} attempt(s) remaining."
                )
            else:
                # No more attempts
                correct_sequence = " -> ".join(self.current_sequence)
                return ChallengeResult(
                    success=False,
                    message=f"Memory challenge failed. The correct sequence was: {correct_sequence}",
                    damage=8  # Mental strain penalty
                )
    
    def _check_pattern_answer(self, response: str) -> ChallengeResult:
        """Check pattern memory answer.
        
        Args:
            response: Player's pattern answer
            
        Returns:
            ChallengeResult with outcome
        """
        # Parse player response
        player_patterns = []
        
        # Split by semicolons or newlines
        entries = response.replace('\n', ';').split(';')
        
        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue
            
            # Parse format: row,col,symbol
            parts = entry.split(',')
            if len(parts) == 3:
                try:
                    row = int(parts[0].strip()) - 1  # Convert to 0-based
                    col = int(parts[1].strip()) - 1  # Convert to 0-based
                    symbol = parts[2].strip()
                    
                    if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                        player_patterns.append((row, col, symbol))
                except ValueError:
                    continue  # Skip invalid entries
        
        # Check accuracy
        correct_count = 0
        total_items = len(self.current_sequence)
        
        for correct_pattern in self.current_sequence:
            if correct_pattern in player_patterns:
                correct_count += 1
        
        # Calculate accuracy
        accuracy = (correct_count / total_items) * 100 if total_items > 0 else 0
        
        # Determine success threshold
        success_threshold = max(60, 100 - (self.difficulty * 5))
        
        if accuracy >= success_threshold:
            # Success!
            self.mark_completed()
            self.phase = 'complete'
            return ChallengeResult(
                success=True,
                message=f"Perfect pattern memory! You got {correct_count}/{total_items} positions correct ({accuracy:.1f}%).",
                reward=self.reward_item
            )
        else:
            # Failure
            remaining_attempts = self.max_attempts - self.attempts
            
            if remaining_attempts > 0:
                self.phase = 'presentation'  # Reset to try again
                return ChallengeResult(
                    success=False,
                    message=f"Pattern not quite right. You got {correct_count}/{total_items} positions correct ({accuracy:.1f}%). "
                           f"You need at least {success_threshold:.0f}% accuracy. {remaining_attempts} attempt(s) remaining."
                )
            else:
                # Show correct pattern
                correct_info = []
                for row, col, symbol in self.current_sequence:
                    correct_info.append(f"{row+1},{col+1},{symbol}")
                correct_pattern = "; ".join(correct_info)
                
                return ChallengeResult(
                    success=False,
                    message=f"Pattern memory failed. The correct pattern was: {correct_pattern}",
                    damage=8  # Mental strain penalty
                )
    
    def get_reward(self) -> Optional[Item]:
        """Get the reward for completing this memory challenge.
        
        Returns:
            The reward item if challenge is completed, None otherwise
        """
        return self.reward_item if self.completed else None
    
    def reset(self) -> None:
        """Reset the memory challenge for a new attempt."""
        self.attempts = 0
        self.completed = False
        self.phase = 'presentation'
        self.player_response = []
        
        # Generate new challenge for variety
        self._generate_challenge()
    
    def get_challenge_info(self) -> Dict[str, Any]:
        """Get detailed information about the challenge.
        
        Returns:
            Dictionary with challenge details
        """
        return {
            "memory_type": self.memory_type,
            "difficulty": self.difficulty,
            "sequence_length": self.sequence_length,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "phase": self.phase,
            "show_time": self.show_time,
            "completed": self.completed
        }
    
    def get_current_sequence(self) -> List:
        """Get the current sequence (for testing purposes).
        
        Returns:
            Current sequence or pattern
        """
        return self.current_sequence.copy()
    
    def set_phase(self, phase: str) -> None:
        """Set the current phase (for testing purposes).
        
        Args:
            phase: Phase to set ('presentation', 'showing', 'input', 'complete')
        """
        if phase in ['presentation', 'showing', 'input', 'complete']:
            self.phase = phase