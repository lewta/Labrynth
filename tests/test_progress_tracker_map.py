"""Tests for progress tracker map functionality."""

import pytest
from src.game.progress import ProgressTracker
from src.utils.exceptions import GameException


class TestProgressTrackerMapData:
    """Test progress tracker functionality for map data."""
    
    def test_visit_chamber_basic(self):
        """Test basic chamber visiting functionality."""
        tracker = ProgressTracker()
        
        # Visit a chamber
        tracker.visit_chamber(1)
        
        assert 1 in tracker.visited_chambers
        assert tracker.is_chamber_visited(1)
        assert not tracker.is_chamber_completed(1)
    
    def test_visit_chamber_with_connections(self):
        """Test visiting chamber with connection data."""
        tracker = ProgressTracker()
        connections = {"north": 2, "east": 3}
        
        tracker.visit_chamber(1, connections)
        
        assert 1 in tracker.visited_chambers
        assert tracker.discovered_connections[1] == connections
    
    def test_discover_connection_basic(self):
        """Test basic connection discovery."""
        tracker = ProgressTracker()
        
        tracker.discover_connection(1, "north", 2)
        
        assert 1 in tracker.discovered_connections
        assert tracker.discovered_connections[1]["north"] == 2
    
    def test_discover_connection_multiple(self):
        """Test discovering multiple connections from same chamber."""
        tracker = ProgressTracker()
        
        tracker.discover_connection(1, "north", 2)
        tracker.discover_connection(1, "east", 3)
        
        expected = {"north": 2, "east": 3}
        assert tracker.discovered_connections[1] == expected
    
    def test_discover_connection_validation(self):
        """Test connection discovery input validation."""
        tracker = ProgressTracker()
        
        # Invalid from_chamber
        with pytest.raises(GameException, match="From chamber ID must be a positive integer"):
            tracker.discover_connection(0, "north", 2)
        
        with pytest.raises(GameException, match="From chamber ID must be a positive integer"):
            tracker.discover_connection(-1, "north", 2)
        
        with pytest.raises(GameException, match="From chamber ID must be a positive integer"):
            tracker.discover_connection("invalid", "north", 2)
        
        # Invalid to_chamber
        with pytest.raises(GameException, match="To chamber ID must be a positive integer"):
            tracker.discover_connection(1, "north", 0)
        
        with pytest.raises(GameException, match="To chamber ID must be a positive integer"):
            tracker.discover_connection(1, "north", -1)
        
        with pytest.raises(GameException, match="To chamber ID must be a positive integer"):
            tracker.discover_connection(1, "north", "invalid")
        
        # Invalid direction
        with pytest.raises(GameException, match="Direction must be a non-empty string"):
            tracker.discover_connection(1, "", 2)
        
        with pytest.raises(GameException, match="Direction must be a non-empty string"):
            tracker.discover_connection(1, None, 2)
        
        with pytest.raises(GameException, match="Direction must be one of"):
            tracker.discover_connection(1, "invalid", 2)
    
    def test_discover_connection_direction_normalization(self):
        """Test that directions are normalized to lowercase."""
        tracker = ProgressTracker()
        
        tracker.discover_connection(1, "NORTH", 2)
        tracker.discover_connection(1, "East", 3)
        tracker.discover_connection(1, " south ", 4)
        
        expected = {"north": 2, "east": 3, "south": 4}
        assert tracker.discovered_connections[1] == expected
    
    def test_get_discovered_connections(self):
        """Test getting discovered connections."""
        tracker = ProgressTracker()
        
        # Add some connections
        tracker.discover_connection(1, "north", 2)
        tracker.discover_connection(1, "east", 3)
        tracker.discover_connection(2, "south", 1)
        
        connections = tracker.get_discovered_connections()
        
        # Should return a copy
        assert connections == tracker.discovered_connections
        assert connections is not tracker.discovered_connections
        
        # Modifying returned dict shouldn't affect original
        connections[1]["west"] = 4
        assert "west" not in tracker.discovered_connections[1]
    
    def test_get_discovered_connections_empty(self):
        """Test getting discovered connections when none exist."""
        tracker = ProgressTracker()
        
        connections = tracker.get_discovered_connections()
        
        assert connections == {}
        assert isinstance(connections, dict)
    
    def test_visit_chamber_validation(self):
        """Test chamber visit input validation."""
        tracker = ProgressTracker()
        
        # Invalid chamber IDs
        with pytest.raises(GameException, match="Chamber ID must be a positive integer"):
            tracker.visit_chamber(0)
        
        with pytest.raises(GameException, match="Chamber ID must be a positive integer"):
            tracker.visit_chamber(-1)
        
        with pytest.raises(GameException, match="Chamber ID must be a positive integer"):
            tracker.visit_chamber("invalid")
    
    def test_map_data_integration(self):
        """Test that map data includes all necessary information."""
        tracker = ProgressTracker()
        
        # Visit some chambers
        tracker.visit_chamber(1, {"north": 2, "east": 3})
        tracker.visit_chamber(2, {"south": 1})
        tracker.complete_chamber(1)
        
        map_data = tracker.get_map_data()
        
        # Check chamber 1 data
        assert 1 in map_data
        chamber1_data = map_data[1]
        assert chamber1_data['chamber_id'] == 1
        assert chamber1_data['visited'] is True
        assert chamber1_data['completed'] is True
        assert chamber1_data['connections'] == {"north": 2, "east": 3}
        
        # Check chamber 2 data
        assert 2 in map_data
        chamber2_data = map_data[2]
        assert chamber2_data['chamber_id'] == 2
        assert chamber2_data['visited'] is True
        assert chamber2_data['completed'] is False
        assert chamber2_data['connections'] == {"south": 1}
    
    def test_reset_clears_map_data(self):
        """Test that reset clears all map-related data."""
        tracker = ProgressTracker()
        
        # Add some data
        tracker.visit_chamber(1, {"north": 2})
        tracker.discover_connection(1, "east", 3)
        tracker.complete_chamber(1)
        
        # Verify data exists
        assert len(tracker.visited_chambers) > 0
        assert len(tracker.discovered_connections) > 0
        assert len(tracker.completed_chambers) > 0
        
        # Reset and verify everything is cleared
        tracker.reset()
        
        assert len(tracker.visited_chambers) == 0
        assert len(tracker.discovered_connections) == 0
        assert len(tracker.completed_chambers) == 0
        
        # Map data should be empty
        map_data = tracker.get_map_data()
        assert map_data == {}
    
    def test_progress_summary_includes_map_data(self):
        """Test that progress summary includes map-related information."""
        tracker = ProgressTracker()
        
        # Add some progress
        tracker.visit_chamber(1)
        tracker.visit_chamber(2)
        tracker.complete_chamber(1)
        
        summary = tracker.get_progress_summary()
        
        assert 'visited_chambers' in summary
        assert 'completed_chambers' in summary
        assert 'visited_chamber_ids' in summary
        assert 'completed_chamber_ids' in summary
        
        assert summary['visited_chambers'] == 2
        assert summary['completed_chambers'] == 1
        assert set(summary['visited_chamber_ids']) == {1, 2}
        assert summary['completed_chamber_ids'] == [1]