"""Main entry point for the Labyrinth Adventure Game."""

import argparse
import sys
import os
from typing import Optional

from src.game.engine import GameEngine
from src.utils.exceptions import GameException
from src.utils.logging import setup_logging, get_logger, create_log_filename


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='labrynth',
        description='A text-based adventure game where you navigate through a labyrinth of chambers.',
        epilog='Navigate through 13 unique chambers, solve challenges, and escape the labyrinth!'
    )
    
    # Game mode options
    game_group = parser.add_mutually_exclusive_group()
    game_group.add_argument(
        '--new-game', '-n',
        action='store_true',
        help='Start a new game (default behavior)'
    )
    game_group.add_argument(
        '--load-game', '-l',
        metavar='FILENAME',
        help='Load a saved game from the specified file'
    )
    
    # Configuration options
    parser.add_argument(
        '--config', '-c',
        metavar='CONFIG_FILE',
        help='Use a custom labyrinth configuration file'
    )
    
    # Display options
    parser.add_argument(
        '--no-colors',
        action='store_true',
        help='Disable colored output'
    )
    
    # Debug and logging options
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug mode with verbose output'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    # Information options
    parser.add_argument(
        '--version',
        action='version',
        version='Labyrinth Adventure Game 1.0.0'
    )
    
    return parser


def display_game_introduction() -> None:
    """Display the game introduction and objectives."""
    print("=" * 60)
    print("         WELCOME TO THE LABYRINTH ADVENTURE GAME")
    print("=" * 60)
    print()
    print("You find yourself at the entrance of an ancient underground labyrinth.")
    print("The air is thick with mystery, and the walls whisper of forgotten secrets.")
    print()
    print("OBJECTIVE:")
    print("  Navigate through 13 interconnected chambers, each containing a unique")
    print("  challenge that must be overcome to progress. Solve riddles, defeat")
    print("  enemies, complete puzzles, and test your skills to escape the labyrinth!")
    print()
    print("HOW TO WIN:")
    print("  Complete all challenges in the chambers to unlock the final exit.")
    print("  Manage your health and inventory wisely - some challenges may be")
    print("  dangerous, but rewards await those who succeed!")
    print()
    print("BASIC COMMANDS:")
    print("  • Movement: north, south, east, west (or n, s, e, w)")
    print("  • Look around: look, examine")
    print("  • Inventory: inventory, items")
    print("  • Help: help (for complete command list)")
    print("  • Save/Load: save, load")
    print("  • Quit: quit, exit")
    print()
    print("Type 'help' at any time for a complete list of commands.")
    print("Good luck, adventurer!")
    print("=" * 60)
    print()


def initialize_game_engine(args: argparse.Namespace) -> GameEngine:
    """Initialize the game engine with the provided arguments.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Initialized GameEngine instance
        
    Raises:
        GameException: If game initialization fails
    """
    try:
        # Set up logging
        log_file = None
        if args.debug or args.verbose:
            log_file = create_log_filename()
        
        logger = setup_logging(
            debug=args.debug,
            verbose=args.verbose,
            log_file=log_file
        )
        
        logger.info("Initializing Labyrinth Adventure Game")
        logger.debug(f"Arguments: debug={args.debug}, verbose={args.verbose}, "
                    f"config={args.config}, no_colors={args.no_colors}")
        
        # Determine color usage
        use_colors = not args.no_colors
        
        # Initialize game engine
        engine = GameEngine(
            config_file=args.config,
            use_colors=use_colors
        )
        
        logger.info("Game engine initialized successfully")
        
        return engine
        
    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to initialize game: {e}")
        raise GameException(f"Failed to initialize game: {e}")


def handle_new_game(engine: GameEngine) -> None:
    """Handle starting a new game.
    
    Args:
        engine: The game engine instance
    """
    logger = get_logger()
    logger.info("Starting new game")
    
    display_game_introduction()
    
    # Ask user if they're ready to start
    response = input("Press Enter to begin your adventure, or 'q' to quit: ").strip().lower()
    if response == 'q':
        logger.info("User chose to quit before starting")
        print("Maybe next time, adventurer!")
        return
    
    logger.info("User confirmed game start")
    # Start the game
    engine.start_game()


def handle_load_game(engine: GameEngine, filename: str) -> None:
    """Handle loading a saved game.
    
    Args:
        engine: The game engine instance
        filename: Name of the save file to load
    """
    logger = get_logger()
    logger.info(f"Attempting to load game from '{filename}'")
    
    try:
        if engine.load_game(filename):
            logger.info(f"Successfully loaded game from '{filename}'")
            print(f"Successfully loaded game from '{filename}'")
            print("Continuing your adventure...")
            print()
            
            # Start the game loop (the loaded state will be applied)
            engine.game_loop()
        else:
            logger.warning(f"Failed to load game from '{filename}'")
            print(f"Failed to load game from '{filename}'")
            print("Starting a new game instead...")
            handle_new_game(engine)
            
    except Exception as e:
        logger.error(f"Error loading game: {e}")
        print(f"Error loading game: {e}")
        print("Starting a new game instead...")
        handle_new_game(engine)


def main() -> None:
    """Main entry point for the game."""
    logger = None
    
    try:
        # Parse command-line arguments
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # Initialize the game engine (this also sets up logging)
        engine = initialize_game_engine(args)
        logger = get_logger()
        
        # Handle the requested game mode
        if args.load_game:
            logger.info(f"Load game mode requested: {args.load_game}")
            handle_load_game(engine, args.load_game)
        else:
            logger.info("New game mode (default)")
            # Default to new game
            handle_new_game(engine)
            
    except KeyboardInterrupt:
        if logger:
            logger.info("Game interrupted by user (Ctrl+C)")
        print("\nGame interrupted by user. Goodbye!")
        sys.exit(0)
    except GameException as e:
        if logger:
            logger.error(f"Game error: {e}")
        print(f"Game Error: {e}")
        sys.exit(1)
    except Exception as e:
        if logger:
            logger.critical(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()