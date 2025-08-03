"""
Secure Configuration Manager
Handles encrypted storage and retrieval of sensitive configuration data
"""

import os
import json
import base64
import logging
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SecureConfigManager:
    """Manages encrypted configuration with secure key storage"""
    
    def __init__(self, config_path: str = "config/secure_config.enc"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(exist_ok=True)
        self._cipher_suite = None
        self._master_key = None
        
    def _derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def initialize_encryption(self, master_password: Optional[str] = None) -> None:
        """Initialize encryption with master password or environment variable"""
        if master_password is None:
            # Try to get from environment variable
            master_password = os.environ.get('MT5_COPIER_MASTER_KEY')
            if not master_password:
                raise ValueError("Master password not provided and MT5_COPIER_MASTER_KEY not set")
        
        # Use a fixed salt for this application (in production, store this securely)
        salt = b'MT5-MatchTrader-MVP-Salt-2024'
        self._master_key = self._derive_key_from_password(master_password, salt)
        self._cipher_suite = Fernet(self._master_key)
        
    def encrypt_config(self, config_data: Dict[str, Any]) -> None:
        """Encrypt and save configuration data"""
        if not self._cipher_suite:
            raise RuntimeError("Encryption not initialized. Call initialize_encryption first.")
        
        # Convert config to JSON
        json_data = json.dumps(config_data, indent=2)
        
        # Encrypt the data
        encrypted_data = self._cipher_suite.encrypt(json_data.encode())
        
        # Save to file
        with open(self.config_path, 'wb') as f:
            f.write(encrypted_data)
            
        logger.info(f"Configuration encrypted and saved to {self.config_path}")
        
    def decrypt_config(self) -> Dict[str, Any]:
        """Decrypt and load configuration data"""
        if not self._cipher_suite:
            raise RuntimeError("Encryption not initialized. Call initialize_encryption first.")
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Encrypted config file not found: {self.config_path}")
        
        # Read encrypted data
        with open(self.config_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt the data
        try:
            decrypted_data = self._cipher_suite.decrypt(encrypted_data)
            config_data = json.loads(decrypted_data.decode())
            logger.info("Configuration decrypted successfully")
            return config_data
        except Exception as e:
            logger.error(f"Failed to decrypt configuration: {e}")
            raise ValueError("Invalid master password or corrupted configuration file")
    
    def secure_get_credential(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a credential from environment variables or encrypted config"""
        # First check environment variables
        env_value = os.environ.get(key.upper())
        if env_value:
            return env_value
        
        # Then check encrypted config
        try:
            config = self.decrypt_config()
            return config.get(key, default)
        except:
            return default
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration structure and required fields"""
        required_fields = {
            'mt5_accounts': ['login', 'password', 'server'],
            'matchtrade_accounts': ['username', 'password', 'broker_name']
        }
        
        try:
            # Check MT5 accounts
            if 'mt5_accounts' not in config or not config['mt5_accounts']:
                logger.error("No MT5 accounts configured")
                return False
                
            for account in config['mt5_accounts']:
                for field in required_fields['mt5_accounts']:
                    if field not in account:
                        logger.error(f"Missing required field '{field}' in MT5 account")
                        return False
            
            # Check MatchTrader accounts
            if 'matchtrade_accounts' not in config or not config['matchtrade_accounts']:
                logger.error("No MatchTrader accounts configured")
                return False
                
            for account in config['matchtrade_accounts']:
                for field in required_fields['matchtrade_accounts']:
                    if field not in account:
                        logger.error(f"Missing required field '{field}' in MatchTrader account")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False
    
    def create_secure_config_template(self) -> Dict[str, Any]:
        """Create a template for secure configuration"""
        return {
            "mt5_accounts": [
                {
                    "account_id": "my_mt5_account",
                    "login": 12345678,
                    "password": "your_mt5_password",
                    "server": "Your-Broker-Server"
                }
            ],
            "matchtrade_accounts": [
                {
                    "account_id": "my_prop_firm_account",
                    "username": "your_email@example.com",
                    "password": "your_password",
                    "broker_name": "e8markets",
                    "account_number": "optional_account_number"
                }
            ],
            "security_settings": {
                "enable_ssl_verification": True,
                "api_timeout": 30,
                "max_retries": 3,
                "rate_limit_delay": 1.0
            },
            "operational_settings": {
                "lot_multiplier": 1.0,
                "max_lot_size": 10.0,
                "min_lot_size": 0.01,
                "allowed_symbols": ["EURUSD", "GBPUSD", "XAUUSD", "US30"],
                "enable_notifications": True
            }
        }
