"""Player management system for the Labyrinth Adventure Game."""

from typing import Dict, Any, Optional, List
from src.game.inventory import Inventory
from src.game.progress import ProgressTracker
from src.utils.data_models import Item, PlayerStats
from src.utils.exceptions import GameException


class PlayerManager:
    """Manages player state including health, stats, and inventory."""
    
    def __init__(self, max_health: int = 100, max_inventory_capacity: int = 20):
        """
        Initialize player manager with default values.
        
        Args:
            max_health: Maximum player health
            max_inventory_capacity: Maximum inventory capacity
        """
        if not isinstance(max_health, int) or max_health < 1:
            raise GameException("Max health must be a positive integer")
        
        if not isinstance(max_inventory_capacity, int) or max_inventory_capacity < 1:
            raise GameException("Max inventory capacity must be a positive integer")
        
        self.max_health = max_health
        self.current_health = max_health
        self.stats = PlayerStats()
        self.inventory = Inventory(max_capacity=max_inventory_capacity)
        self.progress = ProgressTracker()
        self._experience_points = 0
        self._level = 1
    
    @property
    def health(self) -> int:
        """Get current health (for test compatibility)."""
        return self.current_health
    
    @health.setter
    def health(self, value: int) -> None:
        """Set current health (for test compatibility)."""
        if not isinstance(value, int) or value < 0:
            raise GameException("Health must be a non-negative integer")
        self.current_health = min(value, self.max_health)
    
    def take_damage(self, amount: int) -> bool:
        """
        Apply damage to the player.
        
        Args:
            amount: Amount of damage to apply
            
        Returns:
            bool: True if player is still alive, False if player died
            
        Raises:
            GameException: If damage amount is invalid
        """
        if not isinstance(amount, int) or amount < 0:
            raise GameException("Damage amount must be a non-negative integer")
        
        self.current_health = max(0, self.current_health - amount)
        return self.current_health > 0
    
    def heal(self, amount: int) -> int:
        """
        Heal the player by the specified amount.
        
        Args:
            amount: Amount of health to restore
            
        Returns:
            int: Actual amount healed (may be less if at max health)
            
        Raises:
            GameException: If heal amount is invalid
        """
        if not isinstance(amount, int) or amount < 0:
            raise GameException("Heal amount must be a non-negative integer")
        
        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        return self.current_health - old_health
    
    def modify_stat(self, stat_name: str, amount: int) -> None:
        """
        Modify a player stat by the given amount.
        
        Args:
            stat_name: Name of the stat to modify
            amount: Amount to modify the stat by
            
        Raises:
            GameException: If stat name is invalid or amount is invalid
        """
        if not isinstance(stat_name, str) or not stat_name.strip():
            raise GameException("Stat name must be a non-empty string")
        
        if not isinstance(amount, int):
            raise GameException("Stat modification amount must be an integer")
        
        self.stats.modify_stat(stat_name, amount)
    
    def get_stat(self, stat_name: str) -> int:
        """
        Get the value of a specific stat.
        
        Args:
            stat_name: Name of the stat to retrieve
            
        Returns:
            int: Current value of the stat
            
        Raises:
            GameException: If stat name is invalid
        """
        return self.stats.get_stat(stat_name)
    
    def add_item(self, item: Item) -> bool:
        """
        Add an item to the player's inventory.
        
        Args:
            item: Item to add to inventory
            
        Returns:
            bool: True if item was added successfully, False if inventory is full
            
        Raises:
            GameException: If item is invalid
        """
        return self.inventory.add_item(item)
    
    def remove_item(self, item_name: str) -> Optional[Item]:
        """
        Remove an item from the player's inventory.
        
        Args:
            item_name: Name of the item to remove
            
        Returns:
            Optional[Item]: The removed item, or None if not found
        """
        return self.inventory.remove_item(item_name)
    
    def use_item(self, item_name: str) -> Optional[Item]:
        """
        Use an item from the player's inventory.
        
        Args:
            item_name: Name of the item to use
            
        Returns:
            Optional[Item]: The used item, or None if not found or not usable
        """
        item = self.inventory.use_item(item_name)
        
        if item is not None:
            # Apply item effects based on item type
            self._apply_item_effects(item)
        
        return item
    
    def _apply_item_effects(self, item: Item) -> None:
        """
        Apply the effects of using an item.
        
        Args:
            item: The item whose effects to apply
        """
        # Basic item effect system based on item type
        if item.item_type == "potion":
            # Health potions restore health based on their value
            heal_amount = item.value // 2  # Half the item's value as healing
            self.heal(heal_amount)
        
        elif item.item_type == "scroll":
            # Scrolls might boost stats temporarily or permanently
            if "strength" in item.name.lower():
                self.modify_stat("strength", 1)
            elif "intelligence" in item.name.lower():
                self.modify_stat("intelligence", 1)
            elif "dexterity" in item.name.lower():
                self.modify_stat("dexterity", 1)
            elif "luck" in item.name.lower():
                self.modify_stat("luck", 1)
        
        elif item.item_type == "food":
            # Food items provide small health restoration
            heal_amount = max(1, item.value // 5)
            self.heal(heal_amount)
    
    def has_item(self, item_name: str) -> bool:
        """
        Check if the player has a specific item.
        
        Args:
            item_name: Name of the item to check for
            
        Returns:
            bool: True if player has the item
        """
        return self.inventory.has_item(item_name)
    
    def get_item_count(self, item_name: str) -> int:
        """
        Get the count of a specific item in inventory.
        
        Args:
            item_name: Name of the item to count
            
        Returns:
            int: Number of items with that name
        """
        return self.inventory.get_item_count(item_name)
    
    def is_alive(self) -> bool:
        """
        Check if the player is alive.
        
        Returns:
            bool: True if player has health > 0
        """
        return self.current_health > 0
    
    def is_at_full_health(self) -> bool:
        """
        Check if the player is at maximum health.
        
        Returns:
            bool: True if current health equals max health
        """
        return self.current_health >= self.max_health
    
    def get_health_percentage(self) -> float:
        """
        Get the player's health as a percentage.
        
        Returns:
            float: Health percentage (0.0 to 1.0)
        """
        return self.current_health / self.max_health
    
    def add_experience(self, amount: int) -> bool:
        """
        Add experience points to the player.
        
        Args:
            amount: Amount of experience to add
            
        Returns:
            bool: True if player leveled up, False otherwise
            
        Raises:
            GameException: If experience amount is invalid
        """
        if not isinstance(amount, int) or amount < 0:
            raise GameException("Experience amount must be a non-negative integer")
        
        self._experience_points += amount
        
        # Check for level up (simple formula: 100 * level XP needed for next level)
        xp_needed_for_next_level = 100 * self._level
        if self._experience_points >= xp_needed_for_next_level:
            self._level_up()
            return True
        
        return False
    
    def _level_up(self) -> None:
        """Handle player leveling up."""
        self._level += 1
        
        # Increase max health by 10 per level
        self.max_health += 10
        self.current_health = self.max_health  # Full heal on level up
        
        # Increase all stats by 1 per level
        self.modify_stat("strength", 1)
        self.modify_stat("intelligence", 1)
        self.modify_stat("dexterity", 1)
        self.modify_stat("luck", 1)
    
    def get_level(self) -> int:
        """
        Get the player's current level.
        
        Returns:
            int: Current player level
        """
        return self._level
    
    def get_experience(self) -> int:
        """
        Get the player's current experience points.
        
        Returns:
            int: Current experience points
        """
        return self._experience_points
    
    def get_experience_to_next_level(self) -> int:
        """
        Get experience points needed for next level.
        
        Returns:
            int: Experience points needed to reach next level
        """
        xp_needed = 100 * self._level
        return max(0, xp_needed - self._experience_points)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive player status information.
        
        Returns:
            Dict[str, Any]: Dictionary containing all player status information
        """
        inventory_info = self.inventory.get_capacity_info()
        
        return {
            'health': {
                'current': self.current_health,
                'max': self.max_health,
                'percentage': self.get_health_percentage()
            },
            'level': self._level,
            'experience': {
                'current': self._experience_points,
                'to_next_level': self.get_experience_to_next_level()
            },
            'stats': {
                'strength': self.stats.strength,
                'intelligence': self.stats.intelligence,
                'dexterity': self.stats.dexterity,
                'luck': self.stats.luck
            },
            'inventory': {
                'items': len(self.inventory),
                'capacity': inventory_info['max'],
                'available': inventory_info['available'],
                'total_value': self.inventory.get_total_value()
            },
            'alive': self.is_alive()
        }
    
    def get_combat_stats(self) -> Dict[str, int]:
        """
        Get stats relevant for combat calculations.
        
        Returns:
            Dict[str, int]: Combat-relevant stats
        """
        return {
            'attack_power': self.stats.strength + (self._level - 1) * 2,
            'defense': self.stats.dexterity + (self._level - 1),
            'accuracy': self.stats.dexterity + self.stats.luck,
            'critical_chance': self.stats.luck,
            'health': self.current_health,
            'max_health': self.max_health
        }
    
    def reset_to_defaults(self) -> None:
        """Reset player to default starting state."""
        self.current_health = self.max_health
        self.stats = PlayerStats()
        self.inventory.clear()
        self.progress.reset()
        self._experience_points = 0
        self._level = 1
    
    def __str__(self) -> str:
        """Return a string representation of the player status."""
        status = self.get_status()
        health = status['health']
        stats = status['stats']
        inventory = status['inventory']
        
        lines = [
            f"Player Status (Level {status['level']}):",
            f"  Health: {health['current']}/{health['max']} ({health['percentage']:.1%})",
            f"  Experience: {status['experience']['current']} ({status['experience']['to_next_level']} to next level)",
            f"  Stats: STR {stats['strength']}, INT {stats['intelligence']}, DEX {stats['dexterity']}, LCK {stats['luck']}",
            f"  Inventory: {inventory['items']}/{inventory['capacity']} items (value: {inventory['total_value']})"
        ]
        
        return "\n".join(lines)