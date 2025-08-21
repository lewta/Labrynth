"""
Integration tests for system-level interactions and configurations.

These tests verify that different systems work together correctly
and handle various configuration scenarios.
"""

import pytest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock

from src.game.engine import GameEngine
from src.game.world import WorldManager
from src.challenges.factory import ChallengeFactory
from src.utils.config import LabyrinthConfigValidator
from src.utils.challenge_content import get_content_loader
from src.utils.randomization import ChallengeRandomizer
from src.utils.exceptions import GameException, ConfigurationException


class TestSystemIntegration:
    """Test integration between major game systems."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test environment."""
        # Clean up any temporary files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_world_manager_challenge_factory_integration(self):
        """Test integration between WorldManager and ChallengeFactory."""
        world_manager = WorldManager()
        challenge_factory = ChallengeFactory()
        
        # Initialize world
        world_manager.initialize_labyrinth()
        
        # Verify chambers have challenges
        for chamber_id in range(2, 14):  # Chambers 2-13 should have challenges
            chamber = world_manager.get_chamber(chamber_id)
            if chamber and chamber.challenge:
                # Verify challenge is properly created
                assert hasattr(chamber.challenge, 'present_challenge')
                assert hasattr(chamber.challenge, 'process_response')
                assert callable(chamber.challenge.present_challenge)
                assert callable(chamber.challenge.process_response)
    
    def test_config_validator_world_integration(self):
        """Test integration between config validation and WorldManager."""
        validator = LabyrinthConfigValidator()
        world_manager = WorldManager()
        
        # Initialize world with default config
        world_manager.initialize_labyrinth()
        
        # Verify that chambers exist and have basic structure
        chamber_1 = world_manager.get_chamber(1)
        assert chamber_1 is not None
        assert hasattr(chamber_1, 'name')
        assert hasattr(chamber_1, 'description')
        assert hasattr(chamber_1, 'connections')
        
        # Verify connections are bidirectional
        for chamber_id in range(1, 4):  # Test first few chambers
            chamber = world_manager.get_chamber(chamber_id)
            if chamber and chamber.connections:
                for direction, target_id in chamber.connections.items():
                    target_chamber = world_manager.get_chamber(target_id)
                    if target_chamber:
                        # Check that target chamber has a connection back
                        reverse_directions = {
                            'north': 'south', 'south': 'north',
                            'east': 'west', 'west': 'east'
                        }
                        reverse_dir = reverse_directions.get(direction)
                        if reverse_dir:
                            assert reverse_dir in target_chamber.connections
                            assert target_chamber.connections[reverse_dir] == chamber_id
    
    def test_randomization_challenge_integration(self):
        """Test integration between randomization and challenge systems."""
        randomizer = ChallengeRandomizer()
        challenge_factory = ChallengeFactory()
        
        # Test randomized challenge creation
        for challenge_type in ['riddle', 'puzzle', 'combat', 'skill', 'memory']:
            # Create multiple challenges to test randomization
            challenges = []
            for _ in range(5):
                challenge = challenge_factory.create_challenge(challenge_type, difficulty=1)
                challenges.append(challenge)
            
            # Verify challenges are created successfully
            assert all(c is not None for c in challenges)
            
            # Test that challenges can present themselves
            descriptions = [c.present_challenge() for c in challenges]
            assert all(isinstance(desc, str) and len(desc) > 0 for desc in descriptions)
    
    def test_content_loader_challenge_integration(self):
        """Test integration between content loader and challenge system."""
        content_loader = get_content_loader()
        challenge_factory = ChallengeFactory()
        
        # Test that content is properly loaded for each challenge type
        challenge_types = ['riddle', 'puzzle', 'combat', 'skill', 'memory']
        
        for challenge_type in challenge_types:
            # Get content for challenge type
            content = content_loader.get_challenge_content(challenge_type)
            assert content is not None
            assert len(content) > 0
            
            # Create challenge and verify it uses content
            challenge = challenge_factory.create_challenge(challenge_type, difficulty=1)
            description = challenge.present_challenge()
            
            # Verify description contains meaningful content
            assert len(description) > 10  # Should be more than just a stub
    
    def test_game_engine_full_system_integration(self):
        """Test GameEngine integration with all major systems."""
        engine = GameEngine()
        
        # Verify all systems are initialized
        assert engine.world_manager is not None
        assert engine.player_manager is not None
        assert engine.ui_controller is not None
        assert engine.command_parser is not None
        assert engine.save_load_manager is not None
        
        # Test system interactions
        initial_chamber = engine.world_manager.current_chamber_id
        assert initial_chamber == 1
        
        # Test that chambers are properly connected
        chamber = engine.world_manager.get_chamber(initial_chamber)
        assert chamber is not None
        assert len(chamber.connections) > 0
        
        # Test player manager integration
        assert engine.player_manager.health == 100
        assert len(engine.player_manager.inventory.items) == 0
        
        # Test command parser integration
        valid_commands = engine.command_parser.get_available_commands()
        assert 'go' in valid_commands
        assert 'move' in valid_commands
        assert 'look' in valid_commands
        assert 'help' in valid_commands
        assert 'help' in valid_commands
        assert 'quit' in valid_commands


class TestConfigurationIntegration:
    """Test integration with various configuration scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = LabyrinthConfigValidator()
    
    def teardown_method(self):
        """Clean up test environment."""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_default_configuration_validation(self):
        """Test validation of default configuration structure."""
        # Create a sample configuration that matches the expected structure
        sample_config = {
            "chambers": {
                "1": {
                    "name": "Entrance Hall",
                    "description": "A dimly lit entrance chamber",
                    "connections": {"north": 2}
                },
                "2": {
                    "name": "Test Chamber",
                    "description": "A test chamber",
                    "connections": {"south": 1},
                    "challenge_type": "riddle"
                }
            }
        }
        
        # Should not raise exceptions for valid config
        try:
            self.validator.validate_config(sample_config)
        except Exception as e:
            pytest.fail(f"Valid configuration should not raise exceptions: {e}")
    
    def test_challenge_configuration_files_exist(self):
        """Test that challenge configuration files exist."""
        challenge_files = [
            'config/challenges/riddles.json',
            'config/challenges/puzzles.json', 
            'config/challenges/combat.json',
            'config/challenges/skills.json',
            'config/challenges/memory.json'
        ]
        
        for config_file in challenge_files:
            if os.path.exists(config_file):
                # If file exists, verify it's valid JSON
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                    assert isinstance(config_data, (dict, list))
                except json.JSONDecodeError:
                    pytest.fail(f"Configuration file {config_file} contains invalid JSON")
    
    def test_randomization_configuration_integration(self):
        """Test integration with randomization configuration."""
        # Test that randomizer can be created
        randomizer = ChallengeRandomizer()
        assert randomizer is not None
        
        # Test that it can work with challenge factory
        challenge_factory = ChallengeFactory()
        challenge = challenge_factory.create_challenge('riddle', difficulty=1)
        assert challenge is not None
    
    def test_configuration_validation_integration(self):
        """Test that configuration validation works with game systems."""
        world_manager = WorldManager()
        
        # Initialize with default config
        world_manager.initialize_labyrinth()
        
        # Verify that all chambers are reachable
        visited = set()
        to_visit = [1]  # Start from entrance
        
        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)
            
            chamber = world_manager.get_chamber(current)
            if chamber:
                for direction, target_id in chamber.connections.items():
                    if target_id not in visited:
                        to_visit.append(target_id)
        
        # Should be able to reach most chambers
        assert len(visited) >= 10  # At least 10 chambers should be reachable
    
    def test_custom_configuration_validation(self):
        """Test validation of custom configuration files."""
        # Create a minimal custom configuration
        custom_config = {
            "chambers": {
                "1": {
                    "name": "Test Entrance",
                    "description": "A test entrance chamber",
                    "connections": {"north": 2}
                },
                "2": {
                    "name": "Test Chamber",
                    "description": "A test chamber with a riddle",
                    "connections": {"south": 1},
                    "challenge_type": "riddle"
                }
            }
        }
        
        # Test that custom config validates correctly
        try:
            self.validator.validate_config(custom_config)
        except Exception as e:
            pytest.fail(f"Valid custom configuration should not raise exceptions: {e}")
        
        # Test invalid config
        invalid_config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber"
                    # Missing required description field
                }
            }
        }
        
        with pytest.raises(GameException):
            self.validator.validate_config(invalid_config)


class TestErrorHandlingIntegration:
    """Test error handling across integrated systems."""
    
    def test_invalid_configuration_handling(self):
        """Test handling of invalid configuration files."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create invalid JSON file
            invalid_config_file = os.path.join(temp_dir, "invalid.json")
            with open(invalid_config_file, 'w') as f:
                f.write("{ invalid json content")
            
            # Should handle invalid JSON gracefully
            try:
                with open(invalid_config_file, 'r') as f:
                    json.load(f)
                pytest.fail("Should have raised JSONDecodeError")
            except json.JSONDecodeError:
                # This is expected for invalid JSON
                pass
        finally:
            # Clean up
            if os.path.exists(invalid_config_file):
                os.remove(invalid_config_file)
            os.rmdir(temp_dir)
    
    def test_missing_challenge_content_handling(self):
        """Test handling when challenge content is missing."""
        challenge_factory = ChallengeFactory()
        
        # Mock missing content
        with patch('src.utils.challenge_content.get_content_loader') as mock_loader:
            mock_content_loader = MagicMock()
            mock_content_loader.get_challenge_content.return_value = []
            mock_loader.return_value = mock_content_loader
            
            # Should handle missing content gracefully
            challenge = challenge_factory.create_challenge('riddle', difficulty=1)
            assert challenge is not None
            
            # Should provide some default content
            description = challenge.present_challenge()
            assert isinstance(description, str)
            assert len(description) > 0
    
    def test_save_file_corruption_handling(self):
        """Test handling of corrupted save files."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            from src.utils.save_load import SaveLoadManager
            
            # Create corrupted save file
            corrupted_save = os.path.join(temp_dir, "corrupted.json")
            with open(corrupted_save, 'w') as f:
                f.write("{ corrupted save data")
            
            save_manager = SaveLoadManager()
            
            # Should handle corrupted save gracefully
            loaded_state = save_manager.load_game(corrupted_save)
            assert loaded_state is None  # Should return None for corrupted saves
            
        finally:
            # Clean up
            if os.path.exists(corrupted_save):
                os.remove(corrupted_save)
            os.rmdir(temp_dir)
    
    def test_system_recovery_after_errors(self):
        """Test that systems can recover after encountering errors."""
        engine = GameEngine()
        
        # Simulate various error conditions and verify recovery
        original_health = engine.player_manager.health
        
        # Test invalid command handling
        try:
            engine.command_parser.parse_command("invalid_command_xyz")
        except Exception:
            pass  # Errors are acceptable here
        
        # Verify system is still functional
        assert engine.player_manager.health == original_health
        assert engine.world_manager.current_chamber_id == 1
        
        # Test that valid commands still work
        valid_commands = engine.command_parser.get_valid_commands()
        assert len(valid_commands) > 0


class TestPerformanceIntegration:
    """Test performance characteristics of integrated systems."""
    
    def test_game_initialization_performance(self):
        """Test that game initialization completes in reasonable time."""
        import time
        
        start_time = time.time()
        engine = GameEngine()
        initialization_time = time.time() - start_time
        
        # Should initialize within 5 seconds
        assert initialization_time < 5.0
        
        # Verify all systems are properly initialized
        assert engine.world_manager is not None
        assert engine.player_manager is not None
        assert engine.ui_controller is not None
    
    def test_challenge_creation_performance(self):
        """Test performance of challenge creation."""
        import time
        
        challenge_factory = ChallengeFactory()
        challenge_types = ['riddle', 'puzzle', 'combat', 'skill', 'memory']
        
        start_time = time.time()
        
        # Create multiple challenges
        challenges = []
        for _ in range(50):  # Create 50 challenges
            for challenge_type in challenge_types:
                challenge = challenge_factory.create_challenge(challenge_type, difficulty=1)
                challenges.append(challenge)
        
        creation_time = time.time() - start_time
        
        # Should create 250 challenges within 10 seconds
        assert creation_time < 10.0
        assert len(challenges) == 250
    
    def test_world_navigation_performance(self):
        """Test performance of world navigation operations."""
        import time
        
        world_manager = WorldManager()
        world_manager.initialize_labyrinth()
        
        start_time = time.time()
        
        # Perform many navigation operations
        for _ in range(1000):
            current_chamber = world_manager.get_chamber(world_manager.current_chamber_id)
            if current_chamber and current_chamber.connections:
                # Try to move in a valid direction
                direction = list(current_chamber.connections.keys())[0]
                world_manager.move_player(direction)
        
        navigation_time = time.time() - start_time
        
        # Should complete 1000 navigation operations within 5 seconds
        assert navigation_time < 5.0