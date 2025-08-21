"""Integration tests for WorldManager with configuration system."""

import pytest
import os
from src.game.world import WorldManager
from src.utils.exceptions import GameException


class TestWorldManagerConfigIntegration:
    """Test cases for WorldManager integration with configuration system."""
    
    def test_load_default_labyrinth_config(self):
        """Test loading the default labyrinth configuration."""
        config_path = "config/default_labyrinth.json"
        
        # Skip test if config file doesn't exist
        if not os.path.exists(config_path):
            pytest.skip(f"Configuration file not found: {config_path}")
        
        world = WorldManager()
        world.load_from_file(config_path)
        
        # Verify basic structure
        assert len(world.chambers) == 3
        assert world.starting_chamber_id == 1
        assert world.current_chamber_id == 1
        
        # Verify chamber names
        assert world.chambers[1].name == "Entrance Hall"
        assert world.chambers[2].name == "Crystal Cavern"
        assert world.chambers[3].name == "Exit Chamber"
        
        # Verify connections
        assert world.chambers[1].has_connection("north")
        assert world.chambers[2].has_connection("south")
        assert world.chambers[2].has_connection("east")
        assert world.chambers[3].has_connection("west")
    
    def test_load_full_labyrinth_config(self):
        """Test loading the full 13-chamber labyrinth configuration."""
        config_path = "config/full_labyrinth.json"
        
        # Skip test if config file doesn't exist
        if not os.path.exists(config_path):
            pytest.skip(f"Configuration file not found: {config_path}")
        
        world = WorldManager()
        world.load_from_file(config_path)
        
        # Verify basic structure
        assert len(world.chambers) == 13
        assert world.starting_chamber_id == 1
        assert world.current_chamber_id == 1
        
        # Verify all chambers exist
        for i in range(1, 14):
            assert i in world.chambers
            assert world.chambers[i].name is not None
            assert len(world.chambers[i].name) > 0
            assert world.chambers[i].description is not None
            assert len(world.chambers[i].description) > 0
        
        # Verify connectivity - all chambers should be reachable
        reachable = world._get_reachable_chambers(1)
        assert len(reachable) == 13
        assert reachable == set(range(1, 14))
    
    def test_navigation_in_loaded_labyrinth(self):
        """Test navigation functionality in a loaded labyrinth."""
        config_path = "config/default_labyrinth.json"
        
        # Skip test if config file doesn't exist
        if not os.path.exists(config_path):
            pytest.skip(f"Configuration file not found: {config_path}")
        
        world = WorldManager()
        world.load_from_file(config_path)
        
        # Start at chamber 1
        assert world.current_chamber_id == 1
        
        # Move north to chamber 2
        result = world.move_player("north")
        assert result is True
        assert world.current_chamber_id == 2
        
        # Move east to chamber 3
        result = world.move_player("east")
        assert result is True
        assert world.current_chamber_id == 3
        
        # Try to move north (should fail - no connection)
        result = world.move_player("north")
        assert result is False
        assert world.current_chamber_id == 3  # Should stay in same chamber
        
        # Move back west to chamber 2
        result = world.move_player("west")
        assert result is True
        assert world.current_chamber_id == 2
    
    def test_world_state_with_loaded_config(self):
        """Test world state functionality with loaded configuration."""
        config_path = "config/default_labyrinth.json"
        
        # Skip test if config file doesn't exist
        if not os.path.exists(config_path):
            pytest.skip(f"Configuration file not found: {config_path}")
        
        world = WorldManager()
        world.load_from_file(config_path)
        
        # Get initial state
        state = world.get_world_state()
        assert state["current_chamber_id"] == 1
        assert state["starting_chamber_id"] == 1
        assert state["total_chambers"] == 3
        assert state["completed_chambers"] == []
        assert set(state["chamber_ids"]) == {1, 2, 3}
        
        # Complete a chamber and check state
        world.chambers[2].completed = True
        state = world.get_world_state()
        assert state["completed_chambers"] == [2]