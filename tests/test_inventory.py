"""Unit tests for the Inventory class."""

import pytest
from src.game.inventory import Inventory
from src.utils.data_models import Item
from src.utils.exceptions import GameException


class TestInventory:
    """Test cases for the Inventory class."""
    
    def test_inventory_initialization(self):
        """Test inventory initialization with default and custom capacity."""
        # Default capacity
        inventory = Inventory()
        assert inventory.max_capacity == 20
        assert inventory.is_empty()
        assert len(inventory) == 0
        
        # Custom capacity
        inventory = Inventory(max_capacity=10)
        assert inventory.max_capacity == 10
        assert inventory.is_empty()
    
    def test_inventory_initialization_invalid_capacity(self):
        """Test inventory initialization with invalid capacity values."""
        with pytest.raises(GameException, match="Max capacity must be a positive integer"):
            Inventory(max_capacity=0)
        
        with pytest.raises(GameException, match="Max capacity must be a positive integer"):
            Inventory(max_capacity=-5)
        
        with pytest.raises(GameException, match="Max capacity must be a positive integer"):
            Inventory(max_capacity="invalid")
    
    def test_add_item_success(self):
        """Test successfully adding items to inventory."""
        inventory = Inventory(max_capacity=5)
        item = Item("Health Potion", "Restores 50 HP", "potion", 25)
        
        result = inventory.add_item(item)
        assert result is True
        assert not inventory.is_empty()
        assert len(inventory) == 1
        assert inventory.has_item("Health Potion")
        assert inventory.get_item_count("Health Potion") == 1
    
    def test_add_item_invalid(self):
        """Test adding invalid items to inventory."""
        inventory = Inventory()
        
        with pytest.raises(GameException, match="Item must be an Item instance"):
            inventory.add_item("not an item")
        
        with pytest.raises(GameException, match="Item must be an Item instance"):
            inventory.add_item(None)
    
    def test_add_item_capacity_limit(self):
        """Test inventory capacity limits."""
        inventory = Inventory(max_capacity=2)
        item1 = Item("Sword", "A sharp blade", "sword", 100)
        item2 = Item("Shield", "Protective gear", "shield", 75)
        item3 = Item("Potion", "Healing item", "potion", 25)
        
        # Add items up to capacity
        assert inventory.add_item(item1) is True
        assert inventory.add_item(item2) is True
        assert inventory.is_full()
        
        # Try to add beyond capacity
        assert inventory.add_item(item3) is False
        assert len(inventory) == 2
        assert not inventory.has_item("Potion")
    
    def test_remove_item_success(self):
        """Test successfully removing items from inventory."""
        inventory = Inventory()
        item = Item("Magic Ring", "Increases luck", "jewelry", 200)
        
        inventory.add_item(item)
        removed_item = inventory.remove_item("Magic Ring")
        
        assert removed_item is not None
        assert removed_item.name == "Magic Ring"
        assert not inventory.has_item("Magic Ring")
        assert inventory.get_item_count("Magic Ring") == 0
        assert inventory.is_empty()
    
    def test_remove_item_not_found(self):
        """Test removing items that don't exist."""
        inventory = Inventory()
        item = Item("Torch", "Provides light", "torch", 10)
        inventory.add_item(item)
        
        removed_item = inventory.remove_item("Nonexistent Item")
        assert removed_item is None
        assert len(inventory) == 1  # Original item still there
    
    def test_remove_item_invalid_name(self):
        """Test removing items with invalid names."""
        inventory = Inventory()
        
        with pytest.raises(GameException, match="Item name must be a non-empty string"):
            inventory.remove_item("")
        
        with pytest.raises(GameException, match="Item name must be a non-empty string"):
            inventory.remove_item("   ")
        
        with pytest.raises(GameException, match="Item name must be a non-empty string"):
            inventory.remove_item(123)
    
    def test_use_item_success(self):
        """Test successfully using items from inventory."""
        inventory = Inventory()
        item = Item("Health Potion", "Restores HP", "potion", 25, usable=True)
        
        inventory.add_item(item)
        used_item = inventory.use_item("Health Potion")
        
        assert used_item is not None
        assert used_item.name == "Health Potion"
        assert not inventory.has_item("Health Potion")
        assert inventory.is_empty()
    
    def test_use_item_not_usable(self):
        """Test using items that are not usable."""
        inventory = Inventory()
        item = Item("Ancient Artifact", "Cannot be used", "artifact", 500, usable=False)
        
        inventory.add_item(item)
        
        with pytest.raises(GameException, match="Item 'Ancient Artifact' is not usable"):
            inventory.use_item("Ancient Artifact")
        
        # Item should still be in inventory
        assert inventory.has_item("Ancient Artifact")
    
    def test_use_item_not_found(self):
        """Test using items that don't exist."""
        inventory = Inventory()
        used_item = inventory.use_item("Nonexistent Item")
        assert used_item is None
    
    def test_multiple_same_items(self):
        """Test handling multiple items with the same name."""
        inventory = Inventory()
        item1 = Item("Arrow", "Sharp projectile", "arrow", 5)
        item2 = Item("Arrow", "Sharp projectile", "arrow", 5)
        item3 = Item("Arrow", "Sharp projectile", "arrow", 5)
        
        inventory.add_item(item1)
        inventory.add_item(item2)
        inventory.add_item(item3)
        
        assert inventory.get_item_count("Arrow") == 3
        assert len(inventory) == 3
        
        # Remove one arrow
        removed = inventory.remove_item("Arrow")
        assert removed is not None
        assert inventory.get_item_count("Arrow") == 2
        assert len(inventory) == 2
    
    def test_get_items_by_type(self):
        """Test retrieving items by type."""
        inventory = Inventory()
        sword = Item("Iron Sword", "A sturdy blade", "sword", 100)
        dagger = Item("Steel Dagger", "A quick blade", "dagger", 75)
        potion = Item("Health Potion", "Restores HP", "potion", 25)
        
        inventory.add_item(sword)
        inventory.add_item(dagger)
        inventory.add_item(potion)
        
        swords = inventory.get_items_by_type("sword")
        assert len(swords) == 1
        assert swords[0].name == "Iron Sword"
        
        potions = inventory.get_items_by_type("potion")
        assert len(potions) == 1
        assert potions[0].name == "Health Potion"
        
        bows = inventory.get_items_by_type("bow")
        assert len(bows) == 0
    
    def test_get_items_by_category(self):
        """Test retrieving items by category."""
        inventory = Inventory()
        sword = Item("Iron Sword", "A sturdy blade", "sword", 100)
        dagger = Item("Steel Dagger", "A quick blade", "dagger", 75)
        helmet = Item("Iron Helmet", "Protective headgear", "helmet", 50)
        potion = Item("Health Potion", "Restores HP", "potion", 25)
        
        inventory.add_item(sword)
        inventory.add_item(dagger)
        inventory.add_item(helmet)
        inventory.add_item(potion)
        
        weapons = inventory.get_items_by_category("weapon")
        assert len(weapons) == 2
        weapon_names = [item.name for item in weapons]
        assert "Iron Sword" in weapon_names
        assert "Steel Dagger" in weapon_names
        
        armor = inventory.get_items_by_category("armor")
        assert len(armor) == 1
        assert armor[0].name == "Iron Helmet"
        
        consumables = inventory.get_items_by_category("consumable")
        assert len(consumables) == 1
        assert consumables[0].name == "Health Potion"
        
        # Test invalid category
        invalid = inventory.get_items_by_category("invalid_category")
        assert len(invalid) == 0
    
    def test_get_categories(self):
        """Test getting all items organized by category."""
        inventory = Inventory()
        sword = Item("Iron Sword", "A sturdy blade", "sword", 100)
        helmet = Item("Iron Helmet", "Protective headgear", "helmet", 50)
        potion = Item("Health Potion", "Restores HP", "potion", 25)
        unknown = Item("Mystery Item", "Unknown purpose", "mystery", 1)
        
        inventory.add_item(sword)
        inventory.add_item(helmet)
        inventory.add_item(potion)
        inventory.add_item(unknown)
        
        categories = inventory.get_categories()
        
        assert "weapon" in categories
        assert len(categories["weapon"]) == 1
        assert categories["weapon"][0].name == "Iron Sword"
        
        assert "armor" in categories
        assert len(categories["armor"]) == 1
        assert categories["armor"][0].name == "Iron Helmet"
        
        assert "consumable" in categories
        assert len(categories["consumable"]) == 1
        assert categories["consumable"][0].name == "Health Potion"
        
        assert "other" in categories
        assert len(categories["other"]) == 1
        assert categories["other"][0].name == "Mystery Item"
    
    def test_capacity_info(self):
        """Test getting capacity information."""
        inventory = Inventory(max_capacity=5)
        item = Item("Test Item", "For testing", "test", 1)
        
        # Empty inventory
        info = inventory.get_capacity_info()
        assert info["current"] == 0
        assert info["max"] == 5
        assert info["available"] == 5
        
        # Add some items
        inventory.add_item(item)
        inventory.add_item(item)
        
        info = inventory.get_capacity_info()
        assert info["current"] == 2
        assert info["max"] == 5
        assert info["available"] == 3
    
    def test_total_value(self):
        """Test calculating total inventory value."""
        inventory = Inventory()
        
        # Empty inventory
        assert inventory.get_total_value() == 0
        
        # Add items with different values
        item1 = Item("Cheap Item", "Low value", "misc", 10)
        item2 = Item("Expensive Item", "High value", "treasure", 100)
        item3 = Item("Medium Item", "Medium value", "tool", 50)
        
        inventory.add_item(item1)
        inventory.add_item(item2)
        inventory.add_item(item3)
        
        assert inventory.get_total_value() == 160
    
    def test_clear_inventory(self):
        """Test clearing all items from inventory."""
        inventory = Inventory()
        item1 = Item("Item 1", "First item", "misc", 10)
        item2 = Item("Item 2", "Second item", "misc", 20)
        
        inventory.add_item(item1)
        inventory.add_item(item2)
        assert len(inventory) == 2
        
        inventory.clear()
        assert inventory.is_empty()
        assert len(inventory) == 0
        assert inventory.get_total_value() == 0
    
    def test_contains_operator(self):
        """Test the 'in' operator for checking item existence."""
        inventory = Inventory()
        item = Item("Test Item", "For testing", "test", 1)
        
        assert "Test Item" not in inventory
        
        inventory.add_item(item)
        assert "Test Item" in inventory
        
        inventory.remove_item("Test Item")
        assert "Test Item" not in inventory
    
    def test_string_representation(self):
        """Test string representation of inventory."""
        inventory = Inventory()
        
        # Empty inventory
        assert str(inventory) == "Inventory is empty"
        
        # Add items
        item1 = Item("Sword", "A blade", "sword", 100)
        item2 = Item("Potion", "Healing item", "potion", 25)
        item3 = Item("Potion", "Another healing item", "potion", 25)
        
        inventory.add_item(item1)
        inventory.add_item(item2)
        inventory.add_item(item3)
        
        inventory_str = str(inventory)
        assert "Inventory (3/20 items):" in inventory_str
        assert "Sword" in inventory_str
        assert "Potion x2" in inventory_str
    
    def test_edge_cases(self):
        """Test various edge cases and boundary conditions."""
        inventory = Inventory(max_capacity=1)
        
        # Test with capacity of 1
        item = Item("Single Item", "Only item", "misc", 1)
        assert inventory.add_item(item) is True
        assert inventory.is_full()
        assert not inventory.is_empty()
        
        # Test invalid item type parameter
        assert inventory.get_items_by_type(None) == []
        assert inventory.get_items_by_type(123) == []
        
        # Test has_item with invalid parameter
        assert inventory.has_item(None) is False
        assert inventory.has_item(123) is False
        
        # Test get_item_count with invalid parameter
        assert inventory.get_item_count(None) == 0
        assert inventory.get_item_count(123) == 0