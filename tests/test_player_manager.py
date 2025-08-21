"""Unit tests for the PlayerManager class."""

import pytest
from src.game.player import PlayerManager
from src.utils.data_models import Item, PlayerStats
from src.utils.exceptions import GameException


class TestPlayerManager:
    """Test cases for the PlayerManager class."""
    
    def test_player_manager_initialization(self):
        """Test player manager initialization with default and custom values."""
        # Default initialization
        player = PlayerManager()
        assert player.max_health == 100
        assert player.current_health == 100
        assert player.is_alive()
        assert player.is_at_full_health()
        assert player.get_level() == 1
        assert player.get_experience() == 0
        
        # Custom initialization
        player = PlayerManager(max_health=150, max_inventory_capacity=30)
        assert player.max_health == 150
        assert player.current_health == 150
        assert player.inventory.max_capacity == 30
    
    def test_player_manager_initialization_invalid(self):
        """Test player manager initialization with invalid values."""
        with pytest.raises(GameException, match="Max health must be a positive integer"):
            PlayerManager(max_health=0)
        
        with pytest.raises(GameException, match="Max health must be a positive integer"):
            PlayerManager(max_health=-10)
        
        with pytest.raises(GameException, match="Max inventory capacity must be a positive integer"):
            PlayerManager(max_inventory_capacity=0)
    
    def test_take_damage(self):
        """Test taking damage and health management."""
        player = PlayerManager(max_health=100)
        
        # Take some damage
        result = player.take_damage(30)
        assert result is True  # Still alive
        assert player.current_health == 70
        assert player.is_alive()
        assert not player.is_at_full_health()
        
        # Take more damage
        result = player.take_damage(50)
        assert result is True  # Still alive
        assert player.current_health == 20
        
        # Take fatal damage
        result = player.take_damage(25)
        assert result is False  # Dead
        assert player.current_health == 0
        assert not player.is_alive()
    
    def test_take_damage_invalid(self):
        """Test taking damage with invalid values."""
        player = PlayerManager()
        
        with pytest.raises(GameException, match="Damage amount must be a non-negative integer"):
            player.take_damage(-5)
        
        with pytest.raises(GameException, match="Damage amount must be a non-negative integer"):
            player.take_damage("invalid")
    
    def test_heal(self):
        """Test healing functionality."""
        player = PlayerManager(max_health=100)
        
        # Take damage first
        player.take_damage(40)
        assert player.current_health == 60
        
        # Heal partially
        healed = player.heal(20)
        assert healed == 20
        assert player.current_health == 80
        
        # Heal beyond max health
        healed = player.heal(30)
        assert healed == 20  # Only healed to max
        assert player.current_health == 100
        assert player.is_at_full_health()
        
        # Try to heal when at full health
        healed = player.heal(10)
        assert healed == 0
        assert player.current_health == 100
    
    def test_heal_invalid(self):
        """Test healing with invalid values."""
        player = PlayerManager()
        
        with pytest.raises(GameException, match="Heal amount must be a non-negative integer"):
            player.heal(-5)
        
        with pytest.raises(GameException, match="Heal amount must be a non-negative integer"):
            player.heal("invalid")
    
    def test_stat_management(self):
        """Test stat modification and retrieval."""
        player = PlayerManager()
        
        # Check initial stats
        assert player.get_stat("strength") == 10
        assert player.get_stat("intelligence") == 10
        assert player.get_stat("dexterity") == 10
        assert player.get_stat("luck") == 10
        
        # Modify stats
        player.modify_stat("strength", 5)
        assert player.get_stat("strength") == 15
        
        player.modify_stat("intelligence", -3)
        assert player.get_stat("intelligence") == 7
        
        # Test stat floor (can't go below 0)
        player.modify_stat("intelligence", -10)
        assert player.get_stat("intelligence") == 0
    
    def test_stat_management_invalid(self):
        """Test stat management with invalid values."""
        player = PlayerManager()
        
        with pytest.raises(GameException, match="Stat name must be a non-empty string"):
            player.modify_stat("", 5)
        
        with pytest.raises(GameException, match="Stat modification amount must be an integer"):
            player.modify_stat("strength", "invalid")
        
        with pytest.raises(GameException, match="Unknown stat"):
            player.get_stat("invalid_stat")
    
    def test_inventory_integration(self):
        """Test inventory management through player manager."""
        player = PlayerManager()
        item = Item("Health Potion", "Restores HP", "potion", 50)
        
        # Add item
        result = player.add_item(item)
        assert result is True
        assert player.has_item("Health Potion")
        assert player.get_item_count("Health Potion") == 1
        
        # Remove item
        removed_item = player.remove_item("Health Potion")
        assert removed_item is not None
        assert removed_item.name == "Health Potion"
        assert not player.has_item("Health Potion")
    
    def test_use_item_healing(self):
        """Test using healing items."""
        player = PlayerManager()
        
        # Take damage first
        player.take_damage(40)
        assert player.current_health == 60
        
        # Add and use a health potion
        potion = Item("Health Potion", "Restores HP", "potion", 50)
        player.add_item(potion)
        
        used_item = player.use_item("Health Potion")
        assert used_item is not None
        assert used_item.name == "Health Potion"
        assert not player.has_item("Health Potion")  # Item consumed
        assert player.current_health == 85  # 60 + (50/2) = 85
    
    def test_use_item_stat_scrolls(self):
        """Test using stat-boosting scrolls."""
        player = PlayerManager()
        
        # Test strength scroll
        strength_scroll = Item("Strength Scroll", "Boosts strength", "scroll", 100)
        player.add_item(strength_scroll)
        
        initial_strength = player.get_stat("strength")
        used_item = player.use_item("Strength Scroll")
        assert used_item is not None
        assert player.get_stat("strength") == initial_strength + 1
        
        # Test intelligence scroll
        intelligence_scroll = Item("Intelligence Scroll", "Boosts intelligence", "scroll", 100)
        player.add_item(intelligence_scroll)
        
        initial_intelligence = player.get_stat("intelligence")
        used_item = player.use_item("Intelligence Scroll")
        assert used_item is not None
        assert player.get_stat("intelligence") == initial_intelligence + 1
    
    def test_use_item_food(self):
        """Test using food items."""
        player = PlayerManager()
        
        # Take damage first
        player.take_damage(20)
        assert player.current_health == 80
        
        # Add and use food
        bread = Item("Bread", "Nutritious food", "food", 25)
        player.add_item(bread)
        
        used_item = player.use_item("Bread")
        assert used_item is not None
        assert player.current_health == 85  # 80 + max(1, 25/5) = 85
    
    def test_experience_and_leveling(self):
        """Test experience gain and leveling up."""
        player = PlayerManager()
        
        # Initial state
        assert player.get_level() == 1
        assert player.get_experience() == 0
        assert player.get_experience_to_next_level() == 100
        
        # Add some experience (not enough to level)
        leveled_up = player.add_experience(50)
        assert leveled_up is False
        assert player.get_level() == 1
        assert player.get_experience() == 50
        assert player.get_experience_to_next_level() == 50
        
        # Add enough experience to level up
        leveled_up = player.add_experience(50)
        assert leveled_up is True
        assert player.get_level() == 2
        assert player.get_experience() == 100
        assert player.get_experience_to_next_level() == 100  # Need 200 total for level 3
        
        # Check level up benefits
        assert player.max_health == 110  # 100 + 10
        assert player.current_health == 110  # Full heal on level up
        assert player.get_stat("strength") == 11  # 10 + 1
        assert player.get_stat("intelligence") == 11
        assert player.get_stat("dexterity") == 11
        assert player.get_stat("luck") == 11
    
    def test_experience_invalid(self):
        """Test adding invalid experience values."""
        player = PlayerManager()
        
        with pytest.raises(GameException, match="Experience amount must be a non-negative integer"):
            player.add_experience(-10)
        
        with pytest.raises(GameException, match="Experience amount must be a non-negative integer"):
            player.add_experience("invalid")
    
    def test_health_percentage(self):
        """Test health percentage calculation."""
        player = PlayerManager(max_health=100)
        
        assert player.get_health_percentage() == 1.0
        
        player.take_damage(25)
        assert player.get_health_percentage() == 0.75
        
        player.take_damage(50)
        assert player.get_health_percentage() == 0.25
        
        player.take_damage(25)
        assert player.get_health_percentage() == 0.0
    
    def test_get_status(self):
        """Test comprehensive status information."""
        player = PlayerManager()
        
        # Add some items and modify state
        item = Item("Test Item", "For testing", "misc", 100)
        player.add_item(item)
        player.take_damage(20)
        player.add_experience(50)
        player.modify_stat("strength", 5)
        
        status = player.get_status()
        
        # Check structure and values
        assert 'health' in status
        assert status['health']['current'] == 80
        assert status['health']['max'] == 100
        assert status['health']['percentage'] == 0.8
        
        assert status['level'] == 1
        
        assert 'experience' in status
        assert status['experience']['current'] == 50
        assert status['experience']['to_next_level'] == 50
        
        assert 'stats' in status
        assert status['stats']['strength'] == 15
        assert status['stats']['intelligence'] == 10
        
        assert 'inventory' in status
        assert status['inventory']['items'] == 1
        assert status['inventory']['total_value'] == 100
        
        assert status['alive'] is True
    
    def test_get_combat_stats(self):
        """Test combat-relevant stats calculation."""
        player = PlayerManager()
        
        # Modify some stats
        player.modify_stat("strength", 5)
        player.modify_stat("dexterity", 3)
        player.modify_stat("luck", 2)
        
        combat_stats = player.get_combat_stats()
        
        assert combat_stats['attack_power'] == 15  # 15 strength + 0 level bonus
        assert combat_stats['defense'] == 13  # 13 dexterity + 0 level bonus
        assert combat_stats['accuracy'] == 25  # 13 dex + 12 luck
        assert combat_stats['critical_chance'] == 12  # 12 luck
        assert combat_stats['health'] == 100
        assert combat_stats['max_health'] == 100
        
        # Test with level up
        player.add_experience(100)  # Level up to 2
        combat_stats = player.get_combat_stats()
        
        assert combat_stats['attack_power'] == 18  # 16 strength + 2 level bonus
        assert combat_stats['defense'] == 15  # 14 dexterity + 1 level bonus
    
    def test_reset_to_defaults(self):
        """Test resetting player to default state."""
        player = PlayerManager()
        
        # Modify player state
        item = Item("Test Item", "For testing", "misc", 50)
        player.add_item(item)
        player.take_damage(30)
        player.add_experience(75)
        player.modify_stat("strength", 10)
        
        # Verify modified state
        assert player.current_health == 70
        assert player.get_experience() == 75
        assert player.get_stat("strength") == 20
        assert player.has_item("Test Item")
        
        # Reset to defaults
        player.reset_to_defaults()
        
        # Verify reset state
        assert player.current_health == 100
        assert player.max_health == 100
        assert player.get_experience() == 0
        assert player.get_level() == 1
        assert player.get_stat("strength") == 10
        assert player.get_stat("intelligence") == 10
        assert player.get_stat("dexterity") == 10
        assert player.get_stat("luck") == 10
        assert not player.has_item("Test Item")
        assert len(player.inventory) == 0
    
    def test_string_representation(self):
        """Test string representation of player status."""
        player = PlayerManager()
        
        # Add some state
        item = Item("Test Item", "For testing", "misc", 50)
        player.add_item(item)
        player.take_damage(25)
        player.add_experience(30)
        
        player_str = str(player)
        
        assert "Player Status (Level 1):" in player_str
        assert "Health: 75/100 (75.0%)" in player_str
        assert "Experience: 30 (70 to next level)" in player_str
        assert "Stats: STR 10, INT 10, DEX 10, LCK 10" in player_str
        assert "Inventory: 1/20 items (value: 50)" in player_str
    
    def test_edge_cases(self):
        """Test various edge cases and boundary conditions."""
        player = PlayerManager(max_health=1, max_inventory_capacity=1)
        
        # Test with minimal health
        assert player.current_health == 1
        assert player.is_alive()
        
        player.take_damage(1)
        assert player.current_health == 0
        assert not player.is_alive()
        
        # Test healing when dead
        healed = player.heal(10)
        assert healed == 1  # Can heal from 0 to 1
        assert player.current_health == 1
        assert player.is_alive()
        
        # Test inventory at capacity
        item = Item("Only Item", "Single item", "misc", 1)
        assert player.add_item(item) is True
        
        item2 = Item("Second Item", "Won't fit", "misc", 1)
        assert player.add_item(item2) is False
    
    def test_item_effects_edge_cases(self):
        """Test edge cases in item effect application."""
        player = PlayerManager()
        
        # Test potion with very low value
        weak_potion = Item("Weak Potion", "Barely helps", "potion", 1)
        player.add_item(weak_potion)
        player.take_damage(10)
        
        initial_health = player.current_health
        player.use_item("Weak Potion")
        # Should heal at least 0 (1//2 = 0, but heal method handles this)
        assert player.current_health >= initial_health
        
        # Test food with very low value
        crumb = Item("Bread Crumb", "Tiny morsel", "food", 1)
        player.add_item(crumb)
        
        initial_health = player.current_health
        player.use_item("Bread Crumb")
        # Should heal at least 1 (max(1, 1//5) = 1)
        assert player.current_health == initial_health + 1