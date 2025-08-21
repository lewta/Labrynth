"""Labyrinth generation and randomization utilities."""

import random
import math
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from src.utils.exceptions import GameException


class LabyrinthLayout(Enum):
    """Different labyrinth layout patterns."""
    LINEAR = "linear"           # Chambers connected in a line
    CIRCULAR = "circular"       # Chambers arranged in a circle
    TREE = "tree"              # Tree-like branching structure
    GRID = "grid"              # Grid-based layout
    RANDOM = "random"          # Completely random connections
    HYBRID = "hybrid"          # Mix of different patterns


@dataclass
class GenerationConfig:
    """Configuration for labyrinth generation."""
    chamber_count: int = 13
    layout: LabyrinthLayout = LabyrinthLayout.HYBRID
    connectivity: float = 0.3  # How connected the labyrinth is (0.0 to 1.0)
    ensure_solvable: bool = True
    min_path_length: int = 5   # Minimum path from start to end
    max_dead_ends: int = 3     # Maximum number of dead-end chambers
    seed: Optional[int] = None
    
    def __post_init__(self):
        if self.chamber_count < 3:
            raise GameException("Chamber count must be at least 3")
        if not 0.0 <= self.connectivity <= 1.0:
            raise GameException("Connectivity must be between 0.0 and 1.0")
        if self.min_path_length < 2:
            raise GameException("Minimum path length must be at least 2")


class LabyrinthGenerator:
    """Generates randomized but solvable labyrinth configurations."""
    
    def __init__(self, config: GenerationConfig = None):
        """Initialize the generator.
        
        Args:
            config: Generation configuration
        """
        self.config = config or GenerationConfig()
        self._random = random.Random()
        if self.config.seed is not None:
            self._random.seed(self.config.seed)
        
        # Direction mappings for different layouts
        self.directions = ["north", "south", "east", "west"]
        self.opposite_directions = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east"
        }
    
    def generate_labyrinth(self) -> Dict[str, Any]:
        """Generate a complete labyrinth configuration.
        
        Returns:
            Dictionary containing labyrinth configuration
        """
        # Generate chamber layout based on configuration
        connections = self._generate_layout()
        
        # Ensure solvability if required
        if self.config.ensure_solvable:
            connections = self._ensure_solvability(connections)
        
        # Add additional connections based on connectivity setting
        connections = self._add_connectivity(connections)
        
        # Validate the generated labyrinth
        self._validate_generated_labyrinth(connections)
        
        # Create chamber descriptions and challenge assignments
        chambers = self._create_chamber_data(connections)
        
        return {
            "starting_chamber": 1,
            "chambers": chambers,
            "generation_info": {
                "layout": self.config.layout.value,
                "connectivity": self.config.connectivity,
                "chamber_count": self.config.chamber_count,
                "seed": self.config.seed
            }
        }
    
    def _generate_layout(self) -> Dict[int, Dict[str, int]]:
        """Generate the basic layout structure.
        
        Returns:
            Dictionary mapping chamber IDs to their connections
        """
        if self.config.layout == LabyrinthLayout.LINEAR:
            return self._generate_linear_layout()
        elif self.config.layout == LabyrinthLayout.CIRCULAR:
            return self._generate_circular_layout()
        elif self.config.layout == LabyrinthLayout.TREE:
            return self._generate_tree_layout()
        elif self.config.layout == LabyrinthLayout.GRID:
            return self._generate_grid_layout()
        elif self.config.layout == LabyrinthLayout.RANDOM:
            return self._generate_random_layout()
        else:  # HYBRID
            return self._generate_hybrid_layout()
    
    def _generate_linear_layout(self) -> Dict[int, Dict[str, int]]:
        """Generate a linear chain of chambers."""
        connections = {}
        
        for i in range(1, self.config.chamber_count + 1):
            connections[i] = {}
            
            if i > 1:
                connections[i]["west"] = i - 1
            if i < self.config.chamber_count:
                connections[i]["east"] = i + 1
        
        return connections
    
    def _generate_circular_layout(self) -> Dict[int, Dict[str, int]]:
        """Generate a circular arrangement of chambers."""
        connections = {}
        
        for i in range(1, self.config.chamber_count + 1):
            connections[i] = {}
            
            # Connect to previous chamber
            prev_chamber = i - 1 if i > 1 else self.config.chamber_count
            connections[i]["west"] = prev_chamber
            
            # Connect to next chamber
            next_chamber = i + 1 if i < self.config.chamber_count else 1
            connections[i]["east"] = next_chamber
        
        return connections
    
    def _generate_tree_layout(self) -> Dict[int, Dict[str, int]]:
        """Generate a tree-like branching structure."""
        connections = {i: {} for i in range(1, self.config.chamber_count + 1)}
        
        # Start with chamber 1 as root
        unconnected = set(range(2, self.config.chamber_count + 1))
        connected = {1}
        
        while unconnected:
            # Pick a random connected chamber to branch from
            parent = self._random.choice(list(connected))
            
            # Pick a random unconnected chamber to connect
            child = self._random.choice(list(unconnected))
            
            # Choose a random direction for the connection
            available_directions_parent = [d for d in self.directions 
                                         if d not in connections[parent]]
            available_directions_child = [d for d in self.directions 
                                        if d not in connections[child]]
            
            if available_directions_parent and available_directions_child:
                direction = self._random.choice(available_directions_parent)
                opposite = self.opposite_directions[direction]
                
                # Make sure the opposite direction is available on the child
                if opposite in available_directions_child:
                    # Create bidirectional connection
                    connections[parent][direction] = child
                    connections[child][opposite] = parent
                    
                    connected.add(child)
                    unconnected.remove(child)
                else:
                    # Try a different direction
                    continue
            else:
                # If no available directions, we need to handle this case
                # This shouldn't happen with proper chamber counts, but let's be safe
                if len(connected) == 1:
                    # Only one connected chamber, force a connection
                    direction = self.directions[0]  # Use first available direction
                    opposite = self.opposite_directions[direction]
                    
                    connections[parent][direction] = child
                    connections[child][opposite] = parent
                    
                    connected.add(child)
                    unconnected.remove(child)
                else:
                    # Try another parent
                    continue
        
        return connections
    
    def _generate_grid_layout(self) -> Dict[int, Dict[str, int]]:
        """Generate a grid-based layout."""
        # Calculate grid dimensions
        grid_size = math.ceil(math.sqrt(self.config.chamber_count))
        connections = {}
        
        # Create grid positions
        positions = {}
        chamber_id = 1
        
        for row in range(grid_size):
            for col in range(grid_size):
                if chamber_id <= self.config.chamber_count:
                    positions[chamber_id] = (row, col)
                    connections[chamber_id] = {}
                    chamber_id += 1
        
        # Connect adjacent chambers in the grid
        for chamber_id, (row, col) in positions.items():
            # North connection
            north_pos = (row - 1, col)
            north_chamber = self._find_chamber_at_position(positions, north_pos)
            if north_chamber:
                connections[chamber_id]["north"] = north_chamber
            
            # South connection
            south_pos = (row + 1, col)
            south_chamber = self._find_chamber_at_position(positions, south_pos)
            if south_chamber:
                connections[chamber_id]["south"] = south_chamber
            
            # East connection
            east_pos = (row, col + 1)
            east_chamber = self._find_chamber_at_position(positions, east_pos)
            if east_chamber:
                connections[chamber_id]["east"] = east_chamber
            
            # West connection
            west_pos = (row, col - 1)
            west_chamber = self._find_chamber_at_position(positions, west_pos)
            if west_chamber:
                connections[chamber_id]["west"] = west_chamber
        
        return connections
    
    def _find_chamber_at_position(self, positions: Dict[int, Tuple[int, int]], 
                                 target_pos: Tuple[int, int]) -> Optional[int]:
        """Find chamber at a specific grid position."""
        for chamber_id, pos in positions.items():
            if pos == target_pos:
                return chamber_id
        return None
    
    def _generate_random_layout(self) -> Dict[int, Dict[str, int]]:
        """Generate completely random connections."""
        connections = {i: {} for i in range(1, self.config.chamber_count + 1)}
        
        # Start with a minimal spanning tree to ensure connectivity
        unconnected = set(range(2, self.config.chamber_count + 1))
        connected = {1}
        
        # Create minimal connections
        while unconnected:
            from_chamber = self._random.choice(list(connected))
            to_chamber = self._random.choice(list(unconnected))
            
            # Find available directions on both chambers
            available_directions_from = [d for d in self.directions 
                                       if d not in connections[from_chamber]]
            available_directions_to = [d for d in self.directions 
                                     if d not in connections[to_chamber]]
            
            if available_directions_from and available_directions_to:
                direction = self._random.choice(available_directions_from)
                opposite = self.opposite_directions[direction]
                
                # Make sure the opposite direction is available on the target
                if opposite in available_directions_to:
                    # Create bidirectional connection
                    connections[from_chamber][direction] = to_chamber
                    connections[to_chamber][opposite] = from_chamber
                    
                    connected.add(to_chamber)
                    unconnected.remove(to_chamber)
                else:
                    # Try a different direction or chamber
                    continue
            else:
                # If no available directions, force a connection
                if available_directions_from:
                    direction = available_directions_from[0]
                    opposite = self.opposite_directions[direction]
                    
                    connections[from_chamber][direction] = to_chamber
                    connections[to_chamber][opposite] = from_chamber
                    
                    connected.add(to_chamber)
                    unconnected.remove(to_chamber)
                else:
                    # Try another from_chamber
                    continue
        
        return connections
    
    def _generate_hybrid_layout(self) -> Dict[int, Dict[str, int]]:
        """Generate a hybrid layout combining different patterns."""
        # Randomly choose a base layout
        base_layouts = [
            LabyrinthLayout.LINEAR,
            LabyrinthLayout.TREE,
            LabyrinthLayout.GRID
        ]
        
        base_layout = self._random.choice(base_layouts)
        
        # Temporarily change layout and generate
        original_layout = self.config.layout
        self.config.layout = base_layout
        connections = self._generate_layout()
        self.config.layout = original_layout
        
        return connections
    
    def _ensure_solvability(self, connections: Dict[int, Dict[str, int]]) -> Dict[int, Dict[str, int]]:
        """Ensure the labyrinth is solvable with appropriate path length."""
        # Find the current longest path from chamber 1
        longest_path = self._find_longest_path(connections, 1)
        
        # If path is too short, extend it
        if len(longest_path) < self.config.min_path_length:
            connections = self._extend_path(connections, longest_path)
        
        # Ensure all chambers are reachable
        reachable = self._get_reachable_chambers(connections, 1)
        unreachable = set(range(1, self.config.chamber_count + 1)) - reachable
        
        # Connect unreachable chambers
        for chamber_id in unreachable:
            connections = self._connect_chamber(connections, chamber_id, reachable)
            reachable.add(chamber_id)
        
        return connections
    
    def _find_longest_path(self, connections: Dict[int, Dict[str, int]], 
                          start: int) -> List[int]:
        """Find the longest path from the starting chamber."""
        def dfs(current: int, visited: Set[int], path: List[int]) -> List[int]:
            visited.add(current)
            path.append(current)
            
            longest = path.copy()
            
            for direction, neighbor in connections[current].items():
                if neighbor not in visited:
                    candidate_path = dfs(neighbor, visited.copy(), path.copy())
                    if len(candidate_path) > len(longest):
                        longest = candidate_path
            
            return longest
        
        return dfs(start, set(), [])
    
    def _extend_path(self, connections: Dict[int, Dict[str, int]], 
                    current_path: List[int]) -> Dict[int, Dict[str, int]]:
        """Extend the path to meet minimum length requirements."""
        while len(current_path) < self.config.min_path_length:
            # Find chambers not in the current path
            available_chambers = set(range(1, self.config.chamber_count + 1)) - set(current_path)
            
            if not available_chambers:
                break
            
            # Pick the last chamber in the path
            last_chamber = current_path[-1]
            
            # Find an available direction
            available_directions = [d for d in self.directions 
                                  if d not in connections[last_chamber]]
            
            if available_directions:
                direction = self._random.choice(available_directions)
                opposite = self.opposite_directions[direction]
                
                # Pick a chamber to connect
                new_chamber = self._random.choice(list(available_chambers))
                
                # Make sure the opposite direction is available on the new chamber
                available_directions_new = [d for d in self.directions 
                                          if d not in connections[new_chamber]]
                
                if opposite in available_directions_new:
                    # Create bidirectional connection
                    connections[last_chamber][direction] = new_chamber
                    connections[new_chamber][opposite] = last_chamber
                
                current_path.append(new_chamber)
            else:
                break
        
        return connections
    
    def _get_reachable_chambers(self, connections: Dict[int, Dict[str, int]], 
                               start: int) -> Set[int]:
        """Get all chambers reachable from the starting chamber."""
        visited = set()
        queue = [start]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            
            for direction, neighbor in connections[current].items():
                if neighbor not in visited:
                    queue.append(neighbor)
        
        return visited
    
    def _connect_chamber(self, connections: Dict[int, Dict[str, int]], 
                        chamber_id: int, reachable: Set[int]) -> Dict[int, Dict[str, int]]:
        """Connect an unreachable chamber to the reachable set."""
        # Find a reachable chamber to connect to
        target_chamber = self._random.choice(list(reachable))
        
        # Find available directions on both chambers
        available_directions_target = [d for d in self.directions 
                                     if d not in connections[target_chamber]]
        available_directions_chamber = [d for d in self.directions 
                                      if d not in connections[chamber_id]]
        
        if available_directions_target and available_directions_chamber:
            direction = self._random.choice(available_directions_target)
            opposite = self.opposite_directions[direction]
            
            # Make sure the opposite direction is available on the chamber
            if opposite in available_directions_chamber:
                # Create bidirectional connection
                connections[target_chamber][direction] = chamber_id
                connections[chamber_id][opposite] = target_chamber
        
        return connections
    
    def _add_connectivity(self, connections: Dict[int, Dict[str, int]]) -> Dict[int, Dict[str, int]]:
        """Add additional connections based on connectivity setting."""
        if self.config.connectivity <= 0.0:
            return connections
        
        # Calculate how many additional connections to add
        max_possible_connections = self.config.chamber_count * len(self.directions)
        current_connections = sum(len(conns) for conns in connections.values())
        
        additional_connections = int(
            (max_possible_connections - current_connections) * self.config.connectivity
        )
        
        # Add random connections
        for _ in range(additional_connections):
            # Pick random chambers
            chamber1 = self._random.randint(1, self.config.chamber_count)
            chamber2 = self._random.randint(1, self.config.chamber_count)
            
            if chamber1 == chamber2:
                continue
            
            # Check if they're already connected
            if any(target == chamber2 for target in connections[chamber1].values()):
                continue
            
            # Find available directions
            available_directions_1 = [d for d in self.directions 
                                    if d not in connections[chamber1]]
            available_directions_2 = [d for d in self.directions 
                                    if d not in connections[chamber2]]
            
            if available_directions_1 and available_directions_2:
                direction1 = self._random.choice(available_directions_1)
                direction2 = self.opposite_directions[direction1]
                
                if direction2 in available_directions_2:
                    # Create bidirectional connection
                    connections[chamber1][direction1] = chamber2
                    connections[chamber2][direction2] = chamber1
        
        return connections
    
    def _validate_generated_labyrinth(self, connections: Dict[int, Dict[str, int]]) -> None:
        """Validate the generated labyrinth."""
        # Check that all chambers exist
        expected_chambers = set(range(1, self.config.chamber_count + 1))
        actual_chambers = set(connections.keys())
        
        if expected_chambers != actual_chambers:
            raise GameException(f"Generated labyrinth missing chambers: {expected_chambers - actual_chambers}")
        
        # Check connectivity
        reachable = self._get_reachable_chambers(connections, 1)
        if len(reachable) != self.config.chamber_count:
            unreachable = expected_chambers - reachable
            raise GameException(f"Generated labyrinth has unreachable chambers: {unreachable}")
        
        # Check for valid connections
        for chamber_id, chamber_connections in connections.items():
            for direction, target_id in chamber_connections.items():
                if target_id not in connections:
                    raise GameException(f"Chamber {chamber_id} connects to non-existent chamber {target_id}")
                
                # Check bidirectional consistency
                opposite = self.opposite_directions[direction]
                if opposite not in connections[target_id] or connections[target_id][opposite] != chamber_id:
                    raise GameException(f"Non-bidirectional connection between {chamber_id} and {target_id}")
    
    def _create_chamber_data(self, connections: Dict[int, Dict[str, int]]) -> Dict[str, Any]:
        """Create chamber data with descriptions and challenge assignments."""
        chambers = {}
        
        # Chamber name templates
        chamber_names = [
            "Entrance Hall", "Crystal Cavern", "Shadow Corridor", "Ancient Library",
            "Guardian's Chamber", "Mystic Sanctum", "Hall of Echoes", "Prism Chamber",
            "Trial Arena", "Meditation Room", "Treasure Vault", "Throne Room",
            "Exit Portal"
        ]
        
        # Description templates
        description_templates = [
            "A {adjective} chamber with {feature}. {atmosphere}",
            "This {adjective} room contains {feature}. {atmosphere}",
            "A {adjective} space where {feature} dominates the area. {atmosphere}"
        ]
        
        adjectives = [
            "dimly lit", "sparkling", "mysterious", "ancient", "grand",
            "serene", "imposing", "ethereal", "shadowy", "luminous"
        ]
        
        features = [
            "towering stone pillars", "glowing crystals", "ancient murals",
            "mystical symbols", "ornate carvings", "magical artifacts",
            "flowing water", "floating orbs", "intricate mosaics", "golden statues"
        ]
        
        atmospheres = [
            "The air hums with magical energy.",
            "Shadows dance in the flickering light.",
            "An aura of ancient power fills the space.",
            "The atmosphere is thick with mystery.",
            "Whispers of the past echo through the chamber."
        ]
        
        # Challenge types
        challenge_types = ["riddle", "puzzle", "combat", "skill", "memory"]
        
        for chamber_id in connections.keys():
            # Select name (cycle through available names)
            name = chamber_names[(chamber_id - 1) % len(chamber_names)]
            if chamber_id > len(chamber_names):
                name += f" {chamber_id}"
            
            # Generate description
            template = self._random.choice(description_templates)
            adjective = self._random.choice(adjectives)
            feature = self._random.choice(features)
            atmosphere = self._random.choice(atmospheres)
            
            description = template.format(
                adjective=adjective,
                feature=feature,
                atmosphere=atmosphere
            )
            
            # Assign challenge type
            challenge_type = self._random.choice(challenge_types)
            
            chambers[str(chamber_id)] = {
                "name": name,
                "description": description,
                "connections": connections[chamber_id],
                "challenge_type": challenge_type
            }
        
        return chambers
    
    def generate_multiple_variants(self, count: int) -> List[Dict[str, Any]]:
        """Generate multiple labyrinth variants.
        
        Args:
            count: Number of variants to generate
            
        Returns:
            List of labyrinth configurations
        """
        variants = []
        
        for i in range(count):
            # Use different seeds for each variant
            if self.config.seed is not None:
                self._random.seed(self.config.seed + i)
            
            variant = self.generate_labyrinth()
            variant["generation_info"]["variant_number"] = i + 1
            variants.append(variant)
        
        return variants


def create_randomized_labyrinth(chamber_count: int = 13, 
                               layout: str = "hybrid",
                               connectivity: float = 0.3,
                               seed: int = None) -> Dict[str, Any]:
    """Create a randomized labyrinth configuration.
    
    Args:
        chamber_count: Number of chambers to generate
        layout: Layout pattern ('linear', 'circular', 'tree', 'grid', 'random', 'hybrid')
        connectivity: How connected the labyrinth is (0.0 to 1.0)
        seed: Random seed for reproducible generation
        
    Returns:
        Labyrinth configuration dictionary
    """
    config = GenerationConfig(
        chamber_count=chamber_count,
        layout=LabyrinthLayout(layout.lower()),
        connectivity=connectivity,
        seed=seed
    )
    
    generator = LabyrinthGenerator(config)
    return generator.generate_labyrinth()


def validate_labyrinth_solvability(config_data: Dict[str, Any]) -> bool:
    """Validate that a labyrinth configuration is solvable.
    
    Args:
        config_data: Labyrinth configuration dictionary
        
    Returns:
        True if solvable, False otherwise
    """
    try:
        chambers = config_data.get("chambers", {})
        if not chambers:
            return False
        
        starting_chamber = config_data.get("starting_chamber", 1)
        
        # Build adjacency list
        adjacency = {}
        for chamber_id_str, chamber_data in chambers.items():
            chamber_id = int(chamber_id_str)
            adjacency[chamber_id] = []
            
            connections = chamber_data.get("connections", {})
            for direction, target_id in connections.items():
                adjacency[chamber_id].append(target_id)
        
        # BFS to check reachability
        visited = set()
        queue = [starting_chamber]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            
            for neighbor in adjacency.get(current, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        
        # Check if all chambers are reachable
        expected_chambers = set(int(cid) for cid in chambers.keys())
        return visited == expected_chambers
        
    except Exception:
        return False