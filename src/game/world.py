"""World management classes for the Labyrinth Adventure Game."""

import json
from typing import Dict, List, Optional, Set, Any
from src.utils.exceptions import GameException
from src.utils.data_models import Item
from src.utils.config import LabyrinthConfigLoader
from src.utils.labyrinth_generator import LabyrinthGenerator, GenerationConfig, create_randomized_labyrinth


class Chamber:
    """Represents a chamber in the labyrinth with connections and challenges."""
    
    def __init__(self, chamber_id: int, name: str, description: str):
        """Initialize a chamber with basic properties.
        
        Args:
            chamber_id: Unique identifier for the chamber
            name: Display name of the chamber
            description: Detailed description of the chamber
        """
        self.id = chamber_id
        self.name = name
        self.description = description
        self.challenge = None
        self.completed = False
        self.connections: Dict[str, int] = {}
        self.items: List[Item] = []
        
        # Validate inputs
        self._validate_initialization()
    
    def _validate_initialization(self) -> None:
        """Validate chamber initialization parameters."""
        if not isinstance(self.id, int) or self.id < 1:
            raise GameException("Chamber ID must be a positive integer")
        
        if not self.name or not isinstance(self.name, str):
            raise GameException("Chamber name must be a non-empty string")
        
        if not self.description or not isinstance(self.description, str):
            raise GameException("Chamber description must be a non-empty string")
    
    def get_description(self) -> str:
        """Get the full description of the chamber including status."""
        base_description = f"{self.name}\n\n{self.description}"
        
        if self.completed:
            base_description += "\n\n[This chamber has been completed.]"
        
        if self.items:
            item_names = [item.name for item in self.items]
            base_description += f"\n\nItems here: {', '.join(item_names)}"
        
        return base_description
    
    def get_exits(self) -> List[str]:
        """Get a list of available exit directions."""
        return list(self.connections.keys())
    
    def add_connection(self, direction: str, target_chamber_id: int) -> None:
        """Add a connection to another chamber.
        
        Args:
            direction: Direction name (north, south, east, west, etc.)
            target_chamber_id: ID of the target chamber
        """
        if not isinstance(direction, str) or not direction.strip():
            raise GameException("Direction must be a non-empty string")
        
        if not isinstance(target_chamber_id, int) or target_chamber_id < 1:
            raise GameException("Target chamber ID must be a positive integer")
        
        direction = direction.lower().strip()
        self.connections[direction] = target_chamber_id
    
    def remove_connection(self, direction: str) -> bool:
        """Remove a connection in the specified direction.
        
        Args:
            direction: Direction to remove
            
        Returns:
            True if connection was removed, False if it didn't exist
        """
        if not isinstance(direction, str):
            raise GameException("Direction must be a string")
        
        direction = direction.lower().strip()
        if direction in self.connections:
            del self.connections[direction]
            return True
        return False
    
    def get_connection(self, direction: str) -> Optional[int]:
        """Get the chamber ID connected in the specified direction.
        
        Args:
            direction: Direction to check
            
        Returns:
            Chamber ID if connection exists, None otherwise
        """
        if not isinstance(direction, str):
            return None
        
        direction = direction.lower().strip()
        return self.connections.get(direction)
    
    def has_connection(self, direction: str) -> bool:
        """Check if there's a connection in the specified direction.
        
        Args:
            direction: Direction to check
            
        Returns:
            True if connection exists, False otherwise
        """
        if not isinstance(direction, str):
            return False
        
        direction = direction.lower().strip()
        return direction in self.connections
    
    def set_challenge(self, challenge) -> None:
        """Set the challenge for this chamber.
        
        Args:
            challenge: Challenge instance (type checking done by caller)
        """
        self.challenge = challenge
    
    def complete_challenge(self) -> bool:
        """Mark the chamber's challenge as completed.
        
        Returns:
            True if challenge was completed, False if no challenge exists
        """
        if self.challenge is None:
            return False
        
        self.completed = True
        return True
    
    def add_item(self, item: Item) -> None:
        """Add an item to this chamber.
        
        Args:
            item: Item to add to the chamber
        """
        if not isinstance(item, Item):
            raise GameException("Item must be an Item instance")
        
        self.items.append(item)
    
    def remove_item(self, item_name: str) -> Optional[Item]:
        """Remove and return an item from the chamber by name.
        
        Args:
            item_name: Name of the item to remove
            
        Returns:
            The removed item if found, None otherwise
        """
        if not isinstance(item_name, str):
            return None
        
        for i, item in enumerate(self.items):
            if item.name == item_name:
                return self.items.pop(i)
        return None
    
    def has_item(self, item_name: str) -> bool:
        """Check if the chamber contains an item with the given name.
        
        Args:
            item_name: Name of the item to check for
            
        Returns:
            True if item exists, False otherwise
        """
        if not isinstance(item_name, str):
            return False
        
        return any(item.name == item_name for item in self.items)
    
    def get_items(self) -> List[Item]:
        """Get a copy of all items in the chamber.
        
        Returns:
            List of items in the chamber
        """
        return self.items.copy()
    
    def is_completed(self) -> bool:
        """Check if the chamber's challenge has been completed.
        
        Returns:
            True if completed, False otherwise
        """
        return self.completed
    
    def reset(self) -> None:
        """Reset the chamber to its initial state (uncompleted)."""
        self.completed = False
    
    def get_chamber_info(self) -> Dict[str, any]:
        """Get comprehensive information about the chamber.
        
        Returns:
            Dictionary containing chamber information
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'completed': self.completed,
            'exits': self.get_exits(),
            'items': [item.name for item in self.items],
            'has_challenge': self.challenge is not None
        }
    
    def __str__(self) -> str:
        """String representation of the chamber."""
        return f"Chamber {self.id}: {self.name}"
    
    def __repr__(self) -> str:
        """Detailed string representation of the chamber."""
        return f"Chamber(id={self.id}, name='{self.name}', completed={self.completed}, exits={self.get_exits()})"


class WorldManager:
    """Manages the labyrinth world, chambers, and navigation."""
    
    def __init__(self):
        """Initialize the world manager."""
        self.chambers: Dict[int, Chamber] = {}
        self.connections: Dict[int, Dict[str, int]] = {}
        self.current_chamber_id: int = 1
        self.starting_chamber_id: int = 1
        
    def initialize_labyrinth(self, config_data: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the labyrinth from configuration data.
        
        Args:
            config_data: Optional configuration dictionary. If None, creates a default labyrinth.
        """
        if config_data is None:
            self._create_default_labyrinth()
        else:
            self._load_from_config(config_data)
        
        # Store generation info if available
        self._generation_info = config_data.get('generation_info') if config_data else None
        
        # Validate the labyrinth after initialization
        self._validate_labyrinth()
    
    def _create_default_labyrinth(self) -> None:
        """Create a default labyrinth by loading from the full configuration."""
        try:
            # Try to load the full labyrinth configuration
            config_loader = LabyrinthConfigLoader()
            config_data = config_loader.load_from_file("config/full_labyrinth.json")
            self._load_from_config(config_data)
        except Exception:
            # Fallback to a simple 3-chamber labyrinth if full config fails
            chamber1 = Chamber(1, "Entrance Hall", "A dimly lit stone chamber with ancient carvings on the walls.")
            chamber2 = Chamber(2, "Crystal Cavern", "A sparkling chamber filled with glowing crystals.")
            chamber3 = Chamber(3, "Exit Chamber", "The final chamber with a heavy wooden door leading outside.")
            
            # Add chambers
            self.add_chamber(chamber1)
            self.add_chamber(chamber2)
            self.add_chamber(chamber3)
            
            # Connect chambers
            self.add_connection(1, "north", 2)
            self.add_connection(2, "south", 1)
            self.add_connection(2, "east", 3)
            self.add_connection(3, "west", 2)
            
            # Add simple challenges to fallback chambers
            try:
                from src.challenges.factory import ChallengeFactory
                chamber1.set_challenge(ChallengeFactory.create_challenge("riddle", 3))
                chamber2.set_challenge(ChallengeFactory.create_challenge("puzzle", 4))
                chamber3.set_challenge(ChallengeFactory.create_challenge("skill", 5))
            except Exception:
                # If challenge creation fails, chambers will just have no challenges
                pass
        
        # Create connections
        self.add_connection(1, "north", 2)
        self.add_connection(2, "south", 1)
        self.add_connection(2, "east", 3)
        self.add_connection(3, "west", 2)
    
    def _load_from_config(self, config_data: Dict[str, Any]) -> None:
        """Load labyrinth from configuration data.
        
        Args:
            config_data: Configuration dictionary containing chambers and connections
        """
        if not isinstance(config_data, dict):
            raise GameException("Configuration data must be a dictionary")
        
        chambers_config = config_data.get("chambers", {})
        if not chambers_config:
            raise GameException("Configuration must contain chambers data")
        
        # First pass: Create all chambers
        for chamber_id_str, chamber_data in chambers_config.items():
            try:
                chamber_id = int(chamber_id_str)
            except ValueError:
                raise GameException(f"Invalid chamber ID: {chamber_id_str}")
            
            if not isinstance(chamber_data, dict):
                raise GameException(f"Chamber {chamber_id} data must be a dictionary")
            
            name = chamber_data.get("name", f"Chamber {chamber_id}")
            description = chamber_data.get("description", "An empty chamber.")
            
            chamber = Chamber(chamber_id, name, description)
            self.add_chamber(chamber)
        
        # Second pass: Add connections and challenges after all chambers exist
        for chamber_id_str, chamber_data in chambers_config.items():
            chamber_id = int(chamber_id_str)
            
            # Add connections
            connections = chamber_data.get("connections", {})
            for direction, target_id in connections.items():
                if not isinstance(target_id, int):
                    raise GameException(f"Connection target must be an integer: {target_id}")
                self.add_connection(chamber_id, direction, target_id)
            
            # Create and assign challenge if specified
            challenge_type = chamber_data.get("challenge_type")
            if challenge_type:
                try:
                    from src.challenges.factory import ChallengeFactory
                    # Create challenge with moderate difficulty (can be randomized)
                    difficulty = chamber_data.get("difficulty", 5)
                    challenge = ChallengeFactory.create_challenge(challenge_type, difficulty)
                    chamber = self.get_chamber(chamber_id)
                    if chamber:
                        chamber.set_challenge(challenge)
                except Exception as e:
                    # Log warning but don't fail - chamber can exist without challenge
                    print(f"Warning: Could not create challenge for chamber {chamber_id}: {e}")
        
        # Set starting chamber if specified
        starting_chamber = config_data.get("starting_chamber", 1)
        if starting_chamber not in self.chambers:
            raise GameException(f"Starting chamber {starting_chamber} does not exist")
        self.starting_chamber_id = starting_chamber
        self.current_chamber_id = starting_chamber
    
    def _validate_labyrinth(self) -> None:
        """Validate that the labyrinth is properly connected and solvable."""
        if not self.chambers:
            raise GameException("Labyrinth must contain at least one chamber")
        
        if self.starting_chamber_id not in self.chambers:
            raise GameException(f"Starting chamber {self.starting_chamber_id} does not exist")
        
        # Check that all chambers are reachable from the starting chamber
        reachable = self._get_reachable_chambers(self.starting_chamber_id)
        unreachable = set(self.chambers.keys()) - reachable
        
        if unreachable:
            raise GameException(f"Unreachable chambers detected: {unreachable}")
        
        # Validate bidirectional connections
        self._validate_bidirectional_connections()
    
    def _get_reachable_chambers(self, start_chamber_id: int) -> Set[int]:
        """Get all chambers reachable from the starting chamber using BFS.
        
        Args:
            start_chamber_id: ID of the starting chamber
            
        Returns:
            Set of reachable chamber IDs
        """
        visited = set()
        queue = [start_chamber_id]
        
        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            # Add all connected chambers to the queue
            if current_id in self.chambers:
                for direction, target_id in self.chambers[current_id].connections.items():
                    if target_id not in visited:
                        queue.append(target_id)
        
        return visited
    
    def _validate_bidirectional_connections(self) -> None:
        """Validate that all connections reference existing chambers."""
        for chamber_id, chamber in self.chambers.items():
            for direction, target_id in chamber.connections.items():
                if target_id not in self.chambers:
                    raise GameException(f"Chamber {chamber_id} connects to non-existent chamber {target_id}")
    
    def add_chamber(self, chamber: Chamber) -> None:
        """Add a chamber to the world.
        
        Args:
            chamber: Chamber instance to add
        """
        if not isinstance(chamber, Chamber):
            raise GameException("Chamber must be a Chamber instance")
        
        if chamber.id in self.chambers:
            raise GameException(f"Chamber with ID {chamber.id} already exists")
        
        self.chambers[chamber.id] = chamber
    
    def remove_chamber(self, chamber_id: int) -> bool:
        """Remove a chamber from the world.
        
        Args:
            chamber_id: ID of the chamber to remove
            
        Returns:
            True if chamber was removed, False if it didn't exist
        """
        if chamber_id not in self.chambers:
            return False
        
        # Remove all connections to this chamber
        for chamber in self.chambers.values():
            connections_to_remove = []
            for direction, target_id in chamber.connections.items():
                if target_id == chamber_id:
                    connections_to_remove.append(direction)
            
            for direction in connections_to_remove:
                chamber.remove_connection(direction)
        
        # Remove the chamber
        del self.chambers[chamber_id]
        return True
    
    def get_chamber(self, chamber_id: int) -> Optional[Chamber]:
        """Get a chamber by its ID.
        
        Args:
            chamber_id: ID of the chamber to retrieve
            
        Returns:
            Chamber instance if found, None otherwise
        """
        return self.chambers.get(chamber_id)
    
    def get_current_chamber(self) -> Optional[Chamber]:
        """Get the current chamber where the player is located.
        
        Returns:
            Current chamber instance if it exists, None otherwise
        """
        return self.chambers.get(self.current_chamber_id)
    
    def get_connected_chambers(self, chamber_id: int) -> List[int]:
        """Get a list of chamber IDs connected to the specified chamber.
        
        Args:
            chamber_id: ID of the chamber to check connections for
            
        Returns:
            List of connected chamber IDs
        """
        chamber = self.chambers.get(chamber_id)
        if chamber is None:
            return []
        
        return list(chamber.connections.values())
    
    def move_player(self, direction: str) -> bool:
        """Move the player in the specified direction.
        
        Args:
            direction: Direction to move (north, south, east, west, etc.)
            
        Returns:
            True if movement was successful, False otherwise
        """
        if not isinstance(direction, str):
            return False
        
        direction = direction.lower().strip()
        current_chamber = self.chambers.get(self.current_chamber_id)
        
        if current_chamber is None:
            return False
        
        target_chamber_id = current_chamber.get_connection(direction)
        if target_chamber_id is None:
            return False
        
        if target_chamber_id not in self.chambers:
            return False
        
        self.current_chamber_id = target_chamber_id
        return True
    
    def is_valid_direction(self, chamber_id: int, direction: str) -> bool:
        """Check if a direction is valid from the specified chamber.
        
        Args:
            chamber_id: ID of the chamber to check from
            direction: Direction to validate
            
        Returns:
            True if direction is valid, False otherwise
        """
        chamber = self.chambers.get(chamber_id)
        if chamber is None:
            return False
        
        return chamber.has_connection(direction)
    
    def get_available_directions(self, chamber_id: int) -> List[str]:
        """Get all available directions from the specified chamber.
        
        Args:
            chamber_id: ID of the chamber to check
            
        Returns:
            List of available direction strings
        """
        chamber = self.chambers.get(chamber_id)
        if chamber is None:
            return []
        
        return chamber.get_exits()
    
    def add_connection(self, from_chamber_id: int, direction: str, to_chamber_id: int) -> None:
        """Add a connection between two chambers.
        
        Args:
            from_chamber_id: ID of the source chamber
            direction: Direction of the connection
            to_chamber_id: ID of the target chamber
        """
        from_chamber = self.chambers.get(from_chamber_id)
        if from_chamber is None:
            raise GameException(f"Source chamber {from_chamber_id} does not exist")
        
        if to_chamber_id not in self.chambers:
            raise GameException(f"Target chamber {to_chamber_id} does not exist")
        
        from_chamber.add_connection(direction, to_chamber_id)
    
    def remove_connection(self, from_chamber_id: int, direction: str) -> bool:
        """Remove a connection from a chamber.
        
        Args:
            from_chamber_id: ID of the source chamber
            direction: Direction of the connection to remove
            
        Returns:
            True if connection was removed, False if it didn't exist
        """
        from_chamber = self.chambers.get(from_chamber_id)
        if from_chamber is None:
            return False
        
        return from_chamber.remove_connection(direction)
    
    def reset_player_position(self) -> None:
        """Reset the player to the starting chamber."""
        self.current_chamber_id = self.starting_chamber_id
    
    def get_chamber_count(self) -> int:
        """Get the total number of chambers in the labyrinth.
        
        Returns:
            Number of chambers
        """
        return len(self.chambers)
    
    def get_all_chamber_ids(self) -> List[int]:
        """Get a list of all chamber IDs in the labyrinth.
        
        Returns:
            List of chamber IDs
        """
        return list(self.chambers.keys())
    
    def is_chamber_completed(self, chamber_id: int) -> bool:
        """Check if a chamber's challenge has been completed.
        
        Args:
            chamber_id: ID of the chamber to check
            
        Returns:
            True if completed, False otherwise
        """
        chamber = self.chambers.get(chamber_id)
        if chamber is None:
            return False
        
        return chamber.is_completed()
    
    def get_completed_chambers(self) -> List[int]:
        """Get a list of all completed chamber IDs.
        
        Returns:
            List of completed chamber IDs
        """
        return [chamber_id for chamber_id, chamber in self.chambers.items() if chamber.is_completed()]
    
    def get_world_state(self) -> Dict[str, Any]:
        """Get the current state of the world.
        
        Returns:
            Dictionary containing world state information
        """
        return {
            "current_chamber_id": self.current_chamber_id,
            "starting_chamber_id": self.starting_chamber_id,
            "total_chambers": len(self.chambers),
            "completed_chambers": self.get_completed_chambers(),
            "chamber_ids": list(self.chambers.keys())
        }
    
    def load_from_file(self, config_file_path: str) -> None:
        """Load labyrinth configuration from a JSON file.
        
        Args:
            config_file_path: Path to the configuration file
        """
        config_loader = LabyrinthConfigLoader()
        config_data = config_loader.load_from_file(config_file_path)
        self.initialize_labyrinth(config_data)
    
    def generate_random_labyrinth(self, chamber_count: int = 13, 
                                 layout: str = "hybrid",
                                 connectivity: float = 0.3,
                                 seed: int = None) -> None:
        """Generate a randomized labyrinth.
        
        Args:
            chamber_count: Number of chambers to generate
            layout: Layout pattern ('linear', 'circular', 'tree', 'grid', 'random', 'hybrid')
            connectivity: How connected the labyrinth is (0.0 to 1.0)
            seed: Random seed for reproducible generation
        """
        config_data = create_randomized_labyrinth(
            chamber_count=chamber_count,
            layout=layout,
            connectivity=connectivity,
            seed=seed
        )
        self.initialize_labyrinth(config_data)
    
    def generate_labyrinth_with_config(self, generation_config: GenerationConfig) -> None:
        """Generate a labyrinth using a detailed generation configuration.
        
        Args:
            generation_config: Detailed generation configuration
        """
        generator = LabyrinthGenerator(generation_config)
        config_data = generator.generate_labyrinth()
        self.initialize_labyrinth(config_data)
    
    def is_randomized_labyrinth(self) -> bool:
        """Check if the current labyrinth was randomly generated.
        
        Returns:
            True if labyrinth was randomly generated, False otherwise
        """
        # This would need to be tracked during initialization
        # For now, we'll check if we have generation info
        return hasattr(self, '_generation_info') and self._generation_info is not None
    
    def get_generation_info(self) -> Optional[Dict[str, Any]]:
        """Get information about how the labyrinth was generated.
        
        Returns:
            Generation information if available, None otherwise
        """
        return getattr(self, '_generation_info', None)
    
    def __str__(self) -> str:
        """String representation of the world manager."""
        return f"WorldManager({len(self.chambers)} chambers, current: {self.current_chamber_id})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the world manager."""
        return (f"WorldManager(chambers={len(self.chambers)}, "
                f"current_chamber={self.current_chamber_id}, "
                f"starting_chamber={self.starting_chamber_id})")