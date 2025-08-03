"""
Notification and Logging System Module.

- Provides structured logging with rotation and formatting.
- Sends notifications to Slack, Telegram, and other services.
"""

import logging
import requests
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict


class NotificationManager:
    """Handles notifications to external services"""

    def __init__(self, config: Dict):
        self.config = config

    def send_slack_notification(self, message: str):
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return
        payload = {"text": message}
        requests.post(webhook_url, json=payload)

    def send_telegram_notification(self, message: str):
        token = self.config.get("telegram_bot_token")
        chat_id = self.config.get("telegram_chat_id")
        if not token or not chat_id:
            return
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        requests.post(url, data=payload)


class CustomLogger:
    """Sets up a structured logger with rotation"""

    def __init__(self, log_config: Dict):
        level = getattr(logging, log_config.get("level", "INFO"))
        file_path = log_config.get("file_path", "logs/app.log")
        max_file_size = log_config.get("max_file_size_mb", 100) * 1024 * 1024
        backup_count = log_config.get("backup_count", 10)
        console_output = log_config.get("console_output", True)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)

        file_handler = RotatingFileHandler(file_path, maxBytes=max_file_size, backupCount=backup_count)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)


if __name__ == "__main__":
    # Testing the notification manager
    logging_config = {
        "level": "INFO",
        "file_path": "logs/app.log",
        "max_file_size_mb": 10,
        "backup_count": 10,
        "console_output": True,
    }

    custom_logger = CustomLogger(logging_config)
    notification_config = {
        "webhook_url": "your_slack_webhook_url",
        "telegram_bot_token": "your_telegram_bot_token",
        "telegram_chat_id": "your_telegram_chat_id",
    }

    notifier = NotificationManager(notification_config)
    notifier.send_slack_notification("Test Slack Notification")
    notifier.send_telegram_notification("Test Telegram Notification")
