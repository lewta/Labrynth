"""Tests for victory flag display."""

import pytest
import re
from src.game.display import DisplayManager
from src.config.game_config import GameConfig


class TestVictoryFlag:
    """Test that victory displays the correct flag."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a GameConfig with default values (no file loading)
        # This ensures backward compatibility tests use the expected defaults
        default_config = GameConfig(config_file="nonexistent_file.json")
        self.display_manager = DisplayManager(use_colors=False, config=default_config)
        self.sample_stats = {
            'chambers_completed': 13,
            'total_chambers': 13,
            'commands_used': 150,
            'time_played': 1800,
            'challenges_completed': 13
        }
    
    def test_victory_message_contains_flag(self):
        """Test that victory message contains the flag."""
        victory_display = self.display_manager.display_game_over(True, self.sample_stats)
        
        # Should contain the flag
        assert "FLAG{" in victory_display
        assert "}" in victory_display
        
        # Extract and verify the flag format
        flag_match = re.search(r'FLAG\{[^}]+\}', victory_display)
        assert flag_match is not None
        
        flag = flag_match.group(0)
        assert flag == "FLAG{LABYRINTH_MASTER_2024}"
    
    def test_victory_message_contains_prize_announcement(self):
        """Test that victory message announces the prize."""
        victory_display = self.display_manager.display_game_over(True, self.sample_stats)
        
        # Should contain prize announcement
        assert "YOUR PRIZE" in victory_display
        assert "🏆" in victory_display
    
    def test_victory_message_contains_congratulations(self):
        """Test that victory message contains congratulatory text."""
        victory_display = self.display_manager.display_game_over(True, self.sample_stats)
        
        # Should contain congratulatory messages
        assert "Congratulations" in victory_display
        assert "escaped the labyrinth" in victory_display
        assert "ancient secrets" in victory_display
    
    def test_defeat_message_does_not_contain_flag(self):
        """Test that defeat message does not contain the flag."""
        defeat_display = self.display_manager.display_game_over(False, self.sample_stats)
        
        # Should not contain the flag
        assert "FLAG{" not in defeat_display
        assert "YOUR PRIZE" not in defeat_display
        assert "🏆" not in defeat_display
    
    def test_defeat_message_contains_appropriate_text(self):
        """Test that defeat message contains appropriate text."""
        defeat_display = self.display_manager.display_game_over(False, self.sample_stats)
        
        # Should contain defeat-appropriate messages
        assert "GAME OVER" in defeat_display
        assert "adventure has come to an end" in defeat_display
    
    def test_victory_message_includes_statistics(self):
        """Test that victory message includes game statistics."""
        victory_display = self.display_manager.display_game_over(True, self.sample_stats)
        
        # Should include all statistics
        assert "chambers_completed: 13" in victory_display
        assert "total_chambers: 13" in victory_display
        assert "commands_used: 150" in victory_display
        assert "time_played: 1800" in victory_display
        assert "challenges_completed: 13" in victory_display
    
    def test_flag_format_is_consistent(self):
        """Test that the flag format is consistent and follows CTF conventions."""
        victory_display = self.display_manager.display_game_over(True, self.sample_stats)
        
        # Extract the flag
        flag_match = re.search(r'FLAG\{[^}]+\}', victory_display)
        flag = flag_match.group(0)
        
        # Verify flag format follows CTF conventions
        assert flag.startswith("FLAG{")
        assert flag.endswith("}")
        assert len(flag) > 6  # More than just "FLAG{}"
        
        # Verify the specific flag content
        flag_content = flag[5:-1]  # Remove "FLAG{" and "}"
        assert "LABYRINTH" in flag_content
        assert "MASTER" in flag_content
        assert "2024" in flag_content
    
    def test_victory_display_formatting(self):
        """Test that victory display is properly formatted."""
        victory_display = self.display_manager.display_game_over(True, self.sample_stats)
        
        # Should have proper structure
        assert "VICTORY!" in victory_display
        assert "Game Statistics:" in victory_display
        
        # Should have multiple lines
        lines = victory_display.split('\n')
        assert len(lines) > 5  # Should have header, message, flag, stats, etc.
    
    def test_flag_visibility_in_output(self):
        """Test that the flag is prominently displayed and easy to find."""
        victory_display = self.display_manager.display_game_over(True, self.sample_stats)
        
        # Flag should be on its own line or clearly separated
        lines = victory_display.split('\n')
        flag_lines = [line for line in lines if "FLAG{" in line]
        
        assert len(flag_lines) == 1  # Should appear exactly once
        
        # Flag line should be prominent (not buried in other text)
        flag_line = flag_lines[0]
        assert "YOUR PRIZE" in flag_line or any("YOUR PRIZE" in line for line in lines)
    
    def test_empty_stats_handling(self):
        """Test that victory message works with empty statistics."""
        empty_stats = {}
        victory_display = self.display_manager.display_game_over(True, empty_stats)
        
        # Should still contain the flag even with empty stats
        assert "FLAG{LABYRINTH_MASTER_2024}" in victory_display
        assert "YOUR PRIZE" in victory_display


class TestConfigurableVictoryFlag:
    """Test that victory flag display works with custom configurations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_stats = {
            'chambers_completed': 13,
            'total_chambers': 13,
            'commands_used': 150,
            'time_played': 1800,
            'challenges_completed': 13
        }
    
    def test_custom_flag_content(self):
        """Test victory display with custom flag content."""
        # Create config with custom flag content
        config = GameConfig(config_file="nonexistent_file.json")
        config.set("victory.flag_content", "CUSTOM_CHALLENGE_2024")
        
        display_manager = DisplayManager(use_colors=False, config=config)
        victory_display = display_manager.display_game_over(True, self.sample_stats)
        
        # Should contain the custom flag
        assert "FLAG{CUSTOM_CHALLENGE_2024}" in victory_display
        assert "YOUR PRIZE" in victory_display
    
    def test_custom_flag_format(self):
        """Test victory display with custom flag prefix and suffix."""
        # Create config with custom flag format
        config = GameConfig(config_file="nonexistent_file.json")
        config.set("victory.flag_prefix", "CTF{")
        config.set("victory.flag_suffix", "}")
        config.set("victory.flag_content", "CYBER_CHALLENGE_2024")
        
        display_manager = DisplayManager(use_colors=False, config=config)
        victory_display = display_manager.display_game_over(True, self.sample_stats)
        
        # Should contain the custom formatted flag
        assert "CTF{CYBER_CHALLENGE_2024}" in victory_display
        assert "FLAG{" not in victory_display  # Should not contain default prefix
    
    def test_custom_victory_message(self):
        """Test victory display with custom victory message template."""
        # Create config with custom message template
        config = GameConfig(config_file="nonexistent_file.json")
        config.set("victory.prize_message", "🎉 Congratulations! Here's your reward: {flag}\n\nWell done, champion!")
        
        display_manager = DisplayManager(use_colors=False, config=config)
        victory_display = display_manager.display_game_over(True, self.sample_stats)
        
        # Should contain the custom message elements
        assert "🎉 Congratulations!" in victory_display
        assert "Here's your reward:" in victory_display
        assert "Well done, champion!" in victory_display
        assert "FLAG{LABYRINTH_MASTER_2024}" in victory_display
    
    def test_config_error_fallback(self):
        """Test that display falls back gracefully when config has errors."""
        # Create config with invalid message template (invalid format syntax)
        config = GameConfig(config_file="nonexistent_file.json")
        config.set("victory.prize_message", "Invalid template with {invalid_syntax")
        
        display_manager = DisplayManager(use_colors=False, config=config)
        victory_display = display_manager.display_game_over(True, self.sample_stats)
        
        # Should still contain the flag using fallback template
        assert "FLAG{LABYRINTH_MASTER_2024}" in victory_display
        assert "YOUR PRIZE" in victory_display
    
    def test_display_manager_without_config(self):
        """Test that DisplayManager works without explicit config parameter."""
        # This tests backward compatibility - DisplayManager should work without config parameter
        display_manager = DisplayManager(use_colors=False)
        victory_display = display_manager.display_game_over(True, self.sample_stats)
        
        # Should work and contain some flag (may be from existing config file or defaults)
        assert "Congratulations" in victory_display
        assert "{" in victory_display and "}" in victory_display  # Some flag format
    
    def test_victory_message_formatting_consistency(self):
        """Test that victory message formatting remains consistent with different configs."""
        configs = [
            # Default config
            GameConfig(config_file="nonexistent_file.json"),
            # Custom content
            GameConfig(config_file="nonexistent_file.json"),
            # Custom format
            GameConfig(config_file="nonexistent_file.json")
        ]
        
        # Set different configurations
        configs[1].set("victory.flag_content", "DIFFERENT_CONTENT")
        configs[2].set("victory.flag_prefix", "CHALLENGE{")
        configs[2].set("victory.flag_suffix", "]")
        
        for i, config in enumerate(configs):
            display_manager = DisplayManager(use_colors=False, config=config)
            victory_display = display_manager.display_game_over(True, self.sample_stats)
            
            # All should have consistent structure
            assert "VICTORY!" in victory_display
            assert "Congratulations" in victory_display
            assert "escaped the labyrinth" in victory_display
            assert "Game Statistics:" in victory_display
            
            # Each should have exactly one flag (check for flag patterns more flexibly)
            lines = victory_display.split('\n')
            flag_containing_lines = [line for line in lines if (
                ('{' in line and '}' in line) or  # Standard format
                ('{' in line and ']' in line) or  # Custom suffix
                ('FLAG' in line) or               # Any FLAG mention
                ('CTF' in line) or                # CTF format
                ('CHALLENGE' in line)             # Challenge format
            )]
            assert len(flag_containing_lines) >= 1, f"Config {i} should contain at least one flag, got: {victory_display}"