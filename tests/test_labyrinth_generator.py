"""Tests for labyrinth generation and randomization."""

import pytest
from unittest.mock import patch, MagicMock

from src.utils.labyrinth_generator import (
    LabyrinthGenerator, GenerationConfig, LabyrinthLayout,
    create_randomized_labyrinth, validate_labyrinth_solvability
)
from src.utils.exceptions import GameException


class TestGenerationConfig:
    """Test generation configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = GenerationConfig()
        
        assert config.chamber_count == 13
        assert config.layout == LabyrinthLayout.HYBRID
        assert config.connectivity == 0.3
        assert config.ensure_solvable is True
        assert config.min_path_length == 5
        assert config.max_dead_ends == 3
        assert config.seed is None
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = GenerationConfig(
            chamber_count=10,
            layout=LabyrinthLayout.LINEAR,
            connectivity=0.5,
            ensure_solvable=False,
            min_path_length=3,
            max_dead_ends=5,
            seed=42
        )
        
        assert config.chamber_count == 10
        assert config.layout == LabyrinthLayout.LINEAR
        assert config.connectivity == 0.5
        assert config.ensure_solvable is False
        assert config.min_path_length == 3
        assert config.max_dead_ends == 5
        assert config.seed == 42
    
    def test_invalid_chamber_count(self):
        """Test invalid chamber count raises exception."""
        with pytest.raises(GameException, match="Chamber count must be at least 3"):
            GenerationConfig(chamber_count=2)
    
    def test_invalid_connectivity(self):
        """Test invalid connectivity raises exception."""
        with pytest.raises(GameException, match="Connectivity must be between 0.0 and 1.0"):
            GenerationConfig(connectivity=1.5)
        
        with pytest.raises(GameException, match="Connectivity must be between 0.0 and 1.0"):
            GenerationConfig(connectivity=-0.1)
    
    def test_invalid_min_path_length(self):
        """Test invalid minimum path length raises exception."""
        with pytest.raises(GameException, match="Minimum path length must be at least 2"):
            GenerationConfig(min_path_length=1)


class TestLabyrinthGenerator:
    """Test labyrinth generator functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = GenerationConfig(chamber_count=5, seed=42)
        self.generator = LabyrinthGenerator(self.config)
    
    def test_initialization(self):
        """Test generator initialization."""
        assert self.generator.config == self.config
        assert self.generator._random is not None
    
    def test_generate_linear_layout(self):
        """Test linear layout generation."""
        self.config.layout = LabyrinthLayout.LINEAR
        connections = self.generator._generate_linear_layout()
        
        assert len(connections) == 5
        
        # Check linear connections
        assert connections[1] == {"east": 2}
        assert connections[2] == {"west": 1, "east": 3}
        assert connections[3] == {"west": 2, "east": 4}
        assert connections[4] == {"west": 3, "east": 5}
        assert connections[5] == {"west": 4}
    
    def test_generate_circular_layout(self):
        """Test circular layout generation."""
        self.config.layout = LabyrinthLayout.CIRCULAR
        connections = self.generator._generate_circular_layout()
        
        assert len(connections) == 5
        
        # Check circular connections
        assert connections[1]["east"] == 2
        assert connections[1]["west"] == 5
        assert connections[5]["east"] == 1
        assert connections[5]["west"] == 4
    
    def test_generate_tree_layout(self):
        """Test tree layout generation."""
        self.config.layout = LabyrinthLayout.TREE
        connections = self.generator._generate_tree_layout()
        
        assert len(connections) == 5
        
        # Verify all chambers are connected
        reachable = self.generator._get_reachable_chambers(connections, 1)
        assert len(reachable) == 5
    
    def test_generate_grid_layout(self):
        """Test grid layout generation."""
        self.config.layout = LabyrinthLayout.GRID
        connections = self.generator._generate_grid_layout()
        
        assert len(connections) == 5
        
        # Verify all chambers exist
        for i in range(1, 6):
            assert i in connections
    
    def test_generate_random_layout(self):
        """Test random layout generation."""
        self.config.layout = LabyrinthLayout.RANDOM
        connections = self.generator._generate_random_layout()
        
        assert len(connections) == 5
        
        # Verify connectivity
        reachable = self.generator._get_reachable_chambers(connections, 1)
        assert len(reachable) == 5
    
    def test_ensure_solvability(self):
        """Test solvability enforcement."""
        # Create a disconnected layout
        connections = {
            1: {"east": 2},
            2: {"west": 1},
            3: {"east": 4},
            4: {"west": 3},
            5: {}
        }
        
        # Should connect all chambers
        fixed_connections = self.generator._ensure_solvability(connections)
        reachable = self.generator._get_reachable_chambers(fixed_connections, 1)
        assert len(reachable) == 5
    
    def test_get_reachable_chambers(self):
        """Test reachable chamber detection."""
        connections = {
            1: {"east": 2},
            2: {"west": 1, "north": 3},
            3: {"south": 2},
            4: {"east": 5},
            5: {"west": 4}
        }
        
        reachable = self.generator._get_reachable_chambers(connections, 1)
        assert reachable == {1, 2, 3}
        
        reachable_from_4 = self.generator._get_reachable_chambers(connections, 4)
        assert reachable_from_4 == {4, 5}
    
    def test_add_connectivity(self):
        """Test connectivity addition."""
        # Start with minimal connections
        connections = {
            1: {"east": 2},
            2: {"west": 1, "east": 3},
            3: {"west": 2, "east": 4},
            4: {"west": 3, "east": 5},
            5: {"west": 4}
        }
        
        # Add connectivity
        self.config.connectivity = 0.5
        enhanced_connections = self.generator._add_connectivity(connections)
        
        # Should have more connections than before
        original_count = sum(len(conns) for conns in connections.values())
        enhanced_count = sum(len(conns) for conns in enhanced_connections.values())
        assert enhanced_count >= original_count
    
    def test_validate_generated_labyrinth(self):
        """Test labyrinth validation."""
        # Valid labyrinth
        valid_connections = {
            1: {"east": 2},
            2: {"west": 1, "east": 3},
            3: {"west": 2}
        }
        
        # Should not raise exception
        self.config.chamber_count = 3
        self.generator._validate_generated_labyrinth(valid_connections)
        
        # Invalid labyrinth - missing chamber
        invalid_connections = {
            1: {"east": 2},
            2: {"west": 1}
        }
        
        with pytest.raises(GameException, match="missing chambers"):
            self.generator._validate_generated_labyrinth(invalid_connections)
        
        # Invalid labyrinth - unreachable chamber
        unreachable_connections = {
            1: {"east": 2},
            2: {"west": 1},
            3: {}
        }
        
        with pytest.raises(GameException, match="unreachable chambers"):
            self.generator._validate_generated_labyrinth(unreachable_connections)
    
    def test_create_chamber_data(self):
        """Test chamber data creation."""
        connections = {
            1: {"east": 2},
            2: {"west": 1, "east": 3},
            3: {"west": 2}
        }
        
        chamber_data = self.generator._create_chamber_data(connections)
        
        assert len(chamber_data) == 3
        
        for chamber_id in ["1", "2", "3"]:
            assert chamber_id in chamber_data
            chamber = chamber_data[chamber_id]
            
            assert "name" in chamber
            assert "description" in chamber
            assert "connections" in chamber
            assert "challenge_type" in chamber
            
            assert isinstance(chamber["name"], str)
            assert isinstance(chamber["description"], str)
            assert isinstance(chamber["connections"], dict)
            assert chamber["challenge_type"] in ["riddle", "puzzle", "combat", "skill", "memory"]
    
    def test_generate_complete_labyrinth(self):
        """Test complete labyrinth generation."""
        labyrinth = self.generator.generate_labyrinth()
        
        assert "starting_chamber" in labyrinth
        assert "chambers" in labyrinth
        assert "generation_info" in labyrinth
        
        assert labyrinth["starting_chamber"] == 1
        assert len(labyrinth["chambers"]) == 5
        
        generation_info = labyrinth["generation_info"]
        assert "layout" in generation_info
        assert "connectivity" in generation_info
        assert "chamber_count" in generation_info
        assert "seed" in generation_info
    
    def test_generate_multiple_variants(self):
        """Test generating multiple variants."""
        variants = self.generator.generate_multiple_variants(3)
        
        assert len(variants) == 3
        
        for i, variant in enumerate(variants):
            assert variant["generation_info"]["variant_number"] == i + 1
            assert len(variant["chambers"]) == 5
    
    def test_reproducible_generation(self):
        """Test that same seed produces same results."""
        config1 = GenerationConfig(chamber_count=5, seed=12345)
        generator1 = LabyrinthGenerator(config1)
        
        config2 = GenerationConfig(chamber_count=5, seed=12345)
        generator2 = LabyrinthGenerator(config2)
        
        labyrinth1 = generator1.generate_labyrinth()
        labyrinth2 = generator2.generate_labyrinth()
        
        # Should have same structure
        assert labyrinth1["chambers"].keys() == labyrinth2["chambers"].keys()
        
        # Connections should be the same
        for chamber_id in labyrinth1["chambers"]:
            connections1 = labyrinth1["chambers"][chamber_id]["connections"]
            connections2 = labyrinth2["chambers"][chamber_id]["connections"]
            assert connections1 == connections2


class TestLabyrinthLayouts:
    """Test different labyrinth layouts."""
    
    @pytest.mark.parametrize("layout", [
        LabyrinthLayout.LINEAR,
        LabyrinthLayout.CIRCULAR,
        LabyrinthLayout.TREE,
        LabyrinthLayout.GRID,
        LabyrinthLayout.RANDOM,
        LabyrinthLayout.HYBRID
    ])
    def test_all_layouts_generate_solvable_labyrinths(self, layout):
        """Test that all layouts generate solvable labyrinths."""
        config = GenerationConfig(
            chamber_count=8,
            layout=layout,
            seed=42
        )
        
        generator = LabyrinthGenerator(config)
        labyrinth = generator.generate_labyrinth()
        
        # Should be solvable
        assert validate_labyrinth_solvability(labyrinth)
        
        # Should have correct number of chambers
        assert len(labyrinth["chambers"]) == 8
    
    def test_different_chamber_counts(self):
        """Test generation with different chamber counts."""
        for count in [3, 5, 10, 15, 20]:
            config = GenerationConfig(chamber_count=count, seed=42)
            generator = LabyrinthGenerator(config)
            labyrinth = generator.generate_labyrinth()
            
            assert len(labyrinth["chambers"]) == count
            assert validate_labyrinth_solvability(labyrinth)
    
    def test_different_connectivity_levels(self):
        """Test generation with different connectivity levels."""
        for connectivity in [0.0, 0.2, 0.5, 0.8, 1.0]:
            config = GenerationConfig(
                chamber_count=8,
                connectivity=connectivity,
                seed=42
            )
            
            generator = LabyrinthGenerator(config)
            labyrinth = generator.generate_labyrinth()
            
            assert validate_labyrinth_solvability(labyrinth)


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_create_randomized_labyrinth(self):
        """Test convenience function for creating randomized labyrinths."""
        labyrinth = create_randomized_labyrinth(
            chamber_count=7,
            layout="linear",
            connectivity=0.2,
            seed=42
        )
        
        assert len(labyrinth["chambers"]) == 7
        assert labyrinth["generation_info"]["layout"] == "linear"
        assert labyrinth["generation_info"]["connectivity"] == 0.2
        assert labyrinth["generation_info"]["seed"] == 42
        assert validate_labyrinth_solvability(labyrinth)
    
    def test_validate_labyrinth_solvability_valid(self):
        """Test solvability validation with valid labyrinth."""
        valid_labyrinth = {
            "starting_chamber": 1,
            "chambers": {
                "1": {
                    "name": "Start",
                    "description": "Starting chamber",
                    "connections": {"east": 2}
                },
                "2": {
                    "name": "Middle",
                    "description": "Middle chamber",
                    "connections": {"west": 1, "east": 3}
                },
                "3": {
                    "name": "End",
                    "description": "End chamber",
                    "connections": {"west": 2}
                }
            }
        }
        
        assert validate_labyrinth_solvability(valid_labyrinth) is True
    
    def test_validate_labyrinth_solvability_invalid(self):
        """Test solvability validation with invalid labyrinth."""
        # Unreachable chamber
        invalid_labyrinth = {
            "starting_chamber": 1,
            "chambers": {
                "1": {
                    "name": "Start",
                    "description": "Starting chamber",
                    "connections": {"east": 2}
                },
                "2": {
                    "name": "Middle",
                    "description": "Middle chamber",
                    "connections": {"west": 1}
                },
                "3": {
                    "name": "Unreachable",
                    "description": "Unreachable chamber",
                    "connections": {}
                }
            }
        }
        
        assert validate_labyrinth_solvability(invalid_labyrinth) is False
        
        # Empty labyrinth
        empty_labyrinth = {"chambers": {}}
        assert validate_labyrinth_solvability(empty_labyrinth) is False
        
        # Malformed labyrinth
        malformed_labyrinth = {"invalid": "data"}
        assert validate_labyrinth_solvability(malformed_labyrinth) is False


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_minimum_chamber_count(self):
        """Test minimum chamber count."""
        config = GenerationConfig(chamber_count=3, seed=42)
        generator = LabyrinthGenerator(config)
        labyrinth = generator.generate_labyrinth()
        
        assert len(labyrinth["chambers"]) == 3
        assert validate_labyrinth_solvability(labyrinth)
    
    def test_large_chamber_count(self):
        """Test large chamber count."""
        config = GenerationConfig(chamber_count=30, seed=42)
        generator = LabyrinthGenerator(config)
        labyrinth = generator.generate_labyrinth()
        
        assert len(labyrinth["chambers"]) == 30
        assert validate_labyrinth_solvability(labyrinth)
    
    def test_zero_connectivity(self):
        """Test zero connectivity (minimal connections)."""
        config = GenerationConfig(
            chamber_count=8,
            connectivity=0.0,
            seed=42
        )
        
        generator = LabyrinthGenerator(config)
        labyrinth = generator.generate_labyrinth()
        
        # Should still be solvable
        assert validate_labyrinth_solvability(labyrinth)
        
        # Should have minimal connections
        total_connections = sum(
            len(chamber_data["connections"]) 
            for chamber_data in labyrinth["chambers"].values()
        )
        
        # Should be close to minimal (2 * (n-1) for tree structure)
        expected_minimal = 2 * (8 - 1)
        assert total_connections >= expected_minimal
    
    def test_maximum_connectivity(self):
        """Test maximum connectivity."""
        config = GenerationConfig(
            chamber_count=6,
            connectivity=1.0,
            seed=42
        )
        
        generator = LabyrinthGenerator(config)
        labyrinth = generator.generate_labyrinth()
        
        assert validate_labyrinth_solvability(labyrinth)
        
        # Should have many connections
        total_connections = sum(
            len(chamber_data["connections"]) 
            for chamber_data in labyrinth["chambers"].values()
        )
        
        # Should be significantly more than minimal
        minimal_connections = 2 * (6 - 1)
        assert total_connections > minimal_connections