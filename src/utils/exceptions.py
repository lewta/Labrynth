"""Custom exception classes for the Labyrinth Adventure Game."""

from typing import List, Optional, Dict, Any


class GameException(Exception):
    """Base exception for game-related errors.
    
    Provides common functionality for all game exceptions including
    error recovery suggestions and graceful degradation support.
    """
    
    def __init__(self, message: str, recovery_suggestions: Optional[List[str]] = None, 
                 error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.recovery_suggestions = recovery_suggestions or []
        self.error_code = error_code
        self.context = context or {}
    
    def get_user_friendly_message(self) -> str:
        """Return a user-friendly error message."""
        return str(self)
    
    def get_recovery_suggestions(self) -> List[str]:
        """Return list of recovery suggestions for the user."""
        return self.recovery_suggestions
    
    def can_recover(self) -> bool:
        """Return True if this error allows for recovery."""
        return len(self.recovery_suggestions) > 0


class InvalidCommandException(GameException):
    """Raised when user enters an invalid command."""
    
    def __init__(self, command: str, valid_commands: Optional[List[str]] = None, 
                 similar_commands: Optional[List[str]] = None):
        suggestions = []
        if similar_commands:
            suggestions.extend([f"Did you mean '{cmd}'?" for cmd in similar_commands])
        if valid_commands:
            suggestions.append(f"Valid commands are: {', '.join(valid_commands)}")
        suggestions.append("Type 'help' for a list of all available commands.")
        
        super().__init__(
            f"Unknown command: '{command}'",
            recovery_suggestions=suggestions,
            error_code="INVALID_COMMAND",
            context={"command": command, "valid_commands": valid_commands}
        )
        self.command = command
        self.valid_commands = valid_commands or []
        self.similar_commands = similar_commands or []


class ChallengeException(GameException):
    """Raised when challenge processing fails."""
    
    def __init__(self, challenge_type: str, message: str, 
                 can_retry: bool = True, challenge_id: Optional[str] = None):
        suggestions = []
        if can_retry:
            suggestions.append("You can try again or type 'leave' to exit the chamber.")
        else:
            suggestions.append("This challenge cannot be retried. Type 'leave' to exit.")
        
        super().__init__(
            f"Challenge error in {challenge_type}: {message}",
            recovery_suggestions=suggestions,
            error_code="CHALLENGE_ERROR",
            context={"challenge_type": challenge_type, "challenge_id": challenge_id, "can_retry": can_retry}
        )
        self.challenge_type = challenge_type
        self.can_retry = can_retry
        self.challenge_id = challenge_id


class SaveLoadException(GameException):
    """Raised when save/load operations fail."""
    
    def __init__(self, operation: str, filename: str, reason: str, 
                 is_recoverable: bool = True):
        suggestions = []
        if operation == "save":
            if is_recoverable:
                suggestions.extend([
                    "Try saving with a different filename.",
                    "Check that you have write permissions to the save directory.",
                    "Ensure there is enough disk space available."
                ])
            else:
                suggestions.append("Game state could not be saved. Continue playing without saving.")
        elif operation == "load":
            if is_recoverable:
                suggestions.extend([
                    "Check that the save file exists and is not corrupted.",
                    "Try loading a different save file.",
                    "Start a new game if no valid saves are available."
                ])
            else:
                suggestions.append("Save file is corrupted. Please start a new game.")
        
        super().__init__(
            f"Failed to {operation} game '{filename}': {reason}",
            recovery_suggestions=suggestions,
            error_code=f"{operation.upper()}_ERROR",
            context={"operation": operation, "filename": filename, "reason": reason}
        )
        self.operation = operation
        self.filename = filename
        self.reason = reason
        self.is_recoverable = is_recoverable


class WorldException(GameException):
    """Raised when world/chamber operations fail."""
    
    def __init__(self, message: str, chamber_id: Optional[int] = None, 
                 direction: Optional[str] = None):
        suggestions = []
        if direction:
            suggestions.extend([
                f"There is no exit to the {direction}.",
                "Type 'look' to see available exits.",
                "Use 'north', 'south', 'east', or 'west' to move."
            ])
        else:
            suggestions.append("Type 'look' to examine your current location.")
        
        super().__init__(
            message,
            recovery_suggestions=suggestions,
            error_code="WORLD_ERROR",
            context={"chamber_id": chamber_id, "direction": direction}
        )
        self.chamber_id = chamber_id
        self.direction = direction


class InventoryException(GameException):
    """Raised when inventory operations fail."""
    
    def __init__(self, message: str, item_name: Optional[str] = None, 
                 operation: Optional[str] = None):
        suggestions = []
        if operation == "use" and item_name:
            suggestions.extend([
                f"You don't have '{item_name}' in your inventory.",
                "Type 'inventory' to see what items you have.",
                "Check the spelling of the item name."
            ])
        elif operation == "add":
            suggestions.append("Your inventory might be full. Try using or dropping some items.")
        else:
            suggestions.append("Type 'inventory' to see your current items.")
        
        super().__init__(
            message,
            recovery_suggestions=suggestions,
            error_code="INVENTORY_ERROR",
            context={"item_name": item_name, "operation": operation}
        )
        self.item_name = item_name
        self.operation = operation


class PlayerException(GameException):
    """Raised when player state operations fail."""
    
    def __init__(self, message: str, player_stat: Optional[str] = None, 
                 is_fatal: bool = False):
        suggestions = []
        if is_fatal:
            suggestions.extend([
                "Game Over! Your health has reached zero.",
                "Type 'load' to restore a previous save or 'new' to start over."
            ])
        elif player_stat == "health":
            suggestions.extend([
                "Your health is low. Look for healing items or rest areas.",
                "Be careful in combat situations."
            ])
        else:
            suggestions.append("Check your status with the 'status' command.")
        
        super().__init__(
            message,
            recovery_suggestions=suggestions,
            error_code="PLAYER_ERROR",
            context={"player_stat": player_stat, "is_fatal": is_fatal}
        )
        self.player_stat = player_stat
        self.is_fatal = is_fatal


class ConfigurationException(GameException):
    """Raised when configuration loading or validation fails."""
    
    def __init__(self, config_type: str, message: str, 
                 config_file: Optional[str] = None):
        suggestions = [
            "Check that all required configuration files are present.",
            "Verify that configuration files contain valid JSON/YAML.",
            "Try restoring default configuration files."
        ]
        
        super().__init__(
            f"Configuration error in {config_type}: {message}",
            recovery_suggestions=suggestions,
            error_code="CONFIG_ERROR",
            context={"config_type": config_type, "config_file": config_file}
        )
        self.config_type = config_type
        self.config_file = config_file


class GameStateException(GameException):
    """Raised when game state becomes invalid or corrupted."""
    
    def __init__(self, message: str, state_component: Optional[str] = None, 
                 is_recoverable: bool = True):
        suggestions = []
        if is_recoverable:
            suggestions.extend([
                "Try loading a previous save file.",
                "Restart the current chamber if possible.",
                "Check for any corrupted save files."
            ])
        else:
            suggestions.extend([
                "Game state is corrupted and cannot be recovered.",
                "Please start a new game."
            ])
        
        super().__init__(
            f"Game state error: {message}",
            recovery_suggestions=suggestions,
            error_code="STATE_ERROR",
            context={"state_component": state_component, "is_recoverable": is_recoverable}
        )
        self.state_component = state_component
        self.is_recoverable = is_recoverable