"""Unit tests for WorldManager class."""

import pytest
import json
import tempfile
import os
from src.game.world import WorldManager, Chamber
from src.utils.exceptions import GameException
from src.utils.data_models import Item


class TestWorldManager:
    """Test cases for WorldManager class."""
    
    def test_world_manager_initialization(self):
        """Test WorldManager initialization."""
        world = WorldManager()
        assert world.chambers == {}
        assert world.connections == {}
        assert world.current_chamber_id == 1
        assert world.starting_chamber_id == 1
    
    def test_initialize_default_labyrinth(self):
        """Test initializing with default labyrinth."""
        world = WorldManager()
        world.initialize_labyrinth()
        
        assert len(world.chambers) == 3
        assert 1 in world.chambers
        assert 2 in world.chambers
        assert 3 in world.chambers
        
        # Check chamber names
        assert world.chambers[1].name == "Entrance Hall"
        assert world.chambers[2].name == "Crystal Cavern"
        assert world.chambers[3].name == "Exit Chamber"
        
        # Check connections
        assert world.chambers[1].has_connection("north")
        assert world.chambers[2].has_connection("south")
        assert world.chambers[2].has_connection("east")
        assert world.chambers[3].has_connection("west")
    
    def test_initialize_from_config_valid(self):
        """Test initializing from valid configuration."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber 1",
                    "description": "First test chamber",
                    "connections": {"north": 2}
                },
                "2": {
                    "name": "Test Chamber 2",
                    "description": "Second test chamber",
                    "connections": {"south": 1}
                }
            },
            "starting_chamber": 1
        }
        
        world = WorldManager()
        world.initialize_labyrinth(config)
        
        assert len(world.chambers) == 2
        assert world.chambers[1].name == "Test Chamber 1"
        assert world.chambers[2].name == "Test Chamber 2"
        assert world.starting_chamber_id == 1
        assert world.current_chamber_id == 1
    
    def test_initialize_from_config_invalid_data_type(self):
        """Test initializing from invalid configuration data type."""
        world = WorldManager()
        with pytest.raises(GameException, match="Configuration data must be a dictionary"):
            world.initialize_labyrinth("invalid")
    
    def test_initialize_from_config_no_chambers(self):
        """Test initializing from configuration with no chambers."""
        config = {"other_data": "value"}
        world = WorldManager()
        with pytest.raises(GameException, match="Configuration must contain chambers data"):
            world.initialize_labyrinth(config)
    
    def test_initialize_from_config_invalid_chamber_id(self):
        """Test initializing from configuration with invalid chamber ID."""
        config = {
            "chambers": {
                "invalid_id": {
                    "name": "Test Chamber",
                    "description": "Test description"
                }
            }
        }
        world = WorldManager()
        with pytest.raises(GameException, match="Invalid chamber ID: invalid_id"):
            world.initialize_labyrinth(config)
    
    def test_initialize_from_config_invalid_chamber_data(self):
        """Test initializing from configuration with invalid chamber data."""
        config = {
            "chambers": {
                "1": "invalid_chamber_data"
            }
        }
        world = WorldManager()
        with pytest.raises(GameException, match="Chamber 1 data must be a dictionary"):
            world.initialize_labyrinth(config)
    
    def test_initialize_from_config_invalid_connection_target(self):
        """Test initializing from configuration with invalid connection target."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "Test description",
                    "connections": {"north": "invalid_target"}
                }
            }
        }
        world = WorldManager()
        with pytest.raises(GameException, match="Connection target must be an integer"):
            world.initialize_labyrinth(config)
    
    def test_initialize_from_config_invalid_starting_chamber(self):
        """Test initializing from configuration with invalid starting chamber."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "Test description"
                }
            },
            "starting_chamber": 999
        }
        world = WorldManager()
        with pytest.raises(GameException, match="Starting chamber 999 does not exist"):
            world.initialize_labyrinth(config)
    
    def test_validate_labyrinth_empty(self):
        """Test validation with empty labyrinth."""
        world = WorldManager()
        with pytest.raises(GameException, match="Labyrinth must contain at least one chamber"):
            world._validate_labyrinth()
    
    def test_validate_labyrinth_invalid_starting_chamber(self):
        """Test validation with invalid starting chamber."""
        world = WorldManager()
        chamber = Chamber(1, "Test", "Test description")
        world.add_chamber(chamber)
        world.starting_chamber_id = 999
        
        with pytest.raises(GameException, match="Starting chamber 999 does not exist"):
            world._validate_labyrinth()
    
    def test_validate_labyrinth_unreachable_chambers(self):
        """Test validation with unreachable chambers."""
        world = WorldManager()
        chamber1 = Chamber(1, "Chamber 1", "First chamber")
        chamber2 = Chamber(2, "Chamber 2", "Second chamber")
        chamber3 = Chamber(3, "Chamber 3", "Third chamber")
        
        world.add_chamber(chamber1)
        world.add_chamber(chamber2)
        world.add_chamber(chamber3)
        
        # Only connect 1 and 2, leaving 3 unreachable
        world.add_connection(1, "north", 2)
        world.add_connection(2, "south", 1)
        
        with pytest.raises(GameException, match=r"Unreachable chambers detected: \{3\}"):
            world._validate_labyrinth()
    
    def test_validate_bidirectional_connections_nonexistent_target(self):
        """Test validation with connection to non-existent chamber."""
        world = WorldManager()
        chamber = Chamber(1, "Test", "Test description")
        world.add_chamber(chamber)
        chamber.add_connection("north", 999)  # Non-existent chamber
        
        with pytest.raises(GameException, match="Chamber 1 connects to non-existent chamber 999"):
            world._validate_labyrinth()
    
    def test_validate_bidirectional_connections_inconsistent(self):
        """Test validation allows non-bidirectional connections."""
        world = WorldManager()
        chamber1 = Chamber(1, "Chamber 1", "First chamber")
        chamber2 = Chamber(2, "Chamber 2", "Second chamber")
        chamber3 = Chamber(3, "Chamber 3", "Third chamber")
        
        world.add_chamber(chamber1)
        world.add_chamber(chamber2)
        world.add_chamber(chamber3)
        
        # Create non-bidirectional connections (this should be allowed)
        chamber1.add_connection("north", 2)
        chamber2.add_connection("south", 3)  # Points to 3 instead of back to 1
        
        # This should not raise an exception - non-bidirectional connections are allowed
        world._validate_labyrinth()
    
    def test_add_chamber_valid(self):
        """Test adding a valid chamber."""
        world = WorldManager()
        chamber = Chamber(1, "Test Chamber", "Test description")
        world.add_chamber(chamber)
        
        assert 1 in world.chambers
        assert world.chambers[1] == chamber
    
    def test_add_chamber_invalid_type(self):
        """Test adding invalid chamber type."""
        world = WorldManager()
        with pytest.raises(GameException, match="Chamber must be a Chamber instance"):
            world.add_chamber("invalid_chamber")
    
    def test_add_chamber_duplicate_id(self):
        """Test adding chamber with duplicate ID."""
        world = WorldManager()
        chamber1 = Chamber(1, "Chamber 1", "First chamber")
        chamber2 = Chamber(1, "Chamber 2", "Second chamber")
        
        world.add_chamber(chamber1)
        with pytest.raises(GameException, match="Chamber with ID 1 already exists"):
            world.add_chamber(chamber2)
    
    def test_remove_chamber_exists(self):
        """Test removing an existing chamber."""
        world = WorldManager()
        chamber1 = Chamber(1, "Chamber 1", "First chamber")
        chamber2 = Chamber(2, "Chamber 2", "Second chamber")
        
        world.add_chamber(chamber1)
        world.add_chamber(chamber2)
        world.add_connection(1, "north", 2)
        world.add_connection(2, "south", 1)
        
        result = world.remove_chamber(2)
        assert result is True
        assert 2 not in world.chambers
        assert not chamber1.has_connection("north")  # Connection should be removed
    
    def test_remove_chamber_not_exists(self):
        """Test removing a non-existent chamber."""
        world = WorldManager()
        result = world.remove_chamber(999)
        assert result is False
    
    def test_get_chamber_exists(self):
        """Test getting an existing chamber."""
        world = WorldManager()
        chamber = Chamber(1, "Test Chamber", "Test description")
        world.add_chamber(chamber)
        
        retrieved = world.get_chamber(1)
        assert retrieved == chamber
    
    def test_get_chamber_not_exists(self):
        """Test getting a non-existent chamber."""
        world = WorldManager()
        retrieved = world.get_chamber(999)
        assert retrieved is None
    
    def test_get_current_chamber_exists(self):
        """Test getting current chamber when it exists."""
        world = WorldManager()
        chamber = Chamber(1, "Test Chamber", "Test description")
        world.add_chamber(chamber)
        world.current_chamber_id = 1
        
        current = world.get_current_chamber()
        assert current == chamber
    
    def test_get_current_chamber_not_exists(self):
        """Test getting current chamber when it doesn't exist."""
        world = WorldManager()
        world.current_chamber_id = 999
        
        current = world.get_current_chamber()
        assert current is None
    
    def test_get_connected_chambers_exists(self):
        """Test getting connected chambers for existing chamber."""
        world = WorldManager()
        chamber1 = Chamber(1, "Chamber 1", "First chamber")
        chamber2 = Chamber(2, "Chamber 2", "Second chamber")
        chamber3 = Chamber(3, "Chamber 3", "Third chamber")
        
        world.add_chamber(chamber1)
        world.add_chamber(chamber2)
        world.add_chamber(chamber3)
        
        world.add_connection(1, "north", 2)
        world.add_connection(1, "east", 3)
        
        connected = world.get_connected_chambers(1)
        assert set(connected) == {2, 3}
    
    def test_get_connected_chambers_not_exists(self):
        """Test getting connected chambers for non-existent chamber."""
        world = WorldManager()
        connected = world.get_connected_chambers(999)
        assert connected == []
    
    def test_move_player_valid(self):
        """Test valid player movement."""
        world = WorldManager()
        world.initialize_labyrinth()  # Creates default 3-chamber labyrinth
        
        # Start at chamber 1, move north to chamber 2
        assert world.current_chamber_id == 1
        result = world.move_player("north")
        assert result is True
        assert world.current_chamber_id == 2
    
    def test_move_player_invalid_direction(self):
        """Test player movement in invalid direction."""
        world = WorldManager()
        world.initialize_labyrinth()
        
        result = world.move_player("west")  # No west connection from chamber 1
        assert result is False
        assert world.current_chamber_id == 1  # Should stay in same chamber
    
    def test_move_player_invalid_direction_type(self):
        """Test player movement with invalid direction type."""
        world = WorldManager()
        world.initialize_labyrinth()
        
        result = world.move_player(123)
        assert result is False
        assert world.current_chamber_id == 1
    
    def test_move_player_no_current_chamber(self):
        """Test player movement when current chamber doesn't exist."""
        world = WorldManager()
        world.current_chamber_id = 999
        
        result = world.move_player("north")
        assert result is False
    
    def test_move_player_target_chamber_not_exists(self):
        """Test player movement to non-existent target chamber."""
        world = WorldManager()
        chamber = Chamber(1, "Test", "Test description")
        world.add_chamber(chamber)
        chamber.add_connection("north", 999)  # Non-existent target
        world.current_chamber_id = 1
        
        result = world.move_player("north")
        assert result is False
        assert world.current_chamber_id == 1
    
    def test_is_valid_direction_valid(self):
        """Test checking valid direction."""
        world = WorldManager()
        world.initialize_labyrinth()
        
        assert world.is_valid_direction(1, "north") is True
        assert world.is_valid_direction(2, "south") is True
    
    def test_is_valid_direction_invalid(self):
        """Test checking invalid direction."""
        world = WorldManager()
        world.initialize_labyrinth()
        
        assert world.is_valid_direction(1, "west") is False
        assert world.is_valid_direction(999, "north") is False
    
    def test_get_available_directions_exists(self):
        """Test getting available directions for existing chamber."""
        world = WorldManager()
        world.initialize_labyrinth()
        
        directions = world.get_available_directions(1)
        assert directions == ["north"]
        
        directions = world.get_available_directions(2)
        assert set(directions) == {"south", "east"}
    
    def test_get_available_directions_not_exists(self):
        """Test getting available directions for non-existent chamber."""
        world = WorldManager()
        directions = world.get_available_directions(999)
        assert directions == []
    
    def test_add_connection_valid(self):
        """Test adding valid connection."""
        world = WorldManager()
        chamber1 = Chamber(1, "Chamber 1", "First chamber")
        chamber2 = Chamber(2, "Chamber 2", "Second chamber")
        
        world.add_chamber(chamber1)
        world.add_chamber(chamber2)
        
        world.add_connection(1, "north", 2)
        assert chamber1.has_connection("north")
        assert chamber1.get_connection("north") == 2
    
    def test_add_connection_source_not_exists(self):
        """Test adding connection with non-existent source chamber."""
        world = WorldManager()
        chamber = Chamber(2, "Chamber 2", "Second chamber")
        world.add_chamber(chamber)
        
        with pytest.raises(GameException, match="Source chamber 1 does not exist"):
            world.add_connection(1, "north", 2)
    
    def test_add_connection_target_not_exists(self):
        """Test adding connection with non-existent target chamber."""
        world = WorldManager()
        chamber = Chamber(1, "Chamber 1", "First chamber")
        world.add_chamber(chamber)
        
        with pytest.raises(GameException, match="Target chamber 2 does not exist"):
            world.add_connection(1, "north", 2)
    
    def test_remove_connection_exists(self):
        """Test removing existing connection."""
        world = WorldManager()
        chamber1 = Chamber(1, "Chamber 1", "First chamber")
        chamber2 = Chamber(2, "Chamber 2", "Second chamber")
        
        world.add_chamber(chamber1)
        world.add_chamber(chamber2)
        world.add_connection(1, "north", 2)
        
        result = world.remove_connection(1, "north")
        assert result is True
        assert not chamber1.has_connection("north")
    
    def test_remove_connection_not_exists(self):
        """Test removing non-existent connection."""
        world = WorldManager()
        chamber = Chamber(1, "Chamber 1", "First chamber")
        world.add_chamber(chamber)
        
        result = world.remove_connection(1, "north")
        assert result is False
    
    def test_remove_connection_chamber_not_exists(self):
        """Test removing connection from non-existent chamber."""
        world = WorldManager()
        result = world.remove_connection(999, "north")
        assert result is False
    
    def test_reset_player_position(self):
        """Test resetting player position to starting chamber."""
        world = WorldManager()
        world.initialize_labyrinth()
        
        # Move player to different chamber
        world.move_player("north")
        assert world.current_chamber_id == 2
        
        # Reset position
        world.reset_player_position()
        assert world.current_chamber_id == world.starting_chamber_id
    
    def test_get_chamber_count(self):
        """Test getting chamber count."""
        world = WorldManager()
        assert world.get_chamber_count() == 0
        
        world.initialize_labyrinth()
        assert world.get_chamber_count() == 3
    
    def test_get_all_chamber_ids(self):
        """Test getting all chamber IDs."""
        world = WorldManager()
        assert world.get_all_chamber_ids() == []
        
        world.initialize_labyrinth()
        chamber_ids = world.get_all_chamber_ids()
        assert set(chamber_ids) == {1, 2, 3}
    
    def test_is_chamber_completed_exists_completed(self):
        """Test checking completion status of existing completed chamber."""
        world = WorldManager()
        chamber = Chamber(1, "Test", "Test description")
        chamber.completed = True
        world.add_chamber(chamber)
        
        assert world.is_chamber_completed(1) is True
    
    def test_is_chamber_completed_exists_not_completed(self):
        """Test checking completion status of existing uncompleted chamber."""
        world = WorldManager()
        chamber = Chamber(1, "Test", "Test description")
        world.add_chamber(chamber)
        
        assert world.is_chamber_completed(1) is False
    
    def test_is_chamber_completed_not_exists(self):
        """Test checking completion status of non-existent chamber."""
        world = WorldManager()
        assert world.is_chamber_completed(999) is False
    
    def test_get_completed_chambers(self):
        """Test getting list of completed chambers."""
        world = WorldManager()
        chamber1 = Chamber(1, "Chamber 1", "First chamber")
        chamber2 = Chamber(2, "Chamber 2", "Second chamber")
        chamber3 = Chamber(3, "Chamber 3", "Third chamber")
        
        chamber1.completed = True
        chamber3.completed = True
        
        world.add_chamber(chamber1)
        world.add_chamber(chamber2)
        world.add_chamber(chamber3)
        
        completed = world.get_completed_chambers()
        assert set(completed) == {1, 3}
    
    def test_get_world_state(self):
        """Test getting world state information."""
        world = WorldManager()
        world.initialize_labyrinth()
        
        # Complete one chamber
        world.chambers[2].completed = True
        
        state = world.get_world_state()
        expected = {
            "current_chamber_id": 1,
            "starting_chamber_id": 1,
            "total_chambers": 3,
            "completed_chambers": [2],
            "chamber_ids": [1, 2, 3]
        }
        
        assert state["current_chamber_id"] == expected["current_chamber_id"]
        assert state["starting_chamber_id"] == expected["starting_chamber_id"]
        assert state["total_chambers"] == expected["total_chambers"]
        assert state["completed_chambers"] == expected["completed_chambers"]
        assert set(state["chamber_ids"]) == set(expected["chamber_ids"])
    
    def test_load_from_file_valid(self):
        """Test loading configuration from valid file."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "Test description",
                    "connections": {"north": 2}
                },
                "2": {
                    "name": "Second Chamber",
                    "description": "Second description",
                    "connections": {"south": 1}
                }
            }
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_file = f.name
        
        try:
            world = WorldManager()
            world.load_from_file(temp_file)
            
            assert len(world.chambers) == 2
            assert world.chambers[1].name == "Test Chamber"
            assert world.chambers[2].name == "Second Chamber"
        finally:
            os.unlink(temp_file)
    
    def test_load_from_file_not_found(self):
        """Test loading from non-existent file."""
        world = WorldManager()
        with pytest.raises(GameException, match="Configuration file not found"):
            world.load_from_file("non_existent_file.json")
    
    def test_load_from_file_invalid_json(self):
        """Test loading from file with invalid JSON."""
        # Create temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name
        
        try:
            world = WorldManager()
            with pytest.raises(GameException, match="Invalid JSON in configuration file"):
                world.load_from_file(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_str_representation(self):
        """Test string representation of WorldManager."""
        world = WorldManager()
        world.initialize_labyrinth()
        
        str_repr = str(world)
        assert "WorldManager(3 chambers, current: 1)" == str_repr
    
    def test_repr_representation(self):
        """Test detailed string representation of WorldManager."""
        world = WorldManager()
        world.initialize_labyrinth()
        
        repr_str = repr(world)
        expected = "WorldManager(chambers=3, current_chamber=1, starting_chamber=1)"
        assert repr_str == expected
    
    def test_get_reachable_chambers_simple(self):
        """Test getting reachable chambers from a simple labyrinth."""
        world = WorldManager()
        world.initialize_labyrinth()
        
        reachable = world._get_reachable_chambers(1)
        assert reachable == {1, 2, 3}
    
    def test_get_reachable_chambers_partial(self):
        """Test getting reachable chambers with some unreachable."""
        world = WorldManager()
        chamber1 = Chamber(1, "Chamber 1", "First chamber")
        chamber2 = Chamber(2, "Chamber 2", "Second chamber")
        chamber3 = Chamber(3, "Chamber 3", "Third chamber")
        
        world.add_chamber(chamber1)
        world.add_chamber(chamber2)
        world.add_chamber(chamber3)
        
        # Only connect 1 and 2
        world.add_connection(1, "north", 2)
        world.add_connection(2, "south", 1)
        
        reachable = world._get_reachable_chambers(1)
        assert reachable == {1, 2}