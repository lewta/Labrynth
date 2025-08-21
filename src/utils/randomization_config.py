"""Configuration management for randomization settings."""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from src.utils.exceptions import GameException
from src.utils.randomization import RandomizationConfig, RandomizationLevel, create_randomization_config
from src.utils.labyrinth_generator import GenerationConfig, LabyrinthLayout


@dataclass
class GameRandomizationConfig:
    """Complete randomization configuration for the game."""
    labyrinth_enabled: bool = False
    labyrinth_chamber_count: int = 13
    labyrinth_layout: str = "hybrid"
    labyrinth_connectivity: float = 0.3
    labyrinth_ensure_solvable: bool = True
    labyrinth_min_path_length: int = 5
    labyrinth_max_dead_ends: int = 3
    labyrinth_seed: Optional[int] = None
    
    challenge_enabled: bool = True
    challenge_level: str = "moderate"
    challenge_variety: bool = True
    challenge_difficulty_variance: int = 1
    challenge_seed: Optional[int] = None
    
    def to_labyrinth_config(self) -> GenerationConfig:
        """Convert to labyrinth generation configuration."""
        return GenerationConfig(
            chamber_count=self.labyrinth_chamber_count,
            layout=LabyrinthLayout(self.labyrinth_layout.lower()),
            connectivity=self.labyrinth_connectivity,
            ensure_solvable=self.labyrinth_ensure_solvable,
            min_path_length=self.labyrinth_min_path_length,
            max_dead_ends=self.labyrinth_max_dead_ends,
            seed=self.labyrinth_seed
        )
    
    def to_challenge_config(self) -> RandomizationConfig:
        """Convert to challenge randomization configuration."""
        return create_randomization_config(
            level=self.challenge_level,
            seed=self.challenge_seed,
            variety=self.challenge_variety,
            variance=self.challenge_difficulty_variance
        )


class RandomizationConfigManager:
    """Manages randomization configuration loading and saving."""
    
    def __init__(self, config_file: str = "config/randomization_settings.json"):
        """Initialize the configuration manager.
        
        Args:
            config_file: Path to the randomization settings file
        """
        self.config_file = config_file
        self._config_cache = None
    
    def load_config(self, preset: str = None) -> GameRandomizationConfig:
        """Load randomization configuration.
        
        Args:
            preset: Optional preset name to load ('easy', 'normal', 'hard', 'nightmare')
            
        Returns:
            GameRandomizationConfig instance
        """
        config_data = self._load_config_file()
        
        if preset:
            return self._load_preset_config(config_data, preset)
        else:
            return self._load_default_config(config_data)
    
    def _load_config_file(self) -> Dict[str, Any]:
        """Load the configuration file."""
        if self._config_cache is not None:
            return self._config_cache
        
        if not os.path.exists(self.config_file):
            raise GameException(f"Randomization config file not found: {self.config_file}")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self._config_cache = config_data
            return config_data
            
        except json.JSONDecodeError as e:
            raise GameException(f"Invalid JSON in randomization config: {e}")
        except Exception as e:
            raise GameException(f"Error loading randomization config: {e}")
    
    def _load_default_config(self, config_data: Dict[str, Any]) -> GameRandomizationConfig:
        """Load default configuration."""
        labyrinth_config = config_data.get("labyrinth_randomization", {})
        challenge_config = config_data.get("challenge_randomization", {})
        
        return GameRandomizationConfig(
            labyrinth_enabled=labyrinth_config.get("enabled", False),
            labyrinth_chamber_count=labyrinth_config.get("chamber_count", 13),
            labyrinth_layout=labyrinth_config.get("layout", "hybrid"),
            labyrinth_connectivity=labyrinth_config.get("connectivity", 0.3),
            labyrinth_ensure_solvable=labyrinth_config.get("ensure_solvable", True),
            labyrinth_min_path_length=labyrinth_config.get("min_path_length", 5),
            labyrinth_max_dead_ends=labyrinth_config.get("max_dead_ends", 3),
            labyrinth_seed=labyrinth_config.get("seed"),
            
            challenge_enabled=challenge_config.get("enabled", True),
            challenge_level=challenge_config.get("level", "moderate"),
            challenge_variety=challenge_config.get("challenge_variety", True),
            challenge_difficulty_variance=challenge_config.get("difficulty_variance", 1),
            challenge_seed=challenge_config.get("seed")
        )
    
    def _load_preset_config(self, config_data: Dict[str, Any], preset: str) -> GameRandomizationConfig:
        """Load a preset configuration."""
        presets = config_data.get("presets", {})
        
        if preset not in presets:
            available_presets = list(presets.keys())
            raise GameException(f"Unknown preset '{preset}'. Available presets: {available_presets}")
        
        preset_data = presets[preset]
        
        # Start with default config
        base_config = self._load_default_config(config_data)
        
        # Override with preset values
        labyrinth_preset = preset_data.get("labyrinth_randomization", {})
        challenge_preset = preset_data.get("challenge_randomization", {})
        
        # Update labyrinth settings
        if "enabled" in labyrinth_preset:
            base_config.labyrinth_enabled = labyrinth_preset["enabled"]
        if "chamber_count" in labyrinth_preset:
            base_config.labyrinth_chamber_count = labyrinth_preset["chamber_count"]
        if "layout" in labyrinth_preset:
            base_config.labyrinth_layout = labyrinth_preset["layout"]
        if "connectivity" in labyrinth_preset:
            base_config.labyrinth_connectivity = labyrinth_preset["connectivity"]
        if "min_path_length" in labyrinth_preset:
            base_config.labyrinth_min_path_length = labyrinth_preset["min_path_length"]
        
        # Update challenge settings
        if "enabled" in challenge_preset:
            base_config.challenge_enabled = challenge_preset["enabled"]
        if "level" in challenge_preset:
            base_config.challenge_level = challenge_preset["level"]
        if "difficulty_variance" in challenge_preset:
            base_config.challenge_difficulty_variance = challenge_preset["difficulty_variance"]
        
        return base_config
    
    def save_config(self, config: GameRandomizationConfig) -> None:
        """Save randomization configuration.
        
        Args:
            config: Configuration to save
        """
        config_data = self._load_config_file()
        
        # Update the configuration data
        config_data["labyrinth_randomization"] = {
            "enabled": config.labyrinth_enabled,
            "chamber_count": config.labyrinth_chamber_count,
            "layout": config.labyrinth_layout,
            "connectivity": config.labyrinth_connectivity,
            "ensure_solvable": config.labyrinth_ensure_solvable,
            "min_path_length": config.labyrinth_min_path_length,
            "max_dead_ends": config.labyrinth_max_dead_ends,
            "seed": config.labyrinth_seed
        }
        
        config_data["challenge_randomization"] = {
            "enabled": config.challenge_enabled,
            "level": config.challenge_level,
            "challenge_variety": config.challenge_variety,
            "difficulty_variance": config.challenge_difficulty_variance,
            "seed": config.challenge_seed
        }
        
        # Save to file
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            # Clear cache
            self._config_cache = None
            
        except Exception as e:
            raise GameException(f"Error saving randomization config: {e}")
    
    def get_available_presets(self) -> list[str]:
        """Get list of available presets.
        
        Returns:
            List of preset names
        """
        config_data = self._load_config_file()
        presets = config_data.get("presets", {})
        return list(presets.keys())
    
    def get_preset_info(self, preset: str) -> Dict[str, Any]:
        """Get information about a specific preset.
        
        Args:
            preset: Preset name
            
        Returns:
            Dictionary with preset information
        """
        config_data = self._load_config_file()
        presets = config_data.get("presets", {})
        
        if preset not in presets:
            raise GameException(f"Unknown preset: {preset}")
        
        preset_data = presets[preset]
        
        # Extract key information
        labyrinth_info = preset_data.get("labyrinth_randomization", {})
        challenge_info = preset_data.get("challenge_randomization", {})
        
        return {
            "name": preset,
            "labyrinth": {
                "chamber_count": labyrinth_info.get("chamber_count", 13),
                "layout": labyrinth_info.get("layout", "hybrid"),
                "connectivity": labyrinth_info.get("connectivity", 0.3)
            },
            "challenges": {
                "level": challenge_info.get("level", "moderate"),
                "difficulty_variance": challenge_info.get("difficulty_variance", 1)
            }
        }
    
    def validate_config(self, config: GameRandomizationConfig) -> None:
        """Validate a randomization configuration.
        
        Args:
            config: Configuration to validate
            
        Raises:
            GameException: If configuration is invalid
        """
        # Validate labyrinth settings
        if config.labyrinth_chamber_count < 3:
            raise GameException("Labyrinth chamber count must be at least 3")
        
        if config.labyrinth_chamber_count > 50:
            raise GameException("Labyrinth chamber count cannot exceed 50")
        
        if not 0.0 <= config.labyrinth_connectivity <= 1.0:
            raise GameException("Labyrinth connectivity must be between 0.0 and 1.0")
        
        valid_layouts = ["linear", "circular", "tree", "grid", "random", "hybrid"]
        if config.labyrinth_layout not in valid_layouts:
            raise GameException(f"Invalid labyrinth layout. Must be one of: {valid_layouts}")
        
        if config.labyrinth_min_path_length < 2:
            raise GameException("Minimum path length must be at least 2")
        
        if config.labyrinth_min_path_length >= config.labyrinth_chamber_count:
            raise GameException("Minimum path length must be less than chamber count")
        
        # Validate challenge settings
        valid_levels = ["none", "light", "moderate", "heavy"]
        if config.challenge_level not in valid_levels:
            raise GameException(f"Invalid challenge level. Must be one of: {valid_levels}")
        
        if config.challenge_difficulty_variance < 0:
            raise GameException("Challenge difficulty variance cannot be negative")
        
        if config.challenge_difficulty_variance > 5:
            raise GameException("Challenge difficulty variance cannot exceed 5")


# Global configuration manager instance
_config_manager = None


def get_randomization_config_manager() -> RandomizationConfigManager:
    """Get the global randomization configuration manager.
    
    Returns:
        RandomizationConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = RandomizationConfigManager()
    return _config_manager


def load_randomization_config(preset: str = None) -> GameRandomizationConfig:
    """Load randomization configuration.
    
    Args:
        preset: Optional preset name
        
    Returns:
        GameRandomizationConfig instance
    """
    manager = get_randomization_config_manager()
    return manager.load_config(preset)


def save_randomization_config(config: GameRandomizationConfig) -> None:
    """Save randomization configuration.
    
    Args:
        config: Configuration to save
    """
    manager = get_randomization_config_manager()
    manager.save_config(config)


def get_available_randomization_presets() -> list[str]:
    """Get available randomization presets.
    
    Returns:
        List of preset names
    """
    manager = get_randomization_config_manager()
    return manager.get_available_presets()