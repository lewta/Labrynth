"""Map rendering system for visualizing the labyrinth."""

from typing import Dict, Set, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ChamberSymbol(Enum):
    """Symbols used to represent different chamber states."""
    CURRENT = "●"      # Current player location
    VISITED = "○"      # Visited chamber
    COMPLETED = "◉"    # Completed chamber
    UNKNOWN = "?"      # Unknown/unvisited chamber
    WALL = "█"         # Wall/blocked area
    EMPTY = " "        # Empty space


class ConnectionSymbol(Enum):
    """Symbols used to represent connections between chambers."""
    HORIZONTAL = "─"   # Horizontal connection
    VERTICAL = "│"     # Vertical connection
    UNKNOWN_H = "?"    # Unknown horizontal connection
    UNKNOWN_V = "?"    # Unknown vertical connection


@dataclass
class MapPosition:
    """Represents a position on the map grid."""
    x: int
    y: int
    
    def __hash__(self):
        return hash((self.x, self.y))


@dataclass
class ChamberInfo:
    """Information about a chamber for map rendering."""
    chamber_id: int
    name: str
    visited: bool
    completed: bool
    connections: Dict[str, int]  # direction -> target_chamber_id
    position: Optional[MapPosition] = None


class MapRenderer:
    """Renders ASCII art maps of the labyrinth."""
    
    def __init__(self):
        """Initialize the map renderer."""
        self.chamber_positions: Dict[int, MapPosition] = {}
        self.grid_size = 50  # Maximum grid size
        self.center_x = self.grid_size // 2
        self.center_y = self.grid_size // 2
    
    def render_map(self, chambers: Dict[int, ChamberInfo], current_chamber_id: int) -> str:
        """Render a map of the visited chambers.
        
        Args:
            chambers: Dictionary of chamber information
            current_chamber_id: ID of the current chamber
            
        Returns:
            ASCII art representation of the map
        """
        # Calculate positions for all chambers
        self._calculate_positions(chambers, current_chamber_id)
        
        # Create the grid
        grid = self._create_grid()
        
        # Place chambers on the grid
        self._place_chambers(grid, chambers, current_chamber_id)
        
        # Draw connections
        self._draw_connections(grid, chambers)
        
        # Convert grid to string
        map_str = self._grid_to_string(grid)
        
        # Add legend and title
        return self._add_header_and_legend(map_str, chambers, current_chamber_id)
    
    def _calculate_positions(self, chambers: Dict[int, ChamberInfo], start_chamber_id: int) -> None:
        """Calculate positions for chambers using a simple layout algorithm."""
        self.chamber_positions.clear()
        
        # Start with the current chamber at the center
        self.chamber_positions[start_chamber_id] = MapPosition(self.center_x, self.center_y)
        
        # Use BFS to position connected chambers
        visited = {start_chamber_id}
        queue = [(start_chamber_id, self.center_x, self.center_y)]
        
        direction_offsets = {
            'north': (0, -2),
            'south': (0, 2),
            'east': (2, 0),
            'west': (-2, 0),
            'northeast': (2, -2),
            'northwest': (-2, -2),
            'southeast': (2, 2),
            'southwest': (-2, 2)
        }
        
        while queue:
            chamber_id, x, y = queue.pop(0)
            chamber = chambers.get(chamber_id)
            
            if not chamber or not chamber.visited:
                continue
            
            for direction, target_id in chamber.connections.items():
                if target_id in visited or target_id not in chambers:
                    continue
                
                target_chamber = chambers[target_id]
                if not target_chamber.visited:
                    continue
                
                # Calculate new position
                dx, dy = direction_offsets.get(direction, (0, 0))
                new_x, new_y = x + dx, y + dy
                
                # Ensure position is within bounds
                new_x = max(1, min(self.grid_size - 2, new_x))
                new_y = max(1, min(self.grid_size - 2, new_y))
                
                # Avoid overlapping positions
                pos = MapPosition(new_x, new_y)
                while pos in self.chamber_positions.values():
                    new_x += 1
                    if new_x >= self.grid_size - 1:
                        new_x = 1
                        new_y += 1
                    if new_y >= self.grid_size - 1:
                        break
                    pos = MapPosition(new_x, new_y)
                
                self.chamber_positions[target_id] = pos
                visited.add(target_id)
                queue.append((target_id, new_x, new_y))
    
    def _create_grid(self) -> List[List[str]]:
        """Create an empty grid for the map."""
        return [[ChamberSymbol.EMPTY.value for _ in range(self.grid_size)] 
                for _ in range(self.grid_size)]
    
    def _place_chambers(self, grid: List[List[str]], chambers: Dict[int, ChamberInfo], 
                       current_chamber_id: int) -> None:
        """Place chamber symbols on the grid."""
        for chamber_id, chamber in chambers.items():
            if not chamber.visited or chamber_id not in self.chamber_positions:
                continue
            
            pos = self.chamber_positions[chamber_id]
            
            # Determine symbol based on chamber state
            if chamber_id == current_chamber_id:
                symbol = ChamberSymbol.CURRENT.value
            elif chamber.completed:
                symbol = ChamberSymbol.COMPLETED.value
            else:
                symbol = ChamberSymbol.VISITED.value
            
            grid[pos.y][pos.x] = symbol
    
    def _draw_connections(self, grid: List[List[str]], chambers: Dict[int, ChamberInfo]) -> None:
        """Draw connections between chambers on the grid."""
        for chamber_id, chamber in chambers.items():
            if not chamber.visited or chamber_id not in self.chamber_positions:
                continue
            
            pos = self.chamber_positions[chamber_id]
            
            for direction, target_id in chamber.connections.items():
                if target_id not in self.chamber_positions:
                    continue
                
                target_pos = self.chamber_positions[target_id]
                target_chamber = chambers.get(target_id)
                
                if not target_chamber or not target_chamber.visited:
                    continue
                
                # Draw connection line
                self._draw_connection_line(grid, pos, target_pos)
    
    def _draw_connection_line(self, grid: List[List[str]], pos1: MapPosition, 
                             pos2: MapPosition) -> None:
        """Draw a connection line between two positions."""
        x1, y1 = pos1.x, pos1.y
        x2, y2 = pos2.x, pos2.y
        
        # Simple line drawing - horizontal or vertical only
        if x1 == x2:  # Vertical line
            start_y, end_y = min(y1, y2), max(y1, y2)
            for y in range(start_y + 1, end_y):
                if grid[y][x1] == ChamberSymbol.EMPTY.value:
                    grid[y][x1] = ConnectionSymbol.VERTICAL.value
        elif y1 == y2:  # Horizontal line
            start_x, end_x = min(x1, x2), max(x1, x2)
            for x in range(start_x + 1, end_x):
                if grid[y1][x] == ChamberSymbol.EMPTY.value:
                    grid[y1][x] = ConnectionSymbol.HORIZONTAL.value
        else:
            # Diagonal connection - draw L-shaped path
            # First horizontal, then vertical
            if abs(x2 - x1) > abs(y2 - y1):
                # Horizontal first
                start_x, end_x = min(x1, x2), max(x1, x2)
                for x in range(start_x + 1, end_x):
                    if grid[y1][x] == ChamberSymbol.EMPTY.value:
                        grid[y1][x] = ConnectionSymbol.HORIZONTAL.value
                # Then vertical
                start_y, end_y = min(y1, y2), max(y1, y2)
                for y in range(start_y + 1, end_y):
                    if grid[y][x2] == ChamberSymbol.EMPTY.value:
                        grid[y][x2] = ConnectionSymbol.VERTICAL.value
            else:
                # Vertical first
                start_y, end_y = min(y1, y2), max(y1, y2)
                for y in range(start_y + 1, end_y):
                    if grid[y][x1] == ChamberSymbol.EMPTY.value:
                        grid[y][x1] = ConnectionSymbol.VERTICAL.value
                # Then horizontal
                start_x, end_x = min(x1, x2), max(x1, x2)
                for x in range(start_x + 1, end_x):
                    if grid[y2][x] == ChamberSymbol.EMPTY.value:
                        grid[y2][x] = ConnectionSymbol.HORIZONTAL.value
    
    def _grid_to_string(self, grid: List[List[str]]) -> str:
        """Convert the grid to a string representation."""
        # Find the bounding box of non-empty content
        min_x, max_x = self.grid_size, -1
        min_y, max_y = self.grid_size, -1
        
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if grid[y][x] != ChamberSymbol.EMPTY.value:
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
        
        # If no content found, return empty string
        if max_x == -1:
            return ""
        
        # Add padding
        min_x = max(0, min_x - 2)
        max_x = min(self.grid_size - 1, max_x + 2)
        min_y = max(0, min_y - 2)
        max_y = min(self.grid_size - 1, max_y + 2)
        
        # Convert to string
        lines = []
        for y in range(min_y, max_y + 1):
            line = ''.join(grid[y][min_x:max_x + 1])
            lines.append(line.rstrip())
        
        return '\n'.join(lines)
    
    def _add_header_and_legend(self, map_str: str, chambers: Dict[int, ChamberInfo], 
                              current_chamber_id: int) -> str:
        """Add header and legend to the map."""
        current_chamber = chambers.get(current_chamber_id)
        current_name = current_chamber.name if current_chamber else "Unknown"
        
        # Count chambers
        visited_count = sum(1 for c in chambers.values() if c.visited)
        completed_count = sum(1 for c in chambers.values() if c.completed)
        
        # Calculate the required width for proper alignment
        # Base width is 62 characters (content area), plus 2 for borders = 64 total
        min_width = 62
        
        # Check if current location line needs more space
        location_text = f"Current Location: {current_name}"
        stats_text = f"Chambers Visited: {visited_count}  Completed: {completed_count}"
        
        # Calculate required width based on content
        required_width = max(
            min_width,
            len(location_text) + 2,  # +2 for padding
            len(stats_text) + 2,
            len("LABYRINTH MAP") + 20,  # +20 for centering
            len("LEGEND") + 20
        )
        
        # Ensure width is reasonable (max 100 characters)
        content_width = min(required_width, 98)
        total_width = content_width + 2  # +2 for border characters
        
        # Truncate current name if it's too long
        max_name_length = content_width - len("Current Location: ") - 2
        if len(current_name) > max_name_length:
            current_name = current_name[:max_name_length-3] + "..."
        
        # Create border lines
        top_border = "╔" + "═" * content_width + "╗"
        middle_border = "╠" + "═" * content_width + "╣"
        bottom_border = "╚" + "═" * content_width + "╝"
        
        # Create header with proper alignment
        header = f"{top_border}\n"
        header += f"║{'LABYRINTH MAP':^{content_width}}║\n"
        header += f"{middle_border}\n"
        
        # Format location line with proper padding
        location_line = f"Current Location: {current_name}"
        location_padding = content_width - len(location_line) - 1
        header += f"║ {location_line}{' ' * location_padding}║\n"
        
        # Format stats line with proper padding
        stats_line = f"Chambers Visited: {visited_count}  Completed: {completed_count}"
        stats_padding = content_width - len(stats_line) - 1
        header += f"║ {stats_line}{' ' * stats_padding}║\n"
        header += f"{bottom_border}\n\n"
        
        # Create legend with same width
        legend = f"\n\n{top_border}\n"
        legend += f"║{'LEGEND':^{content_width}}║\n"
        legend += f"{middle_border}\n"
        
        # Format legend lines with proper padding
        legend_line1 = f" {ChamberSymbol.CURRENT.value} Current Location    {ChamberSymbol.COMPLETED.value} Completed Chamber"
        legend_padding1 = content_width - len(legend_line1)
        legend += f"║{legend_line1}{' ' * legend_padding1}║\n"
        
        legend_line2 = f" {ChamberSymbol.VISITED.value} Visited Chamber     {ConnectionSymbol.HORIZONTAL.value} Horizontal Connection"
        legend_padding2 = content_width - len(legend_line2)
        legend += f"║{legend_line2}{' ' * legend_padding2}║\n"
        
        legend_line3 = f"                       {ConnectionSymbol.VERTICAL.value} Vertical Connection"
        legend_padding3 = content_width - len(legend_line3)
        legend += f"║{legend_line3}{' ' * legend_padding3}║\n"
        legend += f"{bottom_border}"
        
        return header + map_str + legend
    
    def get_chamber_list(self, chambers: Dict[int, ChamberInfo]) -> str:
        """Get a formatted list of visited chambers."""
        visited_chambers = [c for c in chambers.values() if c.visited]
        visited_chambers.sort(key=lambda c: c.chamber_id)
        
        if not visited_chambers:
            return "No chambers visited yet."
        
        lines = ["Visited Chambers:"]
        for chamber in visited_chambers:
            status = "✓" if chamber.completed else "○"
            lines.append(f"  {status} {chamber.chamber_id}: {chamber.name}")
        
        return "\n".join(lines)