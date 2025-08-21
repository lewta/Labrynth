"""Unit tests for data models."""

import pytest
from src.utils.data_models import Item, ChallengeResult, PlayerStats, GameState
from src.utils.exceptions import GameException


class TestItem:
    """Test cases for Item data model."""
    
    def test_valid_item_creation(self):
        """Test creating a valid item."""
        item = Item(
            name="Health Potion",
            description="Restores 50 health points",
            item_type="consumable",
            value=25,
            usable=True
        )
        assert item.name == "Health Potion"
        assert item.description == "Restores 50 health points"
        assert item.item_type == "consumable"
        assert item.value == 25
        assert item.usable is True
        assert item.is_valid() is True
    
    def test_item_with_defaults(self):
        """Test creating an item with default values."""
        item = Item(
            name="Ancient Key",
            description="Opens mysterious doors",
            item_type="key",
            value=0
        )
        assert item.usable is True  # Default value
        assert item.is_valid() is True
    
    def test_invalid_item_empty_name(self):
        """Test item creation with empty name."""
        with pytest.raises(GameException, match="Item name must be a non-empty string"):
            Item(
                name="",
                description="Test description",
                item_type="test",
                value=10
            )
    
    def test_invalid_item_none_name(self):
        """Test item creation with None name."""
        with pytest.raises(GameException, match="Item name must be a non-empty string"):
            Item(
                name=None,
                description="Test description",
                item_type="test",
                value=10
            )
    
    def test_invalid_item_empty_description(self):
        """Test item creation with empty description."""
        with pytest.raises(GameException, match="Item description must be a non-empty string"):
            Item(
                name="Test Item",
                description="",
                item_type="test",
                value=10
            )
    
    def test_invalid_item_empty_type(self):
        """Test item creation with empty type."""
        with pytest.raises(GameException, match="Item type must be a non-empty string"):
            Item(
                name="Test Item",
                description="Test description",
                item_type="",
                value=10
            )
    
    def test_invalid_item_negative_value(self):
        """Test item creation with negative value."""
        with pytest.raises(GameException, match="Item value must be a non-negative integer"):
            Item(
                name="Test Item",
                description="Test description",
                item_type="test",
                value=-5
            )
    
    def test_invalid_item_non_integer_value(self):
        """Test item creation with non-integer value."""
        with pytest.raises(GameException, match="Item value must be a non-negative integer"):
            Item(
                name="Test Item",
                description="Test description",
                item_type="test",
                value="invalid"
            )
    
    def test_invalid_item_non_boolean_usable(self):
        """Test item creation with non-boolean usable."""
        with pytest.raises(GameException, match="Item usable must be a boolean"):
            Item(
                name="Test Item",
                description="Test description",
                item_type="test",
                value=10,
                usable="yes"
            )


class TestChallengeResult:
    """Test cases for ChallengeResult data model."""
    
    def test_valid_challenge_result_success(self):
        """Test creating a successful challenge result."""
        item = Item("Reward", "Test reward", "treasure", 100)
        result = ChallengeResult(
            success=True,
            message="Challenge completed successfully!",
            reward=item,
            damage=0
        )
        assert result.success is True
        assert result.message == "Challenge completed successfully!"
        assert result.reward == item
        assert result.damage == 0
        assert result.is_valid() is True
    
    def test_valid_challenge_result_failure(self):
        """Test creating a failed challenge result."""
        result = ChallengeResult(
            success=False,
            message="Challenge failed. Try again.",
            reward=None,
            damage=10
        )
        assert result.success is False
        assert result.message == "Challenge failed. Try again."
        assert result.reward is None
        assert result.damage == 10
        assert result.is_valid() is True
    
    def test_challenge_result_with_defaults(self):
        """Test creating a challenge result with default values."""
        result = ChallengeResult(
            success=True,
            message="Success!"
        )
        assert result.reward is None  # Default value
        assert result.damage == 0  # Default value
        assert result.is_valid() is True
    
    def test_invalid_challenge_result_non_boolean_success(self):
        """Test challenge result with non-boolean success."""
        with pytest.raises(GameException, match="Challenge result success must be a boolean"):
            ChallengeResult(
                success="yes",
                message="Test message"
            )
    
    def test_invalid_challenge_result_empty_message(self):
        """Test challenge result with empty message."""
        with pytest.raises(GameException, match="Challenge result message must be a non-empty string"):
            ChallengeResult(
                success=True,
                message=""
            )
    
    def test_invalid_challenge_result_none_message(self):
        """Test challenge result with None message."""
        with pytest.raises(GameException, match="Challenge result message must be a non-empty string"):
            ChallengeResult(
                success=True,
                message=None
            )
    
    def test_invalid_challenge_result_invalid_reward(self):
        """Test challenge result with invalid reward type."""
        with pytest.raises(GameException, match="Challenge result reward must be an Item or None"):
            ChallengeResult(
                success=True,
                message="Test message",
                reward="invalid_reward"
            )
    
    def test_invalid_challenge_result_negative_damage(self):
        """Test challenge result with negative damage."""
        with pytest.raises(GameException, match="Challenge result damage must be a non-negative integer"):
            ChallengeResult(
                success=True,
                message="Test message",
                damage=-5
            )
    
    def test_invalid_challenge_result_non_integer_damage(self):
        """Test challenge result with non-integer damage."""
        with pytest.raises(GameException, match="Challenge result damage must be a non-negative integer"):
            ChallengeResult(
                success=True,
                message="Test message",
                damage="invalid"
            )


class TestPlayerStats:
    """Test cases for PlayerStats data model."""
    
    def test_valid_player_stats_creation(self):
        """Test creating valid player stats."""
        stats = PlayerStats(
            strength=15,
            intelligence=12,
            dexterity=8,
            luck=20
        )
        assert stats.strength == 15
        assert stats.intelligence == 12
        assert stats.dexterity == 8
        assert stats.luck == 20
        assert stats.is_valid() is True
    
    def test_player_stats_with_defaults(self):
        """Test creating player stats with default values."""
        stats = PlayerStats()
        assert stats.strength == 10
        assert stats.intelligence == 10
        assert stats.dexterity == 10
        assert stats.luck == 10
        assert stats.is_valid() is True
    
    def test_modify_stat_positive(self):
        """Test modifying a stat with positive amount."""
        stats = PlayerStats()
        stats.modify_stat("strength", 5)
        assert stats.strength == 15
    
    def test_modify_stat_negative(self):
        """Test modifying a stat with negative amount."""
        stats = PlayerStats(strength=15)
        stats.modify_stat("strength", -10)
        assert stats.strength == 5
    
    def test_modify_stat_below_zero(self):
        """Test modifying a stat below zero (should clamp to 0)."""
        stats = PlayerStats(strength=5)
        stats.modify_stat("strength", -10)
        assert stats.strength == 0
    
    def test_modify_stat_invalid_name(self):
        """Test modifying a non-existent stat."""
        stats = PlayerStats()
        with pytest.raises(GameException, match="Unknown stat: invalid_stat"):
            stats.modify_stat("invalid_stat", 5)
    
    def test_modify_stat_invalid_name_type(self):
        """Test modifying a stat with invalid name type."""
        stats = PlayerStats()
        with pytest.raises(GameException, match="Stat name must be a string"):
            stats.modify_stat(123, 5)
    
    def test_modify_stat_invalid_amount_type(self):
        """Test modifying a stat with invalid amount type."""
        stats = PlayerStats()
        with pytest.raises(GameException, match="Stat modification amount must be an integer"):
            stats.modify_stat("strength", "invalid")
    
    def test_get_stat_valid(self):
        """Test getting a valid stat."""
        stats = PlayerStats(strength=15)
        assert stats.get_stat("strength") == 15
    
    def test_get_stat_invalid(self):
        """Test getting an invalid stat."""
        stats = PlayerStats()
        with pytest.raises(GameException, match="Unknown stat: invalid_stat"):
            stats.get_stat("invalid_stat")
    
    def test_invalid_player_stats_negative_strength(self):
        """Test player stats with negative strength."""
        with pytest.raises(GameException, match="Player stat strength must be a non-negative integer"):
            PlayerStats(strength=-5)
    
    def test_invalid_player_stats_non_integer_intelligence(self):
        """Test player stats with non-integer intelligence."""
        with pytest.raises(GameException, match="Player stat intelligence must be a non-negative integer"):
            PlayerStats(intelligence="invalid")
    
    def test_invalid_player_stats_negative_dexterity(self):
        """Test player stats with negative dexterity."""
        with pytest.raises(GameException, match="Player stat dexterity must be a non-negative integer"):
            PlayerStats(dexterity=-1)
    
    def test_invalid_player_stats_negative_luck(self):
        """Test player stats with negative luck."""
        with pytest.raises(GameException, match="Player stat luck must be a non-negative integer"):
            PlayerStats(luck=-10)


class TestGameState:
    """Test cases for GameState data model."""
    
    def test_valid_game_state_creation(self):
        """Test creating a valid game state."""
        item = Item("Test Item", "Description", "type", 10)
        stats = PlayerStats(strength=15)
        state = GameState(
            current_chamber=1,
            player_health=100,
            inventory_items=[item],
            completed_chambers={1, 2, 3},
            game_time=300,
            player_stats=stats
        )
        assert state.current_chamber == 1
        assert state.player_health == 100
        assert len(state.inventory_items) == 1
        assert state.inventory_items[0] == item
        assert state.completed_chambers == {1, 2, 3}
        assert state.game_time == 300
        assert state.player_stats == stats
        assert state.is_valid() is True
    
    def test_game_state_with_defaults(self):
        """Test creating a game state with default values."""
        state = GameState(
            current_chamber=1,
            player_health=100
        )
        assert state.inventory_items == []
        assert state.completed_chambers == set()
        assert state.game_time == 0
        assert isinstance(state.player_stats, PlayerStats)
        assert state.is_valid() is True
    
    def test_add_completed_chamber(self):
        """Test adding a completed chamber."""
        state = GameState(current_chamber=1, player_health=100)
        state.add_completed_chamber(5)
        assert 5 in state.completed_chambers
    
    def test_add_completed_chamber_invalid(self):
        """Test adding an invalid completed chamber."""
        state = GameState(current_chamber=1, player_health=100)
        with pytest.raises(GameException, match="Chamber ID must be a positive integer"):
            state.add_completed_chamber(-1)
    
    def test_is_chamber_completed(self):
        """Test checking if a chamber is completed."""
        state = GameState(
            current_chamber=1,
            player_health=100,
            completed_chambers={1, 3, 5}
        )
        assert state.is_chamber_completed(1) is True
        assert state.is_chamber_completed(2) is False
        assert state.is_chamber_completed(3) is True
    
    def test_add_inventory_item(self):
        """Test adding an item to inventory."""
        state = GameState(current_chamber=1, player_health=100)
        item = Item("Sword", "Sharp blade", "weapon", 50)
        state.add_inventory_item(item)
        assert len(state.inventory_items) == 1
        assert state.inventory_items[0] == item
    
    def test_add_inventory_item_invalid(self):
        """Test adding an invalid item to inventory."""
        state = GameState(current_chamber=1, player_health=100)
        with pytest.raises(GameException, match="Item must be an Item instance"):
            state.add_inventory_item("invalid_item")
    
    def test_remove_inventory_item_exists(self):
        """Test removing an existing item from inventory."""
        item = Item("Potion", "Healing potion", "consumable", 25)
        state = GameState(
            current_chamber=1,
            player_health=100,
            inventory_items=[item]
        )
        removed_item = state.remove_inventory_item("Potion")
        assert removed_item == item
        assert len(state.inventory_items) == 0
    
    def test_remove_inventory_item_not_exists(self):
        """Test removing a non-existent item from inventory."""
        state = GameState(current_chamber=1, player_health=100)
        removed_item = state.remove_inventory_item("NonExistent")
        assert removed_item is None
    
    def test_invalid_game_state_negative_chamber(self):
        """Test game state with negative current chamber."""
        with pytest.raises(GameException, match="Current chamber must be a positive integer"):
            GameState(current_chamber=-1, player_health=100)
    
    def test_invalid_game_state_zero_chamber(self):
        """Test game state with zero current chamber."""
        with pytest.raises(GameException, match="Current chamber must be a positive integer"):
            GameState(current_chamber=0, player_health=100)
    
    def test_invalid_game_state_negative_health(self):
        """Test game state with negative player health."""
        with pytest.raises(GameException, match="Player health must be a non-negative integer"):
            GameState(current_chamber=1, player_health=-10)
    
    def test_invalid_game_state_non_integer_health(self):
        """Test game state with non-integer player health."""
        with pytest.raises(GameException, match="Player health must be a non-negative integer"):
            GameState(current_chamber=1, player_health="invalid")
    
    def test_invalid_game_state_non_list_inventory(self):
        """Test game state with non-list inventory."""
        with pytest.raises(GameException, match="Inventory items must be a list"):
            GameState(
                current_chamber=1,
                player_health=100,
                inventory_items="invalid"
            )
    
    def test_invalid_game_state_invalid_inventory_item(self):
        """Test game state with invalid item in inventory."""
        with pytest.raises(GameException, match="All inventory items must be Item instances"):
            GameState(
                current_chamber=1,
                player_health=100,
                inventory_items=["invalid_item"]
            )
    
    def test_invalid_game_state_non_set_completed_chambers(self):
        """Test game state with non-set completed chambers."""
        with pytest.raises(GameException, match="Completed chambers must be a set"):
            GameState(
                current_chamber=1,
                player_health=100,
                completed_chambers=["invalid"]
            )
    
    def test_invalid_game_state_invalid_completed_chamber_id(self):
        """Test game state with invalid completed chamber ID."""
        with pytest.raises(GameException, match="All completed chamber IDs must be positive integers"):
            GameState(
                current_chamber=1,
                player_health=100,
                completed_chambers={1, -5, 3}
            )
    
    def test_invalid_game_state_negative_game_time(self):
        """Test game state with negative game time."""
        with pytest.raises(GameException, match="Game time must be a non-negative integer"):
            GameState(
                current_chamber=1,
                player_health=100,
                game_time=-100
            )
    
    def test_invalid_game_state_invalid_player_stats(self):
        """Test game state with invalid player stats."""
        with pytest.raises(GameException, match="Player stats must be a PlayerStats instance"):
            GameState(
                current_chamber=1,
                player_health=100,
                player_stats="invalid"
            )