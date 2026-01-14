import logging
import sys

def setup_logging(debug_mode: bool = False):
    """Configures the logging for the application."""
    level = logging.DEBUG if debug_mode else logging.INFO
    
    # Create logger
    logger = logging.getLogger("webbinder")
    logger.setLevel(level)
    
    # Create console handler and set level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add formatter to ch
    ch.setFormatter(formatter)
    
    # Add ch to logger
    if not logger.handlers:
        logger.addHandler(ch)
    
    return logger
