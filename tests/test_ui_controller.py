"""Tests for the UIController class."""

import pytest
from unittest.mock import Mock, patch

from src.game.ui_controller import UIController
from src.game.display import MessageType
from src.game.command_parser import CommandType
from src.utils.data_models import Item, PlayerStats, ChallengeResult
from src.challenges.base import Challenge


class MockChallenge(Challenge):
    """Mock challenge for testing."""
    
    def present_challenge(self) -> str:
        return "This is a test challenge."
    
    def process_response(self, response: str) -> ChallengeResult:
        return ChallengeResult(success=True, message="Test result")
    
    def get_reward(self):
        return Item("Test Reward", "A test item", "key", 10)


class TestUIController:
    """Test cases for UIController."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_input = Mock()
        self.ui_controller = UIController(use_colors=False, input_handler=self.mock_input)
        self.ui_controller.enable_output_capture()
    
    def test_init_default(self):
        """Test UIController initialization with defaults."""
        ui = UIController()
        assert ui.display_manager is not None
        assert ui.command_parser is not None
        assert ui._capture_output is False
    
    def test_init_with_custom_input_handler(self):
        """Test UIController initialization with custom input handler."""
        mock_handler = Mock()
        ui = UIController(input_handler=mock_handler)
        assert ui._input_handler == mock_handler
    
    def test_output_capture_enable_disable(self):
        """Test output capture functionality."""
        ui = UIController()
        assert ui._capture_output is False
        
        ui.enable_output_capture()
        assert ui._capture_output is True
        
        ui.disable_output_capture()
        assert ui._capture_output is False
    
    def test_display_message(self):
        """Test displaying messages."""
        self.ui_controller.display_message("Test message", MessageType.INFO)
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "Test message" in output[0]
    
    def test_display_chamber(self):
        """Test displaying chamber information."""
        self.ui_controller.display_chamber(
            "Test Chamber", 
            "A mysterious room.", 
            ["north", "south"]
        )
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "Test Chamber" in output[0]
        assert "mysterious room" in output[0]
        assert "north" in output[0]
        assert "south" in output[0]
    
    def test_display_challenge(self):
        """Test displaying challenge information."""
        challenge = MockChallenge("Test Challenge", "A test challenge", 5)
        self.ui_controller.display_challenge(challenge)
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "Test Challenge" in output[0]
        assert "test challenge" in output[0]
    
    def test_display_challenge_result(self):
        """Test displaying challenge results."""
        result = ChallengeResult(
            success=True,
            message="Well done!",
            reward=Item("Gold", "Shiny gold", "treasure", 100)
        )
        self.ui_controller.display_challenge_result(result)
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "SUCCESS" in output[0]
        assert "Well done!" in output[0]
        assert "Gold" in output[0]
    
    def test_display_inventory(self):
        """Test displaying inventory."""
        items = [
            Item("Sword", "A sharp blade", "weapon", 50),
            Item("Potion", "Healing potion", "consumable", 25)
        ]
        self.ui_controller.display_inventory(items)
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "Inventory" in output[0]
        assert "Sword" in output[0]
        assert "Potion" in output[0]
    
    def test_display_player_status(self):
        """Test displaying player status."""
        stats = PlayerStats(strength=12, intelligence=10, dexterity=8, luck=15)
        self.ui_controller.display_player_status(85, stats, 7)
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "Player Status" in output[0]
        assert "Health: 85/100" in output[0]
        assert "Strength: 12" in output[0]
        assert "Chambers Completed: 7/13" in output[0]
    
    def test_display_help_general(self):
        """Test displaying general help."""
        self.ui_controller.display_help()
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "Available Commands" in output[0]
        assert "help" in output[0]
        assert "go" in output[0]
    
    def test_display_help_specific_command(self):
        """Test displaying help for specific command."""
        self.ui_controller.display_help("go")
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "Usage: go <direction>" in output[0]
    
    def test_display_help_invalid_command(self):
        """Test displaying help for invalid command."""
        self.ui_controller.display_help("invalidcommand")
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "Unknown command: invalidcommand" in output[0]
    
    def test_display_game_over_victory(self):
        """Test displaying victory game over screen."""
        stats = {"Chambers Completed": 13, "Time": "30 minutes"}
        self.ui_controller.display_game_over(True, stats)
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "VICTORY" in output[0]
        assert "Congratulations" in output[0]
    
    def test_display_game_over_defeat(self):
        """Test displaying defeat game over screen."""
        stats = {"Chambers Completed": 5, "Time": "15 minutes"}
        self.ui_controller.display_game_over(False, stats)
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "GAME OVER" in output[0]
    
    def test_get_user_input(self):
        """Test getting user input."""
        self.mock_input.return_value = "test input"
        result = self.ui_controller.get_user_input("Test prompt")
        
        assert result == "test input"
        output = self.ui_controller.get_captured_output()
        assert "Test prompt" in output[0]
    
    def test_get_user_input_with_whitespace(self):
        """Test getting user input with whitespace."""
        self.mock_input.return_value = "  test input  "
        result = self.ui_controller.get_user_input()
        
        assert result == "test input"
    
    def test_get_user_input_empty(self):
        """Test getting empty user input."""
        self.mock_input.return_value = ""
        result = self.ui_controller.get_user_input()
        
        assert result == ""
    
    def test_get_user_input_none(self):
        """Test getting None user input."""
        self.mock_input.return_value = None
        result = self.ui_controller.get_user_input()
        
        assert result == ""
    
    def test_get_user_input_keyboard_interrupt(self):
        """Test handling keyboard interrupt during input."""
        self.mock_input.side_effect = KeyboardInterrupt()
        result = self.ui_controller.get_user_input()
        
        assert result == "quit"
    
    def test_get_user_input_eof_error(self):
        """Test handling EOF error during input."""
        self.mock_input.side_effect = EOFError()
        result = self.ui_controller.get_user_input()
        
        assert result == "quit"
    
    def test_parse_command(self):
        """Test parsing commands."""
        result = self.ui_controller.parse_command("go north")
        
        assert result.is_valid
        assert result.action == "go"
        assert result.parameters == ["north"]
        assert result.command_type == CommandType.MOVEMENT
    
    def test_handle_invalid_command(self):
        """Test handling invalid commands."""
        parsed_command = self.ui_controller.parse_command("invalidcommand")
        self.ui_controller.handle_invalid_command(parsed_command)
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "Unknown command" in output[0]
    
    def test_get_command_and_parse(self):
        """Test getting and parsing command in one step."""
        self.mock_input.return_value = "look"
        result = self.ui_controller.get_command_and_parse("Enter action")
        
        assert result.is_valid
        assert result.action == "look"
        assert result.command_type == CommandType.EXAMINATION
    
    def test_display_welcome_message(self):
        """Test displaying welcome message."""
        self.ui_controller.display_welcome_message("Test Game", "2.0")
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "Test Game v2.0" in output[0]
        assert "Welcome" in output[0]
        assert "labyrinth" in output[0]
    
    def test_confirm_action_yes(self):
        """Test confirming action with yes."""
        self.mock_input.return_value = "y"
        result = self.ui_controller.confirm_action("Delete save file?")
        
        assert result is True
        output = self.ui_controller.get_captured_output()
        assert "Delete save file? (y/n)" in output[0]
    
    def test_confirm_action_no(self):
        """Test confirming action with no."""
        self.mock_input.return_value = "n"
        result = self.ui_controller.confirm_action("Delete save file?")
        
        assert result is False
    
    def test_confirm_action_variations(self):
        """Test confirm action with various positive responses."""
        positive_responses = ["yes", "YES", "true", "1", "Y"]
        
        for response in positive_responses:
            self.mock_input.return_value = response
            result = self.ui_controller.confirm_action("Test?")
            assert result is True
    
    def test_display_error(self):
        """Test displaying error messages."""
        self.ui_controller.display_error("Something went wrong")
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "Error: Something went wrong" in output[0]
    
    def test_display_success(self):
        """Test displaying success messages."""
        self.ui_controller.display_success("Operation completed")
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "Operation completed" in output[0]
    
    def test_display_warning(self):
        """Test displaying warning messages."""
        self.ui_controller.display_warning("Be careful")
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "Be careful" in output[0]
    
    def test_display_commands_by_type(self):
        """Test displaying commands by type."""
        self.ui_controller.display_commands_by_type(CommandType.MOVEMENT)
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "Movement Commands" in output[0]
        assert "go" in output[0]
        assert "move" in output[0]
    
    def test_display_separator(self):
        """Test displaying separator line."""
        self.ui_controller.display_separator("=", 30)
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "=" * 30 in output[0]
    
    def test_display_loading_message(self):
        """Test displaying loading message."""
        self.ui_controller.display_loading_message("game data")
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "Loading... game data" in output[0]
    
    def test_get_save_filename(self):
        """Test getting save filename."""
        self.mock_input.return_value = "mysave"
        result = self.ui_controller.get_save_filename()
        
        assert result == "mysave.json"
    
    def test_get_save_filename_with_extension(self):
        """Test getting save filename that already has extension."""
        self.mock_input.return_value = "mysave.json"
        result = self.ui_controller.get_save_filename()
        
        assert result == "mysave.json"
    
    def test_get_save_filename_cancel(self):
        """Test cancelling save filename input."""
        self.mock_input.return_value = "cancel"
        result = self.ui_controller.get_save_filename()
        
        assert result is None
    
    def test_get_save_filename_empty(self):
        """Test getting empty save filename."""
        self.mock_input.return_value = ""
        result = self.ui_controller.get_save_filename()
        
        assert result is None
    
    def test_display_save_files_empty(self):
        """Test displaying empty save files list."""
        self.ui_controller.display_save_files([])
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 1
        assert "No save files found" in output[0]
    
    def test_display_save_files_with_files(self):
        """Test displaying save files list."""
        files = ["save1.json", "save2.json", "save3.json"]
        self.ui_controller.display_save_files(files)
        output = self.ui_controller.get_captured_output()
        
        assert len(output) == 4  # Header + 3 files
        assert "Available save files:" in output[0]
        assert "1. save1.json" in output[1]
        assert "2. save2.json" in output[2]
        assert "3. save3.json" in output[3]
    
    def test_get_load_filename_empty_list(self):
        """Test getting load filename with empty save files list."""
        result = self.ui_controller.get_load_filename([])
        
        assert result is None
        output = self.ui_controller.get_captured_output()
        assert "No save files available" in output[0]
    
    def test_get_load_filename_by_number(self):
        """Test getting load filename by number selection."""
        files = ["save1.json", "save2.json"]
        self.mock_input.return_value = "2"
        result = self.ui_controller.get_load_filename(files)
        
        assert result == "save2.json"
    
    def test_get_load_filename_by_name(self):
        """Test getting load filename by name."""
        files = ["save1.json", "save2.json"]
        self.mock_input.return_value = "save1.json"
        result = self.ui_controller.get_load_filename(files)
        
        assert result == "save1.json"
    
    def test_get_load_filename_by_name_without_extension(self):
        """Test getting load filename by name without extension."""
        files = ["save1.json", "save2.json"]
        self.mock_input.return_value = "save1"
        result = self.ui_controller.get_load_filename(files)
        
        assert result == "save1.json"
    
    def test_get_load_filename_invalid_number(self):
        """Test getting load filename with invalid number."""
        files = ["save1.json"]
        self.mock_input.return_value = "5"
        result = self.ui_controller.get_load_filename(files)
        
        assert result is None
        output = self.ui_controller.get_captured_output()
        assert "Invalid selection" in output[-1]
    
    def test_get_load_filename_invalid_name(self):
        """Test getting load filename with invalid name."""
        files = ["save1.json"]
        self.mock_input.return_value = "nonexistent"
        result = self.ui_controller.get_load_filename(files)
        
        assert result is None
        output = self.ui_controller.get_captured_output()
        assert "Invalid selection" in output[-1]
    
    def test_get_load_filename_cancel(self):
        """Test cancelling load filename selection."""
        files = ["save1.json"]
        self.mock_input.return_value = "cancel"
        result = self.ui_controller.get_load_filename(files)
        
        assert result is None
    
    def test_clear_captured_output(self):
        """Test clearing captured output."""
        self.ui_controller.display_message("Test")
        assert len(self.ui_controller.get_captured_output()) == 1
        
        self.ui_controller.clear_captured_output()
        assert len(self.ui_controller.get_captured_output()) == 0
    
    @patch('os.system')
    def test_clear_screen(self, mock_system):
        """Test clearing screen."""
        ui = UIController()  # Not capturing output
        ui.clear_screen()
        mock_system.assert_called_once()
    
    def test_clear_screen_with_capture(self):
        """Test that clear screen doesn't call os.system when capturing output."""
        with patch('os.system') as mock_system:
            self.ui_controller.clear_screen()  # This one is capturing output
            mock_system.assert_not_called()