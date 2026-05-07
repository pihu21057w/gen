"""
Logging configuration for the pipeline
"""
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import yaml


class LoggerConfig:
    """Configure logging for the pipeline"""
    
    _logger_instance = None
    
    @classmethod
    def setup_logger(
        cls,
        name: str = "dataset_pipeline",
        config_file: Optional[Path] = None,
        log_file: Optional[str] = None,
        level: Optional[str] = None,
    ) -> logging.Logger:
        """
        Setup and configure logger
        
        Args:
            name: Logger name
            config_file: Path to YAML config file
            log_file: Path to log file
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            
        Returns:
            Configured logger instance
        """
        if cls._logger_instance is not None:
            return cls._logger_instance
        
        # Load config if provided
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                log_config = config.get('logging', {})
                log_file = log_file or log_config.get('log_file', 'pipeline.log')
                level = level or log_config.get('level', 'INFO')
        
        level = level or 'INFO'
        log_file = log_file or 'pipeline.log'
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level))
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        cls._logger_instance = logger
        return logger
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get existing logger or create new one"""
        if cls._logger_instance is None:
            return cls.setup_logger()
        return cls._logger_instance


def get_logger(name: str = "dataset_pipeline") -> logging.Logger:
    """Convenience function to get logger"""
    return LoggerConfig.get_logger()
