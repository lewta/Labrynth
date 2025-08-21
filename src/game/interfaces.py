"""Core interfaces for game components."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from src.utils.data_models import Item, GameState


class InventoryInterface(ABC):
    """Interface for inventory management."""
    
    @abstractmethod
    def add_item(self, item: Item) -> bool:
        """Add an item to the inventory."""
        pass
    
    @abstractmethod
    def remove_item(self, item_name: str) -> Optional[Item]:
        """Remove an item from the inventory."""
        pass
    
    @abstractmethod
    def has_item(self, item_name: str) -> bool:
        """Check if inventory contains an item."""
        pass
    
    @abstractmethod
    def get_items(self) -> List[Item]:
        """Get all items in the inventory."""
        pass


class DisplayInterface(ABC):
    """Interface for display management."""
    
    @abstractmethod
    def display_message(self, message: str, message_type: str = "info") -> None:
        """Display a message to the player."""
        pass
    
    @abstractmethod
    def display_chamber_description(self, chamber_name: str, description: str, exits: List[str]) -> None:
        """Display chamber information."""
        pass
    
    @abstractmethod
    def display_inventory(self, items: List[Item]) -> None:
        """Display inventory contents."""
        pass


class SaveLoadInterface(ABC):
    """Interface for save/load functionality."""
    
    @abstractmethod
    def save_game(self, game_state: GameState, filename: str) -> bool:
        """Save the current game state."""
        pass
    
    @abstractmethod
    def load_game(self, filename: str) -> Optional[GameState]:
        """Load a saved game state."""
        pass
    
    @abstractmethod
    def list_save_files(self) -> List[str]:
        """List available save files."""
        pass