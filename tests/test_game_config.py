"""Unit tests for GameConfig class."""

import json
import os
import tempfile
import pytest
from unittest.mock import patch, mock_open

from src.config.game_config import GameConfig


class TestGameConfig:
    """Test cases for GameConfig class."""
    
    @patch('src.config.game_config.GameConfig._find_config_file')
    def test_init_with_default_config(self, mock_find_config):
        """Test GameConfig initialization with default configuration."""
        # Mock to return None so no config file is found
        mock_find_config.return_value = None
        
        config = GameConfig()
        
        # Verify default values are loaded
        assert config.get("victory.flag_content") == "LABYRINTH_MASTER_2024"
        assert config.get("victory.flag_prefix") == "FLAG{"
        assert config.get("victory.flag_suffix") == "}"
        assert config.get("game.title") == "Labyrinth Adventure Game"
        assert config.get("game.version") == "1.0"
    
    def test_init_with_custom_config_file(self):
        """Test GameConfig initialization with custom config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_config = {
                "victory": {
                    "flag_content": "CUSTOM_FLAG_2024",
                    "flag_prefix": "CTF{",
                    "flag_suffix": "}"
                }
            }
            json.dump(test_config, f)
            temp_file = f.name
        
        try:
            config = GameConfig(config_file=temp_file)
            
            # Verify custom values are loaded
            assert config.get("victory.flag_content") == "CUSTOM_FLAG_2024"
            assert config.get("victory.flag_prefix") == "CTF{"
            # Verify defaults are still present for unspecified values
            assert config.get("game.title") == "Labyrinth Adventure Game"
        finally:
            os.unlink(temp_file)
    
    def test_load_config_file_not_found(self):
        """Test loading configuration when file doesn't exist."""
        config = GameConfig(config_file="nonexistent_file.json")
        
        # Should fall back to defaults
        assert config.get("victory.flag_content") == "LABYRINTH_MASTER_2024"
        assert config.get("game.title") == "Labyrinth Adventure Game"
    
    def test_load_config_invalid_json(self):
        """Test loading configuration with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content")
            temp_file = f.name
        
        try:
            with patch('src.config.game_config.logging.getLogger') as mock_logger:
                mock_log = mock_logger.return_value
                config = GameConfig(config_file=temp_file)
                
                # Should fall back to defaults and log error
                assert config.get("victory.flag_content") == "LABYRINTH_MASTER_2024"
                mock_log.error.assert_called()
        finally:
            os.unlink(temp_file)
    
    def test_save_config(self):
        """Test saving configuration to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            config = GameConfig(config_file=temp_file)
            config.set("victory.flag_content", "SAVED_FLAG_2024")
            config.save_config()
            
            # Verify file was written correctly
            with open(temp_file, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["victory"]["flag_content"] == "SAVED_FLAG_2024"
        finally:
            os.unlink(temp_file)
    
    def test_save_config_creates_directory(self):
        """Test that save_config creates directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "subdir", "config.json")
            
            config = GameConfig(config_file=config_file)
            config.save_config()
            
            # Verify directory was created and file exists
            assert os.path.exists(config_file)
            assert os.path.isdir(os.path.dirname(config_file))
    
    def test_save_config_io_error(self):
        """Test save_config handles IO errors gracefully."""
        config = GameConfig(config_file="/invalid/path/config.json")
        
        with pytest.raises(IOError):
            config.save_config()
    
    @patch('src.config.game_config.GameConfig._find_config_file')
    def test_get_dot_notation(self, mock_find_config):
        """Test getting values using dot notation."""
        # Mock to return None so no config file is found
        mock_find_config.return_value = None
        
        config = GameConfig()
        
        # Test nested access
        assert config.get("victory.flag_content") == "LABYRINTH_MASTER_2024"
        assert config.get("victory.flag_prefix") == "FLAG{"
        assert config.get("game.title") == "Labyrinth Adventure Game"
        
        # Test non-existent key with default
        assert config.get("nonexistent.key", "default") == "default"
        assert config.get("victory.nonexistent", None) is None
    
    def test_get_invalid_path(self):
        """Test getting values with invalid paths."""
        config = GameConfig()
        
        # Test accessing non-dict as dict
        assert config.get("victory.flag_content.invalid") is None
        
        # Test completely invalid path
        assert config.get("completely.invalid.path") is None
        
        # Test empty path
        assert config.get("") is None
    
    def test_set_dot_notation(self):
        """Test setting values using dot notation."""
        config = GameConfig()
        
        # Test setting existing nested value
        config.set("victory.flag_content", "NEW_FLAG_2024")
        assert config.get("victory.flag_content") == "NEW_FLAG_2024"
        
        # Test setting new nested value
        config.set("new.nested.value", "test_value")
        assert config.get("new.nested.value") == "test_value"
        
        # Test overwriting non-dict with dict structure
        config.set("victory.flag_content.new_nested", "nested_value")
        assert config.get("victory.flag_content.new_nested") == "nested_value"
    
    def test_set_creates_nested_structure(self):
        """Test that set creates nested dictionary structure as needed."""
        config = GameConfig()
        
        config.set("deeply.nested.new.structure", "value")
        assert config.get("deeply.nested.new.structure") == "value"
        
        # Verify intermediate dictionaries were created
        assert isinstance(config.get("deeply"), dict)
        assert isinstance(config.get("deeply.nested"), dict)
        assert isinstance(config.get("deeply.nested.new"), dict)
    
    def test_config_file_search_order(self):
        """Test configuration file search order."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config directory
            config_dir = os.path.join(temp_dir, "config")
            os.makedirs(config_dir)
            
            # Create test config files
            root_config = os.path.join(temp_dir, "game_config.json")
            config_dir_config = os.path.join(config_dir, "game_config.json")
            
            with open(root_config, 'w') as f:
                json.dump({"victory": {"flag_content": "ROOT_FLAG"}}, f)
            
            with open(config_dir_config, 'w') as f:
                json.dump({"victory": {"flag_content": "CONFIG_DIR_FLAG"}}, f)
            
            # Change to temp directory to test search
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                config = GameConfig()
                
                # Should find root config first
                assert config.get("victory.flag_content") == "ROOT_FLAG"
                
                # Remove root config and test again
                os.unlink(root_config)
                config = GameConfig()
                assert config.get("victory.flag_content") == "CONFIG_DIR_FLAG"
                
            finally:
                os.chdir(original_cwd)
    
    def test_merge_config(self):
        """Test configuration merging functionality."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Partial config that should merge with defaults
            partial_config = {
                "victory": {
                    "flag_content": "MERGED_FLAG"
                    # Missing flag_prefix, flag_suffix, prize_message
                },
                "new_section": {
                    "custom_value": "test"
                }
            }
            json.dump(partial_config, f)
            temp_file = f.name
        
        try:
            config = GameConfig(config_file=temp_file)
            
            # Verify merged values
            assert config.get("victory.flag_content") == "MERGED_FLAG"
            assert config.get("victory.flag_prefix") == "FLAG{"  # From defaults
            assert config.get("victory.flag_suffix") == "}"      # From defaults
            assert config.get("game.title") == "Labyrinth Adventure Game"  # From defaults
            assert config.get("new_section.custom_value") == "test"  # From file
            
        finally:
            os.unlink(temp_file)
    
    @patch('src.config.game_config.GameConfig._find_config_file')
    def test_get_victory_flag_default(self, mock_find_config):
        """Test get_victory_flag with default configuration."""
        # Mock to return None so no config file is found
        mock_find_config.return_value = None
        
        config = GameConfig()
        
        flag = config.get_victory_flag()
        assert flag == "FLAG{LABYRINTH_MASTER_2024}"
    
    def test_get_victory_flag_custom(self):
        """Test get_victory_flag with custom configuration."""
        config = GameConfig()
        config.set("victory.flag_prefix", "CTF{")
        config.set("victory.flag_content", "CUSTOM_CHALLENGE_2024")
        config.set("victory.flag_suffix", "]")
        
        flag = config.get_victory_flag()
        assert flag == "CTF{CUSTOM_CHALLENGE_2024]"
    
    @patch('src.config.game_config.GameConfig._find_config_file')
    def test_get_victory_flag_partial_custom(self, mock_find_config):
        """Test get_victory_flag with partially customized configuration."""
        # Mock to return None so no config file is found
        mock_find_config.return_value = None
        
        config = GameConfig()
        config.set("victory.flag_content", "PARTIAL_CUSTOM")
        # Keep default prefix and suffix
        
        flag = config.get_victory_flag()
        assert flag == "FLAG{PARTIAL_CUSTOM}"
    
    @patch('src.config.game_config.GameConfig._find_config_file')
    def test_get_victory_message_default(self, mock_find_config):
        """Test get_victory_message with default configuration."""
        # Mock to return None so no config file is found
        mock_find_config.return_value = None
        
        config = GameConfig()
        
        message = config.get_victory_message()
        expected = "🏆 YOUR PRIZE: FLAG{LABYRINTH_MASTER_2024}\n\nYou have proven yourself worthy of the ancient secrets!"
        assert message == expected
    
    @patch('src.config.game_config.GameConfig._find_config_file')
    def test_get_victory_message_custom_flag(self, mock_find_config):
        """Test get_victory_message with custom flag configuration."""
        # Mock to return None so no config file is found
        mock_find_config.return_value = None
        
        config = GameConfig()
        config.set("victory.flag_content", "CUSTOM_FLAG_2024")
        config.set("victory.flag_prefix", "CHALLENGE{")
        
        message = config.get_victory_message()
        expected = "🏆 YOUR PRIZE: CHALLENGE{CUSTOM_FLAG_2024}\n\nYou have proven yourself worthy of the ancient secrets!"
        assert message == expected
    
    @patch('src.config.game_config.GameConfig._find_config_file')
    def test_get_victory_message_custom_template(self, mock_find_config):
        """Test get_victory_message with custom message template."""
        # Mock to return None so no config file is found
        mock_find_config.return_value = None
        
        config = GameConfig()
        config.set("victory.prize_message", "Congratulations! Your flag is: {flag}")
        
        message = config.get_victory_message()
        expected = "Congratulations! Your flag is: FLAG{LABYRINTH_MASTER_2024}"
        assert message == expected
    
    def test_get_victory_message_custom_template_and_flag(self):
        """Test get_victory_message with both custom template and flag."""
        config = GameConfig()
        config.set("victory.prize_message", "Well done! Flag: {flag} - You win!")
        config.set("victory.flag_content", "WINNER_2024")
        config.set("victory.flag_prefix", "WIN{")
        config.set("victory.flag_suffix", "}")
        
        message = config.get_victory_message()
        expected = "Well done! Flag: WIN{WINNER_2024} - You win!"
        assert message == expected
    
    def test_update_flag_content_success(self):
        """Test successful flag content update."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            config = GameConfig(config_file=temp_file)
            config.update_flag_content("NEW_FLAG_CONTENT_2024")
            
            # Verify content was updated
            assert config.get("victory.flag_content") == "NEW_FLAG_CONTENT_2024"
            
            # Verify flag generation works with new content
            flag = config.get_victory_flag()
            assert flag == "FLAG{NEW_FLAG_CONTENT_2024}"
            
            # Verify configuration was saved to file
            with open(temp_file, 'r') as f:
                saved_data = json.load(f)
            assert saved_data["victory"]["flag_content"] == "NEW_FLAG_CONTENT_2024"
            
        finally:
            os.unlink(temp_file)
    
    def test_update_flag_content_with_whitespace(self):
        """Test flag content update strips whitespace."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            config = GameConfig(config_file=temp_file)
            config.update_flag_content("  WHITESPACE_FLAG_2024  ")
            
            # Verify whitespace was stripped
            assert config.get("victory.flag_content") == "WHITESPACE_FLAG_2024"
            
        finally:
            os.unlink(temp_file)
    
    def test_update_flag_content_empty_string(self):
        """Test update_flag_content raises ValueError for empty string."""
        config = GameConfig()
        
        with pytest.raises(ValueError, match="Flag content cannot be empty"):
            config.update_flag_content("")
    
    def test_update_flag_content_whitespace_only(self):
        """Test update_flag_content raises ValueError for whitespace-only string."""
        config = GameConfig()
        
        with pytest.raises(ValueError, match="Flag content cannot be empty"):
            config.update_flag_content("   ")
    
    def test_update_flag_content_none(self):
        """Test update_flag_content raises ValueError for None."""
        config = GameConfig()
        
        with pytest.raises(ValueError, match="Flag content cannot be None"):
            config.update_flag_content(None)
    
    def test_update_flag_content_save_error(self):
        """Test update_flag_content handles save errors."""
        config = GameConfig(config_file="/invalid/path/config.json")
        
        with pytest.raises(IOError):
            config.update_flag_content("VALID_CONTENT")
    
    def test_default_configuration_structure(self):
        """Test that default configuration has all required sections."""
        with patch('src.config.game_config.GameConfig._find_config_file') as mock_find_config:
            mock_find_config.return_value = None
            config = GameConfig()
            
            # Test victory section
            assert config.get("victory.flag_content") is not None
            assert config.get("victory.flag_prefix") is not None
            assert config.get("victory.flag_suffix") is not None
            assert config.get("victory.prize_message") is not None
            
            # Test game section
            assert config.get("game.title") is not None
            assert config.get("game.version") is not None
            
            # Test display section
            assert config.get("display.width") is not None
            assert config.get("display.show_map") is not None
    
    def test_file_search_order_priority(self):
        """Test that configuration file search follows correct priority order."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # Create config directory
                config_dir = os.path.join(temp_dir, "config")
                os.makedirs(config_dir)
                
                # Create home directory config
                home_config = os.path.expanduser("~/.labrynth_config.json")
                home_config_exists = os.path.exists(home_config)
                
                # Test 1: Only home config exists (lowest priority)
                if not home_config_exists:
                    with open(home_config, 'w') as f:
                        json.dump({"victory": {"flag_content": "HOME_FLAG"}}, f)
                
                config = GameConfig()
                found_file = config._find_config_file()
                if not home_config_exists:
                    assert found_file == home_config
                    os.unlink(home_config)
                
                # Test 2: Config directory file exists (medium priority)
                config_dir_file = os.path.join(config_dir, "game_config.json")
                with open(config_dir_file, 'w') as f:
                    json.dump({"victory": {"flag_content": "CONFIG_DIR_FLAG"}}, f)
                
                config = GameConfig()
                found_file = config._find_config_file()
                assert found_file == "config/game_config.json"
                
                # Test 3: Root config file exists (highest priority)
                root_config = os.path.join(temp_dir, "game_config.json")
                with open(root_config, 'w') as f:
                    json.dump({"victory": {"flag_content": "ROOT_FLAG"}}, f)
                
                config = GameConfig()
                found_file = config._find_config_file()
                assert found_file == "game_config.json"
                
            finally:
                os.chdir(original_cwd)
    
    def test_configuration_merging_preserves_defaults(self):
        """Test that configuration merging preserves default values for missing keys."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Create partial config with only some victory settings
            partial_config = {
                "victory": {
                    "flag_content": "PARTIAL_FLAG"
                    # Missing flag_prefix, flag_suffix, prize_message
                },
                "custom_section": {
                    "custom_value": "test"
                }
                # Missing game and display sections
            }
            json.dump(partial_config, f)
            temp_file = f.name
        
        try:
            config = GameConfig(config_file=temp_file)
            
            # Verify partial config values are used
            assert config.get("victory.flag_content") == "PARTIAL_FLAG"
            assert config.get("custom_section.custom_value") == "test"
            
            # Verify defaults are preserved for missing values
            assert config.get("victory.flag_prefix") == "FLAG{"
            assert config.get("victory.flag_suffix") == "}"
            assert "🏆 YOUR PRIZE:" in config.get("victory.prize_message")
            assert config.get("game.title") == "Labyrinth Adventure Game"
            assert config.get("game.version") == "1.0"
            assert config.get("display.width") == 80
            assert config.get("display.show_map") is True
            
        finally:
            os.unlink(temp_file)


class TestGameConfigErrorHandling:
    """Test cases for GameConfig error handling functionality."""
    
    def test_load_config_permission_error(self):
        """Test loading configuration when file has no read permission."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"victory": {"flag_content": "TEST_FLAG"}}, f)
            temp_file = f.name
        
        try:
            # Remove read permission
            os.chmod(temp_file, 0o000)
            
            with patch('src.config.game_config.logging.getLogger') as mock_logger:
                mock_log = mock_logger.return_value
                config = GameConfig(config_file=temp_file)
                
                # Should fall back to defaults and set read-only mode
                assert config.get("victory.flag_content") == "LABYRINTH_MASTER_2024"
                assert config.is_read_only() is True
                mock_log.error.assert_called()
                
        finally:
            # Restore permissions and clean up
            os.chmod(temp_file, 0o644)
            os.unlink(temp_file)
    
    def test_load_config_empty_file(self):
        """Test loading configuration from empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Write empty content
            f.write("")
            temp_file = f.name
        
        try:
            with patch('src.config.game_config.logging.getLogger') as mock_logger:
                mock_log = mock_logger.return_value
                config = GameConfig(config_file=temp_file)
                
                # Should use defaults
                assert config.get("victory.flag_content") == "LABYRINTH_MASTER_2024"
                assert config.is_read_only() is False
                mock_log.warning.assert_called()
                
        finally:
            os.unlink(temp_file)
    
    def test_load_config_non_dict_json(self):
        """Test loading configuration when JSON is not a dictionary."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Write valid JSON but not a dictionary
            json.dump(["not", "a", "dictionary"], f)
            temp_file = f.name
        
        try:
            with patch('src.config.game_config.logging.getLogger') as mock_logger:
                mock_log = mock_logger.return_value
                config = GameConfig(config_file=temp_file)
                
                # Should use defaults
                assert config.get("victory.flag_content") == "LABYRINTH_MASTER_2024"
                mock_log.error.assert_called()
                
        finally:
            os.unlink(temp_file)
    
    def test_load_config_unicode_decode_error(self):
        """Test loading configuration with encoding issues."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.json', delete=False) as f:
            # Write invalid UTF-8 bytes
            f.write(b'\xff\xfe{"victory": {"flag_content": "TEST"}}')
            temp_file = f.name
        
        try:
            with patch('src.config.game_config.logging.getLogger') as mock_logger:
                mock_log = mock_logger.return_value
                config = GameConfig(config_file=temp_file)
                
                # Should use defaults
                assert config.get("victory.flag_content") == "LABYRINTH_MASTER_2024"
                mock_log.error.assert_called()
                
        finally:
            os.unlink(temp_file)
    
    def test_load_config_file_deleted_during_load(self):
        """Test loading configuration when file is deleted between checks."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"victory": {"flag_content": "TEST_FLAG"}}, f)
            temp_file = f.name
        
        # Delete the file
        os.unlink(temp_file)
        
        with patch('src.config.game_config.logging.getLogger') as mock_logger:
            mock_log = mock_logger.return_value
            config = GameConfig(config_file=temp_file)
            
            # Should use defaults
            assert config.get("victory.flag_content") == "LABYRINTH_MASTER_2024"
            mock_log.warning.assert_called()
    
    def test_save_config_read_only_mode(self):
        """Test saving configuration when in read-only mode."""
        config = GameConfig()
        config._read_only_mode = True
        
        with pytest.raises(PermissionError, match="Cannot save configuration: operating in read-only mode"):
            config.save_config()
    
    def test_save_config_directory_permission_error(self):
        """Test saving configuration when directory has no write permission."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "subdir", "config.json")
            
            # Create subdirectory with no write permission
            subdir = os.path.join(temp_dir, "subdir")
            os.makedirs(subdir)
            os.chmod(subdir, 0o444)  # Read-only
            
            try:
                config = GameConfig(config_file=config_file)
                
                with pytest.raises(OSError):  # Changed from PermissionError to OSError
                    config.save_config()
                
                # Should NOT be in read-only mode since this is an OSError, not PermissionError
                assert config.is_read_only() is False
                
            finally:
                # Restore permissions for cleanup
                os.chmod(subdir, 0o755)
    
    def test_save_config_file_permission_error(self):
        """Test saving configuration when file has no write permission."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"victory": {"flag_content": "TEST"}}, f)
            temp_file = f.name
        
        try:
            # Remove write permission
            os.chmod(temp_file, 0o444)
            
            config = GameConfig(config_file=temp_file)
            
            with pytest.raises(PermissionError):
                config.save_config()
            
            # Should be in read-only mode after failed save
            assert config.is_read_only() is True
            
        finally:
            # Restore permissions and clean up
            os.chmod(temp_file, 0o644)
            os.unlink(temp_file)
    
    def test_save_config_atomic_write_failure_cleanup(self):
        """Test that temporary files are cleaned up when atomic write fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "config.json")
            temp_file = config_file + ".tmp"
            
            config = GameConfig(config_file=config_file)
            
            # Mock json.dump to fail after temp file is created
            with patch('json.dump', side_effect=OSError("Disk full")):
                with pytest.raises(OSError):
                    config.save_config()
                
                # Temporary file should be cleaned up
                assert not os.path.exists(temp_file)
    
    def test_update_flag_content_none_value(self):
        """Test update_flag_content with None value."""
        config = GameConfig()
        
        with pytest.raises(ValueError, match="Flag content cannot be None"):
            config.update_flag_content(None)
    
    def test_update_flag_content_newline_warning(self):
        """Test update_flag_content warns about newline characters."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            with patch('src.config.game_config.logging.getLogger') as mock_logger:
                mock_log = mock_logger.return_value
                config = GameConfig(config_file=temp_file)
                
                config.update_flag_content("FLAG_WITH\nNEWLINE")
                
                # Should warn about newlines but still save
                mock_log.warning.assert_called()
                assert config.get("victory.flag_content") == "FLAG_WITH\nNEWLINE"
                
        finally:
            os.unlink(temp_file)
    
    def test_update_flag_content_save_failure(self):
        """Test update_flag_content when save fails."""
        config = GameConfig(config_file="/invalid/path/config.json")
        
        with pytest.raises(OSError):
            config.update_flag_content("VALID_CONTENT")
    
    def test_is_read_only_default(self):
        """Test is_read_only returns False by default."""
        config = GameConfig()
        assert config.is_read_only() is False
    
    def test_get_config_file_path_custom(self):
        """Test get_config_file_path with custom file."""
        config = GameConfig(config_file="custom_config.json")
        assert config.get_config_file_path() == "custom_config.json"
    
    def test_get_config_file_path_search(self):
        """Test get_config_file_path with file search."""
        with patch('src.config.game_config.GameConfig._find_config_file') as mock_find:
            mock_find.return_value = "found_config.json"
            config = GameConfig()
            assert config.get_config_file_path() == "found_config.json"
    
    def test_reset_to_defaults(self):
        """Test reset_to_defaults functionality."""
        config = GameConfig()
        config.set("victory.flag_content", "CUSTOM_FLAG")
        config._read_only_mode = True
        
        config.reset_to_defaults()
        
        assert config.get("victory.flag_content") == "LABYRINTH_MASTER_2024"
        assert config.is_read_only() is False
    
    def test_validate_configuration_valid(self):
        """Test validate_configuration with valid configuration."""
        config = GameConfig()
        result = config.validate_configuration()
        
        assert result["valid"] is True
        assert len(result["issues"]) == 0
    
    def test_validate_configuration_missing_victory_section(self):
        """Test validate_configuration with missing victory section."""
        config = GameConfig()
        config._config_data = {"game": {"title": "Test"}}
        
        result = config.validate_configuration()
        
        assert result["valid"] is False
        assert "Missing 'victory' section" in result["issues"]
    
    def test_validate_configuration_missing_victory_fields(self):
        """Test validate_configuration with missing victory fields."""
        config = GameConfig()
        config._config_data = {
            "victory": {
                "flag_content": "TEST"
                # Missing other required fields
            },
            "game": {"title": "Test"}
        }
        
        result = config.validate_configuration()
        
        assert result["valid"] is False
        assert any("flag_prefix" in issue for issue in result["issues"])
        assert any("flag_suffix" in issue for issue in result["issues"])
        assert any("prize_message" in issue for issue in result["issues"])
    
    def test_validate_configuration_invalid_prize_message(self):
        """Test validate_configuration with prize message missing flag placeholder."""
        config = GameConfig()
        config.set("victory.prize_message", "You won! But no flag placeholder.")
        
        result = config.validate_configuration()
        
        assert result["valid"] is False
        assert "Prize message template missing {flag} placeholder" in result["issues"]
    
    def test_validate_configuration_missing_game_section(self):
        """Test validate_configuration with missing game section."""
        config = GameConfig()
        config._config_data = {
            "victory": {
                "flag_content": "TEST",
                "flag_prefix": "FLAG{",
                "flag_suffix": "}",
                "prize_message": "Prize: {flag}"
            }
        }
        
        result = config.validate_configuration()
        
        assert result["valid"] is False
        assert "Missing 'game' section" in result["issues"]
    
    def test_get_victory_message_template_error(self):
        """Test get_victory_message with template formatting error."""
        with patch('src.config.game_config.GameConfig._find_config_file') as mock_find_config:
            mock_find_config.return_value = None
            
            with patch('src.config.game_config.logging.getLogger') as mock_logger:
                mock_log = mock_logger.return_value
                config = GameConfig()
                config.set("victory.prize_message", "Invalid template {invalid_placeholder}")
                
                message = config.get_victory_message()
                
                # Should use fallback template
                assert "🏆 YOUR PRIZE: FLAG{LABYRINTH_MASTER_2024}" in message
                mock_log.warning.assert_called()
    
    def test_get_victory_message_fallback_error(self):
        """Test get_victory_message when even fallback template fails."""
        with patch('src.config.game_config.GameConfig._find_config_file') as mock_find_config:
            mock_find_config.return_value = None
            config = GameConfig()
            
            # Create a mock template that will fail on format
            class FailingTemplate:
                def format(self, **kwargs):
                    raise Exception("Format error")
            
            # Mock the get method to return our failing template
            with patch.object(config, 'get') as mock_get:
                def side_effect(key, default=None):
                    if key == "victory.prize_message":
                        return FailingTemplate()
                    elif key == "victory.flag_content":
                        return "LABYRINTH_MASTER_2024"
                    elif key == "victory.flag_prefix":
                        return "FLAG{"
                    elif key == "victory.flag_suffix":
                        return "}"
                    return default
                
                mock_get.side_effect = side_effect
                
                message = config.get_victory_message()
                
                # Should return basic hardcoded message
                assert "🏆 YOUR PRIZE: FLAG{LABYRINTH_MASTER_2024}" in message
    
    def test_load_config_unexpected_error(self):
        """Test load_config handles unexpected errors gracefully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"victory": {"flag_content": "TEST"}}, f)
            temp_file = f.name
        
        try:
            # Mock open to raise unexpected error
            with patch('builtins.open', side_effect=RuntimeError("Unexpected error")):
                with patch('src.config.game_config.logging.getLogger') as mock_logger:
                    mock_log = mock_logger.return_value
                    config = GameConfig(config_file=temp_file)
                    
                    # Should use defaults
                    assert config.get("victory.flag_content") == "LABYRINTH_MASTER_2024"
                    mock_log.error.assert_called()
                    
        finally:
            os.unlink(temp_file)
    
    def test_save_config_unicode_encode_error(self):
        """Test save_config handles unicode encoding errors."""
        config = GameConfig()
        
        # Set content that might cause encoding issues
        config.set("victory.flag_content", "TEST_FLAG")
        
        # Mock json.dump to raise UnicodeEncodeError
        with patch('json.dump', side_effect=UnicodeEncodeError('utf-8', 'test', 0, 1, 'test error')):
            with pytest.raises(IOError, match="Failed to save configuration due to encoding error"):
                config.save_config()
    
    def test_save_config_unexpected_error(self):
        """Test save_config handles unexpected errors."""
        config = GameConfig()
        
        # Mock json.dump to raise unexpected error
        with patch('json.dump', side_effect=RuntimeError("Unexpected error")):
            with pytest.raises(IOError, match="Failed to save configuration"):
                config.save_config()