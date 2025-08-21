"""Tests for map command functionality."""

import pytest
from unittest.mock import Mock, patch
from src.game.engine import GameEngine
from src.game.command_parser import CommandParser, ParsedCommand, CommandType
from src.game.ui_controller import UIController
from src.game.map_renderer import ChamberInfo


class TestMapCommand:
    """Test map command functionality in the game engine."""
    
    def test_command_parser_recognizes_map(self):
        """Test that CommandParser recognizes 'map' as an examination command."""
        parser = CommandParser()
        
        # Test basic map command
        parsed = parser.parse_command("map")
        
        assert parsed.command_type == CommandType.EXAMINATION
        assert parsed.action == "map"
        assert parsed.parameters == []
        assert parsed.is_valid is True
    
    def test_command_parser_recognizes_map_legend(self):
        """Test that CommandParser recognizes 'map legend' command."""
        parser = CommandParser()
        
        # Test map legend command
        parsed = parser.parse_command("map legend")
        
        assert parsed.command_type == CommandType.EXAMINATION
        assert parsed.action == "map"
        assert parsed.parameters == ["legend"]
        assert parsed.is_valid is True
    
    def test_command_parser_map_alias(self):
        """Test that 'm' alias works for map command."""
        parser = CommandParser()
        
        # Test map alias
        parsed = parser.parse_command("m")
        
        assert parsed.command_type == CommandType.EXAMINATION
        assert parsed.action == "map"
        assert parsed.parameters == []
        assert parsed.is_valid is True
    
    def test_ui_controller_display_map(self):
        """Test UIController display_map method."""
        ui_controller = UIController()
        ui_controller.enable_output_capture()
        
        test_map = "Test map content"
        ui_controller.display_map(test_map)
        
        output = ui_controller.get_captured_output()
        assert len(output) == 1
        assert output[0] == test_map + '\n'
    
    @patch('src.game.engine.MapRenderer')
    def test_game_engine_display_map_no_chambers(self, mock_map_renderer):
        """Test displaying map when no chambers have been visited."""
        engine = GameEngine()
        engine.ui_controller.enable_output_capture()
        
        # Clear visited chambers
        engine.player_manager.progress.visited_chambers.clear()
        
        engine._display_map()
        
        output = engine.ui_controller.get_captured_output()
        assert any("haven't explored any chambers yet" in msg for msg in output)
        
        # MapRenderer should not be called
        mock_map_renderer.return_value.render_map.assert_not_called()
    
    @patch('src.game.engine.MapRenderer')
    def test_game_engine_display_map_with_chambers(self, mock_map_renderer):
        """Test displaying map with visited chambers."""
        engine = GameEngine()
        engine.ui_controller.enable_output_capture()
        
        # Mock world manager to return a chamber
        mock_chamber = Mock()
        mock_chamber.name = "Test Chamber"
        engine.world_manager.get_chamber = Mock(return_value=mock_chamber)
        engine.world_manager.current_chamber_id = 1
        
        # Add some progress data
        engine.player_manager.progress.visit_chamber(1, {"north": 2})
        engine.player_manager.progress.complete_chamber(1)
        
        # Mock map renderer
        mock_map_content = "Mock map content"
        mock_map_renderer.return_value.render_map.return_value = mock_map_content
        
        engine._display_map()
        
        # Verify map renderer was called with correct data
        mock_map_renderer.return_value.render_map.assert_called_once()
        call_args = mock_map_renderer.return_value.render_map.call_args
        chambers_arg = call_args[0][0]
        current_chamber_arg = call_args[0][1]
        
        assert current_chamber_arg == 1
        assert 1 in chambers_arg
        
        chamber_info = chambers_arg[1]
        assert isinstance(chamber_info, ChamberInfo)
        assert chamber_info.chamber_id == 1
        assert chamber_info.name == "Test Chamber"
        assert chamber_info.visited is True
        assert chamber_info.completed is True
        assert chamber_info.connections == {"north": 2}
        
        # Verify map was displayed
        output = engine.ui_controller.get_captured_output()
        assert any(mock_map_content in msg for msg in output)
    
    def test_game_engine_display_map_legend(self):
        """Test displaying map legend."""
        engine = GameEngine()
        engine.ui_controller.enable_output_capture()
        
        engine._display_map_legend()
        
        output = engine.ui_controller.get_captured_output()
        assert len(output) > 0
        
        # Check that legend content is present
        legend_content = ''.join(output)
        assert "LEGEND" in legend_content
        assert "Current Location" in legend_content
        assert "Completed Chamber" in legend_content
        assert "Visited Chamber" in legend_content
        assert "Horizontal Connection" in legend_content
        assert "Vertical Connection" in legend_content
    
    def test_game_engine_handles_map_command(self):
        """Test that GameEngine properly handles map examination command."""
        engine = GameEngine()
        engine.ui_controller.enable_output_capture()
        
        # Mock the display_map method
        engine._display_map = Mock()
        
        # Create a map command
        parsed_command = ParsedCommand(
            command_type=CommandType.EXAMINATION,
            action="map",
            parameters=[],
            raw_input="map"
        )
        
        engine._handle_examination_command(parsed_command)
        
        # Verify display_map was called
        engine._display_map.assert_called_once()
    
    def test_game_engine_handles_map_legend_command(self):
        """Test that GameEngine properly handles map legend command."""
        engine = GameEngine()
        engine.ui_controller.enable_output_capture()
        
        # Mock the display_map_legend method
        engine._display_map_legend = Mock()
        
        # Create a map legend command
        parsed_command = ParsedCommand(
            command_type=CommandType.EXAMINATION,
            action="map",
            parameters=["legend"],
            raw_input="map legend"
        )
        
        engine._handle_examination_command(parsed_command)
        
        # Verify display_map_legend was called
        engine._display_map_legend.assert_called_once()
    
    def test_integration_map_command_processing(self):
        """Test full integration of map command processing."""
        engine = GameEngine()
        engine.ui_controller.enable_output_capture()
        
        # Add some chambers to visit
        mock_chamber = Mock()
        mock_chamber.name = "Integration Test Chamber"
        engine.world_manager.get_chamber = Mock(return_value=mock_chamber)
        engine.world_manager.current_chamber_id = 1
        
        # Add progress
        engine.player_manager.progress.visit_chamber(1, {"east": 2})
        
        # Process map command through the full pipeline
        parsed_command = engine.command_parser.parse_command("map")
        engine.process_command(parsed_command)
        
        # Verify output was generated
        output = engine.ui_controller.get_captured_output()
        assert len(output) > 0
        
        # Should contain map content
        output_text = ''.join(output)
        assert "LABYRINTH MAP" in output_text or "Integration Test Chamber" in output_text
    
    def test_map_command_help_text(self):
        """Test that map command appears in help."""
        parser = CommandParser()
        
        # Get command info
        commands = parser.get_available_commands()
        
        assert "map" in commands
        
        map_description = commands["map"]
        assert "map" in map_description.lower()
        assert "visited chambers" in map_description.lower()
    
    def test_map_command_with_multiple_chambers(self):
        """Test map display with multiple visited chambers."""
        engine = GameEngine()
        engine.ui_controller.enable_output_capture()
        
        # Mock chambers
        chamber1 = Mock()
        chamber1.name = "Chamber 1"
        chamber2 = Mock()
        chamber2.name = "Chamber 2"
        chamber3 = Mock()
        chamber3.name = "Chamber 3"
        
        chambers = {
            1: chamber1,
            2: chamber2,
            3: chamber3
        }
        
        def get_chamber_mock(chamber_id):
            return chambers.get(chamber_id)
        
        engine.world_manager.get_chamber = get_chamber_mock
        engine.world_manager.current_chamber_id = 2
        
        # Add progress for multiple chambers
        progress = engine.player_manager.progress
        progress.visit_chamber(1, {"north": 2})
        progress.visit_chamber(2, {"south": 1, "east": 3})
        progress.visit_chamber(3, {"west": 2})
        progress.complete_chamber(1)
        progress.complete_chamber(3)
        
        engine._display_map()
        
        output = engine.ui_controller.get_captured_output()
        assert len(output) > 0
        
        # Should contain map content
        output_text = ''.join(output)
        assert "LABYRINTH MAP" in output_text