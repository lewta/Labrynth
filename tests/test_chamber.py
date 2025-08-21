"""Unit tests for Chamber class."""

import pytest
from src.game.world import Chamber
from src.utils.data_models import Item
from src.utils.exceptions import GameException


class TestChamber:
    """Test cases for Chamber class."""
    
    def test_valid_chamber_creation(self):
        """Test creating a valid chamber."""
        chamber = Chamber(
            chamber_id=1,
            name="Entrance Hall",
            description="A dimly lit stone chamber with ancient carvings."
        )
        assert chamber.id == 1
        assert chamber.name == "Entrance Hall"
        assert chamber.description == "A dimly lit stone chamber with ancient carvings."
        assert chamber.challenge is None
        assert chamber.completed is False
        assert chamber.connections == {}
        assert chamber.items == []
    
    def test_invalid_chamber_negative_id(self):
        """Test chamber creation with negative ID."""
        with pytest.raises(GameException, match="Chamber ID must be a positive integer"):
            Chamber(
                chamber_id=-1,
                name="Test Chamber",
                description="Test description"
            )
    
    def test_invalid_chamber_zero_id(self):
        """Test chamber creation with zero ID."""
        with pytest.raises(GameException, match="Chamber ID must be a positive integer"):
            Chamber(
                chamber_id=0,
                name="Test Chamber",
                description="Test description"
            )
    
    def test_invalid_chamber_non_integer_id(self):
        """Test chamber creation with non-integer ID."""
        with pytest.raises(GameException, match="Chamber ID must be a positive integer"):
            Chamber(
                chamber_id="invalid",
                name="Test Chamber",
                description="Test description"
            )
    
    def test_invalid_chamber_empty_name(self):
        """Test chamber creation with empty name."""
        with pytest.raises(GameException, match="Chamber name must be a non-empty string"):
            Chamber(
                chamber_id=1,
                name="",
                description="Test description"
            )
    
    def test_invalid_chamber_none_name(self):
        """Test chamber creation with None name."""
        with pytest.raises(GameException, match="Chamber name must be a non-empty string"):
            Chamber(
                chamber_id=1,
                name=None,
                description="Test description"
            )
    
    def test_invalid_chamber_empty_description(self):
        """Test chamber creation with empty description."""
        with pytest.raises(GameException, match="Chamber description must be a non-empty string"):
            Chamber(
                chamber_id=1,
                name="Test Chamber",
                description=""
            )
    
    def test_invalid_chamber_none_description(self):
        """Test chamber creation with None description."""
        with pytest.raises(GameException, match="Chamber description must be a non-empty string"):
            Chamber(
                chamber_id=1,
                name="Test Chamber",
                description=None
            )
    
    def test_get_description_basic(self):
        """Test getting basic chamber description."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        description = chamber.get_description()
        expected = "Test Chamber\n\nA test chamber."
        assert description == expected
    
    def test_get_description_completed(self):
        """Test getting description of completed chamber."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.completed = True
        description = chamber.get_description()
        assert "[This chamber has been completed.]" in description
    
    def test_get_description_with_items(self):
        """Test getting description with items present."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        item1 = Item("Sword", "Sharp blade", "weapon", 50)
        item2 = Item("Potion", "Healing potion", "consumable", 25)
        chamber.add_item(item1)
        chamber.add_item(item2)
        description = chamber.get_description()
        assert "Items here: Sword, Potion" in description
    
    def test_add_connection_valid(self):
        """Test adding a valid connection."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.add_connection("north", 2)
        assert chamber.connections["north"] == 2
        assert "north" in chamber.get_exits()
    
    def test_add_connection_case_insensitive(self):
        """Test adding connection with different cases."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.add_connection("NORTH", 2)
        chamber.add_connection("South", 3)
        assert chamber.connections["north"] == 2
        assert chamber.connections["south"] == 3
    
    def test_add_connection_with_whitespace(self):
        """Test adding connection with whitespace."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.add_connection("  north  ", 2)
        assert chamber.connections["north"] == 2
    
    def test_add_connection_invalid_direction_empty(self):
        """Test adding connection with empty direction."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        with pytest.raises(GameException, match="Direction must be a non-empty string"):
            chamber.add_connection("", 2)
    
    def test_add_connection_invalid_direction_whitespace(self):
        """Test adding connection with whitespace-only direction."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        with pytest.raises(GameException, match="Direction must be a non-empty string"):
            chamber.add_connection("   ", 2)
    
    def test_add_connection_invalid_direction_non_string(self):
        """Test adding connection with non-string direction."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        with pytest.raises(GameException, match="Direction must be a non-empty string"):
            chamber.add_connection(123, 2)
    
    def test_add_connection_invalid_target_negative(self):
        """Test adding connection with negative target ID."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        with pytest.raises(GameException, match="Target chamber ID must be a positive integer"):
            chamber.add_connection("north", -1)
    
    def test_add_connection_invalid_target_zero(self):
        """Test adding connection with zero target ID."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        with pytest.raises(GameException, match="Target chamber ID must be a positive integer"):
            chamber.add_connection("north", 0)
    
    def test_add_connection_invalid_target_non_integer(self):
        """Test adding connection with non-integer target ID."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        with pytest.raises(GameException, match="Target chamber ID must be a positive integer"):
            chamber.add_connection("north", "invalid")
    
    def test_remove_connection_exists(self):
        """Test removing an existing connection."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.add_connection("north", 2)
        result = chamber.remove_connection("north")
        assert result is True
        assert "north" not in chamber.connections
    
    def test_remove_connection_not_exists(self):
        """Test removing a non-existent connection."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        result = chamber.remove_connection("north")
        assert result is False
    
    def test_remove_connection_case_insensitive(self):
        """Test removing connection with different case."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.add_connection("north", 2)
        result = chamber.remove_connection("NORTH")
        assert result is True
        assert "north" not in chamber.connections
    
    def test_remove_connection_invalid_direction(self):
        """Test removing connection with invalid direction type."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        with pytest.raises(GameException, match="Direction must be a string"):
            chamber.remove_connection(123)
    
    def test_get_connection_exists(self):
        """Test getting an existing connection."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.add_connection("north", 2)
        target = chamber.get_connection("north")
        assert target == 2
    
    def test_get_connection_not_exists(self):
        """Test getting a non-existent connection."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        target = chamber.get_connection("north")
        assert target is None
    
    def test_get_connection_case_insensitive(self):
        """Test getting connection with different case."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.add_connection("north", 2)
        target = chamber.get_connection("NORTH")
        assert target == 2
    
    def test_get_connection_invalid_direction(self):
        """Test getting connection with invalid direction type."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        target = chamber.get_connection(123)
        assert target is None
    
    def test_has_connection_exists(self):
        """Test checking for an existing connection."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.add_connection("north", 2)
        assert chamber.has_connection("north") is True
    
    def test_has_connection_not_exists(self):
        """Test checking for a non-existent connection."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        assert chamber.has_connection("north") is False
    
    def test_has_connection_case_insensitive(self):
        """Test checking connection with different case."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.add_connection("north", 2)
        assert chamber.has_connection("NORTH") is True
    
    def test_has_connection_invalid_direction(self):
        """Test checking connection with invalid direction type."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        assert chamber.has_connection(123) is False
    
    def test_get_exits_empty(self):
        """Test getting exits from chamber with no connections."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        exits = chamber.get_exits()
        assert exits == []
    
    def test_get_exits_multiple(self):
        """Test getting exits from chamber with multiple connections."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.add_connection("north", 2)
        chamber.add_connection("south", 3)
        chamber.add_connection("east", 4)
        exits = chamber.get_exits()
        assert set(exits) == {"north", "south", "east"}
    
    def test_set_challenge(self):
        """Test setting a challenge for the chamber."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        mock_challenge = "mock_challenge"  # Using string as mock
        chamber.set_challenge(mock_challenge)
        assert chamber.challenge == mock_challenge
    
    def test_complete_challenge_with_challenge(self):
        """Test completing a challenge when one exists."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.set_challenge("mock_challenge")
        result = chamber.complete_challenge()
        assert result is True
        assert chamber.completed is True
    
    def test_complete_challenge_without_challenge(self):
        """Test completing a challenge when none exists."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        result = chamber.complete_challenge()
        assert result is False
        assert chamber.completed is False
    
    def test_add_item_valid(self):
        """Test adding a valid item to the chamber."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        item = Item("Sword", "Sharp blade", "weapon", 50)
        chamber.add_item(item)
        assert len(chamber.items) == 1
        assert chamber.items[0] == item
    
    def test_add_item_invalid(self):
        """Test adding an invalid item to the chamber."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        with pytest.raises(GameException, match="Item must be an Item instance"):
            chamber.add_item("invalid_item")
    
    def test_remove_item_exists(self):
        """Test removing an existing item from the chamber."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        item = Item("Sword", "Sharp blade", "weapon", 50)
        chamber.add_item(item)
        removed_item = chamber.remove_item("Sword")
        assert removed_item == item
        assert len(chamber.items) == 0
    
    def test_remove_item_not_exists(self):
        """Test removing a non-existent item from the chamber."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        removed_item = chamber.remove_item("NonExistent")
        assert removed_item is None
    
    def test_remove_item_invalid_name(self):
        """Test removing item with invalid name type."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        removed_item = chamber.remove_item(123)
        assert removed_item is None
    
    def test_has_item_exists(self):
        """Test checking for an existing item."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        item = Item("Sword", "Sharp blade", "weapon", 50)
        chamber.add_item(item)
        assert chamber.has_item("Sword") is True
    
    def test_has_item_not_exists(self):
        """Test checking for a non-existent item."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        assert chamber.has_item("NonExistent") is False
    
    def test_has_item_invalid_name(self):
        """Test checking for item with invalid name type."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        assert chamber.has_item(123) is False
    
    def test_get_items_empty(self):
        """Test getting items from empty chamber."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        items = chamber.get_items()
        assert items == []
    
    def test_get_items_multiple(self):
        """Test getting multiple items from chamber."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        item1 = Item("Sword", "Sharp blade", "weapon", 50)
        item2 = Item("Potion", "Healing potion", "consumable", 25)
        chamber.add_item(item1)
        chamber.add_item(item2)
        items = chamber.get_items()
        assert len(items) == 2
        assert item1 in items
        assert item2 in items
    
    def test_get_items_returns_copy(self):
        """Test that get_items returns a copy, not the original list."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        item = Item("Sword", "Sharp blade", "weapon", 50)
        chamber.add_item(item)
        items = chamber.get_items()
        items.clear()  # Modify the returned list
        assert len(chamber.items) == 1  # Original should be unchanged
    
    def test_is_completed_true(self):
        """Test checking completion status when completed."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.completed = True
        assert chamber.is_completed() is True
    
    def test_is_completed_false(self):
        """Test checking completion status when not completed."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        assert chamber.is_completed() is False
    
    def test_reset(self):
        """Test resetting chamber to initial state."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.completed = True
        chamber.reset()
        assert chamber.completed is False
    
    def test_get_chamber_info(self):
        """Test getting comprehensive chamber information."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.add_connection("north", 2)
        chamber.add_connection("south", 3)
        item = Item("Sword", "Sharp blade", "weapon", 50)
        chamber.add_item(item)
        chamber.set_challenge("mock_challenge")
        chamber.completed = True
        
        info = chamber.get_chamber_info()
        expected = {
            'id': 1,
            'name': 'Test Chamber',
            'description': 'A test chamber.',
            'completed': True,
            'exits': ['north', 'south'],
            'items': ['Sword'],
            'has_challenge': True
        }
        
        assert info['id'] == expected['id']
        assert info['name'] == expected['name']
        assert info['description'] == expected['description']
        assert info['completed'] == expected['completed']
        assert set(info['exits']) == set(expected['exits'])
        assert info['items'] == expected['items']
        assert info['has_challenge'] == expected['has_challenge']
    
    def test_str_representation(self):
        """Test string representation of chamber."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        assert str(chamber) == "Chamber 1: Test Chamber"
    
    def test_repr_representation(self):
        """Test detailed string representation of chamber."""
        chamber = Chamber(1, "Test Chamber", "A test chamber.")
        chamber.add_connection("north", 2)
        chamber.completed = True
        repr_str = repr(chamber)
        assert "Chamber(id=1" in repr_str
        assert "name='Test Chamber'" in repr_str
        assert "completed=True" in repr_str
        assert "exits=['north']" in repr_str