"""Integration tests for display manager with configurable flag system."""

import pytest
import tempfile
import json
import os
from src.game.display import DisplayManager
from src.config.game_config import GameConfig


class TestDisplayIntegration:
    """Test display manager integration with configurable flag system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_stats = {
            'chambers_completed': 13,
            'total_chambers': 13,
            'commands_used': 150,
            'time_played': 1800,
            'challenges_completed': 13
        }
    
    def test_display_with_existing_config_file(self):
        """Test that display manager works with the existing game_config.json file."""
        # This tests integration with the actual config file in the project
        display_manager = DisplayManager(use_colors=False)
        victory_display = display_manager.display_game_over(True, self.sample_stats)
        
        # Should work and contain victory elements
        assert "VICTORY!" in victory_display
        assert "Congratulations" in victory_display
        assert "escaped the labyrinth" in victory_display
        assert "Game Statistics:" in victory_display
        
        # Should contain some form of flag (from the existing config file)
        assert "{" in victory_display and "}" in victory_display
    
    def test_display_with_temporary_config_file(self):
        """Test display manager with a temporary configuration file."""
        # Create a temporary config file
        temp_config = {
            "victory": {
                "flag_content": "TEMP_TEST_2024",
                "flag_prefix": "TEMP{",
                "flag_suffix": "}",
                "prize_message": "🎯 Test Prize: {flag}\n\nTemporary test completed!"
            },
            "game": {
                "title": "Test Game",
                "version": "1.0"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(temp_config, f, indent=2)
            temp_file_path = f.name
        
        try:
            # Create config and display manager with temporary file
            config = GameConfig(config_file=temp_file_path)
            display_manager = DisplayManager(use_colors=False, config=config)
            victory_display = display_manager.display_game_over(True, self.sample_stats)
            
            # Should contain the temporary config values
            assert "TEMP{TEMP_TEST_2024}" in victory_display
            assert "🎯 Test Prize:" in victory_display
            assert "Temporary test completed!" in victory_display
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def test_display_backward_compatibility(self):
        """Test that display manager maintains backward compatibility."""
        # Create display manager without explicit config (backward compatibility)
        display_manager = DisplayManager(use_colors=False)
        
        # Test both victory and defeat scenarios
        victory_display = display_manager.display_game_over(True, self.sample_stats)
        defeat_display = display_manager.display_game_over(False, self.sample_stats)
        
        # Victory should have flag and congratulations
        assert "VICTORY!" in victory_display
        assert "Congratulations" in victory_display
        
        # Defeat should not have flag
        assert "GAME OVER" in defeat_display
        assert "adventure has come to an end" in defeat_display
        
        # Both should have statistics
        assert "Game Statistics:" in victory_display
        assert "Game Statistics:" in defeat_display
    
    def test_display_config_error_handling(self):
        """Test display manager handles configuration errors gracefully."""
        # Test with non-existent config file (should use defaults)
        config = GameConfig(config_file="definitely_does_not_exist.json")
        display_manager = DisplayManager(use_colors=False, config=config)
        victory_display = display_manager.display_game_over(True, self.sample_stats)
        
        # Should still work with default values
        assert "VICTORY!" in victory_display
        assert "Congratulations" in victory_display
        assert "FLAG{LABYRINTH_MASTER_2024}" in victory_display
        assert "YOUR PRIZE" in victory_display
    
    def test_display_message_formatting_consistency(self):
        """Test that message formatting remains consistent across different configs."""
        configs = [
            # Default config (no file)
            GameConfig(config_file="nonexistent.json"),
            # Config with custom content
            GameConfig(config_file="nonexistent.json"),
            # Config with custom format
            GameConfig(config_file="nonexistent.json")
        ]
        
        # Customize the configs
        configs[1].set("victory.flag_content", "CUSTOM_CONTENT")
        configs[2].set("victory.flag_prefix", "CUSTOM{")
        configs[2].set("victory.flag_suffix", "]")
        
        for i, config in enumerate(configs):
            display_manager = DisplayManager(use_colors=False, config=config)
            victory_display = display_manager.display_game_over(True, self.sample_stats)
            
            # All should have consistent structure
            lines = victory_display.split('\n')
            
            # Should have header with VICTORY!
            header_lines = [line for line in lines if "VICTORY!" in line]
            assert len(header_lines) >= 1, f"Config {i} missing VICTORY header"
            
            # Should have congratulations message
            assert "Congratulations" in victory_display, f"Config {i} missing congratulations"
            
            # Should have statistics section
            assert "Game Statistics:" in victory_display, f"Config {i} missing statistics"
            
            # Should have some form of flag/prize
            has_flag_indicator = any(
                indicator in victory_display 
                for indicator in ['{', '}', 'FLAG', 'CUSTOM', 'PRIZE', 'prize']
            )
            assert has_flag_indicator, f"Config {i} missing flag/prize indicator"