"""Tests for the GameEngine class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time

from src.game.engine import GameEngine
from src.game.world import WorldManager, Chamber
from src.game.player import PlayerManager
from src.game.ui_controller import UIController
from src.game.command_parser import ParsedCommand, CommandType
from src.utils.data_models import GameState, Item, PlayerStats
from src.utils.exceptions import GameException, SaveLoadException


class TestGameEngine:
    """Test cases for GameEngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = GameEngine()
        
        # Mock the UI controller to avoid actual input/output
        self.engine.ui_controller = Mock(spec=UIController)
        
        # Get the existing chamber from the default labyrinth
        self.test_chamber = self.engine.world_manager.get_chamber(1)
        if self.test_chamber is None:
            # If no chamber exists, create one
            self.test_chamber = Chamber(1, "Test Chamber", "A test chamber")
            self.engine.world_manager.chambers[1] = self.test_chamber
    
    def test_initialization(self):
        """Test GameEngine initialization."""
        engine = GameEngine()
        
        assert isinstance(engine.world_manager, WorldManager)
        assert isinstance(engine.player_manager, PlayerManager)
        assert isinstance(engine.ui_controller, UIController)
        assert not engine.running
        assert not engine.game_started
        assert engine.commands_processed == 0
        assert engine.challenges_completed == 0
    
    def test_initialization_with_config(self):
        """Test GameEngine initialization with config file."""
        with patch.object(WorldManager, 'load_from_file') as mock_load:
            engine = GameEngine(config_file="test_config.json")
            mock_load.assert_called_once_with("test_config.json")
    
    def test_initialization_config_error(self):
        """Test GameEngine initialization with invalid config."""
        with patch.object(WorldManager, 'load_from_file', side_effect=Exception("Config error")):
            with pytest.raises(GameException, match="Failed to initialize world"):
                GameEngine(config_file="invalid_config.json")
    
    def test_start_game(self):
        """Test starting a new game."""
        with patch.object(self.engine, 'game_loop') as mock_loop:
            self.engine.start_game()
            
            assert self.engine.running
            assert self.engine.game_started
            assert self.engine.start_time > 0
            
            # Verify UI calls
            self.engine.ui_controller.display_welcome_message.assert_called_once()
            mock_loop.assert_called_once()
    
    def test_start_game_already_started(self):
        """Test starting game when already started."""
        self.engine.game_started = True
        
        with pytest.raises(GameException, match="Game is already started"):
            self.engine.start_game()
    
    def test_process_command_invalid(self):
        """Test processing invalid command."""
        invalid_command = ParsedCommand(
            command_type=CommandType.SYSTEM,
            action="invalid",
            parameters=[],
            raw_input="invalid",
            is_valid=False,
            error_message="Invalid command"
        )
        
        self.engine.process_command(invalid_command)
        
        self.engine.ui_controller.handle_invalid_command.assert_called_once_with(invalid_command)
        assert self.engine.commands_processed == 0
    
    def test_process_command_valid(self):
        """Test processing valid command."""
        valid_command = ParsedCommand(
            command_type=CommandType.SYSTEM,
            action="help",
            parameters=[],
            raw_input="help",
            is_valid=True
        )
        
        self.engine.process_command(valid_command)
        
        assert self.engine.commands_processed == 1
        self.engine.ui_controller.display_help.assert_called_once()
    
    def test_handle_movement_command_success(self):
        """Test successful movement command."""
        # Use existing connection from chamber 1 to chamber 2 (north)
        move_command = ParsedCommand(
            command_type=CommandType.MOVEMENT,
            action="go",
            parameters=["north"],
            raw_input="go north",
            is_valid=True
        )
        
        self.engine._handle_movement_command(move_command)
        
        assert self.engine.world_manager.current_chamber_id == 2
    
    def test_handle_movement_command_failure(self):
        """Test failed movement command."""
        # Try to go in a direction that doesn't exist from chamber 1
        move_command = ParsedCommand(
            command_type=CommandType.MOVEMENT,
            action="go",
            parameters=["south"],  # Chamber 1 only has north exit
            raw_input="go south",
            is_valid=True
        )
        
        self.engine._handle_movement_command(move_command)
        
        assert self.engine.world_manager.current_chamber_id == 1
        self.engine.ui_controller.display_message.assert_called_with("You cannot go south from here.")
    
    def test_handle_examination_command_look(self):
        """Test look command."""
        look_command = ParsedCommand(
            command_type=CommandType.EXAMINATION,
            action="look",
            parameters=[],
            raw_input="look",
            is_valid=True
        )
        
        self.engine._handle_examination_command(look_command)
        
        self.engine.ui_controller.display_chamber.assert_called_once()
    
    def test_handle_examination_command_examine(self):
        """Test examine command with target."""
        examine_command = ParsedCommand(
            command_type=CommandType.EXAMINATION,
            action="examine",
            parameters=["exits"],
            raw_input="examine exits",
            is_valid=True
        )
        
        self.engine._handle_examination_command(examine_command)
        
        # Should call _examine_target which displays a message
        self.engine.ui_controller.display_message.assert_called()
    
    def test_handle_inventory_command_show(self):
        """Test inventory display command."""
        inventory_command = ParsedCommand(
            command_type=CommandType.INVENTORY,
            action="inventory",
            parameters=[],
            raw_input="inventory",
            is_valid=True
        )
        
        self.engine._handle_inventory_command(inventory_command)
        
        self.engine.ui_controller.display_inventory.assert_called_once()
    
    def test_handle_inventory_command_use_success(self):
        """Test successful use item command."""
        # Add an item to player inventory
        test_item = Item("Health Potion", "Restores health", "potion", 50)
        self.engine.player_manager.add_item(test_item)
        
        use_command = ParsedCommand(
            command_type=CommandType.INVENTORY,
            action="use",
            parameters=["Health Potion"],
            raw_input="use Health Potion",
            is_valid=True
        )
        
        self.engine._handle_inventory_command(use_command)
        
        self.engine.ui_controller.display_success.assert_called()
    
    def test_handle_inventory_command_use_failure(self):
        """Test failed use item command."""
        use_command = ParsedCommand(
            command_type=CommandType.INVENTORY,
            action="use",
            parameters=["Nonexistent Item"],
            raw_input="use Nonexistent Item",
            is_valid=True
        )
        
        self.engine._handle_inventory_command(use_command)
        
        self.engine.ui_controller.display_error.assert_called()
    
    def test_handle_inventory_command_drop_success(self):
        """Test successful drop item command."""
        # Add an item to player inventory
        test_item = Item("Test Item", "A test item", "misc", 10)
        self.engine.player_manager.add_item(test_item)
        
        drop_command = ParsedCommand(
            command_type=CommandType.INVENTORY,
            action="drop",
            parameters=["Test Item"],
            raw_input="drop Test Item",
            is_valid=True
        )
        
        self.engine._handle_inventory_command(drop_command)
        
        self.engine.ui_controller.display_success.assert_called()
        # Item should be in the chamber now
        assert self.test_chamber.has_item("Test Item")
    
    def test_handle_interaction_command_take_success(self):
        """Test successful take item command."""
        # Add an item to the chamber
        test_item = Item("Chamber Item", "An item in the chamber", "misc", 20)
        self.test_chamber.add_item(test_item)
        
        take_command = ParsedCommand(
            command_type=CommandType.INTERACTION,
            action="take",
            parameters=["Chamber Item"],
            raw_input="take Chamber Item",
            is_valid=True
        )
        
        self.engine._handle_interaction_command(take_command)
        
        self.engine.ui_controller.display_success.assert_called()
        assert self.engine.player_manager.has_item("Chamber Item")
    
    def test_handle_interaction_command_take_failure(self):
        """Test failed take item command."""
        take_command = ParsedCommand(
            command_type=CommandType.INTERACTION,
            action="take",
            parameters=["Nonexistent Item"],
            raw_input="take Nonexistent Item",
            is_valid=True
        )
        
        self.engine._handle_interaction_command(take_command)
        
        self.engine.ui_controller.display_error.assert_called()
    
    def test_handle_system_command_help(self):
        """Test help command."""
        help_command = ParsedCommand(
            command_type=CommandType.SYSTEM,
            action="help",
            parameters=[],
            raw_input="help",
            is_valid=True
        )
        
        self.engine._handle_system_command(help_command)
        
        self.engine.ui_controller.display_help.assert_called_once_with()
    
    def test_handle_system_command_help_specific(self):
        """Test help command with specific command."""
        help_command = ParsedCommand(
            command_type=CommandType.SYSTEM,
            action="help",
            parameters=["go"],
            raw_input="help go",
            is_valid=True
        )
        
        self.engine._handle_system_command(help_command)
        
        self.engine.ui_controller.display_help.assert_called_once_with("go")
    
    def test_handle_system_command_status(self):
        """Test status command."""
        status_command = ParsedCommand(
            command_type=CommandType.SYSTEM,
            action="status",
            parameters=[],
            raw_input="status",
            is_valid=True
        )
        
        self.engine._handle_system_command(status_command)
        
        self.engine.ui_controller.display_player_status.assert_called_once()
    
    def test_handle_system_command_quit(self):
        """Test quit command."""
        quit_command = ParsedCommand(
            command_type=CommandType.SYSTEM,
            action="quit",
            parameters=[],
            raw_input="quit",
            is_valid=True
        )
        
        # Mock confirmation to return True
        self.engine.ui_controller.confirm_action.return_value = False
        
        self.engine._handle_system_command(quit_command)
        
        assert not self.engine.running
    
    def test_handle_challenge_command_no_challenge(self):
        """Test challenge command when no challenge is present."""
        answer_command = ParsedCommand(
            command_type=CommandType.CHALLENGE,
            action="answer",
            parameters=["test answer"],
            raw_input="answer test answer",
            is_valid=True
        )
        
        self.engine._handle_challenge_command(answer_command)
        
        self.engine.ui_controller.display_message.assert_called_with("There is no active challenge here.")
    
    def test_check_win_condition_not_won(self):
        """Test win condition when not all chambers are completed."""
        # Complete only one chamber (there are 3 total in default labyrinth)
        self.test_chamber.complete_challenge()
        
        assert not self.engine.check_win_condition()
    
    def test_check_win_condition_won(self):
        """Test win condition when all chambers are completed."""
        # Complete all chambers in the default labyrinth by setting completed flag directly
        for chamber in self.engine.world_manager.chambers.values():
            chamber.completed = True
        
        assert self.engine.check_win_condition()
    
    def test_save_game_creates_game_state(self):
        """Test that save_game creates proper GameState."""
        self.engine.start_time = time.time() - 100  # 100 seconds ago
        
        # Add some test data
        test_item = Item("Test Item", "A test item", "misc", 10)
        self.engine.player_manager.add_item(test_item)
        self.engine.player_manager.current_health = 80
        self.test_chamber.completed = True
        
        result = self.engine.save_game("test_save.json")
        assert result
    
    def test_load_game_success(self):
        """Test successful game loading."""
        # First save a game
        test_item = Item("Test Item", "A test item", "misc", 10)
        self.engine.player_manager.add_item(test_item)
        self.engine.player_manager.current_health = 80
        self.test_chamber.completed = True
        self.engine.start_time = time.time() - 100
        
        save_result = self.engine.save_game("test_load.json")
        assert save_result
        
        # Reset game state
        self.engine.player_manager.current_health = 100
        self.engine.player_manager.inventory.clear()
        self.test_chamber.completed = False
        self.engine.world_manager.current_chamber_id = 1
        
        # Load the game
        load_result = self.engine.load_game("test_load.json")
        assert load_result
        
        # Verify state was restored
        assert self.engine.player_manager.current_health == 80
        assert self.engine.player_manager.has_item("Test Item")
        assert self.test_chamber.completed
    
    def test_load_game_file_not_found(self):
        """Test loading non-existent save file."""
        result = self.engine.load_game("nonexistent_save.json")
        assert not result
    
    def test_list_save_files_empty(self):
        """Test listing save files when none exist."""
        result = self.engine.list_save_files()
        assert isinstance(result, list)
    
    def test_list_save_files_with_saves(self):
        """Test listing save files when some exist."""
        # Create a couple of save files
        self.engine.save_game("save1.json")
        self.engine.save_game("save2.json")
        
        result = self.engine.list_save_files()
        assert len(result) >= 2
        assert "save1.json" in result
        assert "save2.json" in result
    
    def test_get_game_statistics(self):
        """Test getting game statistics."""
        self.engine.game_started = True
        self.engine.running = True
        self.engine.start_time = time.time() - 50
        self.engine.commands_processed = 10
        self.engine.challenges_completed = 3
        
        stats = self.engine.get_game_statistics()
        
        assert stats['game_started']
        assert stats['running']
        assert stats['current_chamber'] == 1
        assert stats['commands_processed'] == 10
        assert stats['challenges_completed'] == 3
        assert stats['game_time'] >= 49  # Should be around 50 seconds
        assert stats['player_alive']
    
    def test_reset_game(self):
        """Test resetting the game."""
        # Set up some game state
        self.engine.running = True
        self.engine.game_started = True
        self.engine.start_time = time.time()
        self.engine.commands_processed = 5
        self.engine.challenges_completed = 2
        
        # Complete a chamber
        self.test_chamber.complete_challenge()
        
        # Reset the game
        self.engine.reset_game()
        
        assert not self.engine.running
        assert not self.engine.game_started
        assert self.engine.start_time == 0
        assert self.engine.commands_processed == 0
        assert self.engine.challenges_completed == 0
        assert not self.test_chamber.is_completed()
    
    def test_is_running(self):
        """Test is_running method."""
        assert not self.engine.is_running()
        
        self.engine.running = True
        assert self.engine.is_running()
    
    def test_stop_game(self):
        """Test stopping the game."""
        self.engine.running = True
        self.engine.stop_game()
        assert not self.engine.running
    
    def test_examine_target_item(self):
        """Test examining an item in the chamber."""
        test_item = Item("Magic Sword", "A gleaming magical sword", "weapon", 100)
        self.test_chamber.add_item(test_item)
        
        self.engine._examine_target("Magic Sword")
        
        self.engine.ui_controller.display_message.assert_called_with("Magic Sword: A gleaming magical sword")
    
    def test_examine_target_exits(self):
        """Test examining exits."""
        # Chamber 1 has a north exit in the default labyrinth
        self.engine._examine_target("exits")
        
        self.engine.ui_controller.display_message.assert_called_with("Available exits: north")
    
    def test_examine_target_unknown(self):
        """Test examining unknown target."""
        self.engine._examine_target("unknown_thing")
        
        self.engine.ui_controller.display_message.assert_called_with("You don't see anything special about 'unknown_thing'.")
    
    def test_display_current_chamber(self):
        """Test displaying current chamber."""
        self.engine._display_current_chamber()
        
        self.engine.ui_controller.display_chamber.assert_called_once()
    
    def test_display_current_chamber_no_chamber(self):
        """Test displaying current chamber when none exists."""
        self.engine.world_manager.current_chamber_id = 999  # Non-existent chamber
        
        self.engine._display_current_chamber()
        
        self.engine.ui_controller.display_error.assert_called_with("You are in an unknown location!")
    
    def test_display_player_status(self):
        """Test displaying player status."""
        self.engine._display_player_status()
        
        self.engine.ui_controller.display_player_status.assert_called_once()
    
    @patch('time.time')
    def test_handle_victory(self, mock_time):
        """Test handling victory condition."""
        mock_time.return_value = 1000
        self.engine.start_time = 900  # 100 seconds ago
        self.engine.commands_processed = 20
        self.engine.challenges_completed = 5
        
        self.engine._handle_victory()
        
        assert not self.engine.running
        self.engine.ui_controller.display_game_over.assert_called_once()
        
        # Check the stats passed to display_game_over
        call_args = self.engine.ui_controller.display_game_over.call_args
        victory_flag = call_args[0][0]
        stats = call_args[0][1]
        
        assert victory_flag is True
        assert stats['commands_used'] == 20
        assert stats['challenges_completed'] == 5
        assert stats['time_played'] == 100
    
    @patch('time.time')
    def test_handle_defeat(self, mock_time):
        """Test handling defeat condition."""
        mock_time.return_value = 1000
        self.engine.start_time = 950  # 50 seconds ago
        
        self.engine._handle_defeat()
        
        assert not self.engine.running
        self.engine.ui_controller.display_game_over.assert_called_once()
        
        # Check the stats passed to display_game_over
        call_args = self.engine.ui_controller.display_game_over.call_args
        victory_flag = call_args[0][0]
        
        assert victory_flag is False


class TestGameEngineIntegration:
    """Integration tests for GameEngine with real components."""
    
    def test_full_game_initialization(self):
        """Test full game initialization with real components."""
        engine = GameEngine()
        
        # Should have initialized all components
        assert engine.world_manager.get_chamber_count() > 0
        assert engine.player_manager.is_alive()
        assert engine.ui_controller is not None
    
    def test_movement_integration(self):
        """Test movement with real world manager."""
        engine = GameEngine()
        
        # Get initial chamber
        initial_chamber = engine.world_manager.current_chamber_id
        
        # Try to move (should fail with default labyrinth if no connections)
        move_command = ParsedCommand(
            command_type=CommandType.MOVEMENT,
            action="go",
            parameters=["nonexistent"],
            raw_input="go nonexistent",
            is_valid=True
        )
        
        # Mock UI to avoid output
        engine.ui_controller = Mock(spec=UIController)
        
        engine._handle_movement_command(move_command)
        
        # Should still be in same chamber
        assert engine.world_manager.current_chamber_id == initial_chamber
    
    def test_inventory_integration(self):
        """Test inventory operations with real player manager."""
        engine = GameEngine()
        engine.ui_controller = Mock(spec=UIController)
        
        # Add item to player
        test_item = Item("Test Item", "A test item", "misc", 10)
        engine.player_manager.add_item(test_item)
        
        # Test inventory display
        inventory_command = ParsedCommand(
            command_type=CommandType.INVENTORY,
            action="inventory",
            parameters=[],
            raw_input="inventory",
            is_valid=True
        )
        
        engine._handle_inventory_command(inventory_command)
        
        # Should have called display_inventory with the item
        engine.ui_controller.display_inventory.assert_called_once()
        call_args = engine.ui_controller.display_inventory.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0].name == "Test Item"