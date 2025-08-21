"""Core data models for the Labyrinth Adventure Game."""

from dataclasses import dataclass, field
from typing import Optional, Set, List, Dict, Any
from src.utils.exceptions import GameException


@dataclass
class Item:
    """Represents an item that can be collected and used by the player."""
    name: str
    description: str
    item_type: str
    value: int
    usable: bool = True
    
    def __post_init__(self):
        """Validate item data after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate item data integrity."""
        if not self.name or not isinstance(self.name, str):
            raise GameException("Item name must be a non-empty string")
        
        if not self.description or not isinstance(self.description, str):
            raise GameException("Item description must be a non-empty string")
        
        if not self.item_type or not isinstance(self.item_type, str):
            raise GameException("Item type must be a non-empty string")
        
        if not isinstance(self.value, int) or self.value < 0:
            raise GameException("Item value must be a non-negative integer")
        
        if not isinstance(self.usable, bool):
            raise GameException("Item usable must be a boolean")
    
    def is_valid(self) -> bool:
        """Check if item is valid without raising exceptions."""
        try:
            self.validate()
            return True
        except GameException:
            return False


@dataclass
class ChallengeResult:
    """Result of a challenge attempt."""
    success: bool
    message: str
    reward: Optional[Item] = None
    damage: int = 0
    is_intermediate: bool = False  # True for intermediate steps like 'ready', 'continue'
    
    def __post_init__(self):
        """Validate challenge result data after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate challenge result data integrity."""
        if not isinstance(self.success, bool):
            raise GameException("Challenge result success must be a boolean")
        
        if not self.message or not isinstance(self.message, str):
            raise GameException("Challenge result message must be a non-empty string")
        
        if self.reward is not None and not isinstance(self.reward, Item):
            raise GameException("Challenge result reward must be an Item or None")
        
        if not isinstance(self.damage, int) or self.damage < 0:
            raise GameException("Challenge result damage must be a non-negative integer")
    
    def is_valid(self) -> bool:
        """Check if challenge result is valid without raising exceptions."""
        try:
            self.validate()
            return True
        except GameException:
            return False


@dataclass
class PlayerStats:
    """Player statistics that affect challenge outcomes."""
    strength: int = 10
    intelligence: int = 10
    dexterity: int = 10
    luck: int = 10
    
    def __post_init__(self):
        """Validate player stats data after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate player stats data integrity."""
        stats = ['strength', 'intelligence', 'dexterity', 'luck']
        for stat in stats:
            value = getattr(self, stat)
            if not isinstance(value, int) or value < 0:
                raise GameException(f"Player stat {stat} must be a non-negative integer")
    
    def modify_stat(self, stat_name: str, amount: int) -> None:
        """Modify a player stat by the given amount."""
        if not isinstance(stat_name, str):
            raise GameException("Stat name must be a string")
        
        if not isinstance(amount, int):
            raise GameException("Stat modification amount must be an integer")
        
        if hasattr(self, stat_name):
            current_value = getattr(self, stat_name)
            new_value = max(0, current_value + amount)  # Don't allow negative stats
            setattr(self, stat_name, new_value)
        else:
            raise GameException(f"Unknown stat: {stat_name}")
    
    def get_stat(self, stat_name: str) -> int:
        """Get the value of a specific stat."""
        if not hasattr(self, stat_name):
            raise GameException(f"Unknown stat: {stat_name}")
        return getattr(self, stat_name)
    
    def is_valid(self) -> bool:
        """Check if player stats are valid without raising exceptions."""
        try:
            self.validate()
            return True
        except GameException:
            return False


@dataclass
class GameState:
    """Complete game state for save/load functionality."""
    current_chamber: int
    player_health: int
    inventory_items: List[Item] = field(default_factory=list)
    completed_chambers: Set[int] = field(default_factory=set)
    visited_chambers: Set[int] = field(default_factory=set)
    discovered_connections: Dict[int, Dict[str, int]] = field(default_factory=dict)
    game_time: int = 0
    player_stats: PlayerStats = field(default_factory=PlayerStats)
    
    def __post_init__(self):
        """Validate game state data after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate game state data integrity."""
        if not isinstance(self.current_chamber, int) or self.current_chamber < 1:
            raise GameException("Current chamber must be a positive integer")
        
        if not isinstance(self.player_health, int) or self.player_health < 0:
            raise GameException("Player health must be a non-negative integer")
        
        if not isinstance(self.inventory_items, list):
            raise GameException("Inventory items must be a list")
        
        for item in self.inventory_items:
            if not isinstance(item, Item):
                raise GameException("All inventory items must be Item instances")
        
        if not isinstance(self.completed_chambers, set):
            raise GameException("Completed chambers must be a set")
        
        for chamber_id in self.completed_chambers:
            if not isinstance(chamber_id, int) or chamber_id < 1:
                raise GameException("All completed chamber IDs must be positive integers")
        
        if not isinstance(self.visited_chambers, set):
            raise GameException("Visited chambers must be a set")
        
        for chamber_id in self.visited_chambers:
            if not isinstance(chamber_id, int) or chamber_id < 1:
                raise GameException("All visited chamber IDs must be positive integers")
        
        if not isinstance(self.discovered_connections, dict):
            raise GameException("Discovered connections must be a dictionary")
        
        for chamber_id, connections in self.discovered_connections.items():
            if not isinstance(chamber_id, int) or chamber_id < 1:
                raise GameException("All connection chamber IDs must be positive integers")
            if not isinstance(connections, dict):
                raise GameException("Chamber connections must be a dictionary")
            for direction, target_id in connections.items():
                if not isinstance(direction, str) or not direction.strip():
                    raise GameException("Connection directions must be non-empty strings")
                if not isinstance(target_id, int) or target_id < 1:
                    raise GameException("Connection target IDs must be positive integers")
        
        if not isinstance(self.game_time, int) or self.game_time < 0:
            raise GameException("Game time must be a non-negative integer")
        
        if not isinstance(self.player_stats, PlayerStats):
            raise GameException("Player stats must be a PlayerStats instance")
    
    def add_completed_chamber(self, chamber_id: int) -> None:
        """Add a chamber to the completed set."""
        if not isinstance(chamber_id, int) or chamber_id < 1:
            raise GameException("Chamber ID must be a positive integer")
        self.completed_chambers.add(chamber_id)
    
    def is_chamber_completed(self, chamber_id: int) -> bool:
        """Check if a chamber has been completed."""
        return chamber_id in self.completed_chambers
    
    def add_inventory_item(self, item: Item) -> None:
        """Add an item to the inventory."""
        if not isinstance(item, Item):
            raise GameException("Item must be an Item instance")
        self.inventory_items.append(item)
    
    def remove_inventory_item(self, item_name: str) -> Optional[Item]:
        """Remove and return an item from inventory by name."""
        for i, item in enumerate(self.inventory_items):
            if item.name == item_name:
                return self.inventory_items.pop(i)
        return None
    
    def is_valid(self) -> bool:
        """Check if game state is valid without raising exceptions."""
        try:
            self.validate()
            return True
        except GameException:
            return False