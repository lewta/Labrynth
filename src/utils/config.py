"""Configuration management for the Labyrinth Adventure Game."""

import json
import os
from typing import Dict, Any, List, Set
from src.utils.exceptions import GameException


class LabyrinthConfigValidator:
    """Validates labyrinth configuration data."""
    
    def __init__(self):
        """Initialize the validator."""
        self.required_chamber_fields = {"name", "description"}
        self.optional_chamber_fields = {"connections", "challenge_type", "items"}
        self.valid_directions = {
            "north", "south", "east", "west", 
            "northeast", "northwest", "southeast", "southwest",
            "up", "down"
        }
    
    def validate_config(self, config_data: Dict[str, Any]) -> None:
        """Validate the complete configuration data.
        
        Args:
            config_data: Configuration dictionary to validate
            
        Raises:
            GameException: If configuration is invalid
        """
        if not isinstance(config_data, dict):
            raise GameException("Configuration must be a dictionary")
        
        # Validate chambers section
        if "chambers" not in config_data:
            raise GameException("Configuration must contain 'chambers' section")
        
        chambers = config_data["chambers"]
        if not isinstance(chambers, dict):
            raise GameException("'chambers' must be a dictionary")
        
        if not chambers:
            raise GameException("Configuration must contain at least one chamber")
        
        # Validate each chamber
        chamber_ids = set()
        for chamber_id_str, chamber_data in chambers.items():
            chamber_id = self._validate_chamber_id(chamber_id_str)
            chamber_ids.add(chamber_id)
            self._validate_chamber_data(chamber_id, chamber_data)
        
        # Validate connections reference existing chambers
        self._validate_connections(chambers, chamber_ids)
        
        # Validate starting chamber
        self._validate_starting_chamber(config_data, chamber_ids)
        
        # Validate connectivity
        self._validate_connectivity(chambers, chamber_ids)
    
    def _validate_chamber_id(self, chamber_id_str: str) -> int:
        """Validate and convert chamber ID.
        
        Args:
            chamber_id_str: String representation of chamber ID
            
        Returns:
            Integer chamber ID
            
        Raises:
            GameException: If chamber ID is invalid
        """
        try:
            chamber_id = int(chamber_id_str)
        except ValueError:
            raise GameException(f"Chamber ID must be an integer: {chamber_id_str}")
        
        if chamber_id < 1:
            raise GameException(f"Chamber ID must be positive: {chamber_id}")
        
        return chamber_id
    
    def _validate_chamber_data(self, chamber_id: int, chamber_data: Any) -> None:
        """Validate chamber data structure.
        
        Args:
            chamber_id: ID of the chamber being validated
            chamber_data: Chamber data to validate
            
        Raises:
            GameException: If chamber data is invalid
        """
        if not isinstance(chamber_data, dict):
            raise GameException(f"Chamber {chamber_id} data must be a dictionary")
        
        # Check required fields
        for field in self.required_chamber_fields:
            if field not in chamber_data:
                raise GameException(f"Chamber {chamber_id} missing required field: {field}")
            
            if not isinstance(chamber_data[field], str) or not chamber_data[field].strip():
                raise GameException(f"Chamber {chamber_id} field '{field}' must be a non-empty string")
        
        # Validate optional fields
        for field, value in chamber_data.items():
            if field not in self.required_chamber_fields and field not in self.optional_chamber_fields:
                raise GameException(f"Chamber {chamber_id} contains unknown field: {field}")
        
        # Validate connections if present
        if "connections" in chamber_data:
            self._validate_chamber_connections(chamber_id, chamber_data["connections"])
        
        # Validate challenge_type if present
        if "challenge_type" in chamber_data:
            if not isinstance(chamber_data["challenge_type"], str):
                raise GameException(f"Chamber {chamber_id} challenge_type must be a string")
        
        # Validate items if present
        if "items" in chamber_data:
            if not isinstance(chamber_data["items"], list):
                raise GameException(f"Chamber {chamber_id} items must be a list")
    
    def _validate_chamber_connections(self, chamber_id: int, connections: Any) -> None:
        """Validate chamber connections.
        
        Args:
            chamber_id: ID of the chamber being validated
            connections: Connections data to validate
            
        Raises:
            GameException: If connections are invalid
        """
        if not isinstance(connections, dict):
            raise GameException(f"Chamber {chamber_id} connections must be a dictionary")
        
        for direction, target_id in connections.items():
            if not isinstance(direction, str) or direction.lower() not in self.valid_directions:
                raise GameException(f"Chamber {chamber_id} invalid direction: {direction}")
            
            if not isinstance(target_id, int) or target_id < 1:
                raise GameException(f"Chamber {chamber_id} connection target must be a positive integer: {target_id}")
    
    def _validate_connections(self, chambers: Dict[str, Any], chamber_ids: Set[int]) -> None:
        """Validate that all connections reference existing chambers.
        
        Args:
            chambers: Dictionary of chamber data
            chamber_ids: Set of valid chamber IDs
            
        Raises:
            GameException: If connections reference non-existent chambers
        """
        for chamber_id_str, chamber_data in chambers.items():
            chamber_id = int(chamber_id_str)
            connections = chamber_data.get("connections", {})
            
            for direction, target_id in connections.items():
                if target_id not in chamber_ids:
                    raise GameException(
                        f"Chamber {chamber_id} connects to non-existent chamber {target_id} via {direction}"
                    )
    
    def _validate_starting_chamber(self, config_data: Dict[str, Any], chamber_ids: Set[int]) -> None:
        """Validate starting chamber specification.
        
        Args:
            config_data: Complete configuration data
            chamber_ids: Set of valid chamber IDs
            
        Raises:
            GameException: If starting chamber is invalid
        """
        starting_chamber = config_data.get("starting_chamber", 1)
        
        if not isinstance(starting_chamber, int):
            raise GameException("starting_chamber must be an integer")
        
        if starting_chamber not in chamber_ids:
            raise GameException(f"starting_chamber {starting_chamber} does not exist")
    
    def _validate_connectivity(self, chambers: Dict[str, Any], chamber_ids: Set[int]) -> None:
        """Validate that all chambers are reachable from the starting chamber.
        
        Args:
            chambers: Dictionary of chamber data
            chamber_ids: Set of valid chamber IDs
            
        Raises:
            GameException: If some chambers are unreachable
        """
        # Build adjacency list
        adjacency = {chamber_id: [] for chamber_id in chamber_ids}
        
        for chamber_id_str, chamber_data in chambers.items():
            chamber_id = int(chamber_id_str)
            connections = chamber_data.get("connections", {})
            
            for direction, target_id in connections.items():
                adjacency[chamber_id].append(target_id)
        
        # Find starting chamber
        starting_chamber = 1  # Default
        for chamber_id_str in chambers.keys():
            # Use the first chamber as starting if not specified
            starting_chamber = int(chamber_id_str)
            break
        
        # BFS to find reachable chambers
        visited = set()
        queue = [starting_chamber]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            
            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    queue.append(neighbor)
        
        # Check for unreachable chambers
        unreachable = chamber_ids - visited
        if unreachable:
            raise GameException(f"Unreachable chambers detected: {sorted(unreachable)}")


class LabyrinthConfigLoader:
    """Loads and manages labyrinth configuration files."""
    
    def __init__(self):
        """Initialize the config loader."""
        self.validator = LabyrinthConfigValidator()
    
    def load_from_file(self, config_file_path: str) -> Dict[str, Any]:
        """Load configuration from a JSON file.
        
        Args:
            config_file_path: Path to the configuration file
            
        Returns:
            Validated configuration dictionary
            
        Raises:
            GameException: If file cannot be loaded or configuration is invalid
        """
        if not os.path.exists(config_file_path):
            raise GameException(f"Configuration file not found: {config_file_path}")
        
        try:
            with open(config_file_path, 'r', encoding='utf-8') as file:
                config_data = json.load(file)
        except json.JSONDecodeError as e:
            raise GameException(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise GameException(f"Error reading configuration file: {e}")
        
        # Validate the configuration
        self.validator.validate_config(config_data)
        
        return config_data
    
    def save_to_file(self, config_data: Dict[str, Any], config_file_path: str) -> None:
        """Save configuration to a JSON file.
        
        Args:
            config_data: Configuration dictionary to save
            config_file_path: Path where to save the configuration
            
        Raises:
            GameException: If configuration is invalid or cannot be saved
        """
        # Validate before saving
        self.validator.validate_config(config_data)
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
            
            with open(config_file_path, 'w', encoding='utf-8') as file:
                json.dump(config_data, file, indent=2, ensure_ascii=False)
        except Exception as e:
            raise GameException(f"Error saving configuration file: {e}")
    
    def create_default_config(self) -> Dict[str, Any]:
        """Create a default labyrinth configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "starting_chamber": 1,
            "chambers": {
                "1": {
                    "name": "Entrance Hall",
                    "description": "A dimly lit stone chamber with ancient carvings on the walls. The air is thick with mystery and the scent of ages past.",
                    "connections": {"north": 2},
                    "challenge_type": "riddle"
                },
                "2": {
                    "name": "Crystal Cavern",
                    "description": "A sparkling chamber filled with glowing crystals that cast dancing shadows on the walls. The crystals hum with magical energy.",
                    "connections": {"south": 1, "east": 3},
                    "challenge_type": "puzzle"
                },
                "3": {
                    "name": "Exit Chamber",
                    "description": "The final chamber with a heavy wooden door leading outside. Sunlight streams through cracks in the door, promising freedom.",
                    "connections": {"west": 2},
                    "challenge_type": "skill"
                }
            }
        }
    
    def create_full_labyrinth_config(self) -> Dict[str, Any]:
        """Create a full 13-chamber labyrinth configuration.
        
        Returns:
            Full labyrinth configuration dictionary
        """
        return {
            "starting_chamber": 1,
            "chambers": {
                "1": {
                    "name": "Entrance Hall",
                    "description": "A grand stone chamber with towering pillars and ancient murals depicting forgotten legends. Torches flicker in iron sconces, casting dancing shadows.",
                    "connections": {"north": 2, "east": 4},
                    "challenge_type": "riddle"
                },
                "2": {
                    "name": "Hall of Echoes",
                    "description": "A long corridor where every sound reverberates endlessly. The walls are lined with mysterious symbols that seem to shift in the torchlight.",
                    "connections": {"south": 1, "north": 3, "west": 5},
                    "challenge_type": "memory"
                },
                "3": {
                    "name": "Crystal Sanctum",
                    "description": "A breathtaking chamber filled with massive crystals that pulse with inner light. The air shimmers with magical energy.",
                    "connections": {"south": 2, "east": 6},
                    "challenge_type": "puzzle"
                },
                "4": {
                    "name": "Guardian's Chamber",
                    "description": "A circular room with weapon racks along the walls and a raised platform in the center. Ancient armor stands sentinel in the corners.",
                    "connections": {"west": 1, "north": 7},
                    "challenge_type": "combat"
                },
                "5": {
                    "name": "Whispering Gallery",
                    "description": "A curved chamber where voices from the past seem to whisper secrets. Strange acoustic properties make every sound carry in unexpected ways.",
                    "connections": {"east": 2, "north": 8},
                    "challenge_type": "riddle"
                },
                "6": {
                    "name": "Prism Chamber",
                    "description": "Light refracts through countless crystal prisms, creating a dazzling display of colors. The patterns seem to hold hidden meanings.",
                    "connections": {"west": 3, "south": 9},
                    "challenge_type": "puzzle"
                },
                "7": {
                    "name": "Trial of Strength",
                    "description": "A training ground with obstacles and challenges designed to test physical prowess. Ancient training equipment lines the walls.",
                    "connections": {"south": 4, "west": 10},
                    "challenge_type": "skill"
                },
                "8": {
                    "name": "Meditation Chamber",
                    "description": "A serene room with smooth stone floors and walls carved with peaceful imagery. The atmosphere promotes deep contemplation.",
                    "connections": {"south": 5, "east": 11},
                    "challenge_type": "memory"
                },
                "9": {
                    "name": "Maze of Mirrors",
                    "description": "A confusing chamber filled with mirrors that reflect not just images, but possibilities. Reality becomes uncertain here.",
                    "connections": {"north": 6, "west": 12},
                    "challenge_type": "puzzle"
                },
                "10": {
                    "name": "Arena of Champions",
                    "description": "A grand arena with tiered seating carved into the stone walls. The floor bears the marks of countless battles.",
                    "connections": {"east": 7},
                    "challenge_type": "combat"
                },
                "11": {
                    "name": "Library of Secrets",
                    "description": "Ancient tomes and scrolls line the walls of this scholarly chamber. The knowledge of ages waits to be discovered.",
                    "connections": {"west": 8, "south": 12},
                    "challenge_type": "riddle"
                },
                "12": {
                    "name": "Chamber of Trials",
                    "description": "A testing ground where multiple challenges await. The room adapts to test the skills of those who enter.",
                    "connections": {"north": 11, "east": 9, "south": 13},
                    "challenge_type": "skill"
                },
                "13": {
                    "name": "Throne of Victory",
                    "description": "The final chamber containing an ancient throne. Those who reach here have proven themselves worthy of the labyrinth's secrets.",
                    "connections": {"north": 12},
                    "challenge_type": "memory"
                }
            }
        }