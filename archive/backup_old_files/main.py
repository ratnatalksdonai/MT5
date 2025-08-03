"""
Main Application Script

Entry point for the application.
"""
import logging
import sys
import os
sys.path.append('src')
from config_manager import ConfigManager
from trade_copier import TradeCopier
from notification_logger import CustomLogger, NotificationManager


if __name__ == "__main__":
    # Configure logging
    logging_config = {
        "level": "INFO",
        "file_path": "logs/trade_copier.log",
        "max_file_size_mb": 10,
        "backup_count": 5,
        "console_output": True
    }
    CustomLogger(logging_config)

    # Load configuration
    config_path = "config/config.json"
    encryption_key_path = "data/secret.key"

    if not os.path.exists(encryption_key_path):
        logging.error("Encryption key is missing. Please run 'setup.py' to generate encryption key.")
        exit(1)

    with open(encryption_key_path, "rb") as key_file:
        encryption_key = key_file.read()

    config_manager = ConfigManager(config_path, encryption_key)
    config = config_manager.load_config()

    # Set up notification manager
    notification_manager = NotificationManager(config.notifications.dict())

    # Create and start trade copier
    trade_copier = TradeCopier(config_manager)
    trade_copier.start()

    # Handle shutdown
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.info("Shutting down trade copier...")
        trade_copier.shutdown()
