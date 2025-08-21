"""Tests for the SaveLoadManager class."""

import pytest
import json
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from src.utils.save_load import SaveLoadManager
from src.utils.data_models import GameState, Item, PlayerStats
from src.utils.exceptions import SaveLoadException


class TestSaveLoadManager:
    """Test cases for SaveLoadManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.save_manager = SaveLoadManager(save_directory=self.temp_dir)
        
        # Create a test game state
        self.test_game_state = GameState(
            current_chamber=2,
            player_health=75,
            inventory_items=[
                Item("Health Potion", "Restores health", "potion", 50),
                Item("Magic Sword", "A powerful weapon", "weapon", 100)
            ],
            completed_chambers={1, 3},
            game_time=1800,  # 30 minutes
            player_stats=PlayerStats(strength=12, intelligence=8, dexterity=15, luck=10)
        )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test SaveLoadManager initialization."""
        manager = SaveLoadManager()
        assert manager.save_directory.name == "saves"
        assert manager.save_directory.exists()
    
    def test_initialization_custom_directory(self):
        """Test SaveLoadManager initialization with custom directory."""
        custom_dir = Path(self.temp_dir) / "custom_saves"
        manager = SaveLoadManager(save_directory=str(custom_dir))
        assert manager.save_directory == custom_dir
        assert manager.save_directory.exists()
    
    def test_save_game_success(self):
        """Test successful game save."""
        result = self.save_manager.save_game(self.test_game_state, "test_save")
        
        assert result is True
        
        # Check that file was created
        save_file = Path(self.temp_dir) / "test_save.json"
        assert save_file.exists()
        
        # Check file contents
        with open(save_file, 'r') as f:
            save_data = json.load(f)
        
        assert 'game_state' in save_data
        assert 'metadata' in save_data
        assert save_data['game_state']['current_chamber'] == 2
        assert save_data['game_state']['player_health'] == 75
        assert len(save_data['game_state']['inventory_items']) == 2
        assert save_data['game_state']['completed_chambers'] == [1, 3]
    
    def test_save_game_adds_json_extension(self):
        """Test that save_game adds .json extension if not present."""
        result = self.save_manager.save_game(self.test_game_state, "test_save_no_ext")
        
        assert result is True
        save_file = Path(self.temp_dir) / "test_save_no_ext.json"
        assert save_file.exists()
    
    def test_save_game_invalid_state(self):
        """Test saving invalid game state."""
        # Create a valid state first, then make it invalid
        invalid_state = GameState(
            current_chamber=1,
            player_health=100
        )
        # Manually set invalid value after creation to bypass validation
        invalid_state.current_chamber = -1
        
        with pytest.raises(SaveLoadException, match="Invalid game state"):
            self.save_manager.save_game(invalid_state, "invalid_save")
    
    def test_save_game_file_error(self):
        """Test save_game with file write error."""
        # Use a read-only directory
        readonly_dir = Path(self.temp_dir) / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only
        
        readonly_manager = SaveLoadManager(save_directory=str(readonly_dir))
        
        with pytest.raises(SaveLoadException, match="Failed to save game"):
            readonly_manager.save_game(self.test_game_state, "test_save")
    
    def test_load_game_success(self):
        """Test successful game load."""
        # First save a game
        self.save_manager.save_game(self.test_game_state, "test_load")
        
        # Then load it
        loaded_state = self.save_manager.load_game("test_load")
        
        assert loaded_state is not None
        assert loaded_state.current_chamber == 2
        assert loaded_state.player_health == 75
        assert len(loaded_state.inventory_items) == 2
        assert loaded_state.completed_chambers == {1, 3}
        assert loaded_state.game_time == 1800
        assert loaded_state.player_stats.strength == 12
    
    def test_load_game_adds_json_extension(self):
        """Test that load_game adds .json extension if not present."""
        self.save_manager.save_game(self.test_game_state, "test_load_no_ext")
        
        loaded_state = self.save_manager.load_game("test_load_no_ext")
        assert loaded_state is not None
    
    def test_load_game_file_not_found(self):
        """Test loading non-existent save file."""
        with pytest.raises(SaveLoadException, match=".*Save file not found"):
            self.save_manager.load_game("nonexistent_save")
    
    def test_load_game_corrupted_json(self):
        """Test loading corrupted JSON file."""
        # Create a corrupted save file
        save_file = Path(self.temp_dir) / "corrupted_save.json"
        with open(save_file, 'w') as f:
            f.write("{ invalid json content")
        
        with pytest.raises(SaveLoadException, match="Save file is corrupted"):
            self.save_manager.load_game("corrupted_save")
    
    def test_load_game_invalid_structure(self):
        """Test loading save file with invalid structure."""
        # Create a save file with invalid structure
        save_file = Path(self.temp_dir) / "invalid_structure.json"
        with open(save_file, 'w') as f:
            json.dump({"invalid": "structure"}, f)
        
        with pytest.raises(SaveLoadException, match="Save file missing 'game_state'"):
            self.save_manager.load_game("invalid_structure")
    
    def test_load_game_missing_required_fields(self):
        """Test loading save file with missing required fields."""
        # Create a save file missing required fields
        save_file = Path(self.temp_dir) / "missing_fields.json"
        save_data = {
            "game_state": {
                "current_chamber": 1
                # Missing player_health
            }
        }
        with open(save_file, 'w') as f:
            json.dump(save_data, f)
        
        with pytest.raises(SaveLoadException, match="Save file missing required field"):
            self.save_manager.load_game("missing_fields")
    
    def test_list_save_files_empty(self):
        """Test listing save files when directory is empty."""
        files = self.save_manager.list_save_files()
        assert files == []
    
    def test_list_save_files_with_files(self):
        """Test listing save files with multiple files."""
        # Create some save files
        self.save_manager.save_game(self.test_game_state, "save1")
        self.save_manager.save_game(self.test_game_state, "save2")
        self.save_manager.save_game(self.test_game_state, "save3")
        
        files = self.save_manager.list_save_files()
        assert len(files) == 3
        assert "save1.json" in files
        assert "save2.json" in files
        assert "save3.json" in files
        assert files == sorted(files)  # Should be sorted
    
    def test_delete_save_file_success(self):
        """Test successful save file deletion."""
        # Create a save file
        self.save_manager.save_game(self.test_game_state, "delete_test")
        
        # Verify it exists
        save_file = Path(self.temp_dir) / "delete_test.json"
        assert save_file.exists()
        
        # Delete it
        result = self.save_manager.delete_save_file("delete_test")
        assert result is True
        assert not save_file.exists()
    
    def test_delete_save_file_not_found(self):
        """Test deleting non-existent save file."""
        result = self.save_manager.delete_save_file("nonexistent")
        assert result is False
    
    def test_get_save_info_success(self):
        """Test getting save file information."""
        # Create a save file
        self.save_manager.save_game(self.test_game_state, "info_test")
        
        info = self.save_manager.get_save_info("info_test")
        
        assert info is not None
        assert info['filename'] == "info_test.json"
        assert info['current_chamber'] == 2
        assert info['player_health'] == 75
        assert info['completed_chambers'] == 2
        assert info['game_time'] == 1800
        assert 'save_time' in info
        assert 'file_size' in info
    
    def test_get_save_info_not_found(self):
        """Test getting info for non-existent save file."""
        info = self.save_manager.get_save_info("nonexistent")
        assert info is None
    
    def test_backup_save_file_success(self):
        """Test creating backup of save file."""
        # Create a save file
        self.save_manager.save_game(self.test_game_state, "backup_test")
        
        # Create backup
        result = self.save_manager.backup_save_file("backup_test")
        assert result is True
        
        # Check that backup file was created
        backup_files = list(Path(self.temp_dir).glob("backup_test_backup_*.json"))
        assert len(backup_files) == 1
    
    def test_backup_save_file_not_found(self):
        """Test backing up non-existent save file."""
        result = self.save_manager.backup_save_file("nonexistent")
        assert result is False
    
    def test_cleanup_old_backups(self):
        """Test cleaning up old backup files."""
        # Create original save file
        self.save_manager.save_game(self.test_game_state, "cleanup_test")
        
        # Create multiple backup files manually with different timestamps
        import time
        for i in range(7):
            timestamp = f"20250101_{100000 + i:06d}"  # Different timestamps
            backup_name = f"cleanup_test_backup_{timestamp}.json"
            backup_path = Path(self.temp_dir) / backup_name
            with open(backup_path, 'w') as f:
                json.dump({"test": "backup"}, f)
            # Set different modification times
            os.utime(backup_path, (time.time() - i, time.time() - i))
        
        # Verify we have 7 backup files
        backup_files = list(Path(self.temp_dir).glob("cleanup_test_backup_*.json"))
        assert len(backup_files) == 7
        
        # Cleanup, keeping only 3
        deleted_count = self.save_manager.cleanup_old_backups(max_backups=3)
        assert deleted_count == 4
        
        # Verify only 3 backup files remain
        remaining_backups = list(Path(self.temp_dir).glob("cleanup_test_backup_*.json"))
        assert len(remaining_backups) == 3
    
    def test_serialize_deserialize_item(self):
        """Test item serialization and deserialization."""
        item = Item("Test Item", "A test item", "misc", 42, usable=False)
        
        # Serialize
        serialized = self.save_manager._serialize_item(item)
        
        assert serialized['name'] == "Test Item"
        assert serialized['description'] == "A test item"
        assert serialized['item_type'] == "misc"
        assert serialized['value'] == 42
        assert serialized['usable'] is False
        
        # Deserialize
        deserialized = self.save_manager._deserialize_item(serialized)
        
        assert deserialized.name == item.name
        assert deserialized.description == item.description
        assert deserialized.item_type == item.item_type
        assert deserialized.value == item.value
        assert deserialized.usable == item.usable
    
    def test_serialize_deserialize_game_state(self):
        """Test game state serialization and deserialization."""
        # Serialize
        serialized = self.save_manager._serialize_game_state(self.test_game_state)
        
        assert 'game_state' in serialized
        game_data = serialized['game_state']
        assert game_data['current_chamber'] == 2
        assert game_data['player_health'] == 75
        assert len(game_data['inventory_items']) == 2
        assert game_data['completed_chambers'] == [1, 3]
        assert game_data['game_time'] == 1800
        
        # Deserialize
        deserialized = self.save_manager._deserialize_game_state(serialized)
        
        assert deserialized.current_chamber == self.test_game_state.current_chamber
        assert deserialized.player_health == self.test_game_state.player_health
        assert len(deserialized.inventory_items) == len(self.test_game_state.inventory_items)
        assert deserialized.completed_chambers == self.test_game_state.completed_chambers
        assert deserialized.game_time == self.test_game_state.game_time
        assert deserialized.player_stats.strength == self.test_game_state.player_stats.strength
    
    def test_validate_save_file_valid(self):
        """Test validation of valid save file."""
        valid_save_data = {
            'game_state': {
                'current_chamber': 1,
                'player_health': 100,
                'inventory_items': [],
                'completed_chambers': []
            }
        }
        
        # Should not raise exception
        self.save_manager._validate_save_file(valid_save_data)
    
    def test_validate_save_file_invalid_type(self):
        """Test validation of save file with invalid data types."""
        invalid_save_data = {
            'game_state': {
                'current_chamber': "not_an_int",  # Should be int
                'player_health': 100
            }
        }
        
        with pytest.raises(SaveLoadException, match="current_chamber must be an integer"):
            self.save_manager._validate_save_file(invalid_save_data)
    
    def test_round_trip_save_load(self):
        """Test complete save and load cycle."""
        # Save the game state
        save_result = self.save_manager.save_game(self.test_game_state, "round_trip_test")
        assert save_result is True
        
        # Load the game state
        loaded_state = self.save_manager.load_game("round_trip_test")
        assert loaded_state is not None
        
        # Verify all data matches
        assert loaded_state.current_chamber == self.test_game_state.current_chamber
        assert loaded_state.player_health == self.test_game_state.player_health
        assert loaded_state.completed_chambers == self.test_game_state.completed_chambers
        assert loaded_state.game_time == self.test_game_state.game_time
        
        # Check inventory items
        assert len(loaded_state.inventory_items) == len(self.test_game_state.inventory_items)
        for original, loaded in zip(self.test_game_state.inventory_items, loaded_state.inventory_items):
            assert loaded.name == original.name
            assert loaded.description == original.description
            assert loaded.item_type == original.item_type
            assert loaded.value == original.value
            assert loaded.usable == original.usable
        
        # Check player stats
        assert loaded_state.player_stats.strength == self.test_game_state.player_stats.strength
        assert loaded_state.player_stats.intelligence == self.test_game_state.player_stats.intelligence
        assert loaded_state.player_stats.dexterity == self.test_game_state.player_stats.dexterity
        assert loaded_state.player_stats.luck == self.test_game_state.player_stats.luck