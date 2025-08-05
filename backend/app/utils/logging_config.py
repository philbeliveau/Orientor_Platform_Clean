import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Set up logging configuration"""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up logging configuration
    log_file = os.path.join(log_dir, 'app.log')
    
    # Create a rotating file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    
    # Set up the formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Add the handlers to the root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create a logger for the application
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)
    
    return logger 