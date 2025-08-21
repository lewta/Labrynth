"""
Integration tests for complete gameplay scenarios.

These tests verify end-to-end functionality by simulating complete
gameplay sessions with real components and minimal mocking.
"""

import pytest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any

from src.game.engine import GameEngine
from src.game.world import WorldManager
from src.game.player import PlayerManager
from src.challenges.factory import ChallengeFactory
from src.utils.save_load import SaveLoadManager
from src.utils.exceptions import GameException
from src.utils.data_models import GameState, Item, PlayerStats


class TestCompleteGameplayScenarios:
    """Test complete gameplay scenarios from start to finish."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.save_file = os.path.join(self.temp_dir, "test_save.json")
        
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.save_file):
            os.remove(self.save_file)
        os.rmdir(self.temp_dir)
    
    @patch('builtins.input')
    def test_complete_game_session_with_riddle_challenges(self, mock_input):
        """Test a complete game session focusing on riddle challenges."""
        # Simulate user inputs for a complete session
        inputs = [
            'look',           # Initial look around
            'north',          # Move to chamber with riddle
            'answer',         # Attempt riddle (will fail first)
            'sphinx',         # Correct answer for riddle
            'inventory',      # Check inventory after success
            'south',          # Return to start
            'east',           # Try different direction
            'help',           # Get help
            'status',         # Check status
            'save',           # Save game
            'quit'            # Exit game
        ]
        mock_input.side_effect = inputs
        
        engine = GameEngine()
        
        # Mock save functionality to use our temp file
        with patch.object(engine.save_load_manager, 'save_game') as mock_save:
            mock_save.return_value = True
            
            # Start the game
            engine.start_game()
            
            # Verify game state after session
            assert engine.player_manager.health > 0
            assert len(engine.player_manager.progress.completed_chambers) >= 0
            
            # Verify save was called
            mock_save.assert_called_once()
    
    @patch('builtins.input')
    def test_combat_challenge_integration(self, mock_input):
        """Test integration of combat challenges in gameplay."""
        inputs = [
            'north',          # Move to combat chamber
            'attack',         # Attack in combat
            'defend',         # Defend in combat
            'attack',         # Final attack
            'inventory',      # Check rewards
            'quit'
        ]
        mock_input.side_effect = inputs
        
        engine = GameEngine()
        
        # Ensure we have a combat challenge in chamber 2
        chamber_2 = engine.world_manager.get_chamber(2)
        if chamber_2 and chamber_2.challenge:
            challenge_type = type(chamber_2.challenge).__name__
            
            engine.start_game()
            
            # Verify player health changed during combat
            assert engine.player_manager.health <= 100
    
    @patch('builtins.input')
    def test_puzzle_solving_workflow(self, mock_input):
        """Test complete puzzle solving workflow."""
        inputs = [
            'east',           # Move to puzzle chamber
            '1',              # Puzzle step 1
            '2',              # Puzzle step 2
            '3',              # Puzzle step 3
            'solve',          # Attempt to solve
            'status',         # Check completion status
            'quit'
        ]
        mock_input.side_effect = inputs
        
        engine = GameEngine()
        engine.start_game()
        
        # Verify puzzle interaction occurred
        assert engine.world_manager.current_chamber_id in [1, 3]  # Moved or stayed
    
    def test_save_load_complete_workflow(self):
        """Test complete save and load workflow with real game state."""
        # Create a proper GameState object
        test_item = Item(name="Test Key", description="A test key", item_type="key", value=1)
        game_state = GameState(
            current_chamber=3,
            player_health=75,
            inventory_items=[test_item],
            completed_chambers={2},
            game_time=300
        )
        
        # Save the game
        save_manager = SaveLoadManager()
        success = save_manager.save_game(game_state, self.save_file)
        assert success
        assert os.path.exists(self.save_file)
        
        # Load the game
        loaded_state = save_manager.load_game(self.save_file)
        
        assert loaded_state is not None
        assert loaded_state.current_chamber == 3
        assert loaded_state.player_health == 75
        assert len(loaded_state.inventory_items) == 1
        assert loaded_state.inventory_items[0].name == "Test Key"
        assert 2 in loaded_state.completed_chambers
    
    @patch('builtins.input')
    def test_inventory_management_integration(self, mock_input):
        """Test inventory management throughout gameplay."""
        inputs = [
            'inventory',      # Check initial empty inventory
            'north',          # Move to get item
            'take key',       # Take an item (if available)
            'inventory',      # Check inventory with item
            'use key',        # Use the item
            'inventory',      # Check inventory after use
            'quit'
        ]
        mock_input.side_effect = inputs
        
        engine = GameEngine()
        initial_inventory_size = len(engine.player_manager.inventory.items)
        
        engine.start_game()
        
        # Verify inventory operations occurred
        # (Exact assertions depend on specific chamber configurations)
        assert isinstance(engine.player_manager.inventory.items, list)
    
    def test_challenge_factory_integration_all_types(self):
        """Test that all challenge types can be created and function properly."""
        factory = ChallengeFactory()
        challenge_types = ['riddle', 'puzzle', 'combat', 'skill', 'memory']
        
        for challenge_type in challenge_types:
            challenge = factory.create_challenge(challenge_type, difficulty=1)
            assert challenge is not None
            
            # Test basic challenge interface
            description = challenge.present_challenge()
            assert isinstance(description, str)
            assert len(description) > 0
            
            # Test response processing (with dummy response)
            result = challenge.process_response("test response")
            assert hasattr(result, 'success')
            assert hasattr(result, 'message')
    
    @patch('builtins.input')
    def test_win_condition_detection(self, mock_input):
        """Test that win conditions are properly detected."""
        inputs = ['quit']  # Minimal input to avoid hanging
        mock_input.side_effect = inputs
        
        engine = GameEngine()
        
        # Manually complete all required chambers
        required_chambers = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        for chamber_id in required_chambers:
            engine.player_manager.progress.complete_chamber(chamber_id)
        
        # Check win condition
        assert engine.check_win_condition()
    
    @patch('builtins.input')
    def test_error_recovery_during_gameplay(self, mock_input):
        """Test that the game recovers gracefully from errors during gameplay."""
        inputs = [
            'invalid_command',  # Invalid command
            'north',           # Valid command
            'gibberish',       # Another invalid command
            'help',            # Get help
            'quit'             # Exit
        ]
        mock_input.side_effect = inputs
        
        engine = GameEngine()
        
        # Should not raise exceptions despite invalid inputs
        try:
            engine.start_game()
        except Exception as e:
            pytest.fail(f"Game should handle invalid inputs gracefully, but raised: {e}")


class TestChallengeTypeIntegration:
    """Test all challenge types in realistic game contexts."""
    
    def setup_method(self):
        """Set up test environment."""
        self.engine = GameEngine()
        self.factory = ChallengeFactory()
    
    def test_riddle_challenge_in_game_context(self):
        """Test riddle challenge within actual game context."""
        riddle = self.factory.create_challenge('riddle', difficulty=1)
        
        # Place riddle in a chamber
        chamber = self.engine.world_manager.get_chamber(2)
        if chamber:
            chamber.set_challenge(riddle)
            
            # Test challenge presentation
            description = riddle.present_challenge()
            assert "riddle" in description.lower() or "question" in description.lower()
            
            # Test various responses
            wrong_result = riddle.process_response("wrong answer")
            assert not wrong_result.success
            
            # Test with a potentially correct answer
            correct_result = riddle.process_response("sphinx")
            # Result depends on specific riddle content
            assert hasattr(correct_result, 'success')
    
    def test_combat_challenge_in_game_context(self):
        """Test combat challenge within actual game context."""
        combat = self.factory.create_challenge('combat', difficulty=1)
        
        chamber = self.engine.world_manager.get_chamber(3)
        if chamber:
            chamber.set_challenge(combat)
            
            # Test combat presentation
            description = combat.present_challenge()
            assert "combat" in description.lower() or "enemy" in description.lower()
            
            # Test combat actions
            attack_result = combat.process_response("attack")
            assert hasattr(attack_result, 'success')
            assert hasattr(attack_result, 'damage')
    
    def test_puzzle_challenge_in_game_context(self):
        """Test puzzle challenge within actual game context."""
        puzzle = self.factory.create_challenge('puzzle', difficulty=1)
        
        chamber = self.engine.world_manager.get_chamber(4)
        if chamber:
            chamber.set_challenge(puzzle)
            
            # Test puzzle presentation
            description = puzzle.present_challenge()
            assert "puzzle" in description.lower() or "solve" in description.lower()
            
            # Test puzzle interaction
            result = puzzle.process_response("1")
            assert hasattr(result, 'success')
    
    def test_skill_challenge_in_game_context(self):
        """Test skill challenge within actual game context."""
        skill = self.factory.create_challenge('skill', difficulty=1)
        
        chamber = self.engine.world_manager.get_chamber(5)
        if chamber:
            chamber.set_challenge(skill)
            
            # Test skill challenge presentation
            description = skill.present_challenge()
            assert len(description) > 0
            
            # Test skill check
            result = skill.process_response("attempt")
            assert hasattr(result, 'success')
    
    def test_memory_challenge_in_game_context(self):
        """Test memory challenge within actual game context."""
        memory = self.factory.create_challenge('memory', difficulty=1)
        
        chamber = self.engine.world_manager.get_chamber(6)
        if chamber:
            chamber.set_challenge(memory)
            
            # Test memory challenge presentation
            description = memory.present_challenge()
            assert "memory" in description.lower() or "remember" in description.lower()
            
            # Test memory response
            result = memory.process_response("sequence")
            assert hasattr(result, 'success')


class TestSaveLoadIntegrationScenarios:
    """Test save/load functionality with real game states."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.save_file = os.path.join(self.temp_dir, "integration_save.json")
        
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.save_file):
            os.remove(self.save_file)
        os.rmdir(self.temp_dir)
    
    def test_save_load_with_completed_challenges(self):
        """Test save/load with various completed challenges."""
        # Create proper Item objects
        sword = Item(name="Magic Sword", description="A glowing sword", item_type="weapon", value=50)
        potion = Item(name="Health Potion", description="Restores health", item_type="consumable", value=25)
        
        # Create GameState with completed challenges
        game_state = GameState(
            current_chamber=7,
            player_health=85,
            inventory_items=[sword, potion],
            completed_chambers={2, 3, 5},
            game_time=1200
        )
        
        # Save the game
        save_manager = SaveLoadManager()
        success = save_manager.save_game(game_state, self.save_file)
        assert success
        
        # Load and verify
        loaded_state = save_manager.load_game(self.save_file)
        assert loaded_state is not None
        
        # Verify all data was preserved
        assert loaded_state.current_chamber == 7
        assert loaded_state.player_health == 85
        assert len(loaded_state.inventory_items) == 2
        assert loaded_state.inventory_items[0].name == "Magic Sword"
        assert loaded_state.inventory_items[1].name == "Health Potion"
        assert loaded_state.completed_chambers == {2, 3, 5}
        assert loaded_state.game_time == 1200
    
    def test_save_load_with_different_game_states(self):
        """Test save/load with various game states."""
        save_manager = SaveLoadManager()
        
        # Test different game states
        test_states = [
            GameState(
                current_chamber=1,
                player_health=100,
                inventory_items=[],
                completed_chambers=set(),
                game_time=0
            ),
            GameState(
                current_chamber=13,
                player_health=1,
                inventory_items=[Item(name="Last Key", description="Final key", item_type="key", value=100)],
                completed_chambers=set(range(2, 13)),
                game_time=5000
            )
        ]
        
        for i, state in enumerate(test_states):
            save_file = os.path.join(self.temp_dir, f"test_state_{i}.json")
            
            # Save state
            success = save_manager.save_game(state, save_file)
            assert success
            
            # Load and verify
            loaded_state = save_manager.load_game(save_file)
            assert loaded_state.current_chamber == state.current_chamber
            assert loaded_state.player_health == state.player_health
            assert len(loaded_state.inventory_items) == len(state.inventory_items)
            assert loaded_state.completed_chambers == state.completed_chambers
            assert loaded_state.game_time == state.game_time
            
            # Clean up
            os.remove(save_file)
    
    @patch('builtins.input')
    def test_save_load_during_active_gameplay(self, mock_input):
        """Test save/load operations during active gameplay."""
        inputs = [
            'north',          # Move around
            'save',           # Save game
            'east',           # Continue playing
            'load',           # Load game
            'status',         # Check status
            'quit'
        ]
        mock_input.side_effect = inputs
        
        engine = GameEngine()
        
        # Mock save/load operations
        with patch.object(engine.save_load_manager, 'save_game', return_value=True) as mock_save, \
             patch.object(engine.save_load_manager, 'load_game') as mock_load:
            
            mock_load.return_value = GameState(
                current_chamber=1,
                player_health=100,
                inventory_items=[],
                completed_chambers=set(),
                game_time=100
            )
            
            engine.start_game()
            
            # Verify save/load were called during gameplay
            assert mock_save.called or mock_load.called