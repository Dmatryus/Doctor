"""
Logging setup for Doctor service
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from .config import settings


def setup_logging(
    level: Optional[str] = None,
    log_to_file: bool = None,
    log_dir: Optional[Path] = None
) -> None:
    """
    Setup logging configuration for the application
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_dir: Directory for log files
    """
    # Use settings defaults if not provided
    level = level or settings.LOG_LEVEL
    log_to_file = log_to_file if log_to_file is not None else settings.LOG_TO_FILE
    log_dir = log_dir or settings.storage_paths['logs']
    
    # Ensure log directory exists
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt=settings.LOG_FORMAT,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Setup file handler if enabled
    if log_to_file:
        log_file = log_dir / "doctor.log"
        
        if settings.LOG_ROTATION:
            # Use rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_file,
                maxBytes=_parse_size(settings.LOG_MAX_SIZE),
                backupCount=settings.LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
        else:
            # Use regular file handler
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
        
        file_handler.setLevel(getattr(logging, level))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels for third-party libraries
    _configure_third_party_loggers()
    
    # Log startup message
    logger = logging.getLogger("doctor.startup")
    logger.info(f"Logging configured: level={level}, file_logging={log_to_file}")


def _parse_size(size_str: str) -> int:
    """
    Parse size string like '10MB' to bytes
    
    Args:
        size_str: Size string (e.g., '10MB', '1GB')
        
    Returns:
        Size in bytes
    """
    size_str = size_str.upper()
    
    if size_str.endswith('B'):
        size_str = size_str[:-1]
    
    multipliers = {
        'K': 1024,
        'M': 1024 ** 2,
        'G': 1024 ** 3,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
    }
    
    for suffix, multiplier in multipliers.items():
        if size_str.endswith(suffix):
            number = size_str[:-len(suffix)]
            return int(float(number) * multiplier)
    
    # No suffix, assume bytes
    return int(size_str)


def _configure_third_party_loggers() -> None:
    """Configure logging levels for third-party libraries"""
    
    # FastAPI and Uvicorn
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    # HTTP libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Other libraries
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.INFO)
    
    # Conversion libraries
    logging.getLogger("markdown").setLevel(logging.WARNING)
    logging.getLogger("pdfplumber").setLevel(logging.WARNING)
    logging.getLogger("weasyprint").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def get_app_logger() -> logging.Logger:
    """Get the main application logger"""
    return get_logger("doctor.app")


def get_api_logger() -> logging.Logger:
    """Get the API logger"""
    return get_logger("doctor.api")


def get_conversion_logger() -> logging.Logger:
    """Get the conversion logger"""
    return get_logger("doctor.conversion")


def get_websocket_logger() -> logging.Logger:
    """Get the WebSocket logger"""
    return get_logger("doctor.websocket")


def get_task_logger() -> logging.Logger:
    """Get the task logger"""
    return get_logger("doctor.task")


def log_startup_info() -> None:
    """Log application startup information"""
    logger = get_app_logger()
    
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Host: {settings.APP_HOST}:{settings.APP_PORT}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"Storage root: {settings.STORAGE_ROOT}")
    logger.info(f"Max concurrent tasks: {settings.MAX_CONCURRENT_TASKS}")
    logger.info(f"Cache size: {settings.CACHE_SIZE}")
    logger.info("=" * 60)


def log_shutdown_info() -> None:
    """Log application shutdown information"""
    logger = get_app_logger()
    logger.info("Shutting down Doctor service...")


class LoggerMixin:
    """Mixin class to add logging functionality to other classes"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return get_logger(f"doctor.{self.__class__.__name__.lower()}")
    
    def log_debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self.logger.debug(message, **kwargs)
    
    def log_info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self.logger.info(message, **kwargs)
    
    def log_warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self.logger.warning(message, **kwargs)
    
    def log_error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log error message"""
        self.logger.error(message, exc_info=exc_info, **kwargs)
    
    def log_critical(self, message: str, exc_info: bool = True, **kwargs) -> None:
        """Log critical message"""
        self.logger.critical(message, exc_info=exc_info, **kwargs)


# Context manager for temporary log level changes
class TemporaryLogLevel:
    """Context manager to temporarily change log level"""
    
    def __init__(self, logger_name: str, level: str):
        self.logger = logging.getLogger(logger_name)
        self.level = getattr(logging, level.upper())
        self.original_level = None
    
    def __enter__(self):
        self.original_level = self.logger.level
        self.logger.setLevel(self.level)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)