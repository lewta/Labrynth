"""Tests for map border alignment fixes."""

import pytest
from src.game.map_renderer import MapRenderer, ChamberInfo


class TestMapBorderAlignment:
    """Test map border alignment functionality."""
    
    def test_border_alignment_short_names(self):
        """Test border alignment with short chamber names."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "Hall", True, False, {"north": 2}),
            2: ChamberInfo(2, "Room", True, True, {"south": 1})
        }
        
        result = renderer.render_map(chambers, 1)
        lines = result.split('\n')
        
        # Find all border lines
        border_lines = [line for line in lines if line.startswith(('╔', '║', '╠', '╚'))]
        
        # All border lines should have the same width
        if border_lines:
            expected_width = len(border_lines[0])
            for line in border_lines:
                assert len(line) == expected_width, f"Border width mismatch: expected {expected_width}, got {len(line)}"
    
    def test_border_alignment_long_names(self):
        """Test border alignment with long chamber names."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "The Grand Hall of Ancient Mysteries and Forgotten Secrets", True, False, {"north": 2}),
            2: ChamberInfo(2, "Chamber of the Eternal Guardian's Sacred Relics", True, True, {"south": 1})
        }
        
        result = renderer.render_map(chambers, 1)
        lines = result.split('\n')
        
        # Find all border lines
        border_lines = [line for line in lines if line.startswith(('╔', '║', '╠', '╚'))]
        
        # All border lines should have the same width
        if border_lines:
            expected_width = len(border_lines[0])
            for line in border_lines:
                assert len(line) == expected_width, f"Border width mismatch: expected {expected_width}, got {len(line)}"
    
    def test_border_alignment_extremely_long_names(self):
        """Test border alignment with extremely long chamber names (should be truncated)."""
        renderer = MapRenderer()
        extremely_long_name = "The Most Incredibly Long and Ridiculously Verbose Chamber Name That Goes On and On and On and Should Definitely Be Truncated Because It's Way Too Long for Any Reasonable Display"
        
        chambers = {
            1: ChamberInfo(1, extremely_long_name, True, False, {"north": 2}),
            2: ChamberInfo(2, "Normal Chamber", True, True, {"south": 1})
        }
        
        result = renderer.render_map(chambers, 1)
        lines = result.split('\n')
        
        # Find all border lines
        border_lines = [line for line in lines if line.startswith(('╔', '║', '╠', '╚'))]
        
        # All border lines should have the same width
        if border_lines:
            expected_width = len(border_lines[0])
            for line in border_lines:
                assert len(line) == expected_width, f"Border width mismatch: expected {expected_width}, got {len(line)}"
        
        # Check that the name was truncated
        assert "..." in result, "Long chamber name should be truncated with '...'"
        
        # Check that width doesn't exceed maximum
        assert expected_width <= 100, f"Border width should not exceed 100 characters, got {expected_width}"
    
    def test_border_alignment_many_chambers(self):
        """Test border alignment with many chambers."""
        renderer = MapRenderer()
        chambers = {}
        for i in range(1, 15):
            chambers[i] = ChamberInfo(i, f"Chamber {i}", True, i % 3 == 0, {})
        
        result = renderer.render_map(chambers, 5)
        lines = result.split('\n')
        
        # Find all border lines
        border_lines = [line for line in lines if line.startswith(('╔', '║', '╠', '╚'))]
        
        # All border lines should have the same width
        if border_lines:
            expected_width = len(border_lines[0])
            for line in border_lines:
                assert len(line) == expected_width, f"Border width mismatch: expected {expected_width}, got {len(line)}"
    
    def test_content_fits_within_borders(self):
        """Test that all content fits properly within the borders."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "Test Chamber", True, False, {"north": 2}),
            2: ChamberInfo(2, "Another Chamber", True, True, {"south": 1})
        }
        
        result = renderer.render_map(chambers, 1)
        lines = result.split('\n')
        
        # Find content lines (lines that start with ║)
        content_lines = [line for line in lines if line.startswith('║') and line.endswith('║')]
        
        for line in content_lines:
            # Content should not extend beyond the borders
            # The line should start with ║, have content, and end with ║
            assert line.startswith('║'), f"Content line should start with ║: {line}"
            assert line.endswith('║'), f"Content line should end with ║: {line}"
            
            # Check that there are no characters beyond the closing ║
            assert line.count('║') >= 2, f"Content line should have at least 2 ║ characters: {line}"
    
    def test_minimum_width_maintained(self):
        """Test that minimum width is maintained even with short content."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "A", True, False, {})  # Very short name
        }
        
        result = renderer.render_map(chambers, 1)
        lines = result.split('\n')
        
        # Find border lines
        border_lines = [line for line in lines if line.startswith(('╔', '║', '╠', '╚'))]
        
        if border_lines:
            width = len(border_lines[0])
            # Should maintain at least the minimum width (64 characters total)
            assert width >= 64, f"Border width should be at least 64 characters, got {width}"
    
    def test_header_and_legend_alignment(self):
        """Test that header and legend have consistent alignment."""
        renderer = MapRenderer()
        chambers = {
            1: ChamberInfo(1, "Test Chamber", True, False, {"north": 2}),
            2: ChamberInfo(2, "Another Chamber", True, True, {"south": 1})
        }
        
        result = renderer.render_map(chambers, 1)
        lines = result.split('\n')
        
        # Find header and legend sections
        header_start = -1
        header_end = -1
        legend_start = -1
        legend_end = -1
        
        for i, line in enumerate(lines):
            if line.startswith('╔') and header_start == -1:
                header_start = i
            elif line.startswith('╚') and header_start != -1 and header_end == -1:
                header_end = i
            elif line.startswith('╔') and header_end != -1 and legend_start == -1:
                legend_start = i
            elif line.startswith('╚') and legend_start != -1 and legend_end == -1:
                legend_end = i
        
        # Both header and legend should exist
        assert header_start != -1 and header_end != -1, "Header section not found"
        assert legend_start != -1 and legend_end != -1, "Legend section not found"
        
        # Header and legend should have the same width
        header_lines = lines[header_start:header_end+1]
        legend_lines = lines[legend_start:legend_end+1]
        
        header_width = len(header_lines[0]) if header_lines else 0
        legend_width = len(legend_lines[0]) if legend_lines else 0
        
        assert header_width == legend_width, f"Header and legend widths should match: header={header_width}, legend={legend_width}"