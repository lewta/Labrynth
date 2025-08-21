"""Save and load functionality for the Labyrinth Adventure Game."""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from src.utils.data_models import GameState, Item, PlayerStats
from src.utils.exceptions import SaveLoadException


class SaveLoadManager:
    """Manages game state serialization and persistence."""
    
    def __init__(self, save_directory: str = "saves"):
        """Initialize the save/load manager.
        
        Args:
            save_directory: Directory to store save files
        """
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(exist_ok=True)
    
    def save_game(self, game_state: GameState, filename: str) -> bool:
        """Save the current game state to a file.
        
        Args:
            game_state: The game state to save
            filename: Name of the save file
            
        Returns:
            True if save was successful, False otherwise
            
        Raises:
            SaveLoadException: If save operation fails
        """
        try:
            # Validate game state
            if not game_state.is_valid():
                raise SaveLoadException("save", filename, "Invalid game state cannot be saved")
            
            # Ensure filename has .json extension
            if not filename.endswith('.json'):
                filename += '.json'
            
            # Create save data dictionary
            save_data = self._serialize_game_state(game_state)
            
            # Add metadata
            save_data['metadata'] = {
                'save_time': datetime.now().isoformat(),
                'game_version': '1.0',
                'save_format_version': '1.0'
            }
            
            # Write to file
            save_path = self.save_directory / filename
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except SaveLoadException:
            # Re-raise SaveLoadException without modification
            raise
        except Exception as e:
            raise SaveLoadException("save", filename, str(e))
    
    def load_game(self, filename: str) -> Optional[GameState]:
        """Load a saved game state from a file.
        
        Args:
            filename: Name of the save file
            
        Returns:
            GameState object if load was successful, None otherwise
            
        Raises:
            SaveLoadException: If load operation fails due to file not found or permission issues
        """
        try:
            # Ensure filename has .json extension
            if not filename.endswith('.json'):
                filename += '.json'
            
            save_path = self.save_directory / filename
            
            if not save_path.exists():
                raise SaveLoadException("load", filename, "Save file not found")
            
            # Read from file
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Validate save file format
            self._validate_save_file(save_data)
            
            # Deserialize game state
            game_state = self._deserialize_game_state(save_data)
            
            # Validate loaded game state
            if not game_state.is_valid():
                return None  # Return None for invalid game states
            
            return game_state
            
        except json.JSONDecodeError:
            # Return None for corrupted JSON files instead of raising exception
            return None
        except (ValueError, KeyError, TypeError):
            # Return None for corrupted save data instead of raising exception
            return None
        except SaveLoadException:
            # Re-raise SaveLoadException without modification (for file not found, etc.)
            raise
        except Exception:
            # Return None for other unexpected errors
            return None
    
    def list_save_files(self) -> List[str]:
        """List available save files.
        
        Returns:
            List of save file names
        """
        try:
            save_files = []
            for file_path in self.save_directory.glob('*.json'):
                save_files.append(file_path.name)
            return sorted(save_files)
        except Exception:
            return []
    
    def delete_save_file(self, filename: str) -> bool:
        """Delete a save file.
        
        Args:
            filename: Name of the save file to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if not filename.endswith('.json'):
                filename += '.json'
            
            save_path = self.save_directory / filename
            if save_path.exists():
                save_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def get_save_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get information about a save file.
        
        Args:
            filename: Name of the save file
            
        Returns:
            Dictionary with save file information, or None if file doesn't exist
        """
        try:
            if not filename.endswith('.json'):
                filename += '.json'
            
            save_path = self.save_directory / filename
            if not save_path.exists():
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            metadata = save_data.get('metadata', {})
            game_data = save_data.get('game_state', {})
            
            return {
                'filename': filename,
                'save_time': metadata.get('save_time', 'Unknown'),
                'game_version': metadata.get('game_version', 'Unknown'),
                'current_chamber': game_data.get('current_chamber', 1),
                'player_health': game_data.get('player_health', 100),
                'completed_chambers': len(game_data.get('completed_chambers', [])),
                'game_time': game_data.get('game_time', 0),
                'file_size': save_path.stat().st_size
            }
        except Exception:
            return None
    
    def _serialize_game_state(self, game_state: GameState) -> Dict[str, Any]:
        """Serialize a GameState object to a dictionary.
        
        Args:
            game_state: The game state to serialize
            
        Returns:
            Dictionary representation of the game state
        """
        return {
            'game_state': {
                'current_chamber': game_state.current_chamber,
                'player_health': game_state.player_health,
                'inventory_items': [self._serialize_item(item) for item in game_state.inventory_items],
                'completed_chambers': list(game_state.completed_chambers),
                'visited_chambers': list(game_state.visited_chambers),
                'discovered_connections': {str(k): v for k, v in game_state.discovered_connections.items()},
                'game_time': game_state.game_time,
                'player_stats': {
                    'strength': game_state.player_stats.strength,
                    'intelligence': game_state.player_stats.intelligence,
                    'dexterity': game_state.player_stats.dexterity,
                    'luck': game_state.player_stats.luck
                }
            }
        }
    
    def _deserialize_game_state(self, save_data: Dict[str, Any]) -> GameState:
        """Deserialize a dictionary to a GameState object.
        
        Args:
            save_data: Dictionary containing save data
            
        Returns:
            GameState object
        """
        game_data = save_data['game_state']
        
        # Deserialize inventory items
        inventory_items = []
        for item_data in game_data.get('inventory_items', []):
            item = self._deserialize_item(item_data)
            inventory_items.append(item)
        
        # Deserialize player stats
        stats_data = game_data.get('player_stats', {})
        player_stats = PlayerStats(
            strength=stats_data.get('strength', 10),
            intelligence=stats_data.get('intelligence', 10),
            dexterity=stats_data.get('dexterity', 10),
            luck=stats_data.get('luck', 10)
        )
        
        # Deserialize map data
        visited_chambers = set(game_data.get('visited_chambers', []))
        discovered_connections_data = game_data.get('discovered_connections', {})
        discovered_connections = {int(k): v for k, v in discovered_connections_data.items()}
        
        # Create game state
        return GameState(
            current_chamber=game_data.get('current_chamber', 1),
            player_health=game_data.get('player_health', 100),
            inventory_items=inventory_items,
            completed_chambers=set(game_data.get('completed_chambers', [])),
            visited_chambers=visited_chambers,
            discovered_connections=discovered_connections,
            game_time=game_data.get('game_time', 0),
            player_stats=player_stats
        )
    
    def _serialize_item(self, item: Item) -> Dict[str, Any]:
        """Serialize an Item object to a dictionary.
        
        Args:
            item: The item to serialize
            
        Returns:
            Dictionary representation of the item
        """
        return {
            'name': item.name,
            'description': item.description,
            'item_type': item.item_type,
            'value': item.value,
            'usable': item.usable
        }
    
    def _deserialize_item(self, item_data: Dict[str, Any]) -> Item:
        """Deserialize a dictionary to an Item object.
        
        Args:
            item_data: Dictionary containing item data
            
        Returns:
            Item object
        """
        return Item(
            name=item_data['name'],
            description=item_data['description'],
            item_type=item_data['item_type'],
            value=item_data['value'],
            usable=item_data.get('usable', True)
        )
    
    def _validate_save_file(self, save_data: Dict[str, Any]) -> None:
        """Validate the structure of a save file.
        
        Args:
            save_data: The loaded save data
            
        Raises:
            SaveLoadException: If save file structure is invalid
        """
        if not isinstance(save_data, dict):
            raise SaveLoadException("validate", "unknown", "Save file must contain a JSON object")
        
        if 'game_state' not in save_data:
            raise SaveLoadException("validate", "unknown", "Save file missing 'game_state' section")
        
        game_state = save_data['game_state']
        required_fields = ['current_chamber', 'player_health']
        
        for field in required_fields:
            if field not in game_state:
                raise SaveLoadException("validate", "unknown", f"Save file missing required field: {field}")
        
        # Validate data types
        if not isinstance(game_state['current_chamber'], int):
            raise SaveLoadException("validate", "unknown", "current_chamber must be an integer")
        
        if not isinstance(game_state['player_health'], int):
            raise SaveLoadException("validate", "unknown", "player_health must be an integer")
        
        # Validate optional fields if present
        if 'inventory_items' in game_state:
            if not isinstance(game_state['inventory_items'], list):
                raise SaveLoadException("validate", "unknown", "inventory_items must be a list")
        
        if 'completed_chambers' in game_state:
            if not isinstance(game_state['completed_chambers'], list):
                raise SaveLoadException("validate", "unknown", "completed_chambers must be a list")
    
    def backup_save_file(self, filename: str) -> bool:
        """Create a backup of a save file.
        
        Args:
            filename: Name of the save file to backup
            
        Returns:
            True if backup was successful, False otherwise
        """
        try:
            if not filename.endswith('.json'):
                filename += '.json'
            
            save_path = self.save_directory / filename
            if not save_path.exists():
                return False
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{save_path.stem}_backup_{timestamp}.json"
            backup_path = self.save_directory / backup_name
            
            # Copy file
            import shutil
            shutil.copy2(save_path, backup_path)
            
            return True
        except Exception:
            return False
    
    def cleanup_old_backups(self, max_backups: int = 5) -> int:
        """Clean up old backup files, keeping only the most recent ones.
        
        Args:
            max_backups: Maximum number of backup files to keep
            
        Returns:
            Number of backup files deleted
        """
        try:
            backup_files = []
            for file_path in self.save_directory.glob('*_backup_*.json'):
                backup_files.append(file_path)
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Delete old backups
            deleted_count = 0
            for backup_file in backup_files[max_backups:]:
                backup_file.unlink()
                deleted_count += 1
            
            return deleted_count
        except Exception:
            return 0