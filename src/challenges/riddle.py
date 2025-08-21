"""Riddle challenge implementation."""

from typing import List, Optional
from src.challenges.base import Challenge
from src.utils.data_models import Item, ChallengeResult
from src.utils.challenge_content import get_content_loader


class RiddleChallenge(Challenge):
    """A text-based riddle challenge with multiple acceptable answers."""
    
    def __init__(self, difficulty: int = 5, riddle_text: str = None, 
                 answers: List[str] = None, reward_item: Item = None, **kwargs):
        """Initialize a riddle challenge.
        
        Args:
            difficulty: Difficulty level (1-10)
            riddle_text: The riddle question text
            answers: List of acceptable answers (case-insensitive)
            reward_item: Item to give as reward for solving the riddle
            **kwargs: Additional arguments
        """
        name = kwargs.get('name', 'Riddle Challenge')
        description = kwargs.get('description', 'A mysterious riddle that tests your wit')
        
        super().__init__(name, description, difficulty)
        
        # Get riddle content (randomized or default)
        if riddle_text is None or answers is None:
            riddle_data = self._get_riddle_content()
            self.riddle_text = riddle_text or riddle_data['riddle_text']
            self.answers = [answer.lower().strip() for answer in (answers or riddle_data['answers'])]
            self.hint_text = riddle_data.get('hint')
            self.category = riddle_data.get('category', 'mystery')
        else:
            self.riddle_text = riddle_text
            self.answers = [answer.lower().strip() for answer in answers]
            self.hint_text = None
            self.category = 'custom'
        
        # Default reward if none provided
        self.reward_item = reward_item or self._get_default_reward()
        
        # Track attempts for difficulty scaling
        self.attempts = 0
        self.max_attempts = 3
    
    def _get_riddle_content(self) -> dict:
        """Get riddle content from content loader or fallback to defaults.
        
        Returns:
            Dictionary with riddle_text, answers, hint, and category
        """
        try:
            content_loader = get_content_loader()
            riddle_data = content_loader.get_riddle(self.difficulty)
            return {
                'riddle_text': riddle_data.get('riddle'),
                'answers': riddle_data.get('answers', []),
                'hint': riddle_data.get('hint'),
                'category': riddle_data.get('category', 'mystery')
            }
        except Exception:
            # Fallback to default riddle
            return {
                'riddle_text': self._get_default_riddle(),
                'answers': self._get_default_answers(),
                'hint': self._get_default_hint(),
                'category': 'default'
            }
    
    def _get_default_riddle(self) -> str:
        """Get a default riddle based on difficulty level."""
        default_riddles = {
            1: "What has keys but no locks, space but no room, and you can enter but not go inside?",
            2: "I am not alive, but I grow; I don't have lungs, but I need air; I don't have a mouth, but water kills me. What am I?",
            3: "The more you take, the more you leave behind. What am I?",
            4: "I have cities, but no houses. I have mountains, but no trees. I have water, but no fish. What am I?",
            5: "What comes once in a minute, twice in a moment, but never in a thousand years?",
            6: "I am always hungry and will die if not fed, but whatever I touch will soon turn red. What am I?",
            7: "What has a head, a tail, is brown, and has no legs?",
            8: "I speak without a mouth and hear without ears. I have no body, but come alive with wind. What am I?",
            9: "The person who makes it, sells it. The person who buys it, never uses it. The person who uses it, never knows it. What is it?",
            10: "I am the beginning of the end, and the end of time and space. I am essential to creation, and I surround every place. What am I?"
        }
        
        # Use difficulty level, default to medium if out of range
        difficulty_key = min(max(self.difficulty, 1), 10)
        return default_riddles.get(difficulty_key, default_riddles[5])
    
    def _get_default_answers(self) -> List[str]:
        """Get default answers based on the default riddle."""
        default_answer_sets = {
            1: ["keyboard", "computer keyboard"],
            2: ["fire", "flame"],
            3: ["footsteps", "steps", "footprints"],
            4: ["map", "a map"],
            5: ["the letter m", "letter m", "m"],
            6: ["fire", "flame"],
            7: ["penny", "coin", "a penny"],
            8: ["echo", "an echo"],
            9: ["coffin", "a coffin", "casket"],
            10: ["the letter e", "letter e", "e"]
        }
        
        difficulty_key = min(max(self.difficulty, 1), 10)
        return default_answer_sets.get(difficulty_key, ["unknown"])
    
    def _get_default_reward(self) -> Item:
        """Get a default reward item."""
        reward_names = [
            "Ancient Key", "Wisdom Scroll", "Crystal Shard", "Golden Coin",
            "Magic Rune", "Silver Token", "Mystic Gem", "Sacred Amulet"
        ]
        
        reward_name = reward_names[self.difficulty % len(reward_names)]
        
        return Item(
            name=reward_name,
            description=f"A valuable {reward_name.lower()} earned by solving a riddle",
            item_type="treasure",
            value=self.difficulty * 10
        )
    
    def present_challenge(self) -> str:
        """Present the riddle to the player."""
        presentation = f"\n=== {self.name} ===\n"
        presentation += f"Difficulty: {self.difficulty}/10\n\n"
        presentation += f"{self.riddle_text}\n\n"
        
        if self.attempts > 0:
            remaining = self.max_attempts - self.attempts
            presentation += f"Attempts remaining: {remaining}\n\n"
        
        presentation += "What is your answer? "
        return presentation
    
    def process_response(self, response: str) -> ChallengeResult:
        """Process the player's answer to the riddle.
        
        Args:
            response: The player's answer
            
        Returns:
            ChallengeResult indicating success/failure and any rewards
        """
        # Clean and normalize the response
        cleaned_response = response.lower().strip()
        
        # Check if this is a hint request
        if cleaned_response in ['hint', 'help', 'clue', 'tip']:
            hint_message = self._get_hint_message()
            return ChallengeResult(
                success=False,
                message=f"Hint: {hint_message}",
                is_intermediate=True  # This prevents "FAILED!" from being displayed
            )
        
        self.attempts += 1
        
        # Check if the answer is correct
        is_correct = any(cleaned_response == answer for answer in self.answers)
        
        if is_correct:
            self.mark_completed()
            return ChallengeResult(
                success=True,
                message=f"Correct! Well done. {self._get_success_message()}",
                reward=self.reward_item
            )
        else:
            remaining_attempts = self.max_attempts - self.attempts
            
            if remaining_attempts > 0:
                hint_message = self._get_hint_message()
                return ChallengeResult(
                    success=False,
                    message=f"That's not correct. {hint_message} You have {remaining_attempts} attempt(s) remaining."
                )
            else:
                # No more attempts
                correct_answers = ", ".join(self.answers[:3])  # Show first 3 answers
                return ChallengeResult(
                    success=False,
                    message=f"Sorry, you've run out of attempts. The answer was: {correct_answers}",
                    damage=5  # Small penalty for failing
                )
    
    def _get_success_message(self) -> str:
        """Get a success message based on number of attempts."""
        if self.attempts == 1:
            return "Brilliant! You solved it on the first try!"
        elif self.attempts == 2:
            return "Good thinking! You got it on the second attempt."
        else:
            return "You persevered and found the answer!"
    
    def _get_hint_message(self) -> str:
        """Get a hint message based on the current riddle."""
        # Use hint from content if available
        if hasattr(self, 'hint_text') and self.hint_text:
            return self.hint_text
        
        # Fallback to default hints
        return self._get_default_hint()
    
    def _get_default_hint(self) -> str:
        """Get default hint based on difficulty."""
        hints = {
            1: "Think about something you use every day with your computer.",
            2: "It's something that needs oxygen to survive.",
            3: "Think about what you leave behind when you walk.",
            4: "It's a representation of the world, but not the world itself.",
            5: "Look at the letters in the words 'minute' and 'moment'.",
            6: "It's dangerous and consumes everything it touches.",
            7: "It's something small and round that you might find in your pocket.",
            8: "It's a sound that comes back to you.",
            9: "Think about something used in funerals.",
            10: "It's a letter that appears in many important words."
        }
        
        difficulty_key = min(max(self.difficulty, 1), 10)
        return hints.get(difficulty_key, "Think carefully about the clues in the riddle.")
    
    def get_reward(self) -> Optional[Item]:
        """Get the reward for completing this riddle.
        
        Returns:
            The reward item if the riddle is completed, None otherwise
        """
        return self.reward_item if self.completed else None
    
    def reset(self) -> None:
        """Reset the riddle challenge for a new attempt."""
        self.attempts = 0
        self.completed = False
    
    def add_acceptable_answer(self, answer: str) -> None:
        """Add a new acceptable answer to the riddle.
        
        Args:
            answer: New acceptable answer (will be converted to lowercase)
        """
        cleaned_answer = answer.lower().strip()
        if cleaned_answer not in self.answers:
            self.answers.append(cleaned_answer)
    
    def get_acceptable_answers(self) -> List[str]:
        """Get all acceptable answers for this riddle.
        
        Returns:
            List of acceptable answers
        """
        return self.answers.copy()