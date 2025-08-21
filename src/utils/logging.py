"""Logging utilities for the Labyrinth Adventure Game."""

import logging
import logging.handlers
import os
import sys
import json
from typing import Optional, Dict, Any, Union
from datetime import datetime
from pathlib import Path


class GameLogFormatter(logging.Formatter):
    """Custom formatter for game logs with structured output."""
    
    def __init__(self, include_context: bool = True):
        self.include_context = include_context
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with game-specific information."""
        # Base format
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        level = record.levelname
        name = record.name.replace('labrynth.', '')
        message = record.getMessage()
        
        # Add context information if available
        context_info = ""
        if self.include_context and hasattr(record, 'context'):
            context = record.context
            if isinstance(context, dict) and context:
                context_str = json.dumps(context, separators=(',', ':'))
                context_info = f" | Context: {context_str}"
        
        # Add player information if available
        player_info = ""
        if hasattr(record, 'player_id'):
            player_info = f" | Player: {record.player_id}"
        
        # Add session information if available
        session_info = ""
        if hasattr(record, 'session_id'):
            session_info = f" | Session: {record.session_id}"
        
        return f"{timestamp} | {level:8} | {name:15} | {message}{context_info}{player_info}{session_info}"


class GameStateLogger:
    """Specialized logger for game state changes and user actions."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def log_player_action(self, action: str, chamber_id: int, context: Optional[Dict[str, Any]] = None):
        """Log player actions with context."""
        log_context = {
            'action_type': 'player_action',
            'action': action,
            'chamber_id': chamber_id,
            **(context or {})
        }
        self.logger.info(f"Player action: {action} in chamber {chamber_id}", 
                        extra={'context': log_context, 'session_id': self.session_id})
    
    def log_game_state_change(self, component: str, old_state: Any, new_state: Any, 
                             context: Optional[Dict[str, Any]] = None):
        """Log game state changes."""
        log_context = {
            'change_type': 'state_change',
            'component': component,
            'old_state': str(old_state),
            'new_state': str(new_state),
            **(context or {})
        }
        self.logger.debug(f"State change in {component}: {old_state} -> {new_state}",
                         extra={'context': log_context, 'session_id': self.session_id})
    
    def log_challenge_event(self, challenge_type: str, event: str, success: bool = None,
                           context: Optional[Dict[str, Any]] = None):
        """Log challenge-related events."""
        log_context = {
            'event_type': 'challenge_event',
            'challenge_type': challenge_type,
            'event': event,
            'success': success,
            **(context or {})
        }
        level = logging.INFO if success is not False else logging.WARNING
        self.logger.log(level, f"Challenge {challenge_type}: {event}",
                       extra={'context': log_context, 'session_id': self.session_id})
    
    def log_error_recovery(self, error_type: str, recovery_action: str, success: bool,
                          context: Optional[Dict[str, Any]] = None):
        """Log error recovery attempts."""
        log_context = {
            'event_type': 'error_recovery',
            'error_type': error_type,
            'recovery_action': recovery_action,
            'success': success,
            **(context or {})
        }
        level = logging.INFO if success else logging.ERROR
        self.logger.log(level, f"Error recovery: {recovery_action} for {error_type} - {'Success' if success else 'Failed'}",
                       extra={'context': log_context, 'session_id': self.session_id})
    
    def log_performance_metric(self, metric_name: str, value: Union[int, float], 
                              context: Optional[Dict[str, Any]] = None):
        """Log performance metrics."""
        log_context = {
            'metric_type': 'performance',
            'metric_name': metric_name,
            'value': value,
            **(context or {})
        }
        self.logger.debug(f"Performance metric {metric_name}: {value}",
                         extra={'context': log_context, 'session_id': self.session_id})


def setup_logging(debug: bool = False, verbose: bool = False, log_file: Optional[str] = None,
                 max_log_files: int = 10, max_file_size: int = 10 * 1024 * 1024) -> logging.Logger:
    """Set up comprehensive logging configuration for the game.
    
    Args:
        debug: Enable debug level logging
        verbose: Enable verbose (info level) logging
        log_file: Optional log file path
        max_log_files: Maximum number of log files to keep (for rotation)
        max_file_size: Maximum size of each log file in bytes
        
    Returns:
        Configured logger instance
    """
    # Determine log level
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    
    # Create main logger
    logger = logging.getLogger('labrynth')
    logger.setLevel(logging.DEBUG)  # Always capture all levels, handlers will filter
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    console_formatter = GameLogFormatter(include_context=False)
    file_formatter = GameLogFormatter(include_context=True)
    
    # Console handler - only show important messages to user
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    
    # Add filter to prevent debug messages from cluttering console unless debug mode
    if not debug:
        console_handler.addFilter(lambda record: record.levelno >= logging.INFO)
    
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=max_log_files
        )
        file_handler.setLevel(logging.DEBUG)  # Always log debug to file
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Create separate error log
        error_log_file = log_path.parent / f"error_{log_path.name}"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_file_size,
            backupCount=max_log_files
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    # Log initial setup message
    logger.info(f"Logging system initialized - Console Level: {logging.getLevelName(log_level)}")
    if log_file:
        logger.info(f"Log files: {log_file} (main), error_{Path(log_file).name} (errors)")
        logger.debug(f"Log rotation: {max_log_files} files, {max_file_size} bytes each")
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Optional logger name (defaults to 'labrynth')
        
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f'labrynth.{name}')
    return logging.getLogger('labrynth')


def get_game_state_logger(name: Optional[str] = None) -> GameStateLogger:
    """Get a game state logger instance.
    
    Args:
        name: Optional logger name component
        
    Returns:
        GameStateLogger instance
    """
    logger = get_logger(name)
    return GameStateLogger(logger)


def create_log_filename(prefix: str = "game") -> str:
    """Create a timestamped log filename.
    
    Args:
        prefix: Prefix for the log filename
        
    Returns:
        Log filename with timestamp
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"logs/{prefix}_{timestamp}.log"


def log_exception(logger: logging.Logger, exception: Exception, context: Optional[Dict[str, Any]] = None):
    """Log an exception with full traceback and context.
    
    Args:
        logger: Logger instance to use
        exception: Exception to log
        context: Additional context information
    """
    log_context = {
        'exception_type': type(exception).__name__,
        'exception_message': str(exception),
        **(context or {})
    }
    
    logger.error(f"Exception occurred: {type(exception).__name__}: {exception}",
                extra={'context': log_context}, exc_info=True)


def configure_third_party_logging():
    """Configure logging for third-party libraries to reduce noise."""
    # Reduce noise from common third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    # Add more third-party loggers as needed


class LogContext:
    """Context manager for adding context to log messages."""
    
    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.old_context = getattr(logger, '_context', {})
    
    def __enter__(self):
        # Merge contexts
        new_context = {**self.old_context, **self.context}
        self.logger._context = new_context
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore old context
        self.logger._context = self.old_context