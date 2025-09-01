import logging
import os
from pathlib import Path

logger = logging.getLogger("medixai")
logger.setLevel(logging.INFO)

# Create handlers
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)

try:
    # Create log directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create file handler
    file_handler = logging.FileHandler(log_dir / "medical_ai.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.info("Logging initialized successfully")
except Exception as e:
    logger.warning(f"Log directory not found. Skipping file logging. Error: {str(e)}")