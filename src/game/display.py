"""Display manager for formatting and presenting game output."""

from typing import List, Dict, Any, Optional
from enum import Enum

from src.utils.data_models import Item, PlayerStats, ChallengeResult
from src.challenges.base import Challenge
from src.config.game_config import GameConfig


class MessageType(Enum):
    """Types of messages that can be displayed."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CHALLENGE = "challenge"
    CHAMBER = "chamber"
    INVENTORY = "inventory"
    STATUS = "status"


class ColorCode:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Text colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright text colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


class DisplayManager:
    """Manages all game output formatting and display."""
    
    def __init__(self, use_colors: bool = True, config: Optional[GameConfig] = None):
        """Initialize the display manager.
        
        Args:
            use_colors: Whether to use ANSI color codes in output
            config: Optional GameConfig instance for configurable elements
        """
        self.use_colors = use_colors
        self.config = config or GameConfig()
        self._message_colors = {
            MessageType.INFO: ColorCode.WHITE,
            MessageType.SUCCESS: ColorCode.BRIGHT_GREEN,
            MessageType.WARNING: ColorCode.BRIGHT_YELLOW,
            MessageType.ERROR: ColorCode.BRIGHT_RED,
            MessageType.CHALLENGE: ColorCode.BRIGHT_CYAN,
            MessageType.CHAMBER: ColorCode.BRIGHT_BLUE,
            MessageType.INVENTORY: ColorCode.BRIGHT_MAGENTA,
            MessageType.STATUS: ColorCode.BRIGHT_YELLOW,
        }
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color formatting to text if colors are enabled.
        
        Args:
            text: The text to colorize
            color: The color code to apply
            
        Returns:
            Colorized text or plain text if colors disabled
        """
        if not self.use_colors:
            return text
        return f"{color}{text}{ColorCode.RESET}"
    
    def _format_header(self, title: str, width: int = 60) -> str:
        """Create a formatted header with borders.
        
        Args:
            title: The header title
            width: Total width of the header
            
        Returns:
            Formatted header string
        """
        if len(title) > width - 4:
            title = title[:width - 7] + "..."
        
        padding = (width - len(title) - 2) // 2
        border = "=" * width
        header_line = f"|{' ' * padding}{title}{' ' * (width - len(title) - padding - 2)}|"
        
        return f"\n{border}\n{header_line}\n{border}\n"
    
    def display_message(self, message: str, message_type: MessageType = MessageType.INFO) -> str:
        """Format and return a message with appropriate styling.
        
        Args:
            message: The message to display
            message_type: The type of message for styling
            
        Returns:
            Formatted message string
        """
        color = self._message_colors.get(message_type, ColorCode.WHITE)
        return self._colorize(message, color)
    
    def display_chamber_description(self, chamber_name: str, description: str, exits: List[str]) -> str:
        """Format chamber information for display.
        
        Args:
            chamber_name: Name of the chamber
            description: Chamber description
            exits: List of available exits
            
        Returns:
            Formatted chamber display string
        """
        header = self._format_header(chamber_name)
        colored_header = self._colorize(header, ColorCode.BRIGHT_BLUE)
        
        # Format description
        desc_text = f"\n{description}\n"
        
        # Format exits
        if exits:
            exits_text = f"\nExits: {', '.join(exits)}"
            exits_colored = self._colorize(exits_text, ColorCode.BRIGHT_CYAN)
        else:
            exits_colored = self._colorize("\nNo visible exits.", ColorCode.DIM)
        
        return f"{colored_header}{desc_text}{exits_colored}\n"
    
    def display_challenge(self, challenge: Challenge) -> str:
        """Format challenge information for display.
        
        Args:
            challenge: The challenge to display
            
        Returns:
            Formatted challenge display string
        """
        header = self._format_header(f"Challenge: {challenge.name}")
        colored_header = self._colorize(header, ColorCode.BRIGHT_CYAN)
        
        difficulty_stars = "★" * challenge.difficulty + "☆" * (10 - challenge.difficulty)
        difficulty_text = f"Difficulty: {difficulty_stars} ({challenge.difficulty}/10)"
        colored_difficulty = self._colorize(difficulty_text, ColorCode.BRIGHT_YELLOW)
        
        challenge_text = challenge.present_challenge()
        
        return f"{colored_header}\n{colored_difficulty}\n\n{challenge_text}\n"
    
    def display_challenge_result(self, result: ChallengeResult) -> str:
        """Format challenge result for display.
        
        Args:
            result: The challenge result to display
            
        Returns:
            Formatted result display string
        """
        # Don't show SUCCESS/FAILED for intermediate steps
        if result.is_intermediate:
            status_text = ""
        elif result.success:
            status_text = self._colorize("SUCCESS!", ColorCode.BRIGHT_GREEN)
        else:
            status_text = self._colorize("FAILED!", ColorCode.BRIGHT_RED)
        
        message_text = f"\n{result.message}\n" if status_text else result.message
        
        additional_info = []
        if result.damage > 0:
            damage_text = f"You took {result.damage} damage!"
            additional_info.append(self._colorize(damage_text, ColorCode.BRIGHT_RED))
        
        if result.reward:
            reward_text = f"You received: {result.reward.name}"
            additional_info.append(self._colorize(reward_text, ColorCode.BRIGHT_GREEN))
        
        additional_text = "\n".join(additional_info)
        if additional_text:
            additional_text = f"\n{additional_text}"
        
        return f"{status_text}{message_text}{additional_text}\n"
    
    def display_inventory(self, items: List[Item]) -> str:
        """Format inventory contents for display.
        
        Args:
            items: List of items in inventory
            
        Returns:
            Formatted inventory display string
        """
        header = self._format_header("Inventory")
        colored_header = self._colorize(header, ColorCode.BRIGHT_MAGENTA)
        
        if not items:
            empty_text = self._colorize("Your inventory is empty.", ColorCode.DIM)
            count_text = self._colorize(f"\nTotal items: {len(items)}", ColorCode.BRIGHT_CYAN)
            return f"{colored_header}\n{empty_text}{count_text}\n"
        
        item_lines = []
        for item in items:
            item_name = self._colorize(item.name, ColorCode.BRIGHT_WHITE)
            item_type = self._colorize(f"({item.item_type})", ColorCode.DIM)
            usable_status = "✓" if item.usable else "✗"
            usable_colored = self._colorize(usable_status, 
                                          ColorCode.BRIGHT_GREEN if item.usable else ColorCode.BRIGHT_RED)
            
            item_line = f"  {usable_colored} {item_name} {item_type} - {item.description}"
            item_lines.append(item_line)
        
        items_text = "\n".join(item_lines)
        count_text = self._colorize(f"\nTotal items: {len(items)}", ColorCode.BRIGHT_CYAN)
        
        return f"{colored_header}\n{items_text}{count_text}\n"
    
    def display_player_status(self, health: int, stats: PlayerStats, completed_chambers: int) -> str:
        """Format player status information for display.
        
        Args:
            health: Current player health
            stats: Player statistics
            completed_chambers: Number of completed chambers
            
        Returns:
            Formatted status display string
        """
        header = self._format_header("Player Status")
        colored_header = self._colorize(header, ColorCode.BRIGHT_YELLOW)
        
        # Health display with color coding
        if health > 75:
            health_color = ColorCode.BRIGHT_GREEN
        elif health > 50:
            health_color = ColorCode.BRIGHT_YELLOW
        elif health > 25:
            health_color = ColorCode.YELLOW
        else:
            health_color = ColorCode.BRIGHT_RED
        
        health_text = self._colorize(f"Health: {health}/100", health_color)
        
        # Stats display
        stats_lines = [
            f"Strength: {stats.strength}",
            f"Intelligence: {stats.intelligence}",
            f"Dexterity: {stats.dexterity}",
            f"Luck: {stats.luck}"
        ]
        stats_text = self._colorize("Stats:\n  " + "\n  ".join(stats_lines), ColorCode.BRIGHT_CYAN)
        
        # Progress display
        progress_text = self._colorize(f"Chambers Completed: {completed_chambers}/13", ColorCode.BRIGHT_MAGENTA)
        
        return f"{colored_header}\n{health_text}\n\n{stats_text}\n\n{progress_text}\n"
    
    def display_help(self, commands: Dict[str, str]) -> str:
        """Format help information for display.
        
        Args:
            commands: Dictionary of command names and descriptions
            
        Returns:
            Formatted help display string
        """
        header = self._format_header("Available Commands")
        colored_header = self._colorize(header, ColorCode.BRIGHT_CYAN)
        
        command_lines = []
        for command, description in commands.items():
            command_name = self._colorize(command, ColorCode.BRIGHT_WHITE)
            command_line = f"  {command_name} - {description}"
            command_lines.append(command_line)
        
        commands_text = "\n".join(command_lines)
        
        return f"{colored_header}\n{commands_text}\n"
    
    def display_game_over(self, victory: bool, stats: Dict[str, Any]) -> str:
        """Format game over screen for display.
        
        Args:
            victory: Whether the player won or lost
            stats: Game statistics to display
            
        Returns:
            Formatted game over display string
        """
        if victory:
            title = "VICTORY!"
            title_color = ColorCode.BRIGHT_GREEN
            # Use configurable victory message
            victory_message = self.config.get_victory_message()
            message = f"Congratulations! You have successfully escaped the labyrinth!\n\n{victory_message}"
        else:
            title = "GAME OVER"
            title_color = ColorCode.BRIGHT_RED
            message = "Your adventure has come to an end..."
        
        header = self._format_header(title, 70)
        colored_header = self._colorize(header, title_color)
        
        message_text = f"\n{message}\n"
        
        # Format statistics
        stats_lines = []
        for key, value in stats.items():
            stats_lines.append(f"{key}: {value}")
        
        if stats_lines:
            stats_header = self._colorize("\nGame Statistics:", ColorCode.BRIGHT_YELLOW)
            stats_text = "\n  ".join([""] + stats_lines)
        else:
            stats_header = ""
            stats_text = ""
        
        return f"{colored_header}{message_text}{stats_header}{stats_text}\n"
    
    def format_prompt(self, prompt_text: str) -> str:
        """Format an input prompt for display.
        
        Args:
            prompt_text: The prompt text
            
        Returns:
            Formatted prompt string
        """
        return self._colorize(f"\n> {prompt_text}: ", ColorCode.BRIGHT_WHITE)