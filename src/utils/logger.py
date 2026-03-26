import logging
import os
from datetime import datetime
from src.utils.config import config

def setup_logger(name: str = "newsletter_generator") -> logging.Logger:
    """Set up logging configuration."""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.log_level))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler
    log_file = os.path.join(config.log_dir, f"{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Global logger instance
logger = setup_logger()

def log_audit_event(topic, output_file):
    """Log an audit event for newsletter generation."""
    audit_log_path = os.path.join(config.log_dir, 'audit.log')
    timestamp = datetime.now().isoformat()
    with open(audit_log_path, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp}\t{topic}\t{output_file}\n") 