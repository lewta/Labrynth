"""UI Controller for coordinating display and input handling."""

import sys
from typing import List, Dict, Any, Optional, Callable

from src.game.display import DisplayManager, MessageType
from src.game.command_parser import CommandParser, ParsedCommand, CommandType
from src.utils.data_models import Item, PlayerStats, ChallengeResult
from src.challenges.base import Challenge


class UIController:
    """Coordinates user interface components for display and input handling."""
    
    def __init__(self, use_colors: bool = True, input_handler: Optional[Callable[[str], str]] = None):
        """Initialize the UI controller.
        
        Args:
            use_colors: Whether to use colors in display output
            input_handler: Optional custom input handler function (for testing)
        """
        self.display_manager = DisplayManager(use_colors=use_colors)
        self.command_parser = CommandParser()
        self._input_handler = input_handler or input
        self._output_buffer = []  # For testing purposes
        self._capture_output = False
    
    def enable_output_capture(self) -> None:
        """Enable output capture for testing."""
        self._capture_output = True
        self._output_buffer = []
    
    def disable_output_capture(self) -> None:
        """Disable output capture."""
        self._capture_output = False
    
    def get_captured_output(self) -> List[str]:
        """Get captured output for testing."""
        return self._output_buffer.copy()
    
    def clear_captured_output(self) -> None:
        """Clear captured output buffer."""
        self._output_buffer = []
    
    def _output(self, text: str) -> None:
        """Output text to console or capture buffer.
        
        Args:
            text: Text to output
        """
        if self._capture_output:
            self._output_buffer.append(text)
        else:
            print(text, end='')
    
    def display_message(self, message: str, message_type: MessageType = MessageType.INFO) -> None:
        """Display a message to the user.
        
        Args:
            message: The message to display
            message_type: The type of message for styling
        """
        formatted_message = self.display_manager.display_message(message, message_type)
        self._output(formatted_message + '\n')
    
    def display_chamber(self, chamber_name: str, description: str, exits: List[str]) -> None:
        """Display chamber information to the user.
        
        Args:
            chamber_name: Name of the chamber
            description: Chamber description
            exits: List of available exits
        """
        chamber_display = self.display_manager.display_chamber_description(
            chamber_name, description, exits
        )
        self._output(chamber_display)
    
    def display_challenge(self, challenge: Challenge) -> None:
        """Display challenge information to the user.
        
        Args:
            challenge: The challenge to display
        """
        challenge_display = self.display_manager.display_challenge(challenge)
        self._output(challenge_display)
    
    def display_challenge_result(self, result: ChallengeResult) -> None:
        """Display challenge result to the user.
        
        Args:
            result: The challenge result to display
        """
        result_display = self.display_manager.display_challenge_result(result)
        self._output(result_display)
    
    def display_inventory(self, items: List[Item]) -> None:
        """Display inventory contents to the user.
        
        Args:
            items: List of items in inventory
        """
        inventory_display = self.display_manager.display_inventory(items)
        self._output(inventory_display)
    
    def display_map(self, map_content: str) -> None:
        """Display the labyrinth map to the user.
        
        Args:
            map_content: ASCII art map content to display
        """
        self._output(map_content + '\n')
    
    def display_player_status(self, health: int, stats: PlayerStats, completed_chambers: int) -> None:
        """Display player status information to the user.
        
        Args:
            health: Current player health
            stats: Player statistics
            completed_chambers: Number of completed chambers
        """
        status_display = self.display_manager.display_player_status(
            health, stats, completed_chambers
        )
        self._output(status_display)
    
    def display_help(self, specific_command: Optional[str] = None) -> None:
        """Display help information to the user.
        
        Args:
            specific_command: Optional specific command to show help for
        """
        if specific_command:
            usage = self.command_parser.get_command_usage(specific_command)
            if usage:
                self.display_message(f"Usage: {usage}", MessageType.INFO)
            else:
                self.display_message(f"Unknown command: {specific_command}", MessageType.ERROR)
        else:
            commands = self.command_parser.get_available_commands()
            help_display = self.display_manager.display_help(commands)
            self._output(help_display)
    
    def display_game_over(self, victory: bool, stats: Dict[str, Any]) -> None:
        """Display game over screen to the user.
        
        Args:
            victory: Whether the player won or lost
            stats: Game statistics to display
        """
        game_over_display = self.display_manager.display_game_over(victory, stats)
        self._output(game_over_display)
    
    def get_user_input(self, prompt: str = "Enter command") -> str:
        """Get input from the user with a formatted prompt.
        
        Args:
            prompt: The prompt text to display
            
        Returns:
            User input string
        """
        formatted_prompt = self.display_manager.format_prompt(prompt)
        self._output(formatted_prompt)
        
        try:
            user_input = self._input_handler("")
            return user_input.strip() if user_input else ""
        except (EOFError, KeyboardInterrupt):
            return "quit"
    
    def parse_command(self, user_input: str) -> ParsedCommand:
        """Parse user input into a structured command.
        
        Args:
            user_input: Raw user input string
            
        Returns:
            ParsedCommand object with parsed information
        """
        return self.command_parser.parse_command(user_input)
    
    def handle_invalid_command(self, parsed_command: ParsedCommand) -> None:
        """Handle invalid command by displaying error and suggestions.
        
        Args:
            parsed_command: The invalid parsed command
        """
        if parsed_command.error_message:
            self.display_message(parsed_command.error_message, MessageType.ERROR)
        else:
            self.display_message(f"Invalid command: {parsed_command.action}", MessageType.ERROR)
    
    def get_command_and_parse(self, prompt: str = "Enter command") -> ParsedCommand:
        """Get user input and parse it into a command.
        
        Args:
            prompt: The prompt text to display
            
        Returns:
            ParsedCommand object
        """
        user_input = self.get_user_input(prompt)
        return self.parse_command(user_input)
    
    def display_welcome_message(self, game_title: str, version: str = "1.0") -> None:
        """Display welcome message when game starts.
        
        Args:
            game_title: Title of the game
            version: Version of the game
        """
        welcome_text = f"""
{game_title} v{version}

Welcome to the Labyrinth Adventure Game! You find yourself at the entrance 
of an ancient underground labyrinth filled with mysteries and challenges.

Your goal is to navigate through 13 interconnected chambers, solve the 
challenges within each chamber, and ultimately find your way to freedom.

Type 'help' at any time to see available commands.
Type 'look' to examine your surroundings.
Type 'status' to check your current condition.

Good luck, adventurer!
"""
        self.display_message(welcome_text, MessageType.INFO)
    
    def confirm_action(self, message: str) -> bool:
        """Ask user to confirm an action.
        
        Args:
            message: The confirmation message
            
        Returns:
            True if user confirms, False otherwise
        """
        self.display_message(f"{message} (y/n)", MessageType.WARNING)
        response = self.get_user_input("Confirm").lower()
        return response in ['y', 'yes', 'true', '1']
    
    def display_error(self, error_message: str) -> None:
        """Display an error message to the user.
        
        Args:
            error_message: The error message to display
        """
        self.display_message(f"Error: {error_message}", MessageType.ERROR)
    
    def display_success(self, success_message: str) -> None:
        """Display a success message to the user.
        
        Args:
            success_message: The success message to display
        """
        self.display_message(success_message, MessageType.SUCCESS)
    
    def display_warning(self, warning_message: str) -> None:
        """Display a warning message to the user.
        
        Args:
            warning_message: The warning message to display
        """
        self.display_message(warning_message, MessageType.WARNING)
    
    def display_commands_by_type(self, command_type: CommandType) -> None:
        """Display commands of a specific type.
        
        Args:
            command_type: The type of commands to display
        """
        commands = self.command_parser.get_commands_by_type(command_type)
        if commands:
            type_name = command_type.value.title()
            help_display = self.display_manager.display_help(commands)
            # Replace the header to show the specific type
            help_display = help_display.replace("Available Commands", f"{type_name} Commands")
            self._output(help_display)
        else:
            self.display_message(f"No {command_type.value} commands available.", MessageType.INFO)
    
    def clear_screen(self) -> None:
        """Clear the screen (platform-dependent)."""
        if not self._capture_output:
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_separator(self, char: str = "-", length: int = 60) -> None:
        """Display a separator line.
        
        Args:
            char: Character to use for the separator
            length: Length of the separator line
        """
        separator = char * length
        self._output(f"\n{separator}\n")
    
    def display_loading_message(self, message: str) -> None:
        """Display a loading message.
        
        Args:
            message: The loading message to display
        """
        self.display_message(f"Loading... {message}", MessageType.INFO)
    
    def get_save_filename(self) -> Optional[str]:
        """Get a save filename from the user.
        
        Returns:
            Filename string or None if cancelled
        """
        filename = self.get_user_input("Enter save filename (or 'cancel' to abort)")
        if filename.lower() in ['cancel', 'abort', 'quit', '']:
            return None
        
        # Add .json extension if not present
        if not filename.endswith('.json'):
            filename += '.json'
        
        return filename
    
    def display_save_files(self, save_files: List[str]) -> None:
        """Display available save files.
        
        Args:
            save_files: List of save file names
        """
        if not save_files:
            self.display_message("No save files found.", MessageType.INFO)
            return
        
        self.display_message("Available save files:", MessageType.INFO)
        for i, filename in enumerate(save_files, 1):
            self.display_message(f"  {i}. {filename}", MessageType.INFO)
    
    def get_load_filename(self, save_files: List[str]) -> Optional[str]:
        """Get a load filename from the user.
        
        Args:
            save_files: List of available save files
            
        Returns:
            Filename string or None if cancelled
        """
        if not save_files:
            self.display_message("No save files available.", MessageType.ERROR)
            return None
        
        self.display_save_files(save_files)
        
        choice = self.get_user_input("Enter filename or number (or 'cancel' to abort)")
        if choice.lower() in ['cancel', 'abort', 'quit', '']:
            return None
        
        # Check if it's a number
        try:
            index = int(choice) - 1
            if 0 <= index < len(save_files):
                return save_files[index]
        except ValueError:
            pass
        
        # Check if it's a filename
        if choice in save_files:
            return choice
        
        # Add .json extension and check again
        if not choice.endswith('.json'):
            choice += '.json'
            if choice in save_files:
                return choice
        
        self.display_message("Invalid selection.", MessageType.ERROR)
        return None