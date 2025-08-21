"""Command parser for processing user input in the game."""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class CommandType(Enum):
    """Types of commands available in the game."""
    MOVEMENT = "movement"
    EXAMINATION = "examination"
    INVENTORY = "inventory"
    INTERACTION = "interaction"
    SYSTEM = "system"
    CHALLENGE = "challenge"


@dataclass
class ParsedCommand:
    """Represents a parsed user command."""
    command_type: CommandType
    action: str
    parameters: List[str]
    raw_input: str
    is_valid: bool = True
    error_message: Optional[str] = None


class CommandParser:
    """Parses and validates user input commands."""
    
    def __init__(self):
        """Initialize the command parser with available commands."""
        self._commands = self._initialize_commands()
        self._aliases = self._initialize_aliases()
        self._direction_aliases = {
            'n': 'north', 'north': 'north',
            's': 'south', 'south': 'south',
            'e': 'east', 'east': 'east',
            'w': 'west', 'west': 'west',
            'ne': 'northeast', 'northeast': 'northeast',
            'nw': 'northwest', 'northwest': 'northwest',
            'se': 'southeast', 'southeast': 'southeast',
            'sw': 'southwest', 'southwest': 'southwest',
            'up': 'up', 'u': 'up',
            'down': 'down', 'd': 'down'
        }
    
    def _initialize_commands(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the available commands and their metadata."""
        return {
            # Movement commands
            'go': {
                'type': CommandType.MOVEMENT,
                'description': 'Move in the specified direction',
                'usage': 'go <direction>',
                'parameters': ['direction'],
                'min_params': 1,
                'max_params': 1
            },
            'move': {
                'type': CommandType.MOVEMENT,
                'description': 'Move in the specified direction',
                'usage': 'move <direction>',
                'parameters': ['direction'],
                'min_params': 1,
                'max_params': 1
            },
            
            # Examination commands
            'look': {
                'type': CommandType.EXAMINATION,
                'description': 'Examine your surroundings',
                'usage': 'look [target]',
                'parameters': ['target'],
                'min_params': 0,
                'max_params': 1
            },
            'examine': {
                'type': CommandType.EXAMINATION,
                'description': 'Examine something closely',
                'usage': 'examine <target>',
                'parameters': ['target'],
                'min_params': 1,
                'max_params': 1
            },
            'inspect': {
                'type': CommandType.EXAMINATION,
                'description': 'Inspect an object or area',
                'usage': 'inspect <target>',
                'parameters': ['target'],
                'min_params': 1,
                'max_params': 1
            },
            'map': {
                'type': CommandType.EXAMINATION,
                'description': 'Display a map of visited chambers',
                'usage': 'map [legend]',
                'parameters': ['option'],
                'min_params': 0,
                'max_params': 1
            },
            
            # Inventory commands
            'inventory': {
                'type': CommandType.INVENTORY,
                'description': 'View your inventory',
                'usage': 'inventory',
                'parameters': [],
                'min_params': 0,
                'max_params': 0
            },
            'items': {
                'type': CommandType.INVENTORY,
                'description': 'View your items',
                'usage': 'items',
                'parameters': [],
                'min_params': 0,
                'max_params': 0
            },
            'use': {
                'type': CommandType.INVENTORY,
                'description': 'Use an item from your inventory',
                'usage': 'use <item>',
                'parameters': ['item'],
                'min_params': 1,
                'max_params': 1
            },
            'drop': {
                'type': CommandType.INVENTORY,
                'description': 'Drop an item from your inventory',
                'usage': 'drop <item>',
                'parameters': ['item'],
                'min_params': 1,
                'max_params': 1
            },
            
            # Interaction commands
            'take': {
                'type': CommandType.INTERACTION,
                'description': 'Take an item',
                'usage': 'take <item>',
                'parameters': ['item'],
                'min_params': 1,
                'max_params': 1
            },
            'get': {
                'type': CommandType.INTERACTION,
                'description': 'Get an item',
                'usage': 'get <item>',
                'parameters': ['item'],
                'min_params': 1,
                'max_params': 1
            },
            'talk': {
                'type': CommandType.INTERACTION,
                'description': 'Talk to someone or something',
                'usage': 'talk [target]',
                'parameters': ['target'],
                'min_params': 0,
                'max_params': 1
            },
            
            # System commands
            'help': {
                'type': CommandType.SYSTEM,
                'description': 'Show available commands',
                'usage': 'help [command]',
                'parameters': ['command'],
                'min_params': 0,
                'max_params': 1
            },
            'status': {
                'type': CommandType.SYSTEM,
                'description': 'Show your current status',
                'usage': 'status',
                'parameters': [],
                'min_params': 0,
                'max_params': 0
            },
            'save': {
                'type': CommandType.SYSTEM,
                'description': 'Save your game',
                'usage': 'save [filename]',
                'parameters': ['filename'],
                'min_params': 0,
                'max_params': 1
            },
            'load': {
                'type': CommandType.SYSTEM,
                'description': 'Load a saved game',
                'usage': 'load [filename]',
                'parameters': ['filename'],
                'min_params': 0,
                'max_params': 1
            },
            'quit': {
                'type': CommandType.SYSTEM,
                'description': 'Quit the game',
                'usage': 'quit',
                'parameters': [],
                'min_params': 0,
                'max_params': 0
            },
            'exit': {
                'type': CommandType.SYSTEM,
                'description': 'Exit the game',
                'usage': 'exit',
                'parameters': [],
                'min_params': 0,
                'max_params': 0
            },
            
            # Challenge commands
            'answer': {
                'type': CommandType.CHALLENGE,
                'description': 'Answer a challenge question',
                'usage': 'answer <response>',
                'parameters': ['response'],
                'min_params': 1,
                'max_params': -1  # Unlimited parameters for multi-word answers
            },
            'solve': {
                'type': CommandType.CHALLENGE,
                'description': 'Solve a puzzle or challenge',
                'usage': 'solve <solution>',
                'parameters': ['solution'],
                'min_params': 1,
                'max_params': -1
            },
            'skip': {
                'type': CommandType.CHALLENGE,
                'description': 'Skip the current challenge',
                'usage': 'skip',
                'parameters': [],
                'min_params': 0,
                'max_params': 0
            }
        }
    
    def _initialize_aliases(self) -> Dict[str, str]:
        """Initialize command aliases."""
        return {
            # Movement aliases
            'north': 'go', 'n': 'go',
            'south': 'go', 's': 'go',
            'east': 'go', 'e': 'go',
            'west': 'go', 'w': 'go',
            'northeast': 'go', 'ne': 'go',
            'northwest': 'go', 'nw': 'go',
            'southeast': 'go', 'se': 'go',
            'southwest': 'go', 'sw': 'go',
            'up': 'go', 'u': 'go',
            'down': 'go', 'd': 'go',
            
            # Examination aliases
            'l': 'look',
            'ex': 'examine',
            'check': 'examine',
            'm': 'map',
            
            # Inventory aliases
            'inv': 'inventory',
            'i': 'inventory',
            
            # Interaction aliases
            'pick': 'take',
            'pickup': 'take',
            'grab': 'take',
            
            # System aliases
            'h': 'help',
            '?': 'help',
            'stat': 'status',
            'q': 'quit'
        }
    
    def parse_command(self, user_input: str) -> ParsedCommand:
        """Parse user input into a structured command.
        
        Args:
            user_input: Raw user input string
            
        Returns:
            ParsedCommand object with parsed information
        """
        if not user_input or not user_input.strip():
            return ParsedCommand(
                command_type=CommandType.SYSTEM,
                action="",
                parameters=[],
                raw_input=user_input,
                is_valid=False,
                error_message="Please enter a command."
            )
        
        # Clean and split input
        cleaned_input = user_input.strip().lower()
        parts = self._split_input(cleaned_input)
        
        if not parts:
            return ParsedCommand(
                command_type=CommandType.SYSTEM,
                action="",
                parameters=[],
                raw_input=user_input,
                is_valid=False,
                error_message="Please enter a command."
            )
        
        command_word = parts[0]
        parameters = parts[1:] if len(parts) > 1 else []
        
        # Handle direction shortcuts (single direction words)
        if command_word in self._direction_aliases and command_word not in self._commands:
            direction = self._direction_aliases[command_word]
            return ParsedCommand(
                command_type=CommandType.MOVEMENT,
                action="go",
                parameters=[direction],
                raw_input=user_input,
                is_valid=True
            )
        
        # Resolve aliases
        actual_command = self._aliases.get(command_word, command_word)
        
        # Check if command exists
        if actual_command not in self._commands:
            suggestions = self._get_command_suggestions(command_word)
            error_msg = f"Unknown command: '{command_word}'"
            if suggestions:
                error_msg += f". Did you mean: {', '.join(suggestions)}?"
            
            return ParsedCommand(
                command_type=CommandType.SYSTEM,
                action=command_word,
                parameters=parameters,
                raw_input=user_input,
                is_valid=False,
                error_message=error_msg
            )
        
        # Validate parameters
        command_info = self._commands[actual_command]
        validation_result = self._validate_parameters(actual_command, parameters)
        
        if not validation_result[0]:
            return ParsedCommand(
                command_type=command_info['type'],
                action=actual_command,
                parameters=parameters,
                raw_input=user_input,
                is_valid=False,
                error_message=validation_result[1]
            )
        
        # Handle special parameter processing
        processed_params = self._process_parameters(actual_command, parameters)
        
        return ParsedCommand(
            command_type=command_info['type'],
            action=actual_command,
            parameters=processed_params,
            raw_input=user_input,
            is_valid=True
        )
    
    def _split_input(self, input_text: str) -> List[str]:
        """Split input text into command and parameters, handling quoted strings.
        
        Args:
            input_text: The input text to split
            
        Returns:
            List of command parts
        """
        # Handle quoted strings to allow multi-word parameters
        parts = []
        current_part = ""
        in_quotes = False
        quote_char = None
        
        i = 0
        while i < len(input_text):
            char = input_text[i]
            
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif char.isspace() and not in_quotes:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char
            
            i += 1
        
        if current_part:
            parts.append(current_part)
        
        return parts
    
    def _validate_parameters(self, command: str, parameters: List[str]) -> Tuple[bool, Optional[str]]:
        """Validate command parameters.
        
        Args:
            command: The command to validate
            parameters: List of parameters
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        command_info = self._commands[command]
        min_params = command_info['min_params']
        max_params = command_info['max_params']
        
        param_count = len(parameters)
        
        if param_count < min_params:
            if min_params == 1:
                return False, f"Command '{command}' requires a parameter. Usage: {command_info['usage']}"
            else:
                return False, f"Command '{command}' requires at least {min_params} parameters. Usage: {command_info['usage']}"
        
        if max_params != -1 and param_count > max_params:
            if max_params == 0:
                return False, f"Command '{command}' doesn't take any parameters. Usage: {command_info['usage']}"
            else:
                return False, f"Command '{command}' takes at most {max_params} parameters. Usage: {command_info['usage']}"
        
        return True, None
    
    def _process_parameters(self, command: str, parameters: List[str]) -> List[str]:
        """Process and normalize parameters for specific commands.
        
        Args:
            command: The command being processed
            parameters: List of raw parameters
            
        Returns:
            List of processed parameters
        """
        if command in ['go', 'move'] and parameters:
            # Normalize direction parameters
            direction = parameters[0].lower()
            normalized_direction = self._direction_aliases.get(direction, direction)
            return [normalized_direction]
        
        # For answer and solve commands, join multi-word responses
        if command in ['answer', 'solve'] and len(parameters) > 1:
            return [' '.join(parameters)]
        
        return parameters
    
    def _get_command_suggestions(self, invalid_command: str) -> List[str]:
        """Get command suggestions for invalid input using fuzzy matching.
        
        Args:
            invalid_command: The invalid command entered
            
        Returns:
            List of suggested commands
        """
        suggestions = []
        
        # Check all commands and aliases
        all_commands = set(self._commands.keys()) | set(self._aliases.keys())
        
        for command in all_commands:
            # Simple fuzzy matching based on:
            # 1. Commands that start with the same letter
            # 2. Commands that contain the invalid command
            # 3. Commands with similar length and characters
            
            if self._is_similar_command(invalid_command, command):
                # Map aliases back to actual commands for suggestions
                actual_command = self._aliases.get(command, command)
                if actual_command not in suggestions:
                    suggestions.append(actual_command)
        
        # Limit to top 3 suggestions
        return suggestions[:3]
    
    def _is_similar_command(self, invalid: str, valid: str) -> bool:
        """Check if two commands are similar enough to suggest.
        
        Args:
            invalid: The invalid command
            valid: A valid command to compare against
            
        Returns:
            True if commands are similar enough
        """
        # Exact match (shouldn't happen, but just in case)
        if invalid == valid:
            return True
        
        # One contains the other (substring matching)
        if invalid in valid or valid in invalid:
            return True
        
        # Same starting letter and similar length
        if invalid[0] == valid[0] and abs(len(invalid) - len(valid)) <= 3:
            return True
        
        # Check for common prefix of at least 2 characters
        if len(invalid) >= 2 and len(valid) >= 2:
            if invalid[:2] == valid[:2]:
                return True
        
        # Levenshtein-like distance check for very similar commands
        if abs(len(invalid) - len(valid)) <= 1:
            differences = 0
            min_len = min(len(invalid), len(valid))
            for i in range(min_len):
                if invalid[i] != valid[i]:
                    differences += 1
                if differences > 1:
                    break
            if differences <= 1:
                return True
        
        return False
    
    def get_available_commands(self) -> Dict[str, str]:
        """Get all available commands and their descriptions.
        
        Returns:
            Dictionary mapping command names to descriptions
        """
        return {cmd: info['description'] for cmd, info in self._commands.items()}
    
    def get_command_usage(self, command: str) -> Optional[str]:
        """Get usage information for a specific command.
        
        Args:
            command: The command to get usage for
            
        Returns:
            Usage string or None if command doesn't exist
        """
        if command in self._commands:
            return self._commands[command]['usage']
        
        # Check if it's an alias
        actual_command = self._aliases.get(command)
        if actual_command and actual_command in self._commands:
            return self._commands[actual_command]['usage']
        
        return None
    
    def get_commands_by_type(self, command_type: CommandType) -> Dict[str, str]:
        """Get commands of a specific type.
        
        Args:
            command_type: The type of commands to retrieve
            
        Returns:
            Dictionary of commands of the specified type
        """
        return {
            cmd: info['description'] 
            for cmd, info in self._commands.items() 
            if info['type'] == command_type
        }
    
    def is_valid_direction(self, direction: str) -> bool:
        """Check if a string is a valid direction.
        
        Args:
            direction: The direction to validate
            
        Returns:
            True if it's a valid direction
        """
        return direction.lower() in self._direction_aliases