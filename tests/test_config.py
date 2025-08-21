"""Unit tests for configuration management."""

import pytest
import json
import tempfile
import os
from src.utils.config import LabyrinthConfigValidator, LabyrinthConfigLoader
from src.utils.exceptions import GameException


class TestLabyrinthConfigValidator:
    """Test cases for LabyrinthConfigValidator class."""
    
    def test_valid_simple_config(self):
        """Test validation of a simple valid configuration."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "A test chamber",
                    "connections": {"north": 2}
                },
                "2": {
                    "name": "Second Chamber",
                    "description": "Another test chamber",
                    "connections": {"south": 1}
                }
            },
            "starting_chamber": 1
        }
        
        validator = LabyrinthConfigValidator()
        # Should not raise any exception
        validator.validate_config(config)
    
    def test_invalid_config_not_dict(self):
        """Test validation with non-dictionary config."""
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Configuration must be a dictionary"):
            validator.validate_config("invalid")
    
    def test_invalid_config_no_chambers(self):
        """Test validation with missing chambers section."""
        config = {"other_data": "value"}
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Configuration must contain 'chambers' section"):
            validator.validate_config(config)
    
    def test_invalid_chambers_not_dict(self):
        """Test validation with chambers not being a dictionary."""
        config = {"chambers": "invalid"}
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="'chambers' must be a dictionary"):
            validator.validate_config(config)
    
    def test_invalid_empty_chambers(self):
        """Test validation with empty chambers dictionary."""
        config = {"chambers": {}}
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Configuration must contain at least one chamber"):
            validator.validate_config(config)
    
    def test_invalid_chamber_id_not_integer(self):
        """Test validation with non-integer chamber ID."""
        config = {
            "chambers": {
                "invalid_id": {
                    "name": "Test Chamber",
                    "description": "A test chamber"
                }
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Chamber ID must be an integer: invalid_id"):
            validator.validate_config(config)
    
    def test_invalid_chamber_id_negative(self):
        """Test validation with negative chamber ID."""
        config = {
            "chambers": {
                "-1": {
                    "name": "Test Chamber",
                    "description": "A test chamber"
                }
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Chamber ID must be positive: -1"):
            validator.validate_config(config)
    
    def test_invalid_chamber_data_not_dict(self):
        """Test validation with chamber data not being a dictionary."""
        config = {
            "chambers": {
                "1": "invalid_chamber_data"
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Chamber 1 data must be a dictionary"):
            validator.validate_config(config)
    
    def test_invalid_chamber_missing_name(self):
        """Test validation with chamber missing name field."""
        config = {
            "chambers": {
                "1": {
                    "description": "A test chamber"
                }
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Chamber 1 missing required field: name"):
            validator.validate_config(config)
    
    def test_invalid_chamber_missing_description(self):
        """Test validation with chamber missing description field."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber"
                }
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Chamber 1 missing required field: description"):
            validator.validate_config(config)
    
    def test_invalid_chamber_empty_name(self):
        """Test validation with chamber having empty name."""
        config = {
            "chambers": {
                "1": {
                    "name": "",
                    "description": "A test chamber"
                }
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Chamber 1 field 'name' must be a non-empty string"):
            validator.validate_config(config)
    
    def test_invalid_chamber_empty_description(self):
        """Test validation with chamber having empty description."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "   "
                }
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Chamber 1 field 'description' must be a non-empty string"):
            validator.validate_config(config)
    
    def test_invalid_chamber_unknown_field(self):
        """Test validation with chamber having unknown field."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "A test chamber",
                    "unknown_field": "value"
                }
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Chamber 1 contains unknown field: unknown_field"):
            validator.validate_config(config)
    
    def test_invalid_connections_not_dict(self):
        """Test validation with connections not being a dictionary."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "A test chamber",
                    "connections": "invalid"
                }
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Chamber 1 connections must be a dictionary"):
            validator.validate_config(config)
    
    def test_invalid_connection_direction(self):
        """Test validation with invalid connection direction."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "A test chamber",
                    "connections": {"invalid_direction": 2}
                },
                "2": {
                    "name": "Second Chamber",
                    "description": "Another chamber"
                }
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Chamber 1 invalid direction: invalid_direction"):
            validator.validate_config(config)
    
    def test_invalid_connection_target_not_integer(self):
        """Test validation with connection target not being an integer."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "A test chamber",
                    "connections": {"north": "invalid"}
                }
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Chamber 1 connection target must be a positive integer: invalid"):
            validator.validate_config(config)
    
    def test_invalid_connection_target_negative(self):
        """Test validation with negative connection target."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "A test chamber",
                    "connections": {"north": -1}
                }
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Chamber 1 connection target must be a positive integer: -1"):
            validator.validate_config(config)
    
    def test_invalid_connection_to_nonexistent_chamber(self):
        """Test validation with connection to non-existent chamber."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "A test chamber",
                    "connections": {"north": 999}
                }
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Chamber 1 connects to non-existent chamber 999 via north"):
            validator.validate_config(config)
    
    def test_invalid_starting_chamber_not_integer(self):
        """Test validation with starting chamber not being an integer."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "A test chamber"
                }
            },
            "starting_chamber": "invalid"
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="starting_chamber must be an integer"):
            validator.validate_config(config)
    
    def test_invalid_starting_chamber_nonexistent(self):
        """Test validation with starting chamber that doesn't exist."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "A test chamber"
                }
            },
            "starting_chamber": 999
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="starting_chamber 999 does not exist"):
            validator.validate_config(config)
    
    def test_invalid_unreachable_chambers(self):
        """Test validation with unreachable chambers."""
        config = {
            "chambers": {
                "1": {
                    "name": "Chamber 1",
                    "description": "First chamber",
                    "connections": {"north": 2}
                },
                "2": {
                    "name": "Chamber 2",
                    "description": "Second chamber",
                    "connections": {"south": 1}
                },
                "3": {
                    "name": "Chamber 3",
                    "description": "Third chamber"
                }
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Unreachable chambers detected: \\[3\\]"):
            validator.validate_config(config)
    
    def test_valid_challenge_type(self):
        """Test validation with valid challenge type."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "A test chamber",
                    "challenge_type": "riddle"
                }
            }
        }
        validator = LabyrinthConfigValidator()
        validator.validate_config(config)
    
    def test_invalid_challenge_type_not_string(self):
        """Test validation with challenge type not being a string."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "A test chamber",
                    "challenge_type": 123
                }
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Chamber 1 challenge_type must be a string"):
            validator.validate_config(config)
    
    def test_valid_items_list(self):
        """Test validation with valid items list."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "A test chamber",
                    "items": ["sword", "potion"]
                }
            }
        }
        validator = LabyrinthConfigValidator()
        validator.validate_config(config)
    
    def test_invalid_items_not_list(self):
        """Test validation with items not being a list."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "A test chamber",
                    "items": "invalid"
                }
            }
        }
        validator = LabyrinthConfigValidator()
        with pytest.raises(GameException, match="Chamber 1 items must be a list"):
            validator.validate_config(config)
    
    def test_valid_all_directions(self):
        """Test validation with all valid directions."""
        directions = ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest", "up", "down"]
        
        chambers = {}
        for i, direction in enumerate(directions, 1):
            chambers[str(i)] = {
                "name": f"Chamber {i}",
                "description": f"Chamber {i} description"
            }
            if i < len(directions):
                chambers[str(i)]["connections"] = {direction: i + 1}
        
        config = {"chambers": chambers}
        validator = LabyrinthConfigValidator()
        validator.validate_config(config)


class TestLabyrinthConfigLoader:
    """Test cases for LabyrinthConfigLoader class."""
    
    def test_load_valid_file(self):
        """Test loading from a valid configuration file."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "A test chamber",
                    "connections": {"north": 2}
                },
                "2": {
                    "name": "Second Chamber",
                    "description": "Another chamber",
                    "connections": {"south": 1}
                }
            }
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_file = f.name
        
        try:
            loader = LabyrinthConfigLoader()
            loaded_config = loader.load_from_file(temp_file)
            
            assert loaded_config == config
        finally:
            os.unlink(temp_file)
    
    def test_load_nonexistent_file(self):
        """Test loading from non-existent file."""
        loader = LabyrinthConfigLoader()
        with pytest.raises(GameException, match="Configuration file not found"):
            loader.load_from_file("nonexistent_file.json")
    
    def test_load_invalid_json(self):
        """Test loading from file with invalid JSON."""
        # Create temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name
        
        try:
            loader = LabyrinthConfigLoader()
            with pytest.raises(GameException, match="Invalid JSON in configuration file"):
                loader.load_from_file(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_load_invalid_config(self):
        """Test loading from file with invalid configuration."""
        config = {"invalid": "config"}
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_file = f.name
        
        try:
            loader = LabyrinthConfigLoader()
            with pytest.raises(GameException, match="Configuration must contain 'chambers' section"):
                loader.load_from_file(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_save_valid_config(self):
        """Test saving a valid configuration to file."""
        config = {
            "chambers": {
                "1": {
                    "name": "Test Chamber",
                    "description": "A test chamber"
                }
            }
        }
        
        # Create temporary directory and file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test_config.json")
            
            loader = LabyrinthConfigLoader()
            loader.save_to_file(config, temp_file)
            
            # Verify file was created and contains correct data
            assert os.path.exists(temp_file)
            
            with open(temp_file, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
            
            assert saved_config == config
    
    def test_save_invalid_config(self):
        """Test saving an invalid configuration."""
        config = {"invalid": "config"}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test_config.json")
            
            loader = LabyrinthConfigLoader()
            with pytest.raises(GameException, match="Configuration must contain 'chambers' section"):
                loader.save_to_file(config, temp_file)
    
    def test_create_default_config(self):
        """Test creating default configuration."""
        loader = LabyrinthConfigLoader()
        config = loader.create_default_config()
        
        # Validate the default config
        loader.validator.validate_config(config)
        
        # Check basic structure
        assert "chambers" in config
        assert "starting_chamber" in config
        assert len(config["chambers"]) == 3
        assert config["starting_chamber"] == 1
    
    def test_create_full_labyrinth_config(self):
        """Test creating full 13-chamber labyrinth configuration."""
        loader = LabyrinthConfigLoader()
        config = loader.create_full_labyrinth_config()
        
        # Validate the full config
        loader.validator.validate_config(config)
        
        # Check basic structure
        assert "chambers" in config
        assert "starting_chamber" in config
        assert len(config["chambers"]) == 13
        assert config["starting_chamber"] == 1
        
        # Check that all chambers have required fields
        for chamber_id, chamber_data in config["chambers"].items():
            assert "name" in chamber_data
            assert "description" in chamber_data
            assert isinstance(chamber_data["name"], str)
            assert isinstance(chamber_data["description"], str)
            assert len(chamber_data["name"]) > 0
            assert len(chamber_data["description"]) > 0
    
    def test_save_and_load_roundtrip(self):
        """Test saving and loading configuration maintains data integrity."""
        loader = LabyrinthConfigLoader()
        original_config = loader.create_default_config()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "roundtrip_config.json")
            
            # Save and load
            loader.save_to_file(original_config, temp_file)
            loaded_config = loader.load_from_file(temp_file)
            
            # Should be identical
            assert loaded_config == original_config


class TestLabyrinthConnectivity:
    """Test cases for labyrinth connectivity and completability."""
    
    def test_full_labyrinth_connectivity(self):
        """Test that the full 13-chamber labyrinth has proper connectivity."""
        loader = LabyrinthConfigLoader()
        config = loader.create_full_labyrinth_config()
        
        chambers = config["chambers"]
        
        # Test bidirectional connections
        reverse_dirs = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
        
        for chamber_id, chamber_data in chambers.items():
            connections = chamber_data.get("connections", {})
            for direction, target_id in connections.items():
                target_chamber = chambers[str(target_id)]
                target_connections = target_chamber.get("connections", {})
                
                reverse_dir = reverse_dirs.get(direction)
                if reverse_dir:
                    assert reverse_dir in target_connections, \
                        f"Chamber {chamber_id} connects to {target_id} via {direction}, but no reverse connection"
                    assert target_connections[reverse_dir] == int(chamber_id), \
                        f"Chamber {chamber_id} -> {target_id} via {direction}, but reverse points to {target_connections[reverse_dir]}"
    
    def test_full_labyrinth_reachability(self):
        """Test that all chambers in the full labyrinth are reachable."""
        loader = LabyrinthConfigLoader()
        config = loader.create_full_labyrinth_config()
        
        chambers = config["chambers"]
        starting_chamber = config["starting_chamber"]
        
        # Build adjacency list
        adjacency = {}
        for chamber_id, chamber_data in chambers.items():
            chamber_id_int = int(chamber_id)
            adjacency[chamber_id_int] = []
            connections = chamber_data.get("connections", {})
            for direction, target_id in connections.items():
                adjacency[chamber_id_int].append(target_id)
        
        # BFS to find reachable chambers
        visited = set()
        queue = [starting_chamber]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            
            for neighbor in adjacency.get(current, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        
        # All chambers should be reachable
        all_chamber_ids = {int(chamber_id) for chamber_id in chambers.keys()}
        assert visited == all_chamber_ids, f"Unreachable chambers: {all_chamber_ids - visited}"
    
    def test_full_labyrinth_has_13_chambers(self):
        """Test that the full labyrinth has exactly 13 chambers."""
        loader = LabyrinthConfigLoader()
        config = loader.create_full_labyrinth_config()
        
        assert len(config["chambers"]) == 13, "Full labyrinth must have exactly 13 chambers"
        
        # Check chamber IDs are 1-13
        chamber_ids = {int(chamber_id) for chamber_id in config["chambers"].keys()}
        expected_ids = set(range(1, 14))
        assert chamber_ids == expected_ids, f"Expected chambers 1-13, got {sorted(chamber_ids)}"
    
    def test_full_labyrinth_challenge_distribution(self):
        """Test that the full labyrinth has a good distribution of challenge types."""
        loader = LabyrinthConfigLoader()
        config = loader.create_full_labyrinth_config()
        
        challenge_counts = {}
        for chamber_data in config["chambers"].values():
            challenge_type = chamber_data.get("challenge_type", "none")
            challenge_counts[challenge_type] = challenge_counts.get(challenge_type, 0) + 1
        
        # Should have all 5 challenge types
        expected_types = {"riddle", "puzzle", "combat", "skill", "memory"}
        actual_types = set(challenge_counts.keys())
        assert expected_types.issubset(actual_types), f"Missing challenge types: {expected_types - actual_types}"
        
        # Each type should appear at least once
        for challenge_type in expected_types:
            assert challenge_counts[challenge_type] > 0, f"Challenge type '{challenge_type}' not found"
    
    def test_labyrinth_completability_path_exists(self):
        """Test that there's a valid path through the labyrinth."""
        loader = LabyrinthConfigLoader()
        config = loader.create_full_labyrinth_config()
        
        chambers = config["chambers"]
        starting_chamber = config["starting_chamber"]
        
        # Find the final chamber (chamber with no exits or designated end)
        # For our labyrinth, chamber 13 is the final chamber
        final_chamber = 13
        
        # Use BFS to find if there's a path from start to end
        visited = set()
        queue = [(starting_chamber, [starting_chamber])]
        
        while queue:
            current, path = queue.pop(0)
            if current == final_chamber:
                # Found a path to the final chamber
                assert len(path) > 1, "Path should have multiple chambers"
                return
            
            if current in visited:
                continue
            
            visited.add(current)
            
            connections = chambers[str(current)].get("connections", {})
            for direction, target_id in connections.items():
                if target_id not in visited:
                    queue.append((target_id, path + [target_id]))
        
        assert False, f"No path found from chamber {starting_chamber} to final chamber {final_chamber}"
    
    def test_labyrinth_no_isolated_chambers(self):
        """Test that no chambers are isolated (have no connections)."""
        loader = LabyrinthConfigLoader()
        config = loader.create_full_labyrinth_config()
        
        chambers = config["chambers"]
        
        for chamber_id, chamber_data in chambers.items():
            connections = chamber_data.get("connections", {})
            # Every chamber should have at least one connection
            # (except possibly the final chamber, but even that should be reachable)
            assert len(connections) > 0 or chamber_id == "13", \
                f"Chamber {chamber_id} has no connections and is not the final chamber"
    
    def test_labyrinth_structural_integrity(self):
        """Test overall structural integrity of the labyrinth."""
        loader = LabyrinthConfigLoader()
        config = loader.create_full_labyrinth_config()
        
        chambers = config["chambers"]
        
        # Count total connections
        total_connections = 0
        for chamber_data in chambers.values():
            connections = chamber_data.get("connections", {})
            total_connections += len(connections)
        
        # Should have reasonable number of connections for 13 chambers
        # Minimum: 12 connections for a linear path
        # Maximum: 78 connections for fully connected graph (13*12/2*2)
        assert 12 <= total_connections <= 78, f"Unexpected number of connections: {total_connections}"
        
        # Should be even number (bidirectional connections)
        assert total_connections % 2 == 0, "Total connections should be even (bidirectional)"
    
    def test_default_labyrinth_connectivity(self):
        """Test that the default 3-chamber labyrinth is properly connected."""
        loader = LabyrinthConfigLoader()
        config = loader.create_default_config()
        
        # Should pass all validation
        loader.validator.validate_config(config)
        
        # Should have exactly 3 chambers
        assert len(config["chambers"]) == 3
        
        # All chambers should be reachable
        chambers = config["chambers"]
        starting_chamber = config["starting_chamber"]
        
        # Build adjacency list
        adjacency = {}
        for chamber_id, chamber_data in chambers.items():
            chamber_id_int = int(chamber_id)
            adjacency[chamber_id_int] = []
            connections = chamber_data.get("connections", {})
            for direction, target_id in connections.items():
                adjacency[chamber_id_int].append(target_id)
        
        # BFS to find reachable chambers
        visited = set()
        queue = [starting_chamber]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            
            for neighbor in adjacency.get(current, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        
        # All chambers should be reachable
        all_chamber_ids = {int(chamber_id) for chamber_id in chambers.keys()}
        assert visited == all_chamber_ids, f"Unreachable chambers in default config: {all_chamber_ids - visited}"