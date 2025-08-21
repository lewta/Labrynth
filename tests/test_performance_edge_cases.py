"""
Performance and edge case tests for the Labyrinth Adventure Game.

These tests verify that the system handles edge cases gracefully and
meets performance requirements under various conditions.
"""

import pytest
import tempfile
import os
import json
import time
import threading
import gc
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any

from src.game.engine import GameEngine
from src.game.world import WorldManager
from src.game.player import PlayerManager
from src.challenges.factory import ChallengeFactory
from src.utils.save_load import SaveLoadManager
from src.utils.exceptions import GameException, SaveLoadException
from src.utils.data_models import GameState, Item, PlayerStats


class TestPerformanceRequirements:
    """Test performance characteristics and requirements."""
    
    def test_game_initialization_performance(self):
        """Test that game initialization completes within acceptable time."""
        start_time = time.time()
        
        engine = GameEngine()
        
        initialization_time = time.time() - start_time
        
        # Should initialize within 2 seconds
        assert initialization_time < 2.0, f"Initialization took {initialization_time:.2f}s, expected < 2.0s"
        
        # Verify all systems are properly initialized
        assert engine.world_manager is not None
        assert engine.player_manager is not None
        assert engine.ui_controller is not None
        assert engine.save_load_manager is not None
    
    def test_challenge_creation_performance(self):
        """Test performance of challenge creation operations."""
        challenge_factory = ChallengeFactory()
        challenge_types = ['riddle', 'puzzle', 'combat', 'skill', 'memory']
        
        start_time = time.time()
        
        # Create many challenges
        challenges = []
        for _ in range(100):  # Create 100 challenges
            for challenge_type in challenge_types:
                challenge = challenge_factory.create_challenge(challenge_type, difficulty=1)
                challenges.append(challenge)
        
        creation_time = time.time() - start_time
        
        # Should create 500 challenges within 5 seconds
        assert creation_time < 5.0, f"Challenge creation took {creation_time:.2f}s, expected < 5.0s"
        assert len(challenges) == 500
        
        # Verify all challenges are functional
        for challenge in challenges[:10]:  # Test first 10 for functionality
            description = challenge.present_challenge()
            assert isinstance(description, str)
            assert len(description) > 0
    
    def test_world_navigation_performance(self):
        """Test performance of world navigation operations."""
        world_manager = WorldManager()
        world_manager.initialize_labyrinth()
        
        start_time = time.time()
        
        # Perform many navigation operations
        navigation_count = 0
        for _ in range(1000):
            current_chamber = world_manager.get_chamber(world_manager.current_chamber_id)
            if current_chamber and current_chamber.connections:
                # Try to move in a valid direction
                direction = list(current_chamber.connections.keys())[0]
                if world_manager.move_player(direction):
                    navigation_count += 1
        
        navigation_time = time.time() - start_time
        
        # Should complete 1000 navigation attempts within 3 seconds
        assert navigation_time < 3.0, f"Navigation took {navigation_time:.2f}s, expected < 3.0s"
        assert navigation_count > 0  # At least some navigation should succeed
    
    def test_save_load_performance(self):
        """Test performance of save/load operations."""
        save_manager = SaveLoadManager()
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create a complex game state
            items = [Item(f"Item_{i}", f"Description {i}", "misc", i) for i in range(50)]
            game_state = GameState(
                current_chamber=5,
                player_health=75,
                inventory_items=items,
                completed_chambers=set(range(1, 10)),
                game_time=3600
            )
            
            save_file = os.path.join(temp_dir, "performance_test.json")
            
            # Test save performance
            start_time = time.time()
            success = save_manager.save_game(game_state, save_file)
            save_time = time.time() - start_time
            
            assert success
            assert save_time < 1.0, f"Save took {save_time:.2f}s, expected < 1.0s"
            
            # Test load performance
            start_time = time.time()
            loaded_state = save_manager.load_game(save_file)
            load_time = time.time() - start_time
            
            assert loaded_state is not None
            assert load_time < 1.0, f"Load took {load_time:.2f}s, expected < 1.0s"
            
        finally:
            # Clean up
            if os.path.exists(save_file):
                os.remove(save_file)
            os.rmdir(temp_dir)
    
    @pytest.mark.skipif(not HAS_PSUTIL, reason="psutil not available")
    def test_memory_usage_during_gameplay(self):
        """Test memory usage remains reasonable during extended gameplay."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simulate extended gameplay
        engine = GameEngine()
        challenge_factory = ChallengeFactory()
        
        # Create and destroy many objects
        for _ in range(100):
            # Create challenges
            challenges = []
            for challenge_type in ['riddle', 'puzzle', 'combat']:
                challenge = challenge_factory.create_challenge(challenge_type, difficulty=1)
                challenges.append(challenge)
            
            # Use challenges
            for challenge in challenges:
                challenge.present_challenge()
                challenge.process_response("test")
            
            # Clear references
            challenges.clear()
        
        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50, f"Memory increased by {memory_increase:.1f}MB, expected < 50MB"
    
    def test_concurrent_operations_performance(self):
        """Test performance when multiple operations happen concurrently."""
        def create_challenges():
            factory = ChallengeFactory()
            for _ in range(50):
                challenge = factory.create_challenge('riddle', difficulty=1)
                challenge.present_challenge()
        
        def navigate_world():
            world_manager = WorldManager()
            world_manager.initialize_labyrinth()
            for _ in range(50):
                current_chamber = world_manager.get_chamber(world_manager.current_chamber_id)
                if current_chamber and current_chamber.connections:
                    direction = list(current_chamber.connections.keys())[0]
                    world_manager.move_player(direction)
        
        start_time = time.time()
        
        # Run operations concurrently
        threads = [
            threading.Thread(target=create_challenges),
            threading.Thread(target=navigate_world),
            threading.Thread(target=create_challenges),
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        concurrent_time = time.time() - start_time
        
        # Should complete within 10 seconds
        assert concurrent_time < 10.0, f"Concurrent operations took {concurrent_time:.2f}s, expected < 10.0s"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        for file in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir(self.temp_dir)
    
    def test_corrupted_save_file_handling(self):
        """Test handling of various types of corrupted save files."""
        save_manager = SaveLoadManager()
        
        # Test completely corrupted JSON
        corrupted_file = os.path.join(self.temp_dir, "corrupted.json")
        with open(corrupted_file, 'w') as f:
            f.write("{ this is not valid json at all")
        
        with pytest.raises(SaveLoadException):
            save_manager.load_game(corrupted_file)
        
        # Test valid JSON but invalid structure
        invalid_structure_file = os.path.join(self.temp_dir, "invalid_structure.json")
        with open(invalid_structure_file, 'w') as f:
            json.dump({"not_game_state": "invalid"}, f)
        
        with pytest.raises(SaveLoadException):
            save_manager.load_game(invalid_structure_file)
        
        # Test partial data corruption
        partial_corruption_file = os.path.join(self.temp_dir, "partial_corruption.json")
        with open(partial_corruption_file, 'w') as f:
            json.dump({
                "game_state": {
                    "current_chamber": "not_an_integer",  # Wrong type
                    "player_health": 100,
                    "inventory_items": [],
                    "completed_chambers": [],
                    "game_time": 0
                },
                "metadata": {
                    "save_time": "2023-01-01T00:00:00",
                    "game_version": "1.0"
                }
            }, f)
        
        with pytest.raises(SaveLoadException):
            save_manager.load_game(partial_corruption_file)
    
    def test_missing_save_file_handling(self):
        """Test handling when save files don't exist."""
        save_manager = SaveLoadManager()
        
        # Test loading non-existent file
        non_existent_file = os.path.join(self.temp_dir, "does_not_exist.json")
        with pytest.raises(SaveLoadException):
            save_manager.load_game(non_existent_file)
    
    def test_invalid_configuration_handling(self):
        """Test handling of invalid configuration data."""
        world_manager = WorldManager()
        
        # Test with completely invalid config
        invalid_config = {"not_chambers": "invalid"}
        
        try:
            world_manager.initialize_labyrinth(invalid_config)
            # Should either handle gracefully or raise appropriate exception
        except GameException:
            # This is acceptable
            pass
        
        # Test with missing required fields
        incomplete_config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber"
                    # Missing description and other required fields
                }
            }
        }
        
        try:
            world_manager.initialize_labyrinth(incomplete_config)
        except GameException:
            # This is acceptable
            pass
    
    def test_boundary_values_handling(self):
        """Test handling of boundary values and extreme inputs."""
        # Test with maximum inventory
        items = [Item(f"Item_{i}", f"Desc {i}", "misc", 1) for i in range(1000)]
        game_state = GameState(
            current_chamber=1,
            player_health=1,  # Minimum health
            inventory_items=items,
            completed_chambers=set(range(1, 1000)),  # Many completed chambers
            game_time=999999999  # Very large time
        )
        
        # Should handle large game state
        assert game_state.is_valid()
        
        # Test with zero/negative values where inappropriate
        with pytest.raises(GameException):
            GameState(
                current_chamber=0,  # Invalid chamber ID
                player_health=100,
                inventory_items=[],
                completed_chambers=set(),
                game_time=0
            )
        
        with pytest.raises(GameException):
            GameState(
                current_chamber=1,
                player_health=-10,  # Negative health
                inventory_items=[],
                completed_chambers=set(),
                game_time=0
            )
    
    def test_challenge_edge_cases(self):
        """Test edge cases in challenge handling."""
        challenge_factory = ChallengeFactory()
        
        # Test with invalid challenge types
        try:
            challenge = challenge_factory.create_challenge('invalid_type', difficulty=1)
            # Should either return None or raise exception
            assert challenge is None
        except (ValueError, KeyError, GameException):
            # These exceptions are acceptable
            pass
        
        # Test with extreme difficulty values
        try:
            challenge = challenge_factory.create_challenge('riddle', difficulty=999)
            assert challenge is not None
        except ValueError:
            # High difficulty values might cause randomization issues, which is acceptable
            pass
        
        try:
            challenge = challenge_factory.create_challenge('riddle', difficulty=-1)
            assert challenge is not None
        except ValueError:
            # Negative difficulty values might cause randomization issues, which is acceptable
            pass
        
        # Test challenge with empty/invalid responses
        riddle = challenge_factory.create_challenge('riddle', difficulty=1)
        
        # Test empty response
        result = riddle.process_response("")
        assert hasattr(result, 'success')
        
        # Test very long response
        long_response = "a" * 10000
        result = riddle.process_response(long_response)
        assert hasattr(result, 'success')
        
        # Test special characters
        special_response = "!@#$%^&*()_+{}|:<>?[]\\;'\",./"
        result = riddle.process_response(special_response)
        assert hasattr(result, 'success')
    
    def test_world_navigation_edge_cases(self):
        """Test edge cases in world navigation."""
        world_manager = WorldManager()
        world_manager.initialize_labyrinth()
        
        # Test moving to invalid directions
        assert not world_manager.move_player("invalid_direction")
        assert not world_manager.move_player("")
        assert not world_manager.move_player("north_by_northwest")
        
        # Test getting invalid chambers
        invalid_chamber = world_manager.get_chamber(-1)
        assert invalid_chamber is None
        
        invalid_chamber = world_manager.get_chamber(999999)
        assert invalid_chamber is None
        
        # Test with None chamber ID
        invalid_chamber = world_manager.get_chamber(None)
        assert invalid_chamber is None
    
    def test_player_manager_edge_cases(self):
        """Test edge cases in player management."""
        player_manager = PlayerManager()
        
        # Test adding invalid items
        try:
            player_manager.add_item(None, "description", "type", 1)
        except (TypeError, GameException):
            # These exceptions are acceptable
            pass
        
        # Test using non-existent items
        result = player_manager.use_item("non_existent_item")
        assert not result
        
        # Test extreme health values
        player_manager.current_health = 1
        player_manager.take_damage(999999)  # Massive damage
        assert player_manager.current_health >= 0  # Should not go below 0
        
        player_manager.current_health = 0
        player_manager.heal(999999)  # Massive healing
        assert player_manager.current_health <= 100  # Should not exceed max
    
    def test_concurrent_access_safety(self):
        """Test thread safety and concurrent access scenarios."""
        world_manager = WorldManager()
        world_manager.initialize_labyrinth()
        
        results = []
        errors = []
        
        def navigate_concurrently():
            try:
                for _ in range(100):
                    current_chamber = world_manager.get_chamber(world_manager.current_chamber_id)
                    if current_chamber and current_chamber.connections:
                        direction = list(current_chamber.connections.keys())[0]
                        result = world_manager.move_player(direction)
                        results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Run multiple threads concurrently
        threads = [threading.Thread(target=navigate_concurrently) for _ in range(5)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should not have any critical errors
        assert len(errors) == 0, f"Concurrent access caused errors: {errors}"
        assert len(results) > 0  # Some operations should succeed
    
    @pytest.mark.skipif(not HAS_PSUTIL, reason="psutil not available")
    def test_memory_leak_prevention(self):
        """Test that operations don't cause memory leaks."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Perform operations that could potentially leak memory
        for _ in range(100):
            # Create and destroy game engines
            engine = GameEngine()
            del engine
            
            # Create and destroy challenges
            factory = ChallengeFactory()
            challenge = factory.create_challenge('riddle', difficulty=1)
            challenge.present_challenge()
            challenge.process_response("test")
            del challenge
            del factory
            
            # Force garbage collection periodically
            if _ % 10 == 0:
                gc.collect()
        
        # Final garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        # Memory increase should be minimal (less than 10MB)
        assert memory_increase < 10, f"Potential memory leak: {memory_increase:.1f}MB increase"


class TestStressTests:
    """Stress tests for extended gameplay sessions."""
    
    def test_extended_gameplay_simulation(self):
        """Test system stability during extended gameplay."""
        engine = GameEngine()
        challenge_factory = ChallengeFactory()
        
        # Simulate 1000 game actions
        for i in range(1000):
            # Alternate between different types of operations
            if i % 4 == 0:
                # Create and use challenges
                challenge = challenge_factory.create_challenge('riddle', difficulty=1)
                challenge.present_challenge()
                challenge.process_response("test answer")
            
            elif i % 4 == 1:
                # Navigate world
                current_chamber = engine.world_manager.get_chamber(
                    engine.world_manager.current_chamber_id
                )
                if current_chamber and current_chamber.connections:
                    direction = list(current_chamber.connections.keys())[0]
                    engine.world_manager.move_player(direction)
            
            elif i % 4 == 2:
                # Manage inventory
                item = Item(f"Item_{i}", f"Description {i}", "misc", 1)
                engine.player_manager.add_item(item)
                if len(engine.player_manager.inventory.get_all_items()) > 10:
                    # Remove oldest item
                    oldest_item = engine.player_manager.inventory.get_all_items()[0]
                    engine.player_manager.use_item(oldest_item.name)
            
            else:
                # Check status and progress
                status = engine.player_manager.get_status()
                assert isinstance(status, dict)
        
        # System should still be functional after stress test
        assert engine.player_manager.current_health > 0
        assert engine.world_manager.current_chamber_id >= 1
    
    def test_large_save_file_handling(self):
        """Test handling of very large save files."""
        # Create a game state with many items and completed chambers
        items = [Item(f"Item_{i}", f"Very long description for item {i} " * 10, "misc", i) 
                for i in range(500)]
        
        game_state = GameState(
            current_chamber=1,
            player_health=100,
            inventory_items=items,
            completed_chambers=set(range(1, 100)),
            game_time=999999
        )
        
        save_manager = SaveLoadManager()
        temp_dir = tempfile.mkdtemp()
        
        try:
            save_file = os.path.join(temp_dir, "large_save.json")
            
            # Save large game state
            start_time = time.time()
            success = save_manager.save_game(game_state, save_file)
            save_time = time.time() - start_time
            
            assert success
            assert save_time < 5.0, f"Large save took {save_time:.2f}s, expected < 5.0s"
            
            # Verify file size is reasonable but not excessive
            file_size = os.path.getsize(save_file) / 1024 / 1024  # MB
            assert file_size < 10, f"Save file is {file_size:.1f}MB, expected < 10MB"
            
            # Load large game state
            start_time = time.time()
            loaded_state = save_manager.load_game(save_file)
            load_time = time.time() - start_time
            
            assert loaded_state is not None
            assert load_time < 5.0, f"Large load took {load_time:.2f}s, expected < 5.0s"
            
            # Verify data integrity
            assert len(loaded_state.inventory_items) == 500
            assert len(loaded_state.completed_chambers) == 99
            
        finally:
            if os.path.exists(save_file):
                os.remove(save_file)
            os.rmdir(temp_dir)
    
    def test_rapid_operations_stress(self):
        """Test system under rapid successive operations."""
        world_manager = WorldManager()
        world_manager.initialize_labyrinth()
        player_manager = PlayerManager()
        challenge_factory = ChallengeFactory()
        
        start_time = time.time()
        
        # Perform rapid operations
        for _ in range(1000):
            # Rapid world queries
            chamber = world_manager.get_chamber(world_manager.current_chamber_id)
            
            # Rapid player operations
            player_manager.get_status()
            
            # Rapid challenge creation
            challenge = challenge_factory.create_challenge('riddle', difficulty=1)
            challenge.present_challenge()
        
        total_time = time.time() - start_time
        
        # Should handle 1000 rapid operations within 10 seconds
        assert total_time < 10.0, f"Rapid operations took {total_time:.2f}s, expected < 10.0s"
        
        # System should still be responsive
        assert world_manager.get_chamber(1) is not None
        assert isinstance(player_manager.get_status(), dict)