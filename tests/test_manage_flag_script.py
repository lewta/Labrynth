"""
Unit tests for the flag management command-line script.
"""

import pytest
import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

# Add scripts directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

import manage_flag


class TestShowCommand:
    """Test cases for the show command."""
    
    def test_show_command_success(self, capsys):
        """Test successful display of flag configuration."""
        # Mock the GameConfig to return predictable values
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            # Set up mock return values
            mock_config.get.side_effect = lambda key: {
                'victory.flag_content': 'TEST_CONTENT',
                'victory.flag_prefix': 'FLAG{',
                'victory.flag_suffix': '}',
                'victory.prize_message': 'Test message: {flag}'
            }.get(key)
            mock_config.get_victory_flag.return_value = 'FLAG{TEST_CONTENT}'
            mock_config.get_victory_message.return_value = 'Test message: FLAG{TEST_CONTENT}'
            
            # Create mock args
            args = MagicMock()
            
            # Execute show command
            result = manage_flag.show_command(args)
            
            # Verify success
            assert result == 0
            
            # Verify output
            captured = capsys.readouterr()
            assert 'Current Flag Configuration:' in captured.out
            assert 'Flag Content: TEST_CONTENT' in captured.out
            assert 'Flag Prefix:  FLAG{' in captured.out
            assert 'Flag Suffix:  }' in captured.out
            assert 'Complete Flag: FLAG{TEST_CONTENT}' in captured.out
            assert 'Test message: FLAG{TEST_CONTENT}' in captured.out
    
    def test_show_command_config_error(self, capsys):
        """Test show command when configuration loading fails."""
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config_class.side_effect = Exception("Config load error")
            
            args = MagicMock()
            result = manage_flag.show_command(args)
            
            # Verify error handling
            assert result == 1
            captured = capsys.readouterr()
            assert 'Error loading configuration: Config load error' in captured.err


class TestUpdateCommand:
    """Test cases for the update command."""
    
    def test_update_command_success(self, capsys):
        """Test successful flag content update."""
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            # Set up mock return values
            mock_config.get.return_value = 'OLD_CONTENT'
            mock_config.get_victory_flag.return_value = 'FLAG{NEW_CONTENT}'
            
            # Create mock args
            args = MagicMock()
            args.content = 'NEW_CONTENT'
            
            # Execute update command
            result = manage_flag.update_command(args)
            
            # Verify success
            assert result == 0
            
            # Verify config was updated
            mock_config.update_flag_content.assert_called_once_with('NEW_CONTENT')
            
            # Verify output
            captured = capsys.readouterr()
            assert 'Flag content updated successfully!' in captured.out
            assert 'Old content: OLD_CONTENT' in captured.out
            assert 'New content: NEW_CONTENT' in captured.out
            assert 'Complete flag: FLAG{NEW_CONTENT}' in captured.out
    
    def test_update_command_empty_content(self, capsys):
        """Test update command with empty content."""
        args = MagicMock()
        args.content = ''
        
        result = manage_flag.update_command(args)
        
        # Verify error handling
        assert result == 1
        captured = capsys.readouterr()
        assert 'Error: Flag content cannot be empty' in captured.err
    
    def test_update_command_whitespace_only_content(self, capsys):
        """Test update command with whitespace-only content."""
        args = MagicMock()
        args.content = '   \t\n   '
        
        result = manage_flag.update_command(args)
        
        # Verify error handling
        assert result == 1
        captured = capsys.readouterr()
        assert 'Error: Flag content cannot be empty or whitespace only' in captured.err
    
    def test_update_command_config_error(self, capsys):
        """Test update command when configuration update fails."""
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            mock_config.update_flag_content.side_effect = Exception("Update error")
            
            args = MagicMock()
            args.content = 'VALID_CONTENT'
            
            result = manage_flag.update_command(args)
            
            # Verify error handling
            assert result == 1
            captured = capsys.readouterr()
            assert 'Error updating flag content: Update error' in captured.err


class TestFormatCommand:
    """Test cases for the format command."""
    
    def test_format_command_prefix_only(self, capsys):
        """Test format command updating only prefix."""
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            # Set up mock return values
            mock_config.get.side_effect = lambda key: {
                'victory.flag_prefix': 'FLAG{',
                'victory.flag_suffix': '}'
            }.get(key)
            mock_config.get_victory_flag.side_effect = ['FLAG{CONTENT}', 'CTF{CONTENT}']
            
            # Create mock args
            args = MagicMock()
            args.prefix = 'CTF{'
            args.suffix = None
            
            # Execute format command
            result = manage_flag.format_command(args)
            
            # Verify success
            assert result == 0
            
            # Verify config was updated
            mock_config.set.assert_called_once_with('victory.flag_prefix', 'CTF{')
            mock_config.save_config.assert_called_once()
            
            # Verify output
            captured = capsys.readouterr()
            assert 'Flag format updated successfully!' in captured.out
            assert "Old prefix: 'FLAG{' -> New prefix: 'CTF{'" in captured.out
            assert 'Old flag: FLAG{CONTENT}' in captured.out
            assert 'New flag: CTF{CONTENT}' in captured.out
    
    def test_format_command_suffix_only(self, capsys):
        """Test format command updating only suffix."""
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            # Set up mock return values
            mock_config.get.side_effect = lambda key: {
                'victory.flag_prefix': 'FLAG{',
                'victory.flag_suffix': '}'
            }.get(key)
            mock_config.get_victory_flag.side_effect = ['FLAG{CONTENT}', 'FLAG{CONTENT]']
            
            # Create mock args
            args = MagicMock()
            args.prefix = None
            args.suffix = ']'
            
            # Execute format command
            result = manage_flag.format_command(args)
            
            # Verify success
            assert result == 0
            
            # Verify config was updated
            mock_config.set.assert_called_once_with('victory.flag_suffix', ']')
            mock_config.save_config.assert_called_once()
            
            # Verify output
            captured = capsys.readouterr()
            assert 'Flag format updated successfully!' in captured.out
            assert "Old suffix: '}' -> New suffix: ']'" in captured.out
    
    def test_format_command_both_prefix_and_suffix(self, capsys):
        """Test format command updating both prefix and suffix."""
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            # Set up mock return values
            mock_config.get.side_effect = lambda key: {
                'victory.flag_prefix': 'FLAG{',
                'victory.flag_suffix': '}'
            }.get(key)
            mock_config.get_victory_flag.side_effect = ['FLAG{CONTENT}', 'CTF{CONTENT]']
            
            # Create mock args
            args = MagicMock()
            args.prefix = 'CTF{'
            args.suffix = ']'
            
            # Execute format command
            result = manage_flag.format_command(args)
            
            # Verify success
            assert result == 0
            
            # Verify config was updated
            expected_calls = [
                (('victory.flag_prefix', 'CTF{'),),
                (('victory.flag_suffix', ']'),)
            ]
            assert mock_config.set.call_args_list == expected_calls
            mock_config.save_config.assert_called_once()
    
    def test_format_command_no_options(self, capsys):
        """Test format command with no prefix or suffix specified."""
        args = MagicMock()
        args.prefix = None
        args.suffix = None
        
        result = manage_flag.format_command(args)
        
        # Verify error handling
        assert result == 1
        captured = capsys.readouterr()
        assert 'Error: At least one of --prefix or --suffix must be specified' in captured.err
    
    def test_format_command_config_error(self, capsys):
        """Test format command when configuration save fails."""
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            mock_config.save_config.side_effect = Exception("Save error")
            
            args = MagicMock()
            args.prefix = 'CTF{'
            args.suffix = None
            
            result = manage_flag.format_command(args)
            
            # Verify error handling
            assert result == 1
            captured = capsys.readouterr()
            assert 'Error updating flag format: Save error' in captured.err


class TestMessageCommand:
    """Test cases for the message command."""
    
    def test_message_command_success(self, capsys):
        """Test successful message template update."""
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            # Set up mock return values
            mock_config.get.return_value = 'Old template: {flag}'
            mock_config.get_victory_message.return_value = 'New template: FLAG{CONTENT}'
            
            # Create mock args
            args = MagicMock()
            args.template = 'New template: {flag}'
            
            # Execute message command
            result = manage_flag.message_command(args)
            
            # Verify success
            assert result == 0
            
            # Verify config was updated
            mock_config.set.assert_called_once_with('victory.prize_message', 'New template: {flag}')
            mock_config.save_config.assert_called_once()
            
            # Verify output
            captured = capsys.readouterr()
            assert 'Victory message template updated successfully!' in captured.out
            assert 'Old template:' in captured.out
            assert 'New template:' in captured.out
            assert 'Preview with current flag:' in captured.out
    
    def test_message_command_empty_template(self, capsys):
        """Test message command with empty template."""
        args = MagicMock()
        args.template = ''
        
        result = manage_flag.message_command(args)
        
        # Verify error handling
        assert result == 1
        captured = capsys.readouterr()
        assert 'Error: Message template cannot be empty' in captured.err
    
    def test_message_command_whitespace_only_template(self, capsys):
        """Test message command with whitespace-only template."""
        args = MagicMock()
        args.template = '   \t\n   '
        
        result = manage_flag.message_command(args)
        
        # Verify error handling
        assert result == 1
        captured = capsys.readouterr()
        assert 'Error: Message template cannot be empty or whitespace only' in captured.err
    
    def test_message_command_missing_flag_placeholder(self, capsys):
        """Test message command with template missing {flag} placeholder."""
        args = MagicMock()
        args.template = 'This template has no placeholder'
        
        result = manage_flag.message_command(args)
        
        # Verify error handling
        assert result == 1
        captured = capsys.readouterr()
        assert 'Error: Message template must contain {flag} placeholder' in captured.err
    
    def test_message_command_invalid_template_format(self, capsys):
        """Test message command with invalid template format."""
        args = MagicMock()
        args.template = 'Invalid template: {flag} {invalid_placeholder'
        
        result = manage_flag.message_command(args)
        
        # Verify error handling
        assert result == 1
        captured = capsys.readouterr()
        assert 'Error: Invalid message template format:' in captured.err
    
    def test_message_command_config_error(self, capsys):
        """Test message command when configuration save fails."""
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            mock_config.save_config.side_effect = Exception("Save error")
            
            args = MagicMock()
            args.template = 'Valid template: {flag}'
            
            result = manage_flag.message_command(args)
            
            # Verify error handling
            assert result == 1
            captured = capsys.readouterr()
            assert 'Error updating message template: Save error' in captured.err


class TestMainFunction:
    """Test cases for the main function and argument parsing."""
    
    def test_main_no_command(self, capsys):
        """Test main function when no command is provided."""
        with patch('sys.argv', ['manage_flag.py']):
            result = manage_flag.main()
            
            # Verify help is displayed and error code returned
            assert result == 1
            captured = capsys.readouterr()
            assert 'usage:' in captured.out
    
    def test_main_show_command(self):
        """Test main function with show command."""
        with patch('sys.argv', ['manage_flag.py', 'show']):
            with patch('manage_flag.show_command') as mock_show:
                mock_show.return_value = 0
                
                result = manage_flag.main()
                
                # Verify show command was called
                assert result == 0
                mock_show.assert_called_once()
    
    def test_main_update_command(self):
        """Test main function with update command."""
        with patch('sys.argv', ['manage_flag.py', 'update', 'TEST_CONTENT']):
            with patch('manage_flag.update_command') as mock_update:
                mock_update.return_value = 0
                
                result = manage_flag.main()
                
                # Verify update command was called
                assert result == 0
                mock_update.assert_called_once()
                
                # Verify args were parsed correctly
                args = mock_update.call_args[0][0]
                assert args.content == 'TEST_CONTENT'
    
    def test_main_format_command(self):
        """Test main function with format command."""
        with patch('sys.argv', ['manage_flag.py', 'format', '--prefix', 'CTF{', '--suffix', ']']):
            with patch('manage_flag.format_command') as mock_format:
                mock_format.return_value = 0
                
                result = manage_flag.main()
                
                # Verify format command was called
                assert result == 0
                mock_format.assert_called_once()
                
                # Verify args were parsed correctly
                args = mock_format.call_args[0][0]
                assert args.prefix == 'CTF{'
                assert args.suffix == ']'
    
    def test_main_message_command(self):
        """Test main function with message command."""
        with patch('sys.argv', ['manage_flag.py', 'message', 'Test message: {flag}']):
            with patch('manage_flag.message_command') as mock_message:
                mock_message.return_value = 0
                
                result = manage_flag.main()
                
                # Verify message command was called
                assert result == 0
                mock_message.assert_called_once()
                
                # Verify args were parsed correctly
                args = mock_message.call_args[0][0]
                assert args.template == 'Test message: {flag}'
    
    def test_main_invalid_command(self, capsys):
        """Test main function with invalid command."""
        with patch('sys.argv', ['manage_flag.py', 'invalid']):
            with pytest.raises(SystemExit):
                manage_flag.main()


class TestSampleCommand:
    """Test cases for the sample command."""
    
    def test_sample_command_success(self, capsys):
        """Test successful creation of sample configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, 'test_config.json')
            
            # Create mock args
            args = MagicMock()
            args.output = output_file
            args.force = False
            
            # Execute sample command
            result = manage_flag.sample_command(args)
            
            # Verify success
            assert result == 0
            
            # Verify file was created
            assert os.path.exists(output_file)
            
            # Verify file content
            with open(output_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Check structure
            assert '_comment' in config_data
            assert '_description' in config_data
            assert 'victory' in config_data
            assert 'game' in config_data
            assert 'display' in config_data
            assert '_examples' in config_data
            
            # Check victory section
            victory = config_data['victory']
            assert 'flag_content' in victory
            assert 'flag_prefix' in victory
            assert 'flag_suffix' in victory
            assert 'prize_message' in victory
            assert '_flag_content_help' in victory
            
            # Check examples section
            examples = config_data['_examples']
            assert 'ctf_event' in examples
            assert 'themed_event' in examples
            assert 'simple_format' in examples
            
            # Verify output
            captured = capsys.readouterr()
            assert f'Sample configuration file created: {output_file}' in captured.out
            assert 'Default configuration values' in captured.out
            assert 'Helpful comments explaining each setting' in captured.out
            assert 'Example configurations for different use cases' in captured.out
    
    def test_sample_command_default_output(self, capsys):
        """Test sample command with default output file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create mock args
                args = MagicMock()
                args.output = None  # Should use default
                args.force = False
                
                # Execute sample command
                result = manage_flag.sample_command(args)
                
                # Verify success
                assert result == 0
                
                # Verify default file was created
                assert os.path.exists('game_config.json')
                
                # Verify output mentions default file
                captured = capsys.readouterr()
                assert 'Sample configuration file created: game_config.json' in captured.out
                
            finally:
                os.chdir(original_cwd)
    
    def test_sample_command_file_exists_no_force(self, capsys):
        """Test sample command when file exists and force is not used."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, 'existing_config.json')
            
            # Create existing file
            with open(output_file, 'w') as f:
                f.write('{"existing": "config"}')
            
            # Create mock args
            args = MagicMock()
            args.output = output_file
            args.force = False
            
            # Execute sample command
            result = manage_flag.sample_command(args)
            
            # Verify error
            assert result == 1
            
            # Verify error message
            captured = capsys.readouterr()
            assert f"Error: Configuration file '{output_file}' already exists." in captured.err
            assert 'Use --force to overwrite' in captured.err
            
            # Verify original file is unchanged
            with open(output_file, 'r') as f:
                content = json.load(f)
                assert content == {"existing": "config"}
    
    def test_sample_command_file_exists_with_force(self, capsys):
        """Test sample command when file exists and force is used."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, 'existing_config.json')
            
            # Create existing file
            with open(output_file, 'w') as f:
                f.write('{"existing": "config"}')
            
            # Create mock args
            args = MagicMock()
            args.output = output_file
            args.force = True
            
            # Execute sample command
            result = manage_flag.sample_command(args)
            
            # Verify success
            assert result == 0
            
            # Verify file was overwritten
            with open(output_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                assert '_comment' in config_data
                assert 'victory' in config_data
    
    def test_sample_command_write_error(self, capsys):
        """Test sample command when file write fails."""
        # Try to write to a directory that doesn't exist
        invalid_path = '/nonexistent/directory/config.json'
        
        # Create mock args
        args = MagicMock()
        args.output = invalid_path
        args.force = False
        
        # Execute sample command
        result = manage_flag.sample_command(args)
        
        # Verify error
        assert result == 1
        
        # Verify error message
        captured = capsys.readouterr()
        assert 'Error creating sample configuration file:' in captured.err


class TestTestCommand:
    """Test cases for the test command."""
    
    def test_test_command_success(self, capsys):
        """Test successful configuration testing."""
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            # Set up mock return values
            mock_config.get_config_file_path.return_value = '/path/to/config.json'
            mock_config.is_read_only.return_value = False
            mock_config.validate_configuration.return_value = {
                'valid': True,
                'issues': []
            }
            mock_config.get.side_effect = lambda key: {
                'victory.flag_content': 'TEST_CONTENT',
                'victory.flag_prefix': 'FLAG{',
                'victory.flag_suffix': '}',
                'victory.prize_message': 'Your prize: {flag}'
            }.get(key)
            mock_config.get_victory_flag.return_value = 'FLAG{TEST_CONTENT}'
            mock_config.get_victory_message.return_value = 'Your prize: FLAG{TEST_CONTENT}'
            
            # Create mock args
            args = MagicMock()
            
            # Execute test command
            result = manage_flag.test_command(args)
            
            # Verify success
            assert result == 0
            
            # Verify output
            captured = capsys.readouterr()
            assert 'Configuration Test Results' in captured.out
            assert 'Using configuration file: /path/to/config.json' in captured.out
            assert '✅ Configuration validation: PASSED' in captured.out
            assert 'Flag Components:' in captured.out
            assert "Content: 'TEST_CONTENT'" in captured.out
            assert "Prefix:  'FLAG{'" in captured.out
            assert "Suffix:  '}'" in captured.out
            assert 'Complete Flag: FLAG{TEST_CONTENT}' in captured.out
            assert 'Victory Message Preview:' in captured.out
            assert 'Your prize: FLAG{TEST_CONTENT}' in captured.out
            assert 'Message Template:' in captured.out
            assert 'Contains {flag} placeholder: ✅' in captured.out
            assert 'Template formatting: ✅ Valid' in captured.out
            assert 'Usage Suggestions:' in captured.out
    
    def test_test_command_no_config_file(self, capsys):
        """Test test command when no configuration file is found."""
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            # Set up mock return values
            mock_config.get_config_file_path.return_value = None
            mock_config.is_read_only.return_value = False
            mock_config.validate_configuration.return_value = {
                'valid': True,
                'issues': []
            }
            mock_config.get.side_effect = lambda key: {
                'victory.flag_content': 'LABYRINTH_MASTER_2024',
                'victory.flag_prefix': 'FLAG{',
                'victory.flag_suffix': '}',
                'victory.prize_message': 'Default message: {flag}'
            }.get(key)
            mock_config.get_victory_flag.return_value = 'FLAG{LABYRINTH_MASTER_2024}'
            mock_config.get_victory_message.return_value = 'Default message: FLAG{LABYRINTH_MASTER_2024}'
            
            # Create mock args
            args = MagicMock()
            
            # Execute test command
            result = manage_flag.test_command(args)
            
            # Verify success
            assert result == 0
            
            # Verify output
            captured = capsys.readouterr()
            assert 'Using default configuration (no config file found)' in captured.out
    
    def test_test_command_read_only_mode(self, capsys):
        """Test test command when configuration is in read-only mode."""
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            # Set up mock return values
            mock_config.get_config_file_path.return_value = '/path/to/config.json'
            mock_config.is_read_only.return_value = True
            mock_config.validate_configuration.return_value = {
                'valid': True,
                'issues': []
            }
            mock_config.get.side_effect = lambda key: {
                'victory.flag_content': 'TEST_CONTENT',
                'victory.flag_prefix': 'FLAG{',
                'victory.flag_suffix': '}',
                'victory.prize_message': 'Your prize: {flag}'
            }.get(key)
            mock_config.get_victory_flag.return_value = 'FLAG{TEST_CONTENT}'
            mock_config.get_victory_message.return_value = 'Your prize: FLAG{TEST_CONTENT}'
            
            # Create mock args
            args = MagicMock()
            
            # Execute test command
            result = manage_flag.test_command(args)
            
            # Verify success
            assert result == 0
            
            # Verify output
            captured = capsys.readouterr()
            assert '⚠️  WARNING: Configuration is in read-only mode' in captured.out
    
    def test_test_command_validation_failed(self, capsys):
        """Test test command when configuration validation fails."""
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            # Set up mock return values
            mock_config.get_config_file_path.return_value = '/path/to/config.json'
            mock_config.is_read_only.return_value = False
            mock_config.validate_configuration.return_value = {
                'valid': False,
                'issues': ['Missing flag content', 'Invalid message template']
            }
            mock_config.get.side_effect = lambda key: {
                'victory.flag_content': '',
                'victory.flag_prefix': 'FLAG{',
                'victory.flag_suffix': '}',
                'victory.prize_message': 'Invalid template without placeholder'
            }.get(key)
            mock_config.get_victory_flag.return_value = 'FLAG{}'
            mock_config.get_victory_message.return_value = 'Invalid template without placeholder'
            
            # Create mock args
            args = MagicMock()
            
            # Execute test command
            result = manage_flag.test_command(args)
            
            # Verify success (test command shows issues but doesn't fail)
            assert result == 0
            
            # Verify output
            captured = capsys.readouterr()
            assert '❌ Configuration validation: FAILED' in captured.out
            assert '• Missing flag content' in captured.out
            assert '• Invalid message template' in captured.out
            assert 'Contains {flag} placeholder: ❌' in captured.out
            assert '• Fix configuration issues listed above' in captured.out
    
    def test_test_command_template_formatting_error(self, capsys):
        """Test test command when template formatting fails."""
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            # Set up mock return values
            mock_config.get_config_file_path.return_value = '/path/to/config.json'
            mock_config.is_read_only.return_value = False
            mock_config.validate_configuration.return_value = {
                'valid': True,
                'issues': []
            }
            mock_config.get.side_effect = lambda key: {
                'victory.flag_content': 'TEST_CONTENT',
                'victory.flag_prefix': 'FLAG{',
                'victory.flag_suffix': '}',
                'victory.prize_message': 'Invalid template: {flag} {invalid'
            }.get(key)
            mock_config.get_victory_flag.return_value = 'FLAG{TEST_CONTENT}'
            mock_config.get_victory_message.return_value = 'Invalid template: FLAG{TEST_CONTENT} {invalid'
            
            # Create mock args
            args = MagicMock()
            
            # Execute test command
            result = manage_flag.test_command(args)
            
            # Verify success
            assert result == 0
            
            # Verify output
            captured = capsys.readouterr()
            assert 'Template formatting: ❌ Error -' in captured.out
    
    def test_test_command_config_error(self, capsys):
        """Test test command when configuration loading fails."""
        with patch('manage_flag.GameConfig') as mock_config_class:
            mock_config_class.side_effect = Exception("Config load error")
            
            args = MagicMock()
            result = manage_flag.test_command(args)
            
            # Verify error handling
            assert result == 1
            captured = capsys.readouterr()
            assert 'Error testing configuration: Config load error' in captured.err


class TestMainFunctionExtended:
    """Extended test cases for the main function with new commands."""
    
    def test_main_sample_command(self):
        """Test main function with sample command."""
        with patch('sys.argv', ['manage_flag.py', 'sample', '--output', 'test.json', '--force']):
            with patch('manage_flag.sample_command') as mock_sample:
                mock_sample.return_value = 0
                
                result = manage_flag.main()
                
                # Verify sample command was called
                assert result == 0
                mock_sample.assert_called_once()
                
                # Verify args were parsed correctly
                args = mock_sample.call_args[0][0]
                assert args.output == 'test.json'
                assert args.force is True
    
    def test_main_test_command(self):
        """Test main function with test command."""
        with patch('sys.argv', ['manage_flag.py', 'test']):
            with patch('manage_flag.test_command') as mock_test:
                mock_test.return_value = 0
                
                result = manage_flag.main()
                
                # Verify test command was called
                assert result == 0
                mock_test.assert_called_once()


class TestCommandLineIntegration:
    """Integration tests for command-line functionality."""
    
    def test_script_executable_permissions(self):
        """Test that the script has executable permissions."""
        script_path = Path(__file__).parent.parent / 'scripts' / 'manage_flag.py'
        assert script_path.exists()
        
        # Check if file is executable (on Unix-like systems)
        if os.name != 'nt':  # Not Windows
            assert os.access(script_path, os.X_OK)
    
    def test_script_shebang(self):
        """Test that the script has proper shebang line."""
        script_path = Path(__file__).parent.parent / 'scripts' / 'manage_flag.py'
        
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
            assert first_line == '#!/usr/bin/env python3'
    
    def test_help_text_includes_new_commands(self, capsys):
        """Test that help text includes the new sample and test commands."""
        with patch('sys.argv', ['manage_flag.py', '--help']):
            with pytest.raises(SystemExit):
                manage_flag.main()
            
            captured = capsys.readouterr()
            assert 'sample' in captured.out
            assert 'test' in captured.out
            assert 'Create sample configuration file with examples' in captured.out
            assert 'Test and preview current configuration' in captured.out