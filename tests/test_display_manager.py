"""Tests for the DisplayManager class."""

import pytest
from unittest.mock import Mock

from src.game.display import DisplayManager, MessageType, ColorCode
from src.utils.data_models import Item, PlayerStats, ChallengeResult
from src.challenges.base import Challenge


class MockChallenge(Challenge):
    """Mock challenge for testing."""
    
    def present_challenge(self) -> str:
        return "This is a test challenge. What is 2 + 2?"
    
    def process_response(self, response: str) -> ChallengeResult:
        success = response.strip() == "4"
        return ChallengeResult(
            success=success,
            message="Correct!" if success else "Wrong answer.",
            reward=Item("Test Reward", "A test item", "key", 10) if success else None
        )
    
    def get_reward(self):
        return Item("Test Reward", "A test item", "key", 10)


class TestDisplayManager:
    """Test cases for DisplayManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.display_manager = DisplayManager(use_colors=True)
        self.display_manager_no_color = DisplayManager(use_colors=False)
    
    def test_init_with_colors(self):
        """Test DisplayManager initialization with colors enabled."""
        dm = DisplayManager(use_colors=True)
        assert dm.use_colors is True
        assert MessageType.SUCCESS in dm._message_colors
    
    def test_init_without_colors(self):
        """Test DisplayManager initialization with colors disabled."""
        dm = DisplayManager(use_colors=False)
        assert dm.use_colors is False
    
    def test_colorize_with_colors_enabled(self):
        """Test text colorization when colors are enabled."""
        text = "Hello World"
        colored = self.display_manager._colorize(text, ColorCode.BRIGHT_GREEN)
        assert colored.startswith(ColorCode.BRIGHT_GREEN)
        assert colored.endswith(ColorCode.RESET)
        assert text in colored
    
    def test_colorize_with_colors_disabled(self):
        """Test text colorization when colors are disabled."""
        text = "Hello World"
        result = self.display_manager_no_color._colorize(text, ColorCode.BRIGHT_GREEN)
        assert result == text
        assert ColorCode.BRIGHT_GREEN not in result
        assert ColorCode.RESET not in result
    
    def test_format_header(self):
        """Test header formatting."""
        title = "Test Header"
        header = self.display_manager._format_header(title, 30)
        
        lines = header.strip().split('\n')
        assert len(lines) == 3
        assert all(len(line) == 30 for line in lines[:1] + lines[2:])  # Border lines
        assert title in lines[1]
        assert lines[0] == "=" * 30
        assert lines[2] == "=" * 30
    
    def test_format_header_long_title(self):
        """Test header formatting with title that's too long."""
        long_title = "This is a very long title that should be truncated"
        header = self.display_manager._format_header(long_title, 30)
        
        lines = header.strip().split('\n')
        assert "..." in lines[1]
        assert len(lines[1]) == 30
    
    def test_display_message_info(self):
        """Test displaying info message."""
        message = "This is an info message"
        result = self.display_manager.display_message(message, MessageType.INFO)
        
        assert message in result
        if self.display_manager.use_colors:
            assert ColorCode.WHITE in result
    
    def test_display_message_success(self):
        """Test displaying success message."""
        message = "Success message"
        result = self.display_manager.display_message(message, MessageType.SUCCESS)
        
        assert message in result
        if self.display_manager.use_colors:
            assert ColorCode.BRIGHT_GREEN in result
    
    def test_display_message_error(self):
        """Test displaying error message."""
        message = "Error message"
        result = self.display_manager.display_message(message, MessageType.ERROR)
        
        assert message in result
        if self.display_manager.use_colors:
            assert ColorCode.BRIGHT_RED in result
    
    def test_display_chamber_description(self):
        """Test displaying chamber description."""
        chamber_name = "Test Chamber"
        description = "A mysterious room with ancient symbols."
        exits = ["north", "south", "east"]
        
        result = self.display_manager.display_chamber_description(chamber_name, description, exits)
        
        assert chamber_name in result
        assert description in result
        assert "north" in result
        assert "south" in result
        assert "east" in result
        assert "Exits:" in result
    
    def test_display_chamber_description_no_exits(self):
        """Test displaying chamber description with no exits."""
        chamber_name = "Dead End"
        description = "A room with no way out."
        exits = []
        
        result = self.display_manager.display_chamber_description(chamber_name, description, exits)
        
        assert chamber_name in result
        assert description in result
        assert "No visible exits" in result
    
    def test_display_challenge(self):
        """Test displaying challenge information."""
        challenge = MockChallenge("Math Challenge", "Solve this math problem", 3)
        
        result = self.display_manager.display_challenge(challenge)
        
        assert challenge.name in result
        assert "Difficulty:" in result
        assert "★★★☆☆☆☆☆☆☆" in result  # 3 stars out of 10
        assert "(3/10)" in result
        assert "This is a test challenge" in result
    
    def test_display_challenge_result_success(self):
        """Test displaying successful challenge result."""
        reward = Item("Gold Key", "A shiny golden key", "key", 50)
        result = ChallengeResult(
            success=True,
            message="Well done! You solved the puzzle.",
            reward=reward,
            damage=0
        )
        
        display_result = self.display_manager.display_challenge_result(result)
        
        assert "SUCCESS!" in display_result
        assert result.message in display_result
        assert reward.name in display_result
        assert "You received:" in display_result
    
    def test_display_challenge_result_failure(self):
        """Test displaying failed challenge result."""
        result = ChallengeResult(
            success=False,
            message="That's not correct. Try again.",
            reward=None,
            damage=10
        )
        
        display_result = self.display_manager.display_challenge_result(result)
        
        assert "FAILED!" in display_result
        assert result.message in display_result
        assert "You took 10 damage!" in display_result
        assert "You received:" not in display_result
    
    def test_display_inventory_empty(self):
        """Test displaying empty inventory."""
        items = []
        
        result = self.display_manager.display_inventory(items)
        
        assert "Inventory" in result
        assert "empty" in result.lower()
        assert "Total items: 0" in result
    
    def test_display_inventory_with_items(self):
        """Test displaying inventory with items."""
        items = [
            Item("Health Potion", "Restores 50 health", "consumable", 25, True),
            Item("Broken Sword", "A damaged weapon", "weapon", 5, False),
            Item("Magic Ring", "Increases luck", "accessory", 100, True)
        ]
        
        result = self.display_manager.display_inventory(items)
        
        assert "Inventory" in result
        assert "Health Potion" in result
        assert "Broken Sword" in result
        assert "Magic Ring" in result
        assert "Total items: 3" in result
        assert "✓" in result  # Usable items
        assert "✗" in result  # Non-usable items
    
    def test_display_player_status(self):
        """Test displaying player status."""
        health = 85
        stats = PlayerStats(strength=12, intelligence=15, dexterity=8, luck=10)
        completed_chambers = 5
        
        result = self.display_manager.display_player_status(health, stats, completed_chambers)
        
        assert "Player Status" in result
        assert "Health: 85/100" in result
        assert "Strength: 12" in result
        assert "Intelligence: 15" in result
        assert "Dexterity: 8" in result
        assert "Luck: 10" in result
        assert "Chambers Completed: 5/13" in result
    
    def test_display_player_status_low_health(self):
        """Test displaying player status with low health."""
        health = 15
        stats = PlayerStats()
        completed_chambers = 2
        
        result = self.display_manager.display_player_status(health, stats, completed_chambers)
        
        assert "Health: 15/100" in result
        # Low health should be displayed in red when colors are enabled
        if self.display_manager.use_colors:
            assert ColorCode.BRIGHT_RED in result
    
    def test_display_help(self):
        """Test displaying help information."""
        commands = {
            "look": "Examine your surroundings",
            "go <direction>": "Move in the specified direction",
            "inventory": "View your items",
            "help": "Show this help message"
        }
        
        result = self.display_manager.display_help(commands)
        
        assert "Available Commands" in result
        for command, description in commands.items():
            assert command in result
            assert description in result
    
    def test_display_game_over_victory(self):
        """Test displaying victory game over screen."""
        stats = {
            "Chambers Completed": 13,
            "Items Found": 8,
            "Time Played": "45 minutes"
        }
        
        result = self.display_manager.display_game_over(True, stats)
        
        assert "VICTORY!" in result
        assert "Congratulations" in result
        assert "escaped the labyrinth" in result
        assert "Game Statistics:" in result
        for key, value in stats.items():
            assert f"{key}: {value}" in result
    
    def test_display_game_over_defeat(self):
        """Test displaying defeat game over screen."""
        stats = {
            "Chambers Completed": 7,
            "Items Found": 3,
            "Time Played": "30 minutes"
        }
        
        result = self.display_manager.display_game_over(False, stats)
        
        assert "GAME OVER" in result
        assert "adventure has come to an end" in result
        assert "Game Statistics:" in result
        for key, value in stats.items():
            assert f"{key}: {value}" in result
    
    def test_display_game_over_no_stats(self):
        """Test displaying game over screen with no statistics."""
        result = self.display_manager.display_game_over(True, {})
        
        assert "VICTORY!" in result
        assert "Game Statistics:" not in result
    
    def test_format_prompt(self):
        """Test formatting input prompt."""
        prompt_text = "Enter your command"
        
        result = self.display_manager.format_prompt(prompt_text)
        
        assert prompt_text in result
        assert ">" in result
        assert ":" in result
    
    def test_message_type_enum(self):
        """Test MessageType enum values."""
        assert MessageType.INFO.value == "info"
        assert MessageType.SUCCESS.value == "success"
        assert MessageType.WARNING.value == "warning"
        assert MessageType.ERROR.value == "error"
        assert MessageType.CHALLENGE.value == "challenge"
        assert MessageType.CHAMBER.value == "chamber"
        assert MessageType.INVENTORY.value == "inventory"
        assert MessageType.STATUS.value == "status"
    
    def test_color_codes_exist(self):
        """Test that color codes are properly defined."""
        assert hasattr(ColorCode, 'RESET')
        assert hasattr(ColorCode, 'BOLD')
        assert hasattr(ColorCode, 'BRIGHT_GREEN')
        assert hasattr(ColorCode, 'BRIGHT_RED')
        assert hasattr(ColorCode, 'BRIGHT_YELLOW')
        
        # Test that color codes are strings
        assert isinstance(ColorCode.RESET, str)
        assert isinstance(ColorCode.BRIGHT_GREEN, str)
    
    def test_difficulty_display_edge_cases(self):
        """Test challenge difficulty display for edge cases."""
        # Minimum difficulty
        challenge_min = MockChallenge("Easy", "Easy challenge", 1)
        result_min = self.display_manager.display_challenge(challenge_min)
        assert "★☆☆☆☆☆☆☆☆☆" in result_min
        assert "(1/10)" in result_min
        
        # Maximum difficulty
        challenge_max = MockChallenge("Hard", "Hard challenge", 10)
        result_max = self.display_manager.display_challenge(challenge_max)
        assert "★★★★★★★★★★" in result_max
        assert "(10/10)" in result_max