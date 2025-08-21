"""Game engine for the Labyrinth Adventure Game."""

import time
from typing import Dict, Any, Optional, List
from src.game.world import WorldManager
from src.game.player import PlayerManager
from src.game.ui_controller import UIController
from src.game.command_parser import CommandType, ParsedCommand, CommandParser
from src.game.map_renderer import MapRenderer, ChamberInfo
from src.challenges.factory import ChallengeFactory
from src.utils.data_models import GameState, Item
from src.utils.exceptions import GameException, SaveLoadException
from src.utils.config import LabyrinthConfigLoader
from src.utils.save_load import SaveLoadManager


class GameEngine:
    """Central game engine that coordinates all game systems."""
    
    def __init__(self, config_file: Optional[str] = None, use_colors: bool = True):
        """Initialize the game engine.
        
        Args:
            config_file: Optional path to labyrinth configuration file
            use_colors: Whether to use colors in the UI
        """
        self.world_manager = WorldManager()
        self.player_manager = PlayerManager()
        self.ui_controller = UIController(use_colors=use_colors)
        self.command_parser = CommandParser()
        self.save_load_manager = SaveLoadManager()
        self.map_renderer = MapRenderer()
        
        self.running = False
        self.game_started = False
        self.start_time = 0
        self.config_file = config_file
        
        # Game statistics
        self.commands_processed = 0
        self.challenges_completed = 0
        
        # Initialize the labyrinth
        self._initialize_world()
    
    def _initialize_world(self) -> None:
        """Initialize the game world from configuration."""
        try:
            if self.config_file:
                self.world_manager.load_from_file(self.config_file)
            else:
                # Use default labyrinth if no config file specified
                self.world_manager.initialize_labyrinth()
        except Exception as e:
            raise GameException(f"Failed to initialize world: {e}")
    
    def start_game(self) -> None:
        """Start a new game."""
        if self.game_started:
            raise GameException("Game is already started")
        
        self.running = True
        self.game_started = True
        self.start_time = time.time()
        
        # Display welcome message
        self.ui_controller.display_welcome_message("Labyrinth Adventure Game")
        
        # Show initial chamber
        self._display_current_chamber()
        
        # Start the main game loop
        self.game_loop()
    
    def game_loop(self) -> None:
        """Main game loop that processes commands until the game ends."""
        while self.running:
            try:
                # Get and parse user command
                parsed_command = self.ui_controller.get_command_and_parse()
                
                # Process the command
                self.process_command(parsed_command)
                
                # Check win/lose conditions
                if self.check_win_condition():
                    self._handle_victory()
                    break
                elif not self.player_manager.is_alive():
                    self._handle_defeat()
                    break
                
            except KeyboardInterrupt:
                self.ui_controller.display_message("\nGame interrupted by user.")
                if self.ui_controller.confirm_action("Do you want to save before quitting?"):
                    self._handle_save_command()
                break
            except Exception as e:
                self.ui_controller.display_error(f"An error occurred: {e}")
                # Continue the game loop unless it's a critical error
                if isinstance(e, GameException):
                    continue
                else:
                    break
    
    def process_command(self, parsed_command: ParsedCommand) -> None:
        """Process a parsed command.
        
        Args:
            parsed_command: The parsed command to process
        """
        if not parsed_command.is_valid:
            # Check if there's an active challenge that might handle this input
            if self._try_challenge_response(parsed_command.raw_input):
                return
            self.ui_controller.handle_invalid_command(parsed_command)
            return
        
        self.commands_processed += 1
        
        # Route command to appropriate handler based on type
        if parsed_command.command_type == CommandType.MOVEMENT:
            self._handle_movement_command(parsed_command)
        elif parsed_command.command_type == CommandType.EXAMINATION:
            self._handle_examination_command(parsed_command)
        elif parsed_command.command_type == CommandType.INVENTORY:
            self._handle_inventory_command(parsed_command)
        elif parsed_command.command_type == CommandType.INTERACTION:
            self._handle_interaction_command(parsed_command)
        elif parsed_command.command_type == CommandType.SYSTEM:
            self._handle_system_command(parsed_command)
        elif parsed_command.command_type == CommandType.CHALLENGE:
            self._handle_challenge_command(parsed_command)
        else:
            self.ui_controller.display_error(f"Unknown command type: {parsed_command.command_type}")
    
    def _handle_movement_command(self, parsed_command: ParsedCommand) -> None:
        """Handle movement commands.
        
        Args:
            parsed_command: The parsed movement command
        """
        if parsed_command.action in ['go', 'move']:
            direction = parsed_command.parameters[0]
            
            # Get current chamber before moving
            old_chamber_id = self.world_manager.current_chamber_id
            
            if self.world_manager.move_player(direction):
                # Update progress tracking for the new chamber
                new_chamber_id = self.world_manager.current_chamber_id
                new_chamber = self.world_manager.get_chamber(new_chamber_id)
                
                # Record the chamber visit and discovered connections
                if new_chamber:
                    self.player_manager.progress.visit_chamber(new_chamber_id, new_chamber.connections)
                    
                    # Record the connection we just used
                    self.player_manager.progress.discover_connection(old_chamber_id, direction, new_chamber_id)
                
                self._display_current_chamber()
                self._check_chamber_challenge()
            else:
                self.ui_controller.display_message(f"You cannot go {direction} from here.")
    
    def _handle_examination_command(self, parsed_command: ParsedCommand) -> None:
        """Handle examination commands.
        
        Args:
            parsed_command: The parsed examination command
        """
        if parsed_command.action == 'look':
            if parsed_command.parameters:
                target = parsed_command.parameters[0]
                self._examine_target(target)
            else:
                self._display_current_chamber()
        elif parsed_command.action in ['examine', 'inspect']:
            target = parsed_command.parameters[0]
            self._examine_target(target)
        elif parsed_command.action == 'map':
            if parsed_command.parameters and parsed_command.parameters[0] == 'legend':
                self._display_map_legend()
            else:
                self._display_map()
    
    def _handle_inventory_command(self, parsed_command: ParsedCommand) -> None:
        """Handle inventory commands.
        
        Args:
            parsed_command: The parsed inventory command
        """
        if parsed_command.action in ['inventory', 'items']:
            items = self.player_manager.inventory.get_all_items()
            self.ui_controller.display_inventory(items)
        elif parsed_command.action == 'use':
            item_name = parsed_command.parameters[0]
            used_item = self.player_manager.use_item(item_name)
            if used_item:
                self.ui_controller.display_success(f"You used {used_item.name}.")
            else:
                self.ui_controller.display_error(f"You don't have '{item_name}' or it cannot be used.")
        elif parsed_command.action == 'drop':
            item_name = parsed_command.parameters[0]
            dropped_item = self.player_manager.remove_item(item_name)
            if dropped_item:
                # Add item to current chamber
                current_chamber = self.world_manager.get_current_chamber()
                if current_chamber:
                    current_chamber.add_item(dropped_item)
                    self.ui_controller.display_success(f"You dropped {dropped_item.name}.")
                else:
                    # This shouldn't happen, but handle gracefully
                    self.player_manager.add_item(dropped_item)  # Put it back
                    self.ui_controller.display_error("Cannot drop item here.")
            else:
                self.ui_controller.display_error(f"You don't have '{item_name}'.")
    
    def _handle_interaction_command(self, parsed_command: ParsedCommand) -> None:
        """Handle interaction commands.
        
        Args:
            parsed_command: The parsed interaction command
        """
        if parsed_command.action in ['take', 'get']:
            item_name = parsed_command.parameters[0]
            current_chamber = self.world_manager.get_current_chamber()
            
            if current_chamber and current_chamber.has_item(item_name):
                item = current_chamber.remove_item(item_name)
                if item and self.player_manager.add_item(item):
                    self.ui_controller.display_success(f"You took {item.name}.")
                elif item:
                    # Inventory full, put item back
                    current_chamber.add_item(item)
                    self.ui_controller.display_error("Your inventory is full.")
                else:
                    self.ui_controller.display_error(f"Cannot take '{item_name}'.")
            else:
                self.ui_controller.display_error(f"There is no '{item_name}' here.")
        elif parsed_command.action == 'talk':
            # Basic talk implementation - could be expanded
            self.ui_controller.display_message("There is no one here to talk to.")
    
    def _handle_system_command(self, parsed_command: ParsedCommand) -> None:
        """Handle system commands.
        
        Args:
            parsed_command: The parsed system command
        """
        if parsed_command.action == 'help':
            if parsed_command.parameters:
                self.ui_controller.display_help(parsed_command.parameters[0])
            else:
                self.ui_controller.display_help()
        elif parsed_command.action == 'status':
            self._display_player_status()
        elif parsed_command.action == 'save':
            self._handle_save_command(parsed_command.parameters)
        elif parsed_command.action == 'load':
            self._handle_load_command(parsed_command.parameters)
        elif parsed_command.action in ['quit', 'exit']:
            self._handle_quit_command()
    
    def _handle_challenge_command(self, parsed_command: ParsedCommand) -> None:
        """Handle challenge-specific commands.
        
        Args:
            parsed_command: The parsed challenge command
        """
        current_chamber = self.world_manager.get_current_chamber()
        
        if not current_chamber or not current_chamber.challenge or current_chamber.completed:
            self.ui_controller.display_message("There is no active challenge here.")
            return
        
        if parsed_command.action in ['answer', 'solve']:
            response = parsed_command.parameters[0] if parsed_command.parameters else ""
            result = current_chamber.challenge.process_response(response)
            
            self.ui_controller.display_challenge_result(result)
            
            if result.success:
                current_chamber.complete_challenge()
                self.challenges_completed += 1
                
                # Apply damage if any
                if result.damage > 0:
                    self.player_manager.take_damage(result.damage)
                    self.ui_controller.display_message(f"You took {result.damage} damage!")
                
                # Give reward if any
                if result.reward:
                    if self.player_manager.add_item(result.reward):
                        self.ui_controller.display_success(f"You received: {result.reward.name}")
                    else:
                        # Inventory full, drop in chamber
                        current_chamber.add_item(result.reward)
                        self.ui_controller.display_message(f"Your inventory is full. {result.reward.name} was left in the chamber.")
            else:
                # Apply damage for failed attempts
                if result.damage > 0:
                    self.player_manager.take_damage(result.damage)
                    self.ui_controller.display_message(f"You took {result.damage} damage!")
        
        elif parsed_command.action == 'skip':
            self.ui_controller.display_message("You decided to skip this challenge for now.")
    
    def _try_challenge_response(self, raw_input: str) -> bool:
        """Try to handle input as a challenge response.
        
        Args:
            raw_input: The raw user input
            
        Returns:
            True if the input was handled by a challenge, False otherwise
        """
        current_chamber = self.world_manager.get_current_chamber()
        
        # Check if there's an active challenge
        if not current_chamber or not current_chamber.challenge or current_chamber.completed:
            return False
        
        # Try to process the input as a challenge response
        try:
            result = current_chamber.challenge.process_response(raw_input.strip())
            self.ui_controller.display_challenge_result(result)
            
            if result.success:
                current_chamber.complete_challenge()
                self.challenges_completed += 1
                
                # Apply damage if any
                if result.damage > 0:
                    self.player_manager.take_damage(result.damage)
                    self.ui_controller.display_message(f"You took {result.damage} damage!")
                
                # Give reward if any
                if result.reward:
                    if self.player_manager.add_item(result.reward):
                        self.ui_controller.display_success(f"You received: {result.reward.name}")
                    else:
                        # Inventory full, drop in chamber
                        current_chamber.add_item(result.reward)
                        self.ui_controller.display_message(f"Your inventory is full. {result.reward.name} was left in the chamber.")
            else:
                # Apply damage for failed attempts
                if result.damage > 0:
                    self.player_manager.take_damage(result.damage)
                    self.ui_controller.display_message(f"You took {result.damage} damage!")
            
            return True
        except Exception:
            # If challenge can't handle the input, return False
            return False
    
    def _display_current_chamber(self) -> None:
        """Display information about the current chamber."""
        current_chamber = self.world_manager.get_current_chamber()
        
        if current_chamber:
            exits = current_chamber.get_exits()
            self.ui_controller.display_chamber(
                current_chamber.name,
                current_chamber.get_description(),
                exits
            )
        else:
            self.ui_controller.display_error("You are in an unknown location!")
    
    def _check_chamber_challenge(self) -> None:
        """Check if the current chamber has a challenge and present it."""
        current_chamber = self.world_manager.get_current_chamber()
        
        if current_chamber and current_chamber.challenge and not current_chamber.completed:
            self.ui_controller.display_challenge(current_chamber.challenge)
    
    def _examine_target(self, target: str) -> None:
        """Examine a specific target in the current chamber.
        
        Args:
            target: The target to examine
        """
        current_chamber = self.world_manager.get_current_chamber()
        
        if not current_chamber:
            self.ui_controller.display_error("You are in an unknown location!")
            return
        
        # Check if target is an item in the chamber
        if current_chamber.has_item(target):
            items = current_chamber.get_items()
            for item in items:
                if item.name.lower() == target.lower():
                    self.ui_controller.display_message(f"{item.name}: {item.description}")
                    return
        
        # Check if target is a direction
        if target.lower() in ['exits', 'doors', 'directions']:
            exits = current_chamber.get_exits()
            if exits:
                self.ui_controller.display_message(f"Available exits: {', '.join(exits)}")
            else:
                self.ui_controller.display_message("There are no visible exits.")
            return
        
        # Default response
        self.ui_controller.display_message(f"You don't see anything special about '{target}'.")
    
    def _display_map(self) -> None:
        """Display the labyrinth map showing visited chambers."""
        # Convert progress data to ChamberInfo objects for the map renderer
        chambers = {}
        progress = self.player_manager.progress
        
        for chamber_id in progress.visited_chambers:
            chamber = self.world_manager.get_chamber(chamber_id)
            if chamber:
                chamber_info = ChamberInfo(
                    chamber_id=chamber_id,
                    name=chamber.name,
                    visited=True,
                    completed=progress.is_chamber_completed(chamber_id),
                    connections=progress.discovered_connections.get(chamber_id, {})
                )
                chambers[chamber_id] = chamber_info
        
        if not chambers:
            self.ui_controller.display_message("You haven't explored any chambers yet.")
            return
        
        # Render and display the map
        current_chamber_id = self.world_manager.current_chamber_id
        map_content = self.map_renderer.render_map(chambers, current_chamber_id)
        self.ui_controller.display_map(map_content)
    
    def _display_map_legend(self) -> None:
        """Display just the map legend without the full map."""
        legend = """
╔══════════════════════════════════════════════════════════════╗
║                           LEGEND                             ║
╠══════════════════════════════════════════════════════════════╣
║ ● Current Location    ◉ Completed Chamber              ║
║ ○ Visited Chamber     ─ Horizontal Connection         ║
║                       │ Vertical Connection           ║
╚══════════════════════════════════════════════════════════════╝
"""
        self.ui_controller.display_message(legend.strip())
    
    def _display_player_status(self) -> None:
        """Display comprehensive player status."""
        status = self.player_manager.get_status()
        completed_chambers = len(self.world_manager.get_completed_chambers())
        
        self.ui_controller.display_player_status(
            status['health']['current'],
            self.player_manager.stats,
            completed_chambers
        )
    
    def _handle_save_command(self, parameters: Optional[List[str]] = None) -> None:
        """Handle save game command.
        
        Args:
            parameters: Optional filename parameter
        """
        try:
            filename = None
            if parameters:
                filename = parameters[0]
            else:
                filename = self.ui_controller.get_save_filename()
            
            if filename:
                if self.save_game(filename):
                    self.ui_controller.display_success(f"Game saved as '{filename}'.")
                else:
                    self.ui_controller.display_error("Failed to save game.")
        except Exception as e:
            self.ui_controller.display_error(f"Save failed: {e}")
    
    def _handle_load_command(self, parameters: Optional[List[str]] = None) -> None:
        """Handle load game command.
        
        Args:
            parameters: Optional filename parameter
        """
        try:
            filename = None
            if parameters:
                filename = parameters[0]
            else:
                save_files = self.list_save_files()
                filename = self.ui_controller.get_load_filename(save_files)
            
            if filename:
                if self.load_game(filename):
                    self.ui_controller.display_success(f"Game loaded from '{filename}'.")
                    self._display_current_chamber()
                else:
                    self.ui_controller.display_error("Failed to load game.")
        except Exception as e:
            self.ui_controller.display_error(f"Load failed: {e}")
    
    def _handle_quit_command(self) -> None:
        """Handle quit command."""
        if self.ui_controller.confirm_action("Are you sure you want to quit?"):
            if self.ui_controller.confirm_action("Do you want to save before quitting?"):
                self._handle_save_command()
            self.running = False
            self.ui_controller.display_message("Thanks for playing!")
    
    def _handle_victory(self) -> None:
        """Handle victory condition."""
        game_time = int(time.time() - self.start_time)
        stats = {
            'chambers_completed': len(self.world_manager.get_completed_chambers()),
            'total_chambers': self.world_manager.get_chamber_count(),
            'commands_used': self.commands_processed,
            'time_played': game_time,
            'challenges_completed': self.challenges_completed
        }
        
        self.ui_controller.display_game_over(True, stats)
        self.running = False
    
    def _handle_defeat(self) -> None:
        """Handle defeat condition."""
        game_time = int(time.time() - self.start_time)
        stats = {
            'chambers_completed': len(self.world_manager.get_completed_chambers()),
            'total_chambers': self.world_manager.get_chamber_count(),
            'commands_used': self.commands_processed,
            'time_played': game_time,
            'challenges_completed': self.challenges_completed
        }
        
        self.ui_controller.display_game_over(False, stats)
        self.running = False
    
    def check_win_condition(self) -> bool:
        """Check if the player has won the game.
        
        Returns:
            True if win condition is met, False otherwise
        """
        # Win condition: Complete all chambers (check both world manager and player progress)
        total_chambers = self.world_manager.get_chamber_count()
        
        # Check world manager completion
        world_completed = len(self.world_manager.get_completed_chambers())
        
        # Check player progress completion
        player_completed = len(self.player_manager.progress.completed_chambers)
        
        # Use the higher of the two counts (in case they get out of sync)
        completed_chambers = max(world_completed, player_completed)
        
        return completed_chambers >= total_chambers
    
    def save_game(self, filename: str) -> bool:
        """Save the current game state.
        
        Args:
            filename: Name of the save file
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Create game state object
            game_state = GameState(
                current_chamber=self.world_manager.current_chamber_id,
                player_health=self.player_manager.current_health,
                inventory_items=self.player_manager.inventory.get_all_items(),
                completed_chambers=set(self.world_manager.get_completed_chambers()),
                visited_chambers=self.player_manager.progress.visited_chambers.copy(),
                discovered_connections=self.player_manager.progress.get_discovered_connections(),
                game_time=int(time.time() - self.start_time) if self.start_time else 0,
                player_stats=self.player_manager.stats
            )
            
            # Save using the save/load manager
            return self.save_load_manager.save_game(game_state, filename)
            
        except Exception as e:
            raise SaveLoadException(f"Failed to save game: {e}")
    
    def load_game(self, filename: str) -> bool:
        """Load a saved game state.
        
        Args:
            filename: Name of the save file
            
        Returns:
            True if load was successful, False otherwise
        """
        try:
            # Load game state from file
            game_state = self.save_load_manager.load_game(filename)
            if game_state is None:
                return False
            
            # Apply the loaded state to the game
            self._apply_loaded_state(game_state)
            
            return True
            
        except SaveLoadException:
            # Save/load exceptions are expected for missing files, etc.
            return False
        except Exception as e:
            # Unexpected exceptions should still be raised
            raise SaveLoadException(f"Failed to load game: {e}")
    
    def list_save_files(self) -> List[str]:
        """List available save files.
        
        Returns:
            List of save file names
        """
        return self.save_load_manager.list_save_files()
    
    def get_game_statistics(self) -> Dict[str, Any]:
        """Get current game statistics.
        
        Returns:
            Dictionary containing game statistics
        """
        game_time = int(time.time() - self.start_time) if self.start_time else 0
        
        return {
            'game_started': self.game_started,
            'running': self.running,
            'current_chamber': self.world_manager.current_chamber_id,
            'chambers_completed': len(self.world_manager.get_completed_chambers()),
            'total_chambers': self.world_manager.get_chamber_count(),
            'commands_processed': self.commands_processed,
            'challenges_completed': self.challenges_completed,
            'game_time': game_time,
            'player_alive': self.player_manager.is_alive(),
            'player_health': self.player_manager.current_health
        }
    
    def reset_game(self) -> None:
        """Reset the game to initial state."""
        self.running = False
        self.game_started = False
        self.start_time = 0
        self.commands_processed = 0
        self.challenges_completed = 0
        
        # Reset managers
        self.player_manager.reset_to_defaults()
        self.world_manager.reset_player_position()
        
        # Reset all chambers to uncompleted state
        for chamber in self.world_manager.chambers.values():
            chamber.reset()
    
    def is_running(self) -> bool:
        """Check if the game is currently running.
        
        Returns:
            True if game is running, False otherwise
        """
        return self.running
    
    def stop_game(self) -> None:
        """Stop the game loop."""
        self.running = False
    
    def _apply_loaded_state(self, game_state: GameState) -> None:
        """Apply a loaded game state to the current game.
        
        Args:
            game_state: The loaded game state to apply
        """
        # Update world manager
        self.world_manager.current_chamber_id = game_state.current_chamber
        
        # Update player manager
        self.player_manager.current_health = game_state.player_health
        self.player_manager.stats = game_state.player_stats
        
        # Clear and reload inventory
        self.player_manager.inventory.clear()
        for item in game_state.inventory_items:
            self.player_manager.inventory.add_item(item)
        
        # Update chamber completion status
        for chamber_id in game_state.completed_chambers:
            chamber = self.world_manager.get_chamber(chamber_id)
            if chamber:
                chamber.completed = True
        
        # Update progress tracker with map data
        progress = self.player_manager.progress
        progress.visited_chambers = game_state.visited_chambers.copy()
        progress.discovered_connections = game_state.discovered_connections.copy()
        progress.completed_chambers = game_state.completed_chambers.copy()
        
        # Update game time (adjust start time to account for loaded game time)
        if self.start_time:
            self.start_time = time.time() - game_state.game_time