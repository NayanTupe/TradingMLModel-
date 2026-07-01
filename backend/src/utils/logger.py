"""
Centralised logger for the trading system.
"""
import logging
from logging.handlers import RotatingFileHandler
import sys

def get_logger(name, log_file='logs/trading.log', level=logging.INFO):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured
    
    logger.setLevel(level)
    
    # File handler with rotation (10 MB per file, keep 5)
    fh = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    fh.setLevel(level)
    
    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger