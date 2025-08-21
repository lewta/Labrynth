"""Tests for the logging utilities."""

import pytest
import logging
import logging.handlers
import os
import tempfile
import json
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime
from pathlib import Path

from src.utils.logging import (
    setup_logging, get_logger, create_log_filename, get_game_state_logger,
    GameLogFormatter, GameStateLogger, log_exception, configure_third_party_logging,
    LogContext
)


class TestLoggingSetup:
    """Test logging setup functionality."""
    
    def test_setup_logging_default(self):
        """Test default logging setup."""
        logger = setup_logging()
        
        assert logger.name == 'labrynth'
        assert logger.level == logging.DEBUG  # Logger always captures all levels
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        # Console handler should filter to WARNING level
        assert logger.handlers[0].level == logging.WARNING
    
    def test_setup_logging_debug(self):
        """Test debug logging setup."""
        logger = setup_logging(debug=True)
        
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1
    
    def test_setup_logging_verbose(self):
        """Test verbose logging setup."""
        logger = setup_logging(verbose=True)
        
        assert logger.level == logging.DEBUG  # Logger always captures all levels
        assert len(logger.handlers) == 1
        # Console handler should filter to INFO level
        assert logger.handlers[0].level == logging.INFO
    
    def test_setup_logging_debug_overrides_verbose(self):
        """Test that debug mode overrides verbose mode."""
        logger = setup_logging(debug=True, verbose=True)
        
        assert logger.level == logging.DEBUG
    
    def test_setup_logging_with_file(self):
        """Test logging setup with file output."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            logger = setup_logging(debug=True, log_file=temp_filename)
            
            # Should have console, main file, and error file handlers
            assert len(logger.handlers) == 3
            assert any(isinstance(h, logging.handlers.RotatingFileHandler) for h in logger.handlers)
            assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
            
            # Test that file was created
            assert os.path.exists(temp_filename)
            
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            # Also clean up error log file
            error_file = temp_filename.replace(os.path.basename(temp_filename), f"error_{os.path.basename(temp_filename)}")
            if os.path.exists(error_file):
                os.unlink(error_file)
    
    def test_setup_logging_creates_log_directory(self):
        """Test that logging setup creates log directory if needed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, 'subdir', 'test.log')
            
            logger = setup_logging(debug=True, log_file=log_file)
            
            assert os.path.exists(os.path.dirname(log_file))
            # Should have console, main file, and error file handlers
            assert len(logger.handlers) == 3
    
    def test_setup_logging_clears_existing_handlers(self):
        """Test that setup_logging clears existing handlers."""
        # First setup
        logger1 = setup_logging(debug=True)
        initial_handler_count = len(logger1.handlers)
        
        # Second setup should clear and recreate handlers
        logger2 = setup_logging(verbose=True)
        
        assert logger1 is logger2  # Same logger instance
        assert len(logger2.handlers) == initial_handler_count  # Same number of handlers


class TestGetLogger:
    """Test get_logger functionality."""
    
    def test_get_logger_default(self):
        """Test getting default logger."""
        logger = get_logger()
        
        assert logger.name == 'labrynth'
    
    def test_get_logger_with_name(self):
        """Test getting named logger."""
        logger = get_logger('test_module')
        
        assert logger.name == 'labrynth.test_module'
    
    def test_get_logger_returns_same_instance(self):
        """Test that get_logger returns the same instance for the same name."""
        logger1 = get_logger('test')
        logger2 = get_logger('test')
        
        assert logger1 is logger2


class TestCreateLogFilename:
    """Test log filename creation."""
    
    @patch('src.utils.logging.datetime')
    def test_create_log_filename(self, mock_datetime):
        """Test log filename creation with mocked datetime."""
        mock_now = Mock()
        mock_now.strftime.return_value = '20240101_120000'
        mock_datetime.now.return_value = mock_now
        
        filename = create_log_filename()
        
        assert filename == 'logs/game_20240101_120000.log'
        mock_datetime.now.assert_called_once()
        mock_now.strftime.assert_called_once_with('%Y%m%d_%H%M%S')
    
    def test_create_log_filename_format(self):
        """Test that log filename has correct format."""
        filename = create_log_filename()
        
        assert filename.startswith('logs/game_')
        assert filename.endswith('.log')
        assert len(filename) == len('logs/game_YYYYMMDD_HHMMSS.log')


class TestLoggingIntegration:
    """Test logging integration with actual logging calls."""
    
    def test_logging_levels(self):
        """Test that different log levels work correctly."""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # Setup debug logging with file
            logger = setup_logging(debug=True, log_file=temp_filename)
            
            # Log messages at different levels
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")
            
            # Force flush handlers
            for handler in logger.handlers:
                handler.flush()
            
            # Read log file content
            with open(temp_filename, 'r') as f:
                log_content = f.read()
            
            # Check that all messages are in the log file
            assert "Debug message" in log_content
            assert "Info message" in log_content
            assert "Warning message" in log_content
            assert "Error message" in log_content
            assert "Critical message" in log_content
            
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_console_logging_respects_level(self):
        """Test that console logging respects the set level."""
        with patch('sys.stdout') as mock_stdout:
            # Setup warning level logging (default)
            logger = setup_logging()
            
            # Log messages at different levels
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            
            # Logger captures all levels, but console handler filters
            assert logger.level == logging.DEBUG
            # Console handler should filter to WARNING level
            console_handler = None
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    console_handler = handler
                    break
            assert console_handler is not None
            assert console_handler.level == logging.WARNING
    
    def test_file_logging_always_debug(self):
        """Test that file logging always uses DEBUG level."""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # Setup warning level logging with file
            logger = setup_logging(verbose=False, debug=False, log_file=temp_filename)
            
            # Find the file handler
            file_handler = None
            for handler in logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    file_handler = handler
                    break
            
            assert file_handler is not None
            assert file_handler.level == logging.DEBUG
            
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)


class TestLoggingFormatter:
    """Test logging formatter functionality."""
    
    def test_log_message_format(self):
        """Test that log messages have the correct format."""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            logger = setup_logging(debug=True, log_file=temp_filename)
            
            test_message = "Test log message"
            logger.info(test_message)
            
            # Force flush
            for handler in logger.handlers:
                handler.flush()
            
            # Read and check format
            with open(temp_filename, 'r') as f:
                log_content = f.read().strip()
            
            # Should contain timestamp, logger name, level, and message
            assert test_message in log_content
            assert 'labrynth' in log_content
            assert 'INFO' in log_content
            # Check for timestamp format (YYYY-MM-DD HH:MM:SS)
            import re
            timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
            assert re.search(timestamp_pattern, log_content)
            
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)


class TestGameLogFormatter:
    """Test the custom GameLogFormatter."""
    
    def test_basic_formatting(self):
        """Test basic log formatting without context."""
        formatter = GameLogFormatter(include_context=False)
        
        # Create a mock log record
        record = logging.LogRecord(
            name='labrynth.test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Test message',
            args=(),
            exc_info=None
        )
        record.created = datetime(2024, 1, 1, 12, 0, 0).timestamp()
        
        formatted = formatter.format(record)
        
        assert 'Test message' in formatted
        assert 'INFO' in formatted
        assert 'test' in formatted
        assert '2024-01-01 12:00:00' in formatted
    
    def test_formatting_with_context(self):
        """Test log formatting with context information."""
        formatter = GameLogFormatter(include_context=True)
        
        record = logging.LogRecord(
            name='labrynth.game',
            level=logging.DEBUG,
            pathname='',
            lineno=0,
            msg='State change',
            args=(),
            exc_info=None
        )
        record.created = datetime.now().timestamp()
        record.context = {'chamber_id': 1, 'action': 'move'}
        
        formatted = formatter.format(record)
        
        assert 'State change' in formatted
        assert 'Context:' in formatted
        assert 'chamber_id' in formatted
        assert 'action' in formatted
    
    def test_formatting_with_player_info(self):
        """Test log formatting with player information."""
        formatter = GameLogFormatter(include_context=True)
        
        record = logging.LogRecord(
            name='labrynth.player',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Player action',
            args=(),
            exc_info=None
        )
        record.created = datetime.now().timestamp()
        record.player_id = 'player_123'
        record.session_id = 'session_456'
        
        formatted = formatter.format(record)
        
        assert 'Player action' in formatted
        assert 'Player: player_123' in formatted
        assert 'Session: session_456' in formatted


class TestGameStateLogger:
    """Test the GameStateLogger class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_logger = Mock(spec=logging.Logger)
        self.game_logger = GameStateLogger(self.mock_logger)
    
    def test_log_player_action(self):
        """Test logging player actions."""
        self.game_logger.log_player_action('move north', 1, {'direction': 'north'})
        
        self.mock_logger.info.assert_called_once()
        call_args = self.mock_logger.info.call_args
        
        assert 'Player action: move north in chamber 1' in call_args[0][0]
        assert 'context' in call_args[1]['extra']
        assert call_args[1]['extra']['context']['action'] == 'move north'
        assert call_args[1]['extra']['context']['chamber_id'] == 1
        assert call_args[1]['extra']['context']['direction'] == 'north'
    
    def test_log_game_state_change(self):
        """Test logging game state changes."""
        self.game_logger.log_game_state_change('player_health', 100, 90, {'damage': 10})
        
        self.mock_logger.debug.assert_called_once()
        call_args = self.mock_logger.debug.call_args
        
        assert 'State change in player_health: 100 -> 90' in call_args[0][0]
        assert call_args[1]['extra']['context']['component'] == 'player_health'
        assert call_args[1]['extra']['context']['old_state'] == '100'
        assert call_args[1]['extra']['context']['new_state'] == '90'
    
    def test_log_challenge_event_success(self):
        """Test logging successful challenge events."""
        self.game_logger.log_challenge_event('riddle', 'completed', True, {'answer': 'correct'})
        
        self.mock_logger.log.assert_called_once()
        call_args = self.mock_logger.log.call_args
        
        assert call_args[0][0] == logging.INFO  # Log level
        assert 'Challenge riddle: completed' in call_args[0][1]
        assert call_args[1]['extra']['context']['success'] is True
    
    def test_log_challenge_event_failure(self):
        """Test logging failed challenge events."""
        self.game_logger.log_challenge_event('combat', 'failed', False)
        
        self.mock_logger.log.assert_called_once()
        call_args = self.mock_logger.log.call_args
        
        assert call_args[0][0] == logging.WARNING  # Log level for failure
    
    def test_log_error_recovery_success(self):
        """Test logging successful error recovery."""
        self.game_logger.log_error_recovery('invalid_command', 'suggest_similar', True)
        
        self.mock_logger.log.assert_called_once()
        call_args = self.mock_logger.log.call_args
        
        assert call_args[0][0] == logging.INFO
        assert 'Error recovery: suggest_similar for invalid_command - Success' in call_args[0][1]
    
    def test_log_error_recovery_failure(self):
        """Test logging failed error recovery."""
        self.game_logger.log_error_recovery('save_error', 'retry_save', False)
        
        self.mock_logger.log.assert_called_once()
        call_args = self.mock_logger.log.call_args
        
        assert call_args[0][0] == logging.ERROR
        assert 'Failed' in call_args[0][1]
    
    def test_log_performance_metric(self):
        """Test logging performance metrics."""
        self.game_logger.log_performance_metric('response_time', 0.123, {'command': 'look'})
        
        self.mock_logger.debug.assert_called_once()
        call_args = self.mock_logger.debug.call_args
        
        assert 'Performance metric response_time: 0.123' in call_args[0][0]
        assert call_args[1]['extra']['context']['metric_name'] == 'response_time'
        assert call_args[1]['extra']['context']['value'] == 0.123
    
    def test_session_id_consistency(self):
        """Test that session ID is consistent across logs."""
        self.game_logger.log_player_action('action1', 1)
        self.game_logger.log_player_action('action2', 2)
        
        assert self.mock_logger.info.call_count == 2
        
        # Get session IDs from both calls
        call1_session = self.mock_logger.info.call_args_list[0][1]['extra']['session_id']
        call2_session = self.mock_logger.info.call_args_list[1][1]['extra']['session_id']
        
        assert call1_session == call2_session


class TestEnhancedLoggingSetup:
    """Test enhanced logging setup functionality."""
    
    def test_setup_logging_with_rotation(self):
        """Test logging setup with file rotation."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            logger = setup_logging(debug=True, log_file=temp_filename, 
                                 max_log_files=5, max_file_size=1024)
            
            # Should have console, main file, and error file handlers
            assert len(logger.handlers) == 3
            
            # Check for rotating file handler
            rotating_handlers = [h for h in logger.handlers 
                               if isinstance(h, logging.handlers.RotatingFileHandler)]
            assert len(rotating_handlers) == 2  # Main log and error log
            
            # Check rotation settings
            main_handler = rotating_handlers[0]
            assert main_handler.maxBytes == 1024
            assert main_handler.backupCount == 5
            
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_setup_logging_creates_error_log(self):
        """Test that setup creates separate error log file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, 'test.log')
            error_log_file = os.path.join(temp_dir, 'error_test.log')
            
            logger = setup_logging(debug=True, log_file=log_file)
            
            # Log an error message
            logger.error("Test error message")
            
            # Force flush all handlers
            for handler in logger.handlers:
                handler.flush()
            
            # Check that error log file was created
            assert os.path.exists(error_log_file)
    
    def test_setup_logging_console_filter(self):
        """Test that console handler filters debug messages in non-debug mode."""
        logger = setup_logging(verbose=True)  # INFO level, not DEBUG
        
        console_handler = None
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                console_handler = handler
                break
        
        assert console_handler is not None
        assert console_handler.level == logging.INFO
    
    def test_logger_propagation_disabled(self):
        """Test that logger propagation is disabled."""
        logger = setup_logging()
        assert not logger.propagate


class TestGetGameStateLogger:
    """Test get_game_state_logger function."""
    
    def test_get_game_state_logger_default(self):
        """Test getting default game state logger."""
        game_logger = get_game_state_logger()
        
        assert isinstance(game_logger, GameStateLogger)
        assert game_logger.logger.name == 'labrynth'
    
    def test_get_game_state_logger_with_name(self):
        """Test getting named game state logger."""
        game_logger = get_game_state_logger('engine')
        
        assert isinstance(game_logger, GameStateLogger)
        assert game_logger.logger.name == 'labrynth.engine'


class TestLogException:
    """Test log_exception function."""
    
    def test_log_exception_basic(self):
        """Test basic exception logging."""
        mock_logger = Mock(spec=logging.Logger)
        test_exception = ValueError("Test error")
        
        log_exception(mock_logger, test_exception)
        
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        
        assert 'ValueError: Test error' in call_args[0][0]
        assert call_args[1]['exc_info'] is True
        assert 'context' in call_args[1]['extra']
        assert call_args[1]['extra']['context']['exception_type'] == 'ValueError'
    
    def test_log_exception_with_context(self):
        """Test exception logging with additional context."""
        mock_logger = Mock(spec=logging.Logger)
        test_exception = RuntimeError("Runtime error")
        context = {'operation': 'save_game', 'file': 'test.sav'}
        
        log_exception(mock_logger, test_exception, context)
        
        call_args = mock_logger.error.call_args
        assert call_args[1]['extra']['context']['operation'] == 'save_game'
        assert call_args[1]['extra']['context']['file'] == 'test.sav'


class TestConfigureThirdPartyLogging:
    """Test third-party logging configuration."""
    
    def test_configure_third_party_logging(self):
        """Test that third-party logging is configured correctly."""
        # Reset loggers to default state
        logging.getLogger('urllib3').setLevel(logging.NOTSET)
        logging.getLogger('requests').setLevel(logging.NOTSET)
        
        configure_third_party_logging()
        
        assert logging.getLogger('urllib3').level == logging.WARNING
        assert logging.getLogger('requests').level == logging.WARNING


class TestLogContext:
    """Test LogContext context manager."""
    
    def test_log_context_basic(self):
        """Test basic log context functionality."""
        mock_logger = Mock(spec=logging.Logger)
        mock_logger._context = {}
        
        with LogContext(mock_logger, chamber_id=1, action='move'):
            assert mock_logger._context == {'chamber_id': 1, 'action': 'move'}
        
        assert mock_logger._context == {}
    
    def test_log_context_nested(self):
        """Test nested log contexts."""
        mock_logger = Mock(spec=logging.Logger)
        mock_logger._context = {'session_id': 'test'}
        
        with LogContext(mock_logger, chamber_id=1):
            assert mock_logger._context == {'session_id': 'test', 'chamber_id': 1}
            
            with LogContext(mock_logger, action='move'):
                assert mock_logger._context == {
                    'session_id': 'test', 
                    'chamber_id': 1, 
                    'action': 'move'
                }
            
            assert mock_logger._context == {'session_id': 'test', 'chamber_id': 1}
        
        assert mock_logger._context == {'session_id': 'test'}


class TestCreateLogFilenameEnhanced:
    """Test enhanced log filename creation."""
    
    def test_create_log_filename_with_prefix(self):
        """Test log filename creation with custom prefix."""
        filename = create_log_filename('error')
        
        assert filename.startswith('logs/error_')
        assert filename.endswith('.log')
    
    @patch('src.utils.logging.datetime')
    def test_create_log_filename_custom_prefix(self, mock_datetime):
        """Test log filename creation with custom prefix and mocked datetime."""
        mock_now = Mock()
        mock_now.strftime.return_value = '20240101_120000'
        mock_datetime.now.return_value = mock_now
        
        filename = create_log_filename('debug')
        
        assert filename == 'logs/debug_20240101_120000.log'


class TestLoggingIntegrationEnhanced:
    """Test enhanced logging integration."""
    
    def test_structured_logging_integration(self):
        """Test that structured logging works end-to-end."""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # Setup logging
            logger = setup_logging(debug=True, log_file=temp_filename)
            game_logger = GameStateLogger(logger)
            
            # Log various types of events
            game_logger.log_player_action('move north', 1, {'direction': 'north'})
            game_logger.log_game_state_change('health', 100, 90)
            game_logger.log_challenge_event('riddle', 'completed', True)
            
            # Force flush
            for handler in logger.handlers:
                handler.flush()
            
            # Read and verify log content
            with open(temp_filename, 'r') as f:
                log_content = f.read()
            
            assert 'Player action: move north in chamber 1' in log_content
            assert 'State change in health: 100 -> 90' in log_content
            assert 'Challenge riddle: completed' in log_content
            assert 'Context:' in log_content
            
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_error_logging_separation(self):
        """Test that errors are logged to separate file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, 'test.log')
            error_log_file = os.path.join(temp_dir, 'error_test.log')
            
            logger = setup_logging(debug=True, log_file=log_file)
            
            # Log messages at different levels
            logger.info("Info message")
            logger.error("Error message")
            logger.critical("Critical message")
            
            # Force flush
            for handler in logger.handlers:
                handler.flush()
            
            # Check main log file
            with open(log_file, 'r') as f:
                main_content = f.read()
            
            # Check error log file
            with open(error_log_file, 'r') as f:
                error_content = f.read()
            
            # Main log should have all messages
            assert 'Info message' in main_content
            assert 'Error message' in main_content
            assert 'Critical message' in main_content
            
            # Error log should only have error and critical
            assert 'Info message' not in error_content
            assert 'Error message' in error_content
            assert 'Critical message' in error_content