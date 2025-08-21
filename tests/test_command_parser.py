"""Tests for the CommandParser class."""

import pytest

from src.game.command_parser import CommandParser, ParsedCommand, CommandType


class TestCommandParser:
    """Test cases for CommandParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CommandParser()
    
    def test_init(self):
        """Test CommandParser initialization."""
        assert self.parser is not None
        assert len(self.parser._commands) > 0
        assert len(self.parser._aliases) > 0
        assert len(self.parser._direction_aliases) > 0
    
    def test_parse_empty_command(self):
        """Test parsing empty or whitespace-only input."""
        result = self.parser.parse_command("")
        assert not result.is_valid
        assert "Please enter a command" in result.error_message
        
        result = self.parser.parse_command("   ")
        assert not result.is_valid
        assert "Please enter a command" in result.error_message
    
    def test_parse_valid_movement_command(self):
        """Test parsing valid movement commands."""
        result = self.parser.parse_command("go north")
        assert result.is_valid
        assert result.command_type == CommandType.MOVEMENT
        assert result.action == "go"
        assert result.parameters == ["north"]
        
        result = self.parser.parse_command("move south")
        assert result.is_valid
        assert result.command_type == CommandType.MOVEMENT
        assert result.action == "move"
        assert result.parameters == ["south"]
    
    def test_parse_direction_shortcuts(self):
        """Test parsing direction shortcuts."""
        result = self.parser.parse_command("north")
        assert result.is_valid
        assert result.command_type == CommandType.MOVEMENT
        assert result.action == "go"
        assert result.parameters == ["north"]
        
        result = self.parser.parse_command("n")
        assert result.is_valid
        assert result.command_type == CommandType.MOVEMENT
        assert result.action == "go"
        assert result.parameters == ["north"]
        
        result = self.parser.parse_command("se")
        assert result.is_valid
        assert result.command_type == CommandType.MOVEMENT
        assert result.action == "go"
        assert result.parameters == ["southeast"]
    
    def test_parse_examination_commands(self):
        """Test parsing examination commands."""
        result = self.parser.parse_command("look")
        assert result.is_valid
        assert result.command_type == CommandType.EXAMINATION
        assert result.action == "look"
        assert result.parameters == []
        
        result = self.parser.parse_command("examine sword")
        assert result.is_valid
        assert result.command_type == CommandType.EXAMINATION
        assert result.action == "examine"
        assert result.parameters == ["sword"]
        
        result = self.parser.parse_command("l")
        assert result.is_valid
        assert result.command_type == CommandType.EXAMINATION
        assert result.action == "look"
    
    def test_parse_inventory_commands(self):
        """Test parsing inventory commands."""
        result = self.parser.parse_command("inventory")
        assert result.is_valid
        assert result.command_type == CommandType.INVENTORY
        assert result.action == "inventory"
        assert result.parameters == []
        
        result = self.parser.parse_command("use potion")
        assert result.is_valid
        assert result.command_type == CommandType.INVENTORY
        assert result.action == "use"
        assert result.parameters == ["potion"]
        
        result = self.parser.parse_command("i")
        assert result.is_valid
        assert result.command_type == CommandType.INVENTORY
        assert result.action == "inventory"
    
    def test_parse_interaction_commands(self):
        """Test parsing interaction commands."""
        result = self.parser.parse_command("take key")
        assert result.is_valid
        assert result.command_type == CommandType.INTERACTION
        assert result.action == "take"
        assert result.parameters == ["key"]
        
        result = self.parser.parse_command("talk")
        assert result.is_valid
        assert result.command_type == CommandType.INTERACTION
        assert result.action == "talk"
        assert result.parameters == []
    
    def test_parse_system_commands(self):
        """Test parsing system commands."""
        result = self.parser.parse_command("help")
        assert result.is_valid
        assert result.command_type == CommandType.SYSTEM
        assert result.action == "help"
        assert result.parameters == []
        
        result = self.parser.parse_command("save game1")
        assert result.is_valid
        assert result.command_type == CommandType.SYSTEM
        assert result.action == "save"
        assert result.parameters == ["game1"]
        
        result = self.parser.parse_command("quit")
        assert result.is_valid
        assert result.command_type == CommandType.SYSTEM
        assert result.action == "quit"
        assert result.parameters == []
    
    def test_parse_challenge_commands(self):
        """Test parsing challenge commands."""
        result = self.parser.parse_command("answer 42")
        assert result.is_valid
        assert result.command_type == CommandType.CHALLENGE
        assert result.action == "answer"
        assert result.parameters == ["42"]
        
        result = self.parser.parse_command("solve the riddle is time")
        assert result.is_valid
        assert result.command_type == CommandType.CHALLENGE
        assert result.action == "solve"
        assert result.parameters == ["the riddle is time"]
    
    def test_parse_invalid_command(self):
        """Test parsing invalid commands."""
        result = self.parser.parse_command("invalidcommand")
        assert not result.is_valid
        assert "Unknown command" in result.error_message
        assert result.action == "invalidcommand"
    
    def test_command_suggestions(self):
        """Test command suggestions for invalid input."""
        result = self.parser.parse_command("hel")
        assert not result.is_valid
        assert "Did you mean" in result.error_message
        assert "help" in result.error_message
        
        result = self.parser.parse_command("loo")
        assert not result.is_valid
        assert "look" in result.error_message
    
    def test_parameter_validation_too_few(self):
        """Test parameter validation when too few parameters provided."""
        result = self.parser.parse_command("go")
        assert not result.is_valid
        assert "requires a parameter" in result.error_message
        
        result = self.parser.parse_command("examine")
        assert not result.is_valid
        assert "requires a parameter" in result.error_message
    
    def test_parameter_validation_too_many(self):
        """Test parameter validation when too many parameters provided."""
        result = self.parser.parse_command("inventory extra parameter")
        assert not result.is_valid
        assert "doesn't take any parameters" in result.error_message
        
        result = self.parser.parse_command("quit now please")
        assert not result.is_valid
        assert "doesn't take any parameters" in result.error_message
    
    def test_quoted_parameters(self):
        """Test handling of quoted parameters."""
        result = self.parser.parse_command('answer "the answer is 42"')
        assert result.is_valid
        assert result.parameters == ["the answer is 42"]
        
        result = self.parser.parse_command("examine 'magic sword'")
        assert result.is_valid
        assert result.parameters == ["magic sword"]
    
    def test_case_insensitive_parsing(self):
        """Test that command parsing is case insensitive."""
        result = self.parser.parse_command("LOOK")
        assert result.is_valid
        assert result.action == "look"
        
        result = self.parser.parse_command("Go NORTH")
        assert result.is_valid
        assert result.action == "go"
        assert result.parameters == ["north"]
    
    def test_direction_normalization(self):
        """Test that direction parameters are normalized."""
        result = self.parser.parse_command("go N")
        assert result.is_valid
        assert result.parameters == ["north"]
        
        result = self.parser.parse_command("move SE")
        assert result.is_valid
        assert result.parameters == ["southeast"]
    
    def test_multi_word_answers(self):
        """Test handling of multi-word challenge answers."""
        result = self.parser.parse_command("answer this is a long answer")
        assert result.is_valid
        assert result.parameters == ["this is a long answer"]
        
        result = self.parser.parse_command("solve multiple word solution")
        assert result.is_valid
        assert result.parameters == ["multiple word solution"]
    
    def test_get_available_commands(self):
        """Test getting available commands."""
        commands = self.parser.get_available_commands()
        assert isinstance(commands, dict)
        assert len(commands) > 0
        assert "help" in commands
        assert "go" in commands
        assert "look" in commands
    
    def test_get_command_usage(self):
        """Test getting command usage information."""
        usage = self.parser.get_command_usage("go")
        assert usage is not None
        assert "go <direction>" in usage
        
        usage = self.parser.get_command_usage("help")
        assert usage is not None
        
        usage = self.parser.get_command_usage("nonexistent")
        assert usage is None
    
    def test_get_command_usage_with_alias(self):
        """Test getting command usage for aliases."""
        usage = self.parser.get_command_usage("n")
        assert usage is not None
        assert "go <direction>" in usage
        
        usage = self.parser.get_command_usage("i")
        assert usage is not None
        assert "inventory" in usage
    
    def test_get_commands_by_type(self):
        """Test getting commands by type."""
        movement_commands = self.parser.get_commands_by_type(CommandType.MOVEMENT)
        assert isinstance(movement_commands, dict)
        assert "go" in movement_commands
        assert "move" in movement_commands
        
        system_commands = self.parser.get_commands_by_type(CommandType.SYSTEM)
        assert "help" in system_commands
        assert "quit" in system_commands
    
    def test_is_valid_direction(self):
        """Test direction validation."""
        assert self.parser.is_valid_direction("north")
        assert self.parser.is_valid_direction("n")
        assert self.parser.is_valid_direction("southeast")
        assert self.parser.is_valid_direction("se")
        assert not self.parser.is_valid_direction("invalid")
        assert not self.parser.is_valid_direction("middle")
    
    def test_split_input_with_quotes(self):
        """Test input splitting with quoted strings."""
        parts = self.parser._split_input('answer "hello world"')
        assert parts == ["answer", "hello world"]
        
        parts = self.parser._split_input("examine 'magic sword of power'")
        assert parts == ["examine", "magic sword of power"]
        
        parts = self.parser._split_input("normal command without quotes")
        assert parts == ["normal", "command", "without", "quotes"]
    
    def test_command_suggestions_fuzzy_matching(self):
        """Test fuzzy matching for command suggestions."""
        # Test starting letter matching
        suggestions = self.parser._get_command_suggestions("h")
        assert "help" in suggestions
        
        # Test substring matching
        suggestions = self.parser._get_command_suggestions("inv")
        assert "inventory" in suggestions
        
        # Test similar length matching
        suggestions = self.parser._get_command_suggestions("lok")
        assert "look" in suggestions
    
    def test_parameter_processing(self):
        """Test parameter processing for specific commands."""
        # Test direction processing
        processed = self.parser._process_parameters("go", ["n"])
        assert processed == ["north"]
        
        # Test multi-word answer processing
        processed = self.parser._process_parameters("answer", ["hello", "world"])
        assert processed == ["hello world"]
        
        # Test normal parameter processing
        processed = self.parser._process_parameters("take", ["sword"])
        assert processed == ["sword"]
    
    def test_parsed_command_dataclass(self):
        """Test ParsedCommand dataclass functionality."""
        cmd = ParsedCommand(
            command_type=CommandType.MOVEMENT,
            action="go",
            parameters=["north"],
            raw_input="go north"
        )
        
        assert cmd.command_type == CommandType.MOVEMENT
        assert cmd.action == "go"
        assert cmd.parameters == ["north"]
        assert cmd.raw_input == "go north"
        assert cmd.is_valid is True
        assert cmd.error_message is None
    
    def test_command_type_enum(self):
        """Test CommandType enum values."""
        assert CommandType.MOVEMENT.value == "movement"
        assert CommandType.EXAMINATION.value == "examination"
        assert CommandType.INVENTORY.value == "inventory"
        assert CommandType.INTERACTION.value == "interaction"
        assert CommandType.SYSTEM.value == "system"
        assert CommandType.CHALLENGE.value == "challenge"
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test command with only spaces between words
        result = self.parser.parse_command("go    north")
        assert result.is_valid
        assert result.parameters == ["north"]
        
        # Test command with mixed case
        result = self.parser.parse_command("Go NoRtH")
        assert result.is_valid
        assert result.parameters == ["north"]
        
        # Test very long command
        long_answer = "answer " + "word " * 50
        result = self.parser.parse_command(long_answer)
        assert result.is_valid
        assert len(result.parameters[0]) > 100
    
    def test_alias_resolution(self):
        """Test that aliases are properly resolved to actual commands."""
        # Test movement aliases
        result = self.parser.parse_command("n")
        assert result.action == "go"
        
        # Test examination aliases
        result = self.parser.parse_command("l")
        assert result.action == "look"
        
        # Test inventory aliases
        result = self.parser.parse_command("i")
        assert result.action == "inventory"
        
        # Test system aliases
        result = self.parser.parse_command("q")
        assert result.action == "quit"