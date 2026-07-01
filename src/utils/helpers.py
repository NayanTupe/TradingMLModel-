# helper functions
"""
Utility functions: config loading, time helpers, data validation.
"""

import yaml
import logging
import pandas as pd
import numpy as np
from datetime import datetime

def load_config(config_path):
    """Load YAML configuration file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def setup_logging(log_file, level=logging.INFO, max_bytes=10485760, backup_count=5):
    """Setup rotating file logger."""
    from logging.handlers import RotatingFileHandler
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # File handler with rotation
    fh = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    fh.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    return logger

def validate_data(df, required_columns):
    """Check if DataFrame has required columns and no nulls."""
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    
    if df.isnull().sum().sum() > 0:
        raise ValueError("Data contains null values")
    
    if df[required_columns].isin([np.inf, -np.inf]).any().any():
        raise ValueError("Data contains inf values")
    
    return True

def get_current_time():
    """Return current datetime (timezone naive for simplicity)."""
    return datetime.now()