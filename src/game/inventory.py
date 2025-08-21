"""Inventory management system for the Labyrinth Adventure Game."""

from typing import Dict, List, Optional, Set
from collections import defaultdict
from src.utils.data_models import Item
from src.utils.exceptions import GameException


class Inventory:
    """Manages player inventory with item capacity limits and categorization."""
    
    # Item type categories for organization
    ITEM_CATEGORIES = {
        'weapon': ['sword', 'dagger', 'staff', 'bow'],
        'armor': ['helmet', 'chestplate', 'boots', 'shield'],
        'consumable': ['potion', 'food', 'scroll', 'key'],
        'treasure': ['gem', 'coin', 'artifact', 'jewelry'],
        'tool': ['rope', 'torch', 'lockpick', 'map']
    }
    
    def __init__(self, max_capacity: int = 20):
        """Initialize inventory with specified capacity limit."""
        if not isinstance(max_capacity, int) or max_capacity < 1:
            raise GameException("Max capacity must be a positive integer")
        
        self.max_capacity = max_capacity
        self.items: List[Item] = []  # Public attribute for test compatibility
        self._item_counts: Dict[str, int] = defaultdict(int)
    
    def add_item(self, item: Item) -> bool:
        """
        Add an item to the inventory.
        
        Args:
            item: The item to add
            
        Returns:
            bool: True if item was added successfully, False if inventory is full
            
        Raises:
            GameException: If item is invalid
        """
        if not isinstance(item, Item):
            raise GameException("Item must be an Item instance")
        
        if not item.is_valid():
            raise GameException("Cannot add invalid item to inventory")
        
        if self.is_full():
            return False
        
        self.items.append(item)
        self._item_counts[item.name] += 1
        return True
    
    def remove_item(self, item_name: str) -> Optional[Item]:
        """
        Remove and return the first item with the specified name.
        
        Args:
            item_name: Name of the item to remove
            
        Returns:
            Optional[Item]: The removed item, or None if not found
        """
        if not isinstance(item_name, str) or not item_name.strip():
            raise GameException("Item name must be a non-empty string")
        
        for i, item in enumerate(self.items):
            if item.name == item_name:
                removed_item = self.items.pop(i)
                self._item_counts[item_name] -= 1
                if self._item_counts[item_name] == 0:
                    del self._item_counts[item_name]
                return removed_item
        
        return None
    
    def use_item(self, item_name: str) -> Optional[Item]:
        """
        Use an item from the inventory (removes it if usable).
        
        Args:
            item_name: Name of the item to use
            
        Returns:
            Optional[Item]: The used item, or None if not found or not usable
        """
        if not isinstance(item_name, str) or not item_name.strip():
            raise GameException("Item name must be a non-empty string")
        
        for item in self.items:
            if item.name == item_name:
                if item.usable:
                    return self.remove_item(item_name)
                else:
                    raise GameException(f"Item '{item_name}' is not usable")
        
        return None
    
    def has_item(self, item_name: str) -> bool:
        """
        Check if inventory contains an item with the specified name.
        
        Args:
            item_name: Name of the item to check for
            
        Returns:
            bool: True if item exists in inventory
        """
        if not isinstance(item_name, str):
            return False
        
        return item_name in self._item_counts
    
    def get_item_count(self, item_name: str) -> int:
        """
        Get the count of items with the specified name.
        
        Args:
            item_name: Name of the item to count
            
        Returns:
            int: Number of items with that name
        """
        if not isinstance(item_name, str):
            return 0
        
        return self._item_counts.get(item_name, 0)
    
    def get_all_items(self) -> List[Item]:
        """
        Get a copy of all items in the inventory.
        
        Returns:
            List[Item]: Copy of all items in inventory
        """
        return self.items.copy()
    
    def get_items_by_type(self, item_type: str) -> List[Item]:
        """
        Get all items of a specific type.
        
        Args:
            item_type: The type of items to retrieve
            
        Returns:
            List[Item]: All items matching the specified type
        """
        if not isinstance(item_type, str):
            return []
        
        return [item for item in self.items if item.item_type == item_type]
    
    def get_items_by_category(self, category: str) -> List[Item]:
        """
        Get all items in a specific category.
        
        Args:
            category: The category to retrieve items from
            
        Returns:
            List[Item]: All items in the specified category
        """
        if category not in self.ITEM_CATEGORIES:
            return []
        
        category_types = self.ITEM_CATEGORIES[category]
        return [item for item in self.items if item.item_type in category_types]
    
    def get_categories(self) -> Dict[str, List[Item]]:
        """
        Get all items organized by category.
        
        Returns:
            Dict[str, List[Item]]: Items organized by category
        """
        categorized_items = {}
        
        for category in self.ITEM_CATEGORIES:
            items = self.get_items_by_category(category)
            if items:  # Only include categories that have items
                categorized_items[category] = items
        
        # Add uncategorized items
        uncategorized = []
        all_category_types = set()
        for types in self.ITEM_CATEGORIES.values():
            all_category_types.update(types)
        
        for item in self.items:
            if item.item_type not in all_category_types:
                uncategorized.append(item)
        
        if uncategorized:
            categorized_items['other'] = uncategorized
        
        return categorized_items
    
    def is_full(self) -> bool:
        """
        Check if inventory is at maximum capacity.
        
        Returns:
            bool: True if inventory is full
        """
        return len(self.items) >= self.max_capacity
    
    def is_empty(self) -> bool:
        """
        Check if inventory is empty.
        
        Returns:
            bool: True if inventory has no items
        """
        return len(self.items) == 0
    
    def get_capacity_info(self) -> Dict[str, int]:
        """
        Get information about inventory capacity usage.
        
        Returns:
            Dict[str, int]: Dictionary with current, max, and available capacity
        """
        current = len(self.items)
        return {
            'current': current,
            'max': self.max_capacity,
            'available': self.max_capacity - current
        }
    
    def get_total_value(self) -> int:
        """
        Calculate the total value of all items in inventory.
        
        Returns:
            int: Sum of all item values
        """
        return sum(item.value for item in self.items)
    
    def clear(self) -> None:
        """Remove all items from inventory."""
        self.items.clear()
        self._item_counts.clear()
    
    def __len__(self) -> int:
        """Return the number of items in inventory."""
        return len(self.items)
    
    def __contains__(self, item_name: str) -> bool:
        """Check if inventory contains an item (supports 'in' operator)."""
        return self.has_item(item_name)
    
    def __str__(self) -> str:
        """Return a string representation of the inventory."""
        if self.is_empty():
            return "Inventory is empty"
        
        capacity_info = self.get_capacity_info()
        lines = [f"Inventory ({capacity_info['current']}/{capacity_info['max']} items):"]
        
        # Group items by name and show counts
        for item_name, count in self._item_counts.items():
            if count > 1:
                lines.append(f"  {item_name} x{count}")
            else:
                lines.append(f"  {item_name}")
        
        return "\n".join(lines)