# app/core/logging_config.py

import logging
from logging.handlers import RotatingFileHandler
import sys
import os

def configure_logging():
    """Configures logging for the application."""

    logger = logging.getLogger("app.core")

    # ✅ Prevent duplicate handlers
    if logger.hasHandlers():
        return logger  # Return existing logger without adding new handlers

    logger.setLevel(logging.INFO)
    logger.propagate = False  # Prevents duplicate logs from propagating

    os.makedirs("logs", exist_ok=True)

    # Formatters (include log level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File Handler
    file_handler = RotatingFileHandler("logs/core.log", maxBytes=10**6, backupCount=3)
    file_handler.setFormatter(formatter)

    # Add Handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info("🚀 Console logging test - Should appear in terminal!")

    return logger
