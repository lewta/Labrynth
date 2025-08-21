"""Tests for the MapRenderer class."""

import pytest
from src.game.map_renderer import MapRenderer, ChamberInfo, MapPosition, ChamberSymbol, ConnectionSymbol


class TestMapRenderer:
    """Test the MapRenderer class functionality."""
    
    def test_init(self):
        """Test MapRenderer initialization."""
        renderer = MapRenderer()
        
        assert renderer.chamber_positions == {}
        assert renderer.grid_size == 50
        assert renderer.center_x == 25
        assert renderer.center_y == 25
    
    def test_calculate_positions_single_chamber(self):
        """Test position calculation for a single chamber."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "Start", True, False, {})
        }
        
        renderer._calculate_positions(chambers, 1)
        
        assert 1 in renderer.chamber_positions
        pos = renderer.chamber_positions[1]
        assert pos.x == renderer.center_x
        assert pos.y == renderer.center_y
    
    def test_calculate_positions_connected_chambers(self):
        """Test position calculation for connected chambers."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "Start", True, False, {"north": 2, "east": 3}),
            2: ChamberInfo(2, "North", True, False, {"south": 1}),
            3: ChamberInfo(3, "East", True, True, {"west": 1})
        }
        
        renderer._calculate_positions(chambers, 1)
        
        # All chambers should have positions
        assert len(renderer.chamber_positions) == 3
        
        # Check relative positions
        pos1 = renderer.chamber_positions[1]
        pos2 = renderer.chamber_positions[2]
        pos3 = renderer.chamber_positions[3]
        
        # Chamber 1 should be at center
        assert pos1.x == renderer.center_x
        assert pos1.y == renderer.center_y
        
        # Chamber 2 should be north (y smaller)
        assert pos2.y < pos1.y
        
        # Chamber 3 should be east (x larger)
        assert pos3.x > pos1.x
    
    def test_create_grid(self):
        """Test grid creation."""
        renderer = MapRenderer()
        grid = renderer._create_grid()
        
        assert len(grid) == renderer.grid_size
        assert len(grid[0]) == renderer.grid_size
        assert all(cell == ChamberSymbol.EMPTY.value for row in grid for cell in row)
    
    def test_place_chambers_current(self):
        """Test placing current chamber symbol."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "Current", True, False, {})
        }
        renderer.chamber_positions[1] = MapPosition(25, 25)
        
        grid = renderer._create_grid()
        renderer._place_chambers(grid, chambers, 1)
        
        assert grid[25][25] == ChamberSymbol.CURRENT.value
    
    def test_place_chambers_completed(self):
        """Test placing completed chamber symbol."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "Completed", True, True, {})
        }
        renderer.chamber_positions[1] = MapPosition(25, 25)
        
        grid = renderer._create_grid()
        renderer._place_chambers(grid, chambers, 2)  # Different current chamber
        
        assert grid[25][25] == ChamberSymbol.COMPLETED.value
    
    def test_place_chambers_visited(self):
        """Test placing visited chamber symbol."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "Visited", True, False, {})
        }
        renderer.chamber_positions[1] = MapPosition(25, 25)
        
        grid = renderer._create_grid()
        renderer._place_chambers(grid, chambers, 2)  # Different current chamber
        
        assert grid[25][25] == ChamberSymbol.VISITED.value
    
    def test_place_chambers_unvisited_ignored(self):
        """Test that unvisited chambers are not placed."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "Unvisited", False, False, {})
        }
        renderer.chamber_positions[1] = MapPosition(25, 25)
        
        grid = renderer._create_grid()
        renderer._place_chambers(grid, chambers, 1)
        
        assert grid[25][25] == ChamberSymbol.EMPTY.value
    
    def test_draw_connection_line_horizontal(self):
        """Test drawing horizontal connection line."""
        renderer = MapRenderer()
        grid = renderer._create_grid()
        
        pos1 = MapPosition(20, 25)
        pos2 = MapPosition(30, 25)
        
        renderer._draw_connection_line(grid, pos1, pos2)
        
        # Check that horizontal line is drawn between positions
        for x in range(21, 30):
            assert grid[25][x] == ConnectionSymbol.HORIZONTAL.value
    
    def test_draw_connection_line_vertical(self):
        """Test drawing vertical connection line."""
        renderer = MapRenderer()
        grid = renderer._create_grid()
        
        pos1 = MapPosition(25, 20)
        pos2 = MapPosition(25, 30)
        
        renderer._draw_connection_line(grid, pos1, pos2)
        
        # Check that vertical line is drawn between positions
        for y in range(21, 30):
            assert grid[y][25] == ConnectionSymbol.VERTICAL.value
    
    def test_draw_connection_line_diagonal(self):
        """Test drawing diagonal connection (L-shaped)."""
        renderer = MapRenderer()
        grid = renderer._create_grid()
        
        pos1 = MapPosition(20, 20)
        pos2 = MapPosition(30, 30)
        
        renderer._draw_connection_line(grid, pos1, pos2)
        
        # Should draw L-shaped path
        # Since abs(30-20) == abs(30-20), it goes to else branch (vertical first)
        # Check vertical part first (from y=21 to y=29)
        for y in range(21, 30):
            assert grid[y][20] == ConnectionSymbol.VERTICAL.value
        
        # Check horizontal part (from x=21 to x=29)
        for x in range(21, 30):
            assert grid[30][x] == ConnectionSymbol.HORIZONTAL.value
    
    def test_draw_connections_between_chambers(self):
        """Test drawing connections between visited chambers."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "Start", True, False, {"north": 2}),
            2: ChamberInfo(2, "North", True, False, {"south": 1})
        }
        
        renderer.chamber_positions[1] = MapPosition(25, 25)
        renderer.chamber_positions[2] = MapPosition(25, 20)
        
        grid = renderer._create_grid()
        renderer._draw_connections(grid, chambers)
        
        # Check that vertical connection is drawn
        for y in range(21, 25):
            assert grid[y][25] == ConnectionSymbol.VERTICAL.value
    
    def test_draw_connections_ignores_unvisited(self):
        """Test that connections to unvisited chambers are not drawn."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "Start", True, False, {"north": 2}),
            2: ChamberInfo(2, "North", False, False, {"south": 1})  # Unvisited
        }
        
        renderer.chamber_positions[1] = MapPosition(25, 25)
        renderer.chamber_positions[2] = MapPosition(25, 20)
        
        grid = renderer._create_grid()
        renderer._draw_connections(grid, chambers)
        
        # No connections should be drawn
        for y in range(21, 25):
            assert grid[y][25] == ChamberSymbol.EMPTY.value
    
    def test_grid_to_string_basic(self):
        """Test converting grid to string."""
        renderer = MapRenderer()
        grid = renderer._create_grid()
        
        # Place some content
        grid[25][25] = ChamberSymbol.CURRENT.value
        grid[25][27] = ChamberSymbol.VISITED.value
        grid[25][26] = ConnectionSymbol.HORIZONTAL.value
        
        result = renderer._grid_to_string(grid)
        
        # Should contain the symbols
        assert ChamberSymbol.CURRENT.value in result
        assert ChamberSymbol.VISITED.value in result
        assert ConnectionSymbol.HORIZONTAL.value in result
        
        # Should be trimmed to content area
        lines = result.split('\n')
        assert len(lines) > 0
        # Find the line with content (some lines might be empty due to rstrip)
        content_lines = [line for line in lines if line.strip()]
        assert len(content_lines) > 0
        assert len(content_lines[0]) > 0
    
    def test_render_map_complete(self):
        """Test complete map rendering."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "Entrance", True, True, {"north": 2}),
            2: ChamberInfo(2, "Hall", True, False, {"south": 1, "east": 3}),
            3: ChamberInfo(3, "Exit", True, False, {"west": 2})
        }
        
        result = renderer.render_map(chambers, 2)
        
        # Should contain header
        assert "LABYRINTH MAP" in result
        assert "Current Location: Hall" in result
        assert "Chambers Visited: 3" in result
        assert "Completed: 1" in result
        
        # Should contain legend
        assert "LEGEND" in result
        assert ChamberSymbol.CURRENT.value in result
        assert ChamberSymbol.COMPLETED.value in result
        assert ChamberSymbol.VISITED.value in result
        
        # Should contain chamber symbols
        symbol_count = result.count(ChamberSymbol.CURRENT.value)
        assert symbol_count >= 1  # At least one current symbol
    
    def test_get_chamber_list_empty(self):
        """Test chamber list with no visited chambers."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "Unvisited", False, False, {})
        }
        
        result = renderer.get_chamber_list(chambers)
        
        assert result == "No chambers visited yet."
    
    def test_get_chamber_list_with_chambers(self):
        """Test chamber list with visited chambers."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "Entrance", True, True, {}),
            2: ChamberInfo(2, "Hall", True, False, {}),
            3: ChamberInfo(3, "Exit", True, False, {})
        }
        
        result = renderer.get_chamber_list(chambers)
        
        assert "Visited Chambers:" in result
        assert "✓ 1: Entrance" in result  # Completed
        assert "○ 2: Hall" in result      # Visited but not completed
        assert "○ 3: Exit" in result      # Visited but not completed
    
    def test_map_position_hash(self):
        """Test MapPosition hashing for use in sets/dicts."""
        pos1 = MapPosition(10, 20)
        pos2 = MapPosition(10, 20)
        pos3 = MapPosition(20, 10)
        
        assert hash(pos1) == hash(pos2)
        assert hash(pos1) != hash(pos3)
        
        # Should work in sets
        positions = {pos1, pos2, pos3}
        assert len(positions) == 2  # pos1 and pos2 are the same
    
    def test_chamber_info_dataclass(self):
        """Test ChamberInfo dataclass functionality."""
        chamber = ChamberInfo(
            chamber_id=1,
            name="Test Chamber",
            visited=True,
            completed=False,
            connections={"north": 2}
        )
        
        assert chamber.chamber_id == 1
        assert chamber.name == "Test Chamber"
        assert chamber.visited is True
        assert chamber.completed is False
        assert chamber.connections == {"north": 2}
        assert chamber.position is None  # Default value
        
        # Test with position
        chamber_with_pos = ChamberInfo(
            chamber_id=2,
            name="Test 2",
            visited=True,
            completed=True,
            connections={},
            position=MapPosition(10, 20)
        )
        
        assert chamber_with_pos.position.x == 10
        assert chamber_with_pos.position.y == 20