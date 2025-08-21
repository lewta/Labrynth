"""Progress tracking system for the Labyrinth Adventure Game."""

from typing import Set, Dict, Any
from src.utils.exceptions import GameException


class ProgressTracker:
    """Tracks player progress through the game."""
    
    def __init__(self):
        """Initialize progress tracker."""
        self.completed_chambers: Set[int] = set()
        self.visited_chambers: Set[int] = set()
        self.discovered_connections: Dict[int, Dict[str, int]] = {}  # chamber_id -> {direction: target_id}
        self.challenges_completed: int = 0
        self.total_score: int = 0
        self.game_start_time: float = 0.0
        self.game_end_time: float = 0.0
    
    def complete_chamber(self, chamber_id: int) -> None:
        """Mark a chamber as completed.
        
        Args:
            chamber_id: ID of the chamber to mark as completed
            
        Raises:
            GameException: If chamber_id is invalid
        """
        if not isinstance(chamber_id, int) or chamber_id < 1:
            raise GameException("Chamber ID must be a positive integer")
        
        self.completed_chambers.add(chamber_id)
        self.visited_chambers.add(chamber_id)
        self.challenges_completed += 1
    
    def visit_chamber(self, chamber_id: int, connections: Dict[str, int] = None) -> None:
        """Mark a chamber as visited and record its connections.
        
        Args:
            chamber_id: ID of the chamber to mark as visited
            connections: Dictionary of connections from this chamber
            
        Raises:
            GameException: If chamber_id is invalid
        """
        if not isinstance(chamber_id, int) or chamber_id < 1:
            raise GameException("Chamber ID must be a positive integer")
        
        self.visited_chambers.add(chamber_id)
        
        # Record discovered connections
        if connections:
            self.discovered_connections[chamber_id] = connections.copy()
    
    def discover_connection(self, from_chamber: int, direction: str, to_chamber: int) -> None:
        """Record a discovered connection between chambers.
        
        Args:
            from_chamber: ID of the source chamber
            direction: Direction of the connection (north, south, east, west)
            to_chamber: ID of the target chamber
            
        Raises:
            GameException: If parameters are invalid
        """
        if not isinstance(from_chamber, int) or from_chamber < 1:
            raise GameException("From chamber ID must be a positive integer")
        
        if not isinstance(to_chamber, int) or to_chamber < 1:
            raise GameException("To chamber ID must be a positive integer")
        
        if not isinstance(direction, str) or not direction.strip():
            raise GameException("Direction must be a non-empty string")
        
        direction = direction.lower().strip()
        valid_directions = {'north', 'south', 'east', 'west'}
        if direction not in valid_directions:
            raise GameException(f"Direction must be one of: {', '.join(valid_directions)}")
        
        if from_chamber not in self.discovered_connections:
            self.discovered_connections[from_chamber] = {}
        
        self.discovered_connections[from_chamber][direction] = to_chamber
    
    def get_discovered_connections(self) -> Dict[int, Dict[str, int]]:
        """Get all discovered connections.
        
        Returns:
            Dict[int, Dict[str, int]]: Dictionary mapping chamber IDs to their connections
        """
        # Return a deep copy to prevent modification of internal data
        return {chamber_id: connections.copy() 
                for chamber_id, connections in self.discovered_connections.items()}
    
    def is_chamber_completed(self, chamber_id: int) -> bool:
        """Check if a chamber has been completed.
        
        Args:
            chamber_id: ID of the chamber to check
            
        Returns:
            bool: True if chamber is completed
        """
        return chamber_id in self.completed_chambers
    
    def is_chamber_visited(self, chamber_id: int) -> bool:
        """Check if a chamber has been visited.
        
        Args:
            chamber_id: ID of the chamber to check
            
        Returns:
            bool: True if chamber has been visited
        """
        return chamber_id in self.visited_chambers
    
    def get_completion_percentage(self, total_chambers: int = 13) -> float:
        """Get completion percentage.
        
        Args:
            total_chambers: Total number of chambers in the game
            
        Returns:
            float: Completion percentage (0.0 to 1.0)
        """
        if total_chambers <= 0:
            return 0.0
        
        return len(self.completed_chambers) / total_chambers
    
    def add_score(self, points: int) -> None:
        """Add points to the total score.
        
        Args:
            points: Points to add
            
        Raises:
            GameException: If points is invalid
        """
        if not isinstance(points, int):
            raise GameException("Points must be an integer")
        
        self.total_score += points
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of current progress.
        
        Returns:
            Dict[str, Any]: Progress summary
        """
        return {
            'completed_chambers': len(self.completed_chambers),
            'visited_chambers': len(self.visited_chambers),
            'challenges_completed': self.challenges_completed,
            'total_score': self.total_score,
            'completion_percentage': self.get_completion_percentage(),
            'completed_chamber_ids': sorted(list(self.completed_chambers)),
            'visited_chamber_ids': sorted(list(self.visited_chambers))
        }
    
    def get_map_data(self) -> Dict[int, Dict[str, Any]]:
        """Get map data for rendering.
        
        Returns:
            Dictionary of chamber data for map rendering
        """
        map_data = {}
        
        for chamber_id in self.visited_chambers:
            map_data[chamber_id] = {
                'chamber_id': chamber_id,
                'visited': True,
                'completed': chamber_id in self.completed_chambers,
                'connections': self.discovered_connections.get(chamber_id, {})
            }
        
        return map_data
    
    def reset(self) -> None:
        """Reset all progress."""
        self.completed_chambers.clear()
        self.visited_chambers.clear()
        self.discovered_connections.clear()
        self.challenges_completed = 0
        self.total_score = 0
        self.game_start_time = 0.0
        self.game_end_time = 0.0
    
    def __str__(self) -> str:
        """Return string representation of progress."""
        summary = self.get_progress_summary()
        return (f"Progress: {summary['completed_chambers']}/13 chambers completed, "
                f"{summary['challenges_completed']} challenges, "
                f"Score: {summary['total_score']}")