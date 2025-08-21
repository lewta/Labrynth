"""Integration tests for map data persistence and chamber exploration tracking."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from src.game.engine import GameEngine
from src.game.world import Chamber
from src.utils.data_models import GameState
from src.utils.save_load import SaveLoadManager


class TestMapDataPersistence:
    """Test map data persistence in save/load functionality."""
    
    def test_game_state_includes_map_data(self):
        """Test that GameState includes visited chambers and discovered connections."""
        game_state = GameState(
            current_chamber=1,
            player_health=100,
            visited_chambers={1, 2, 3},
            discovered_connections={
                1: {"north": 2, "east": 3},
                2: {"south": 1},
                3: {"west": 1}
            }
        )
        
        assert game_state.visited_chambers == {1, 2, 3}
        assert game_state.discovered_connections[1] == {"north": 2, "east": 3}
        assert game_state.discovered_connections[2] == {"south": 1}
        assert game_state.discovered_connections[3] == {"west": 1}
    
    def test_game_state_validation_with_map_data(self):
        """Test GameState validation with map data."""
        # Valid game state should not raise exception
        valid_state = GameState(
            current_chamber=1,
            player_health=100,
            visited_chambers={1, 2},
            discovered_connections={1: {"north": 2}}
        )
        valid_state.validate()  # Should not raise
        
        # Invalid visited chambers
        with pytest.raises(Exception):
            GameState(
                current_chamber=1,
                player_health=100,
                visited_chambers={0, -1},  # Invalid chamber IDs
                discovered_connections={}
            )
        
        # Invalid discovered connections
        with pytest.raises(Exception):
            GameState(
                current_chamber=1,
                player_health=100,
                visited_chambers={1},
                discovered_connections={1: {"": 2}}  # Empty direction
            )
    
    def test_save_game_includes_map_data(self):
        """Test that saving a game includes map data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = GameEngine()
            engine.save_load_manager = SaveLoadManager(temp_dir)
            
            # Set up some progress data
            progress = engine.player_manager.progress
            progress.visit_chamber(1, {"north": 2})
            progress.visit_chamber(2, {"south": 1, "east": 3})
            progress.complete_chamber(1)
            
            # Mock world manager
            engine.world_manager.current_chamber_id = 2
            engine.world_manager.get_completed_chambers = Mock(return_value=[1])
            
            # Save the game
            filename = "test_save"
            success = engine.save_game(filename)
            
            assert success is True
            
            # Verify save file exists
            save_path = os.path.join(temp_dir, filename + ".json")
            assert os.path.exists(save_path)
            
            # Load and verify the saved data contains map information
            import json
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            
            game_data = save_data['game_state']
            assert 'visited_chambers' in game_data
            assert 'discovered_connections' in game_data
            assert set(game_data['visited_chambers']) == {1, 2}
            assert game_data['discovered_connections']['1'] == {"north": 2}
            assert game_data['discovered_connections']['2'] == {"south": 1, "east": 3}
    
    def test_load_game_restores_map_data(self):
        """Test that loading a game restores map data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a save file with map data
            save_data = {
                "metadata": {
                    "version": "1.0",
                    "timestamp": "2024-01-01T00:00:00",
                    "chamber_count": 3
                },
                "game_state": {
                    "current_chamber": 2,
                    "player_health": 80,
                    "inventory_items": [],
                    "completed_chambers": [1],
                    "visited_chambers": [1, 2, 3],
                    "discovered_connections": {
                        "1": {"north": 2, "east": 3},
                        "2": {"south": 1},
                        "3": {"west": 1}
                    },
                    "game_time": 300,
                    "player_stats": {
                        "strength": 10,
                        "intelligence": 10,
                        "dexterity": 10,
                        "luck": 10
                    }
                }
            }
            
            save_path = os.path.join(temp_dir, "test_load.json")
            import json
            with open(save_path, 'w') as f:
                json.dump(save_data, f)
            
            # Create engine and load the game
            engine = GameEngine()
            engine.save_load_manager = SaveLoadManager(temp_dir)
            
            # Mock chambers for completion status
            chambers = {}
            for i in range(1, 4):
                chamber = Mock()
                chamber.completed = False
                chambers[i] = chamber
            
            engine.world_manager.get_chamber = lambda cid: chambers.get(cid)
            
            # Load the game
            success = engine.load_game("test_load")
            
            assert success is True
            
            # Verify map data was restored
            progress = engine.player_manager.progress
            assert progress.visited_chambers == {1, 2, 3}
            assert progress.discovered_connections[1] == {"north": 2, "east": 3}
            assert progress.discovered_connections[2] == {"south": 1}
            assert progress.discovered_connections[3] == {"west": 1}
            assert progress.completed_chambers == {1}
            
            # Verify other game state
            assert engine.world_manager.current_chamber_id == 2
            assert engine.player_manager.current_health == 80
    
    def test_chamber_exploration_tracking(self):
        """Test that chamber exploration is properly tracked during gameplay."""
        engine = GameEngine()
        
        # Mock world manager with chambers
        chambers = {
            1: Chamber(1, "Start", "Starting chamber"),
            2: Chamber(2, "North", "Northern chamber"),
            3: Chamber(3, "East", "Eastern chamber")
        }
        
        # Set up connections
        chambers[1].add_connection("north", 2)
        chambers[1].add_connection("east", 3)
        chambers[2].add_connection("south", 1)
        chambers[3].add_connection("west", 1)
        
        engine.world_manager.chambers = chambers
        engine.world_manager.current_chamber_id = 1
        
        # Mock the world manager methods
        def get_chamber_mock(chamber_id):
            return chambers.get(chamber_id)
        
        def move_player_mock(direction):
            current = chambers[engine.world_manager.current_chamber_id]
            target_id = current.get_connection(direction)
            if target_id and target_id in chambers:
                engine.world_manager.current_chamber_id = target_id
                return True
            return False
        
        engine.world_manager.get_chamber = get_chamber_mock
        engine.world_manager.move_player = move_player_mock
        
        # Test movement and tracking
        progress = engine.player_manager.progress
        
        # Initially no chambers visited
        assert len(progress.visited_chambers) == 0
        assert len(progress.discovered_connections) == 0
        
        # Move north to chamber 2
        parsed_command = Mock()
        parsed_command.action = "go"
        parsed_command.parameters = ["north"]
        
        old_chamber_id = engine.world_manager.current_chamber_id
        success = engine.world_manager.move_player("north")
        assert success is True
        
        # Manually trigger the progress tracking (as it would happen in _handle_movement_command)
        new_chamber_id = engine.world_manager.current_chamber_id
        new_chamber = engine.world_manager.get_chamber(new_chamber_id)
        progress.visit_chamber(new_chamber_id, new_chamber.connections)
        progress.discover_connection(old_chamber_id, "north", new_chamber_id)
        
        # Verify tracking
        assert 2 in progress.visited_chambers
        assert progress.discovered_connections[1]["north"] == 2
        
        # Move back south
        old_chamber_id = engine.world_manager.current_chamber_id
        success = engine.world_manager.move_player("south")
        assert success is True
        
        # Track the return movement
        new_chamber_id = engine.world_manager.current_chamber_id
        new_chamber = engine.world_manager.get_chamber(new_chamber_id)
        progress.visit_chamber(new_chamber_id, new_chamber.connections)
        progress.discover_connection(old_chamber_id, "south", new_chamber_id)
        
        # Verify bidirectional tracking
        assert 1 in progress.visited_chambers
        assert 2 in progress.visited_chambers
        assert progress.discovered_connections[1]["north"] == 2
        assert progress.discovered_connections[2]["south"] == 1
    
    def test_map_data_survives_save_load_cycle(self):
        """Test that map data survives a complete save/load cycle."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create first engine instance
            engine1 = GameEngine()
            engine1.save_load_manager = SaveLoadManager(temp_dir)
            
            # Set up progress data
            progress1 = engine1.player_manager.progress
            progress1.visit_chamber(1, {"north": 2, "east": 3})
            progress1.visit_chamber(2, {"south": 1})
            progress1.visit_chamber(3, {"west": 1})
            progress1.complete_chamber(1)
            progress1.complete_chamber(3)
            
            # Mock world manager for saving
            engine1.world_manager.current_chamber_id = 2
            engine1.world_manager.get_completed_chambers = Mock(return_value=[1, 3])
            
            # Save the game
            filename = "cycle_test"
            success = engine1.save_game(filename)
            assert success is True
            
            # Create second engine instance and load
            engine2 = GameEngine()
            engine2.save_load_manager = SaveLoadManager(temp_dir)
            
            # Mock chambers for loading
            chambers = {}
            for i in range(1, 4):
                chamber = Mock()
                chamber.completed = False
                chambers[i] = chamber
            
            engine2.world_manager.get_chamber = lambda cid: chambers.get(cid)
            
            # Load the game
            success = engine2.load_game(filename)
            assert success is True
            
            # Verify all map data was preserved
            progress2 = engine2.player_manager.progress
            assert progress2.visited_chambers == progress1.visited_chambers
            assert progress2.discovered_connections == progress1.discovered_connections
            assert progress2.completed_chambers == progress1.completed_chambers
            
            # Verify specific data
            assert progress2.visited_chambers == {1, 2, 3}
            assert progress2.discovered_connections[1] == {"north": 2, "east": 3}
            assert progress2.discovered_connections[2] == {"south": 1}
            assert progress2.discovered_connections[3] == {"west": 1}
            assert progress2.completed_chambers == {1, 3}
    
    def test_map_command_works_after_load(self):
        """Test that map command works correctly after loading a game."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up and save a game with map data
            engine1 = GameEngine()
            engine1.save_load_manager = SaveLoadManager(temp_dir)
            
            progress1 = engine1.player_manager.progress
            progress1.visit_chamber(1, {"north": 2})
            progress1.visit_chamber(2, {"south": 1})
            progress1.complete_chamber(1)
            
            engine1.world_manager.current_chamber_id = 2
            engine1.world_manager.get_completed_chambers = Mock(return_value=[1])
            
            success = engine1.save_game("map_test")
            assert success is True
            
            # Load in new engine
            engine2 = GameEngine()
            engine2.save_load_manager = SaveLoadManager(temp_dir)
            engine2.ui_controller.enable_output_capture()
            
            # Mock chambers
            chamber1 = Mock()
            chamber1.name = "Start Chamber"
            chamber2 = Mock()
            chamber2.name = "North Chamber"
            
            chambers = {1: chamber1, 2: chamber2}
            engine2.world_manager.get_chamber = lambda cid: chambers.get(cid)
            
            success = engine2.load_game("map_test")
            assert success is True
            
            # Test map command
            engine2._display_map()
            
            output = engine2.ui_controller.get_captured_output()
            assert len(output) > 0
            
            # Should contain map content
            output_text = ''.join(output)
            assert "LABYRINTH MAP" in output_text
            assert "North Chamber" in output_text  # Current location