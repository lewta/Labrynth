"""Tests for custom exception classes and error handling."""

import pytest
from src.utils.exceptions import (
    GameException,
    InvalidCommandException,
    ChallengeException,
    SaveLoadException,
    WorldException,
    InventoryException,
    PlayerException,
    ConfigurationException,
    GameStateException
)


class TestGameException:
    """Test the base GameException class."""
    
    def test_basic_exception_creation(self):
        """Test creating a basic GameException."""
        exc = GameException("Test error")
        assert str(exc) == "Test error"
        assert exc.recovery_suggestions == []
        assert exc.error_code is None
        assert exc.context == {}
        assert not exc.can_recover()
    
    def test_exception_with_recovery_suggestions(self):
        """Test GameException with recovery suggestions."""
        suggestions = ["Try again", "Check input"]
        exc = GameException("Test error", recovery_suggestions=suggestions)
        assert exc.get_recovery_suggestions() == suggestions
        assert exc.can_recover()
    
    def test_exception_with_error_code_and_context(self):
        """Test GameException with error code and context."""
        context = {"key": "value", "number": 42}
        exc = GameException("Test error", error_code="TEST_ERROR", context=context)
        assert exc.error_code == "TEST_ERROR"
        assert exc.context == context
    
    def test_user_friendly_message(self):
        """Test user-friendly message method."""
        exc = GameException("Technical error message")
        assert exc.get_user_friendly_message() == "Technical error message"


class TestInvalidCommandException:
    """Test the InvalidCommandException class."""
    
    def test_invalid_command_basic(self):
        """Test basic invalid command exception."""
        exc = InvalidCommandException("badcommand")
        assert "Unknown command: 'badcommand'" in str(exc)
        assert exc.command == "badcommand"
        assert exc.error_code == "INVALID_COMMAND"
        assert "help" in str(exc.get_recovery_suggestions())
    
    def test_invalid_command_with_similar_commands(self):
        """Test invalid command with similar command suggestions."""
        exc = InvalidCommandException("loook", similar_commands=["look", "lock"])
        suggestions = exc.get_recovery_suggestions()
        assert any("Did you mean 'look'?" in s for s in suggestions)
        assert any("Did you mean 'lock'?" in s for s in suggestions)
    
    def test_invalid_command_with_valid_commands(self):
        """Test invalid command with valid commands list."""
        valid_commands = ["look", "move", "inventory"]
        exc = InvalidCommandException("badcmd", valid_commands=valid_commands)
        suggestions = exc.get_recovery_suggestions()
        assert any("Valid commands are:" in s for s in suggestions)
        assert exc.valid_commands == valid_commands
    
    def test_context_information(self):
        """Test that context information is properly stored."""
        exc = InvalidCommandException("test", valid_commands=["a", "b"])
        assert exc.context["command"] == "test"
        assert exc.context["valid_commands"] == ["a", "b"]


class TestChallengeException:
    """Test the ChallengeException class."""
    
    def test_challenge_exception_retryable(self):
        """Test challenge exception that allows retry."""
        exc = ChallengeException("riddle", "Wrong answer", can_retry=True)
        assert "Challenge error in riddle" in str(exc)
        assert exc.can_retry
        assert exc.challenge_type == "riddle"
        suggestions = exc.get_recovery_suggestions()
        assert any("try again" in s.lower() for s in suggestions)
    
    def test_challenge_exception_non_retryable(self):
        """Test challenge exception that doesn't allow retry."""
        exc = ChallengeException("combat", "Player defeated", can_retry=False)
        assert not exc.can_retry
        suggestions = exc.get_recovery_suggestions()
        assert any("cannot be retried" in s for s in suggestions)
    
    def test_challenge_exception_with_id(self):
        """Test challenge exception with challenge ID."""
        exc = ChallengeException("puzzle", "Invalid move", challenge_id="puzzle_001")
        assert exc.challenge_id == "puzzle_001"
        assert exc.context["challenge_id"] == "puzzle_001"


class TestSaveLoadException:
    """Test the SaveLoadException class."""
    
    def test_save_exception_recoverable(self):
        """Test recoverable save exception."""
        exc = SaveLoadException("save", "game.sav", "Permission denied", is_recoverable=True)
        assert "Failed to save file 'game.sav'" in str(exc)
        assert exc.operation == "save"
        assert exc.filename == "game.sav"
        assert exc.is_recoverable
        suggestions = exc.get_recovery_suggestions()
        assert any("different filename" in s for s in suggestions)
    
    def test_load_exception_non_recoverable(self):
        """Test non-recoverable load exception."""
        exc = SaveLoadException("load", "corrupt.sav", "File corrupted", is_recoverable=False)
        assert not exc.is_recoverable
        suggestions = exc.get_recovery_suggestions()
        assert any("corrupted" in s for s in suggestions)
        assert any("new game" in s for s in suggestions)
    
    def test_error_code_generation(self):
        """Test that error codes are generated correctly."""
        save_exc = SaveLoadException("save", "test.sav", "Error")
        load_exc = SaveLoadException("load", "test.sav", "Error")
        assert save_exc.error_code == "SAVE_ERROR"
        assert load_exc.error_code == "LOAD_ERROR"


class TestWorldException:
    """Test the WorldException class."""
    
    def test_world_exception_with_direction(self):
        """Test world exception with invalid direction."""
        exc = WorldException("Cannot move north", chamber_id=1, direction="north")
        assert exc.chamber_id == 1
        assert exc.direction == "north"
        suggestions = exc.get_recovery_suggestions()
        assert any("no exit to the north" in s for s in suggestions)
        assert any("look" in s for s in suggestions)
    
    def test_world_exception_without_direction(self):
        """Test world exception without specific direction."""
        exc = WorldException("Chamber not found", chamber_id=99)
        assert exc.chamber_id == 99
        assert exc.direction is None
        suggestions = exc.get_recovery_suggestions()
        assert any("look" in s for s in suggestions)


class TestInventoryException:
    """Test the InventoryException class."""
    
    def test_inventory_use_item_not_found(self):
        """Test inventory exception for item not found."""
        exc = InventoryException("Item not found", item_name="sword", operation="use")
        assert exc.item_name == "sword"
        assert exc.operation == "use"
        suggestions = exc.get_recovery_suggestions()
        assert any("don't have 'sword'" in s for s in suggestions)
        assert any("inventory" in s for s in suggestions)
    
    def test_inventory_full_exception(self):
        """Test inventory exception for full inventory."""
        exc = InventoryException("Inventory full", operation="add")
        suggestions = exc.get_recovery_suggestions()
        assert any("inventory might be full" in s for s in suggestions)
    
    def test_inventory_general_exception(self):
        """Test general inventory exception."""
        exc = InventoryException("General inventory error")
        suggestions = exc.get_recovery_suggestions()
        assert any("inventory" in s for s in suggestions)


class TestPlayerException:
    """Test the PlayerException class."""
    
    def test_player_fatal_exception(self):
        """Test fatal player exception (game over)."""
        exc = PlayerException("Player died", is_fatal=True)
        assert exc.is_fatal
        suggestions = exc.get_recovery_suggestions()
        assert any("Game Over" in s for s in suggestions)
        assert any("load" in s for s in suggestions)
    
    def test_player_health_warning(self):
        """Test player health warning exception."""
        exc = PlayerException("Low health", player_stat="health", is_fatal=False)
        assert not exc.is_fatal
        assert exc.player_stat == "health"
        suggestions = exc.get_recovery_suggestions()
        assert any("health is low" in s for s in suggestions)
        assert any("healing items" in s for s in suggestions)
    
    def test_player_general_exception(self):
        """Test general player exception."""
        exc = PlayerException("Stat error")
        suggestions = exc.get_recovery_suggestions()
        assert any("status" in s for s in suggestions)


class TestConfigurationException:
    """Test the ConfigurationException class."""
    
    def test_configuration_exception(self):
        """Test configuration exception."""
        exc = ConfigurationException("labyrinth", "Invalid JSON", config_file="config.json")
        assert "Configuration error in labyrinth" in str(exc)
        assert exc.config_type == "labyrinth"
        assert exc.config_file == "config.json"
        suggestions = exc.get_recovery_suggestions()
        assert any("configuration files" in s for s in suggestions)
        assert any("valid JSON" in s for s in suggestions)
    
    def test_configuration_exception_without_file(self):
        """Test configuration exception without specific file."""
        exc = ConfigurationException("settings", "Missing required field")
        assert exc.config_file is None
        assert exc.error_code == "CONFIG_ERROR"


class TestGameStateException:
    """Test the GameStateException class."""
    
    def test_recoverable_game_state_exception(self):
        """Test recoverable game state exception."""
        exc = GameStateException("Invalid state", state_component="player", is_recoverable=True)
        assert exc.is_recoverable
        assert exc.state_component == "player"
        suggestions = exc.get_recovery_suggestions()
        assert any("previous save" in s for s in suggestions)
        assert any("Restart" in s for s in suggestions)
    
    def test_non_recoverable_game_state_exception(self):
        """Test non-recoverable game state exception."""
        exc = GameStateException("Corrupted state", is_recoverable=False)
        assert not exc.is_recoverable
        suggestions = exc.get_recovery_suggestions()
        assert any("corrupted" in s for s in suggestions)
        assert any("new game" in s for s in suggestions)
    
    def test_game_state_error_code(self):
        """Test game state exception error code."""
        exc = GameStateException("Test error")
        assert exc.error_code == "STATE_ERROR"


class TestExceptionRecovery:
    """Test exception recovery mechanisms."""
    
    def test_exception_hierarchy(self):
        """Test that all exceptions inherit from GameException."""
        exceptions = [
            InvalidCommandException("test"),
            ChallengeException("test", "message"),
            SaveLoadException("save", "file", "reason"),
            WorldException("message"),
            InventoryException("message"),
            PlayerException("message"),
            ConfigurationException("type", "message"),
            GameStateException("message")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, GameException)
            assert hasattr(exc, 'get_recovery_suggestions')
            assert hasattr(exc, 'can_recover')
            assert hasattr(exc, 'get_user_friendly_message')
    
    def test_all_exceptions_have_suggestions(self):
        """Test that all exceptions provide recovery suggestions."""
        exceptions = [
            InvalidCommandException("test"),
            ChallengeException("test", "message"),
            SaveLoadException("save", "file", "reason"),
            WorldException("message", direction="north"),
            InventoryException("message", operation="use"),
            PlayerException("message", is_fatal=True),
            ConfigurationException("type", "message"),
            GameStateException("message")
        ]
        
        for exc in exceptions:
            suggestions = exc.get_recovery_suggestions()
            assert len(suggestions) > 0, f"{type(exc).__name__} should provide recovery suggestions"
            assert all(isinstance(s, str) for s in suggestions), "All suggestions should be strings"
    
    def test_error_codes_are_consistent(self):
        """Test that error codes follow consistent naming."""
        test_cases = [
            (InvalidCommandException("test"), "INVALID_COMMAND"),
            (ChallengeException("test", "msg"), "CHALLENGE_ERROR"),
            (SaveLoadException("save", "file", "reason"), "SAVE_ERROR"),
            (WorldException("msg"), "WORLD_ERROR"),
            (InventoryException("msg"), "INVENTORY_ERROR"),
            (PlayerException("msg"), "PLAYER_ERROR"),
            (ConfigurationException("type", "msg"), "CONFIG_ERROR"),
            (GameStateException("msg"), "STATE_ERROR")
        ]
        
        for exc, expected_code in test_cases:
            assert exc.error_code == expected_code, f"{type(exc).__name__} should have error code {expected_code}"