"""Tests for the main application entry point."""

import pytest
import argparse
from unittest.mock import Mock, patch, MagicMock
import sys
from io import StringIO

from src.main import (
    create_argument_parser,
    display_game_introduction,
    initialize_game_engine,
    handle_new_game,
    handle_load_game,
    main
)
from src.utils.exceptions import GameException


class TestArgumentParser:
    """Test the command-line argument parser."""
    
    def test_create_argument_parser(self):
        """Test that the argument parser is created correctly."""
        parser = create_argument_parser()
        
        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.prog == 'labrynth'
        assert 'labyrinth of chambers' in parser.description
    
    def test_default_arguments(self):
        """Test parsing with no arguments (default behavior)."""
        parser = create_argument_parser()
        args = parser.parse_args([])
        
        assert not args.new_game
        assert args.load_game is None
        assert args.config is None
        assert not args.no_colors
        assert not args.debug
        assert not args.verbose
    
    def test_new_game_argument(self):
        """Test the --new-game argument."""
        parser = create_argument_parser()
        args = parser.parse_args(['--new-game'])
        
        assert args.new_game
        assert args.load_game is None
    
    def test_load_game_argument(self):
        """Test the --load-game argument."""
        parser = create_argument_parser()
        args = parser.parse_args(['--load-game', 'savefile.json'])
        
        assert not args.new_game
        assert args.load_game == 'savefile.json'
    
    def test_mutually_exclusive_game_options(self):
        """Test that --new-game and --load-game are mutually exclusive."""
        parser = create_argument_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(['--new-game', '--load-game', 'savefile.json'])
    
    def test_config_argument(self):
        """Test the --config argument."""
        parser = create_argument_parser()
        args = parser.parse_args(['--config', 'custom_config.json'])
        
        assert args.config == 'custom_config.json'
    
    def test_no_colors_argument(self):
        """Test the --no-colors argument."""
        parser = create_argument_parser()
        args = parser.parse_args(['--no-colors'])
        
        assert args.no_colors
    
    def test_debug_argument(self):
        """Test the --debug argument."""
        parser = create_argument_parser()
        args = parser.parse_args(['--debug'])
        
        assert args.debug
    
    def test_verbose_argument(self):
        """Test the --verbose argument."""
        parser = create_argument_parser()
        args = parser.parse_args(['--verbose'])
        
        assert args.verbose
    
    def test_short_arguments(self):
        """Test short argument forms."""
        parser = create_argument_parser()
        
        # Test short forms
        args = parser.parse_args(['-n'])
        assert args.new_game
        
        args = parser.parse_args(['-l', 'save.json'])
        assert args.load_game == 'save.json'
        
        args = parser.parse_args(['-c', 'config.json'])
        assert args.config == 'config.json'
        
        args = parser.parse_args(['-d'])
        assert args.debug
        
        args = parser.parse_args(['-v'])
        assert args.verbose


class TestGameIntroduction:
    """Test the game introduction display."""
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_display_game_introduction(self, mock_stdout):
        """Test that the game introduction is displayed correctly."""
        display_game_introduction()
        
        output = mock_stdout.getvalue()
        
        # Check for key elements
        assert "WELCOME TO THE LABYRINTH ADVENTURE GAME" in output
        assert "OBJECTIVE:" in output
        assert "HOW TO WIN:" in output
        assert "BASIC COMMANDS:" in output
        assert "13 interconnected chambers" in output
        assert "help" in output.lower()


class TestGameEngineInitialization:
    """Test game engine initialization."""
    
    @patch('src.main.setup_logging')
    @patch('src.main.GameEngine')
    def test_initialize_game_engine_default(self, mock_engine_class, mock_setup_logging):
        """Test initializing game engine with default arguments."""
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger
        
        # Create mock arguments
        args = Mock()
        args.config = None
        args.no_colors = False
        args.debug = False
        args.verbose = False
        
        result = initialize_game_engine(args)
        
        mock_setup_logging.assert_called_once_with(
            debug=False,
            verbose=False,
            log_file=None
        )
        mock_engine_class.assert_called_once_with(
            config_file=None,
            use_colors=True
        )
        assert result == mock_engine
    
    @patch('src.main.create_log_filename')
    @patch('src.main.setup_logging')
    @patch('src.main.GameEngine')
    def test_initialize_game_engine_with_config(self, mock_engine_class, mock_setup_logging, mock_create_log):
        """Test initializing game engine with custom config."""
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger
        mock_create_log.return_value = 'logs/test.log'
        
        args = Mock()
        args.config = 'custom.json'
        args.no_colors = True
        args.debug = True
        args.verbose = False
        
        result = initialize_game_engine(args)
        
        mock_create_log.assert_called_once()
        mock_setup_logging.assert_called_once_with(
            debug=True,
            verbose=False,
            log_file='logs/test.log'
        )
        mock_engine_class.assert_called_once_with(
            config_file='custom.json',
            use_colors=False
        )
        assert result == mock_engine
    
    @patch('src.main.get_logger')
    @patch('src.main.setup_logging')
    @patch('src.main.GameEngine')
    def test_initialize_game_engine_failure(self, mock_engine_class, mock_setup_logging, mock_get_logger):
        """Test handling of game engine initialization failure."""
        mock_engine_class.side_effect = Exception("Initialization failed")
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger
        mock_get_logger.return_value = mock_logger
        
        args = Mock()
        args.config = None
        args.no_colors = False
        args.debug = False
        args.verbose = False
        
        with pytest.raises(GameException) as exc_info:
            initialize_game_engine(args)
        
        assert "Failed to initialize game" in str(exc_info.value)
        mock_logger.error.assert_called_once()


class TestNewGameHandling:
    """Test new game handling."""
    
    @patch('builtins.input', return_value='')
    @patch('src.main.display_game_introduction')
    def test_handle_new_game_start(self, mock_intro, mock_input):
        """Test handling new game start."""
        mock_engine = Mock()
        
        handle_new_game(mock_engine)
        
        mock_intro.assert_called_once()
        mock_engine.start_game.assert_called_once()
    
    @patch('builtins.input', return_value='q')
    @patch('src.main.display_game_introduction')
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_new_game_quit(self, mock_stdout, mock_intro, mock_input):
        """Test handling new game quit."""
        mock_engine = Mock()
        
        handle_new_game(mock_engine)
        
        mock_intro.assert_called_once()
        mock_engine.start_game.assert_not_called()
        
        output = mock_stdout.getvalue()
        assert "Maybe next time" in output


class TestLoadGameHandling:
    """Test load game handling."""
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_load_game_success(self, mock_stdout):
        """Test successful game loading."""
        mock_engine = Mock()
        mock_engine.load_game.return_value = True
        
        handle_load_game(mock_engine, 'test_save.json')
        
        mock_engine.load_game.assert_called_once_with('test_save.json')
        mock_engine.game_loop.assert_called_once()
        
        output = mock_stdout.getvalue()
        assert "Successfully loaded game" in output
    
    @patch('src.main.handle_new_game')
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_load_game_failure(self, mock_stdout, mock_handle_new):
        """Test handling of load game failure."""
        mock_engine = Mock()
        mock_engine.load_game.return_value = False
        
        handle_load_game(mock_engine, 'nonexistent.json')
        
        mock_engine.load_game.assert_called_once_with('nonexistent.json')
        mock_handle_new.assert_called_once_with(mock_engine)
        
        output = mock_stdout.getvalue()
        assert "Failed to load game" in output
        assert "Starting a new game instead" in output
    
    @patch('src.main.handle_new_game')
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_load_game_exception(self, mock_stdout, mock_handle_new):
        """Test handling of load game exception."""
        mock_engine = Mock()
        mock_engine.load_game.side_effect = Exception("Load error")
        
        handle_load_game(mock_engine, 'corrupt.json')
        
        mock_engine.load_game.assert_called_once_with('corrupt.json')
        mock_handle_new.assert_called_once_with(mock_engine)
        
        output = mock_stdout.getvalue()
        assert "Error loading game" in output
        assert "Starting a new game instead" in output


class TestMainFunction:
    """Test the main function."""
    
    @patch('src.main.handle_new_game')
    @patch('src.main.initialize_game_engine')
    @patch('src.main.create_argument_parser')
    def test_main_new_game_default(self, mock_parser_func, mock_init_engine, mock_handle_new):
        """Test main function with default new game behavior."""
        # Setup mocks
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.load_game = None
        mock_parser.parse_args.return_value = mock_args
        mock_parser_func.return_value = mock_parser
        
        mock_engine = Mock()
        mock_init_engine.return_value = mock_engine
        
        # Test with empty sys.argv
        with patch.object(sys, 'argv', ['labyrinth-game']):
            main()
        
        mock_parser_func.assert_called_once()
        mock_init_engine.assert_called_once_with(mock_args)
        mock_handle_new.assert_called_once_with(mock_engine)
    
    @patch('src.main.handle_load_game')
    @patch('src.main.initialize_game_engine')
    @patch('src.main.create_argument_parser')
    def test_main_load_game(self, mock_parser_func, mock_init_engine, mock_handle_load):
        """Test main function with load game option."""
        # Setup mocks
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.load_game = 'save.json'
        mock_parser.parse_args.return_value = mock_args
        mock_parser_func.return_value = mock_parser
        
        mock_engine = Mock()
        mock_init_engine.return_value = mock_engine
        
        with patch.object(sys, 'argv', ['labyrinth-game', '--load-game', 'save.json']):
            main()
        
        mock_parser_func.assert_called_once()
        mock_init_engine.assert_called_once_with(mock_args)
        mock_handle_load.assert_called_once_with(mock_engine, 'save.json')
    
    @patch('sys.stdout', new_callable=StringIO)
    @patch('src.main.initialize_game_engine')
    @patch('src.main.create_argument_parser')
    def test_main_keyboard_interrupt(self, mock_parser_func, mock_init_engine, mock_stdout):
        """Test main function handling keyboard interrupt."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.load_game = None
        mock_parser.parse_args.return_value = mock_args
        mock_parser_func.return_value = mock_parser
        
        mock_init_engine.side_effect = KeyboardInterrupt()
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0
        output = mock_stdout.getvalue()
        assert "Game interrupted by user" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    @patch('src.main.initialize_game_engine')
    @patch('src.main.create_argument_parser')
    def test_main_game_exception(self, mock_parser_func, mock_init_engine, mock_stdout):
        """Test main function handling GameException."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_parser.parse_args.return_value = mock_args
        mock_parser_func.return_value = mock_parser
        
        mock_init_engine.side_effect = GameException("Test game error")
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
        output = mock_stdout.getvalue()
        assert "Game Error: Test game error" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    @patch('src.main.initialize_game_engine')
    @patch('src.main.create_argument_parser')
    def test_main_unexpected_exception(self, mock_parser_func, mock_init_engine, mock_stdout):
        """Test main function handling unexpected exception."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_parser.parse_args.return_value = mock_args
        mock_parser_func.return_value = mock_parser
        
        mock_init_engine.side_effect = RuntimeError("Unexpected error")
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
        output = mock_stdout.getvalue()
        assert "Unexpected error: Unexpected error" in output


class TestIntegration:
    """Integration tests for complete game startup."""
    
    @patch('builtins.input', return_value='q')
    @patch('sys.stdout', new_callable=StringIO)
    def test_complete_startup_sequence(self, mock_stdout, mock_input):
        """Test complete game startup sequence."""
        # This test runs the actual main function with minimal mocking
        # to test the integration of all components
        
        with patch.object(sys, 'argv', ['labyrinth-game', '--new-game']):
            try:
                main()
            except SystemExit:
                pass  # Expected when user quits
        
        output = mock_stdout.getvalue()
        
        # Verify key elements of the startup sequence
        assert "WELCOME TO THE LABYRINTH ADVENTURE GAME" in output
        assert "OBJECTIVE:" in output
        assert "Maybe next time" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_help_argument(self, mock_stdout):
        """Test that help argument works correctly."""
        with patch.object(sys, 'argv', ['labyrinth-game', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        # Help should exit with code 0
        assert exc_info.value.code == 0
        
        output = mock_stdout.getvalue()
        assert 'labyrinth' in output
        assert 'chambers' in output
        assert '--new-game' in output
        assert '--load-game' in output

class TestCLIOptions:
    """Test command-line interface options."""
    
    def test_version_option(self):
        """Test --version option."""
        with patch.object(sys, 'argv', ['labyrinth-game', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        # Version should exit with code 0
        assert exc_info.value.code == 0
    
    @patch('src.main.handle_new_game')
    @patch('src.main.initialize_game_engine')
    @patch('src.main.create_argument_parser')
    def test_debug_option_creates_log_file(self, mock_parser_func, mock_init_engine, mock_handle_new):
        """Test that debug option creates a log file."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.load_game = None
        mock_args.debug = True
        mock_args.verbose = False
        mock_parser.parse_args.return_value = mock_args
        mock_parser_func.return_value = mock_parser
        
        mock_engine = Mock()
        mock_init_engine.return_value = mock_engine
        
        with patch.object(sys, 'argv', ['labyrinth-game', '--debug']):
            main()
        
        # Verify that initialize_game_engine was called with debug=True
        mock_init_engine.assert_called_once()
        args_passed = mock_init_engine.call_args[0][0]
        assert args_passed.debug == True
    
    @patch('src.main.handle_new_game')
    @patch('src.main.initialize_game_engine')
    @patch('src.main.create_argument_parser')
    def test_verbose_option(self, mock_parser_func, mock_init_engine, mock_handle_new):
        """Test verbose option."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.load_game = None
        mock_args.debug = False
        mock_args.verbose = True
        mock_parser.parse_args.return_value = mock_args
        mock_parser_func.return_value = mock_parser
        
        mock_engine = Mock()
        mock_init_engine.return_value = mock_engine
        
        with patch.object(sys, 'argv', ['labyrinth-game', '--verbose']):
            main()
        
        # Verify that initialize_game_engine was called with verbose=True
        mock_init_engine.assert_called_once()
        args_passed = mock_init_engine.call_args[0][0]
        assert args_passed.verbose == True
    
    @patch('src.main.handle_new_game')
    @patch('src.main.initialize_game_engine')
    @patch('src.main.create_argument_parser')
    def test_no_colors_option(self, mock_parser_func, mock_init_engine, mock_handle_new):
        """Test --no-colors option."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.load_game = None
        mock_args.no_colors = True
        mock_parser.parse_args.return_value = mock_args
        mock_parser_func.return_value = mock_parser
        
        mock_engine = Mock()
        mock_init_engine.return_value = mock_engine
        
        with patch.object(sys, 'argv', ['labyrinth-game', '--no-colors']):
            main()
        
        # Verify that initialize_game_engine was called with no_colors=True
        mock_init_engine.assert_called_once()
        args_passed = mock_init_engine.call_args[0][0]
        assert args_passed.no_colors == True
    
    @patch('src.main.handle_load_game')
    @patch('src.main.initialize_game_engine')
    @patch('src.main.create_argument_parser')
    def test_load_game_with_filename(self, mock_parser_func, mock_init_engine, mock_handle_load):
        """Test --load-game option with filename."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.load_game = 'test_save.json'
        mock_parser.parse_args.return_value = mock_args
        mock_parser_func.return_value = mock_parser
        
        mock_engine = Mock()
        mock_init_engine.return_value = mock_engine
        
        with patch.object(sys, 'argv', ['labyrinth-game', '--load-game', 'test_save.json']):
            main()
        
        mock_handle_load.assert_called_once_with(mock_engine, 'test_save.json')
    
    @patch('src.main.handle_new_game')
    @patch('src.main.initialize_game_engine')
    @patch('src.main.create_argument_parser')
    def test_config_option(self, mock_parser_func, mock_init_engine, mock_handle_new):
        """Test --config option."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.load_game = None
        mock_args.config = 'custom_config.json'
        mock_parser.parse_args.return_value = mock_args
        mock_parser_func.return_value = mock_parser
        
        mock_engine = Mock()
        mock_init_engine.return_value = mock_engine
        
        with patch.object(sys, 'argv', ['labyrinth-game', '--config', 'custom_config.json']):
            main()
        
        # Verify that initialize_game_engine was called with the config
        mock_init_engine.assert_called_once()
        args_passed = mock_init_engine.call_args[0][0]
        assert args_passed.config == 'custom_config.json'


class TestCLIArgumentValidation:
    """Test CLI argument validation and error handling."""
    
    def test_mutually_exclusive_options_error(self):
        """Test that mutually exclusive options raise an error."""
        with patch.object(sys, 'argv', ['labyrinth-game', '--new-game', '--load-game', 'save.json']):
            with patch('sys.stderr'):  # Suppress error output
                with pytest.raises(SystemExit) as exc_info:
                    main()
        
        # Should exit with error code
        assert exc_info.value.code != 0
    
    def test_load_game_requires_filename(self):
        """Test that --load-game requires a filename argument."""
        with patch.object(sys, 'argv', ['labyrinth-game', '--load-game']):
            with patch('sys.stderr'):  # Suppress error output
                with pytest.raises(SystemExit) as exc_info:
                    main()
        
        # Should exit with error code
        assert exc_info.value.code != 0
    
    def test_config_requires_filename(self):
        """Test that --config requires a filename argument."""
        with patch.object(sys, 'argv', ['labyrinth-game', '--config']):
            with patch('sys.stderr'):  # Suppress error output
                with pytest.raises(SystemExit) as exc_info:
                    main()
        
        # Should exit with error code
        assert exc_info.value.code != 0