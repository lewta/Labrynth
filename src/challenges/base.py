"""Abstract base class for all challenge types."""

from abc import ABC, abstractmethod
from typing import Optional

from src.utils.data_models import Item, ChallengeResult


class Challenge(ABC):
    """Abstract base class for all challenge types."""
    
    def __init__(self, name: str, description: str, difficulty: int):
        """Initialize a challenge.
        
        Args:
            name: The name of the challenge
            description: A description of what the challenge involves
            difficulty: Difficulty level (1-10)
        """
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.completed = False
    
    @abstractmethod
    def present_challenge(self) -> str:
        """Present the challenge to the player.
        
        Returns:
            A string describing the challenge and what the player needs to do
        """
        pass
    
    @abstractmethod
    def process_response(self, response: str) -> ChallengeResult:
        """Process the player's response to the challenge.
        
        Args:
            response: The player's input/response
            
        Returns:
            ChallengeResult indicating success/failure and any rewards
        """
        pass
    
    @abstractmethod
    def get_reward(self) -> Optional[Item]:
        """Get the reward for completing this challenge.
        
        Returns:
            An Item reward, or None if no reward
        """
        pass
    
    def mark_completed(self) -> None:
        """Mark this challenge as completed."""
        self.completed = True