import os
import sys
sys.path.append('src')
from cryptography.fernet import Fernet
from config_manager import ConfigManager

# Load configuration
def secure_credentials(config_path: str, key_path: str):
    # Generate new encryption key
    key = Fernet.generate_key()
    with open(key_path, "wb") as key_file:
        key_file.write(key)

    # Initialize ConfigManager with encryption
    manager = ConfigManager(config_path, key)
    config_data = manager.load_config().dict()
    
    # Encrypt sensitive fields and save
    encrypted_config = manager.encrypt_sensitive_fields(config_data)
    manager.save_config(encrypted_config)
    print(f"Encryption key stored in: {key_path}")
    print(f"Configuration secured at: {config_path}")

if __name__ == "__main__":
    secure_credentials("config/config.json", "data/secret.key")
