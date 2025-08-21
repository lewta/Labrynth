"""Game configuration management with JSON file support and dot notation access."""

import json
import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union


class GameConfig:
    """Configuration manager for the Labyrinth Adventure Game.
    
    Provides JSON file loading/saving capabilities and dot notation access
    to configuration values.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize GameConfig with optional custom config file path.
        
        Args:
            config_file: Optional path to configuration file. If None, uses default search.
        """
        self._config_file = config_file
        self._config_data: Dict[str, Any] = {}
        self._default_config = self._get_default_config()
        self._read_only_mode = False
        self._logger = logging.getLogger(__name__)
        
        # Load configuration on initialization
        self.load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get the default configuration structure.
        
        Returns:
            Dictionary containing default configuration values.
        """
        import copy
        return copy.deepcopy({
            "victory": {
                "flag_content": "LABYRINTH_MASTER_2024",
                "flag_prefix": "FLAG{",
                "flag_suffix": "}",
                "prize_message": "🏆 YOUR PRIZE: {flag}\n\nYou have proven yourself worthy of the ancient secrets!"
            },
            "game": {
                "title": "Labyrinth Adventure Game",
                "version": "1.0"
            },
            "display": {
                "width": 80,
                "show_map": True
            }
        })
    
    def _find_config_file(self) -> Optional[str]:
        """Find configuration file using search order.
        
        Search order:
        1. game_config.json (project root)
        2. config/game_config.json (config directory)
        3. ~/.labrynth_config.json (user home directory)
        
        Returns:
            Path to first found configuration file, or None if none found.
        """
        search_paths = [
            "game_config.json",
            "config/game_config.json",
            os.path.expanduser("~/.labrynth_config.json")
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def load_config(self) -> None:
        """Load configuration from file with comprehensive error handling.
        
        Falls back to default configuration if file loading fails.
        Handles missing files, invalid JSON, permission errors, and other I/O issues.
        """
        # Start with default configuration
        import copy
        self._config_data = copy.deepcopy(self._default_config)
        self._read_only_mode = False
        
        # Determine config file to use
        config_file = self._config_file or self._find_config_file()
        
        if not config_file:
            # No configuration file found, use defaults
            self._logger.info("No configuration file found, using default configuration")
            return
        
        if not os.path.exists(config_file):
            # Configuration file specified but doesn't exist
            self._logger.warning(f"Configuration file {config_file} does not exist, using default configuration")
            return
        
        try:
            # Check if file is readable
            if not os.access(config_file, os.R_OK):
                raise PermissionError(f"No read permission for configuration file: {config_file}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                file_content = f.read().strip()
                
                # Check for empty file
                if not file_content:
                    self._logger.warning(f"Configuration file {config_file} is empty, using default configuration")
                    return
                
                # Parse JSON
                try:
                    file_config = json.loads(file_content)
                except json.JSONDecodeError as e:
                    self._logger.error(f"Invalid JSON in configuration file {config_file}: {e}")
                    self._logger.info("Using default configuration due to JSON parsing error")
                    return
                
                # Validate that parsed content is a dictionary
                if not isinstance(file_config, dict):
                    self._logger.error(f"Configuration file {config_file} must contain a JSON object, got {type(file_config).__name__}")
                    self._logger.info("Using default configuration due to invalid structure")
                    return
                
                # Merge file configuration with defaults
                self._merge_config(self._config_data, file_config)
                self._logger.info(f"Successfully loaded configuration from {config_file}")
                
        except PermissionError as e:
            self._logger.error(f"Permission denied accessing configuration file {config_file}: {e}")
            self._logger.info("Operating in read-only mode with default configuration")
            self._read_only_mode = True
            
        except FileNotFoundError:
            # File was deleted between existence check and open
            self._logger.warning(f"Configuration file {config_file} was not found during loading")
            self._logger.info("Using default configuration")
            
        except OSError as e:
            # Other OS-level errors (disk full, network issues, etc.)
            self._logger.error(f"OS error accessing configuration file {config_file}: {e}")
            self._logger.info("Using default configuration due to OS error")
            self._read_only_mode = True
            
        except UnicodeDecodeError as e:
            self._logger.error(f"Encoding error reading configuration file {config_file}: {e}")
            self._logger.info("Using default configuration due to encoding error")
            
        except Exception as e:
            # Catch any other unexpected errors
            self._logger.error(f"Unexpected error loading configuration from {config_file}: {e}")
            self._logger.info("Using default configuration due to unexpected error")
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge override configuration into base configuration.
        
        Args:
            base: Base configuration dictionary to merge into.
            override: Override configuration dictionary to merge from.
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def save_config(self) -> None:
        """Save current configuration to file with comprehensive error handling.
        
        Raises:
            IOError: If file cannot be written.
            PermissionError: If no write permission to file or directory.
            OSError: If other OS-level errors occur.
        """
        if self._read_only_mode:
            raise PermissionError("Cannot save configuration: operating in read-only mode due to previous errors")
        
        config_file = self._config_file or "game_config.json"
        
        try:
            # Ensure directory exists
            config_dir = os.path.dirname(config_file)
            if config_dir:
                try:
                    if not os.path.exists(config_dir):
                        os.makedirs(config_dir, exist_ok=True)
                        self._logger.info(f"Created configuration directory: {config_dir}")
                    
                    # Check directory write permissions
                    if not os.access(config_dir, os.W_OK):
                        raise PermissionError(f"No write permission for directory: {config_dir}")
                        
                except OSError as e:
                    raise OSError(f"Failed to create or access configuration directory {config_dir}: {e}")
            
            # Check if file exists and is writable
            if os.path.exists(config_file) and not os.access(config_file, os.W_OK):
                raise PermissionError(f"No write permission for configuration file: {config_file}")
            
            # Create a temporary file first to avoid corrupting existing config on write failure
            temp_file = config_file + ".tmp"
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(self._config_data, f, indent=2, ensure_ascii=False)
                
                # Atomic move to replace original file
                if os.name == 'nt':  # Windows
                    if os.path.exists(config_file):
                        os.remove(config_file)
                    os.rename(temp_file, config_file)
                else:  # Unix-like systems
                    os.rename(temp_file, config_file)
                
                self._logger.info(f"Successfully saved configuration to {config_file}")
                
            except Exception:
                # Clean up temporary file if it exists
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except OSError:
                        pass  # Ignore cleanup errors
                raise
                
        except PermissionError as e:
            self._logger.error(f"Permission denied saving configuration: {e}")
            self._read_only_mode = True
            raise
            
        except OSError as e:
            self._logger.error(f"OS error saving configuration to {config_file}: {e}")
            raise OSError(f"Failed to save configuration to {config_file}: {e}")
            
        except UnicodeEncodeError as e:
            self._logger.error(f"Encoding error saving configuration: {e}")
            raise IOError(f"Failed to save configuration due to encoding error: {e}")
            
        except Exception as e:
            self._logger.error(f"Unexpected error saving configuration to {config_file}: {e}")
            raise IOError(f"Failed to save configuration to {config_file}: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to configuration value (e.g., "victory.flag_content").
            default: Default value to return if key not found.
            
        Returns:
            Configuration value or default if not found.
        """
        keys = key_path.split('.')
        current = self._config_data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to configuration value (e.g., "victory.flag_content").
            value: Value to set.
        """
        keys = key_path.split('.')
        current = self._config_data
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                # Convert non-dict to dict to allow nested setting
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def get_victory_flag(self) -> str:
        """Get complete victory flag by combining prefix, content, and suffix.
        
        Returns:
            Complete flag string (e.g., "FLAG{LABYRINTH_MASTER_2024}").
        """
        prefix = self.get("victory.flag_prefix", "FLAG{")
        content = self.get("victory.flag_content", "LABYRINTH_MASTER_2024")
        suffix = self.get("victory.flag_suffix", "}")
        
        return f"{prefix}{content}{suffix}"
    
    def get_victory_message(self) -> str:
        """Get formatted victory message with flag placeholder replaced.
        
        Returns:
            Complete victory message with flag inserted.
            Falls back to default template if formatting fails.
        """
        message_template = self.get(
            "victory.prize_message", 
            "🏆 YOUR PRIZE: {flag}\n\nYou have proven yourself worthy of the ancient secrets!"
        )
        flag = self.get_victory_flag()
        
        try:
            return message_template.format(flag=flag)
        except Exception as e:
            # Template formatting failed, use fallback
            self._logger.warning(f"Victory message template formatting failed: {e}")
            self._logger.info("Using fallback victory message template")
            
            fallback_template = "🏆 YOUR PRIZE: {flag}\n\nYou have proven yourself worthy of the ancient secrets!"
            try:
                return fallback_template.format(flag=flag)
            except Exception:
                # Even fallback failed, return basic message
                return f"🏆 YOUR PRIZE: {flag}\n\nYou have proven yourself worthy of the ancient secrets!"
    
    def update_flag_content(self, content: str) -> None:
        """Update flag content and save configuration with error handling.
        
        Args:
            content: New flag content to set.
            
        Raises:
            ValueError: If content is empty or None.
            IOError: If configuration cannot be saved.
            PermissionError: If operating in read-only mode.
        """
        if content is None:
            raise ValueError("Flag content cannot be None")
        
        if not content or not content.strip():
            raise ValueError("Flag content cannot be empty")
        
        # Validate content doesn't contain problematic characters
        stripped_content = content.strip()
        if '\n' in stripped_content or '\r' in stripped_content:
            self._logger.warning("Flag content contains newline characters, which may cause display issues")
        
        try:
            self.set("victory.flag_content", stripped_content)
            self.save_config()
            self._logger.info(f"Successfully updated flag content to: {stripped_content}")
            
        except (IOError, OSError, PermissionError) as e:
            # Re-raise with additional context
            self._logger.error(f"Failed to update flag content: {e}")
            raise
    
    def is_read_only(self) -> bool:
        """Check if configuration is in read-only mode.
        
        Returns:
            True if configuration cannot be saved due to previous errors.
        """
        return self._read_only_mode
    
    def get_config_file_path(self) -> Optional[str]:
        """Get the path to the configuration file being used.
        
        Returns:
            Path to configuration file, or None if using defaults only.
        """
        return self._config_file or self._find_config_file()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values.
        
        This can be used for error recovery when configuration becomes corrupted.
        """
        import copy
        self._config_data = copy.deepcopy(self._default_config)
        self._read_only_mode = False
        self._logger.info("Configuration reset to default values")
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration and return any issues found.
        
        Returns:
            Dictionary containing validation results with 'valid' boolean and 'issues' list.
        """
        issues = []
        
        # Check required victory section
        if not self.get("victory"):
            issues.append("Missing 'victory' section")
        else:
            # Check required victory fields
            required_victory_fields = ["flag_content", "flag_prefix", "flag_suffix", "prize_message"]
            for field in required_victory_fields:
                if not self.get(f"victory.{field}"):
                    issues.append(f"Missing or empty 'victory.{field}'")
            
            # Validate prize message has flag placeholder
            prize_message = self.get("victory.prize_message", "")
            if prize_message and "{flag}" not in prize_message:
                issues.append("Prize message template missing {flag} placeholder")
        
        # Check game section
        if not self.get("game"):
            issues.append("Missing 'game' section")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }