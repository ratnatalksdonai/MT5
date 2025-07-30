"""
Configuration Manager Module for managing JSON configuration files.

- Loads, validates, and can hot-reload configurations.
- Provides encryption and decryption for sensitive fields.
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from cryptography.fernet import Fernet
import threading
import time
from pathlib import Path


class MT5AccountConfig(BaseModel):
    """MT5 Account Configuration"""

    account_id: str
    server: str
    login: str
    password: str
    terminal_path: Optional[str] = None


class MatchTradeAccountConfig(BaseModel):
    """Match-Trader Account Configuration"""

    account_id: str
    broker_id: str
    base_url: str
    api_key: str
    secret: str


class TradeSettingsConfig(BaseModel):
    """Trade Settings Configuration"""

    lot_size_mode: str = Field(default="proportional", pattern="^(proportional|equity_based)$")
    lot_multiplier: float = Field(default=1.0, ge=0.01, le=100.0)
    max_lot_size: float = Field(default=10.0, ge=0.01)
    min_lot_size: float = Field(default=0.01, ge=0.01)
    symbol_mapping: Dict[str, str] = Field(default_factory=dict)
    allowed_symbols: List[str] = Field(default_factory=list)
    copy_pending_orders: bool = Field(default=False)
    copy_sl_tp: bool = Field(default=True)


class NotificationConfig(BaseModel):
    """Notification Settings Configuration"""

    enabled: bool = Field(default=True)
    webhook_url: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    email: Optional[Dict[str, Any]] = None


class LoggingConfig(BaseModel):
    """Logging Configuration"""

    level: str = Field(default="INFO")
    file_path: str = Field(default="logs/trade_copier.log")
    max_file_size_mb: int = Field(default=100, ge=1)
    backup_count: int = Field(default=10, ge=1)
    console_output: bool = Field(default=True)


class PerformanceConfig(BaseModel):
    """Performance Settings Configuration"""

    max_latency_ms: int = Field(default=100, ge=10)
    health_check_interval_seconds: int = Field(default=60, ge=10)
    connection_timeout_seconds: int = Field(default=30, ge=5)
    heartbeat_interval_seconds: int = Field(default=30, ge=5)
    retry_max_attempts: int = Field(default=5, ge=1)
    retry_delay_seconds: int = Field(default=5, ge=1)


class TradeCopierConfig(BaseModel):
    """Main Trade Copier Configuration"""

    mt5_accounts: List[MT5AccountConfig]
    matchtrade_accounts: List[MatchTradeAccountConfig]
    trade_settings: TradeSettingsConfig
    notifications: NotificationConfig
    logging: LoggingConfig
    performance: PerformanceConfig


class ConfigManager:
    """Configuration Manager with hot-reload support"""

    def __init__(self, config_path: str, encryption_key: Optional[str] = None):
        self.config_path = Path(config_path)
        self.encryption_key = encryption_key
        self.config: Optional[TradeCopierConfig] = None
        self.last_modified = 0
        self.reload_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        self._fernet = None

        if encryption_key:
            self._fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)

        self.load_config()

    def load_config(self) -> TradeCopierConfig:
        """Load and validate configuration from file"""
        try:
            with self.reload_lock:
                if not self.config_path.exists():
                    raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

                with open(self.config_path, "r") as f:
                    config_data = json.load(f)

                # Decrypt sensitive fields if encryption is enabled
                if self._fernet:
                    config_data = self._decrypt_config(config_data)

                # Validate configuration using Pydantic
                self.config = TradeCopierConfig(**config_data)
                self.last_modified = os.path.getmtime(self.config_path)

                self.logger.info(f"Configuration loaded successfully from {self.config_path}")
                return self.config

        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise

    def _decrypt_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive fields in configuration"""
        # Decrypt MT5 passwords
        for mt5_account in config_data.get("mt5_accounts", []):
            if "password" in mt5_account and mt5_account["password"].startswith("encrypted:"):
                encrypted_value = mt5_account["password"][10:]  # Remove 'encrypted:' prefix
                mt5_account["password"] = self._fernet.decrypt(encrypted_value.encode()).decode()

        # Decrypt Match-Trader API keys and secrets
        for mt_account in config_data.get("matchtrade_accounts", []):
            if "api_key" in mt_account and mt_account["api_key"].startswith("encrypted:"):
                encrypted_value = mt_account["api_key"][10:]
                mt_account["api_key"] = self._fernet.decrypt(encrypted_value.encode()).decode()

            if "secret" in mt_account and mt_account["secret"].startswith("encrypted:"):
                encrypted_value = mt_account["secret"][10:]
                mt_account["secret"] = self._fernet.decrypt(encrypted_value.encode()).decode()

        return config_data

    def encrypt_sensitive_fields(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive fields for secure storage"""
        if not self._fernet:
            raise ValueError("Encryption key not provided")

        encrypted_config = config_data.copy()

        # Encrypt MT5 passwords
        for mt5_account in encrypted_config.get("mt5_accounts", []):
            if "password" in mt5_account and not mt5_account["password"].startswith("encrypted:"):
                encrypted_password = self._fernet.encrypt(mt5_account["password"].encode()).decode()
                mt5_account["password"] = f"encrypted:{encrypted_password}"

        # Encrypt Match-Trader API keys and secrets
        for mt_account in encrypted_config.get("matchtrade_accounts", []):
            if "api_key" in mt_account and not mt_account["api_key"].startswith("encrypted:"):
                encrypted_key = self._fernet.encrypt(mt_account["api_key"].encode()).decode()
                mt_account["api_key"] = f"encrypted:{encrypted_key}"

            if "secret" in mt_account and not mt_account["secret"].startswith("encrypted:"):
                encrypted_secret = self._fernet.encrypt(mt_account["secret"].encode()).decode()
                mt_account["secret"] = f"encrypted:{encrypted_secret}"

        return encrypted_config

    def save_config(self, config_data: Dict[str, Any], encrypt: bool = True):
        """Save configuration to file"""
        try:
            if encrypt and self._fernet:
                config_data = self.encrypt_sensitive_fields(config_data)

            with open(self.config_path, "w") as f:
                json.dump(config_data, f, indent=2)

            self.logger.info(f"Configuration saved to {self.config_path}")

        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            raise

    def check_reload(self) -> bool:
        """Check if configuration file has been modified and reload if necessary"""
        try:
            current_mtime = os.path.getmtime(self.config_path)
            if current_mtime > self.last_modified:
                self.logger.info("Configuration file changed, reloading...")
                self.load_config()
                return True
            return False

        except Exception as e:
            self.logger.error(f"Failed to check configuration reload: {str(e)}")
            return False

    def get_mt5_account(self, account_id: str) -> Optional[MT5AccountConfig]:
        """Get MT5 account configuration by ID"""
        if not self.config:
            return None

        for account in self.config.mt5_accounts:
            if account.account_id == account_id:
                return account
        return None

    def get_matchtrade_account(self, account_id: str) -> Optional[MatchTradeAccountConfig]:
        """Get Match-Trader account configuration by ID"""
        if not self.config:
            return None

        for account in self.config.matchtrade_accounts:
            if account.account_id == account_id:
                return account
        return None

    def validate_symbol_mapping(self, symbol: str) -> Optional[str]:
        """Validate and map symbol according to configuration"""
        if not self.config:
            return None

        # Check direct mapping
        if symbol in self.config.trade_settings.symbol_mapping:
            mapped_symbol = self.config.trade_settings.symbol_mapping[symbol]
        else:
            # Remove .z suffix if present
            mapped_symbol = symbol.replace(".z", "")

        # Check if symbol is allowed (only if allowed_symbols list is not empty)
        if self.config.trade_settings.allowed_symbols:
            if mapped_symbol not in self.config.trade_settings.allowed_symbols:
                return None

        return mapped_symbol

    def generate_encryption_key(self) -> str:
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()


def create_sample_config(output_path: str = "config.json"):
    """Create a sample configuration file"""
    sample_config = {
        "mt5_accounts": [
            {
                "account_id": "12345678",
                "server": "MetaQuotes-Demo",
                "login": "username",
                "password": "password",
                "terminal_path": "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            }
        ],
        "matchtrade_accounts": [
            {
                "account_id": "MT-12345",
                "broker_id": "FTUK",
                "base_url": "wss://api.ftuk.com/ws",
                "api_key": "your_api_key",
                "secret": "your_secret",
            }
        ],
        "trade_settings": {
            "lot_size_mode": "proportional",
            "lot_multiplier": 1.0,
            "max_lot_size": 10.0,
            "min_lot_size": 0.01,
            "symbol_mapping": {"EURUSD.z": "EURUSD", "GBPUSD.z": "GBPUSD"},
            "allowed_symbols": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"],
            "copy_pending_orders": False,
            "copy_sl_tp": True,
        },
        "notifications": {
            "enabled": True,
            "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
            "telegram_bot_token": "YOUR_BOT_TOKEN",
            "telegram_chat_id": "YOUR_CHAT_ID",
        },
        "logging": {
            "level": "INFO",
            "file_path": "logs/trade_copier.log",
            "max_file_size_mb": 100,
            "backup_count": 10,
            "console_output": True,
        },
        "performance": {
            "max_latency_ms": 100,
            "health_check_interval_seconds": 60,
            "connection_timeout_seconds": 30,
            "heartbeat_interval_seconds": 30,
            "retry_max_attempts": 5,
            "retry_delay_seconds": 5,
        },
    }

    with open(output_path, "w") as f:
        json.dump(sample_config, f, indent=2)

    print(f"Sample configuration created at: {output_path}")


if __name__ == "__main__":
    # Example usage
    create_sample_config()
