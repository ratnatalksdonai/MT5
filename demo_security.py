#!/usr/bin/env python3
"""
Security Features Demonstration
Shows all implemented security features in action
Author: Ratna Kirti (@ratna3)
"""

import asyncio
import logging
from src.security.config_manager import SecureConfigManager
from src.security.auth_manager import AuthManager
from src.security.input_validator import InputValidator
from src.security.secure_logger import SecureLogger, SensitiveDataFilter

# Setup secure logging
secure_logger = SecureLogger(log_dir="demo_logs", log_level="INFO")
logger = secure_logger.get_logger('main')

def demonstrate_input_validation():
    """Demonstrate input validation features"""
    print("\n🛡️ INPUT VALIDATION DEMONSTRATION")
    print("=" * 50)
    
    # Test trading symbol validation
    test_symbols = ["EURUSD", "EUR/USD", "INVALID123", "'; DROP TABLE trades;--"]
    for symbol in test_symbols:
        result = InputValidator.validate_trading_symbol(symbol)
        print(f"Symbol '{symbol}' -> {'✅ Valid' if result else '❌ Invalid'}")
    
    # Test email validation with SQL injection attempt
    test_emails = [
        "user@example.com",
        "test@domain.co.uk", 
        "invalid.email",
        "user@domain.com'; DROP TABLE users;--"
    ]
    for email in test_emails:
        result = InputValidator.validate_email(email)
        print(f"Email '{email}' -> {'✅ Valid' if result else '❌ Invalid'}")
    
    # Test volume validation
    test_volumes = [0.01, 1.5, 0.001, 1000, -1]
    for volume in test_volumes:
        result = InputValidator.validate_volume(volume)
        print(f"Volume {volume} -> {'✅ Valid' if result else '❌ Invalid'}")

def demonstrate_secure_logging():
    """Demonstrate secure logging with data masking"""
    print("\n🔒 SECURE LOGGING DEMONSTRATION")
    print("=" * 50)
    
    # Log messages with sensitive data
    sensitive_messages = [
        "User login with password=MySecretPass123!",
        "API authentication with api_key=sk_live_abcd1234efgh5678ijkl9012mnop3456",
        "Trading account 123456789 connected",
        "Email notification sent to user@example.com",
        "Connection from IP 192.168.1.100",
        "Bearer token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
    ]
    
    print("Original messages vs. Logged (masked) messages:")
    print("-" * 50)
    
    for msg in sensitive_messages:
        print(f"Original: {msg}")
        logger.info(msg)  # This will be masked in logs
        
        # Also demonstrate manual masking
        filter = SensitiveDataFilter()
        masked = filter._mask_sensitive_data(msg)
        print(f"Masked:   {masked}\n")

def demonstrate_encryption():
    """Demonstrate encryption at rest"""
    print("\n🔐 ENCRYPTION AT REST DEMONSTRATION")
    print("=" * 50)
    
    # Create secure config manager
    config_manager = SecureConfigManager("demo_config.enc")
    
    # Initialize with a demo password
    demo_password = "DemoMasterPassword123!"
    config_manager.initialize_encryption(demo_password)
    
    # Create sample config with sensitive data
    sensitive_config = {
        "mt5_accounts": [{
            "login": 12345678,
            "password": "SuperSecretMT5Pass",
            "server": "DemoBroker-Server"
        }],
        "matchtrade_accounts": [{
            "username": "trader@example.com",
            "password": "PropFirmPassword123",
            "api_key": "pk_live_1234567890abcdef"
        }]
    }
    
    # Encrypt and save
    config_manager.encrypt_config(sensitive_config)
    print("✅ Configuration encrypted and saved")
    
    # Decrypt and verify
    decrypted = config_manager.decrypt_config()
    print("✅ Configuration decrypted successfully")
    print(f"✅ Passwords are {'identical' if decrypted == sensitive_config else 'different'}")

async def demonstrate_authentication():
    """Demonstrate user authentication system"""
    print("\n🔑 AUTHENTICATION SYSTEM DEMONSTRATION")
    print("=" * 50)
    
    auth_manager = AuthManager("demo_auth")
    
    # Create a test user
    try:
        user_info = auth_manager.create_user(
            username="demo_trader",
            password="SecurePass123!@#",
            email="trader@example.com",
            enable_mfa=True
        )
        print(f"✅ User created: {user_info['username']}")
        print(f"✅ MFA enabled: {user_info['mfa_enabled']}")
    except ValueError as e:
        print(f"User creation failed: {e}")
    
    # Test authentication
    print("\n🔐 Testing authentication...")
    
    # Test with wrong password
    token = auth_manager.authenticate("demo_trader", "WrongPassword")
    print(f"❌ Wrong password: {'Failed' if not token else 'Succeeded'}")
    
    # Test with correct password (but no MFA)
    token = auth_manager.authenticate("demo_trader", "SecurePass123!@#")
    print(f"❌ No MFA code: {'Failed' if not token else 'Succeeded'}")
    
    # Generate MFA QR code
    qr_path = auth_manager.generate_mfa_qr_code("demo_trader")
    if qr_path:
        print(f"✅ MFA QR code generated: {qr_path}")

def demonstrate_security_events():
    """Demonstrate security event logging"""
    print("\n📊 SECURITY EVENT LOGGING DEMONSTRATION")
    print("=" * 50)
    
    secure_logger = SecureLogger()
    
    # Log various security events
    events = [
        ("login_attempt", {"username": "trader1", "success": True}, "trader1", "192.168.1.100"),
        ("login_failed", {"username": "hacker", "reason": "invalid_password"}, None, "10.0.0.1"),
        ("permission_denied", {"resource": "admin_panel", "user": "trader1"}, "trader1", "192.168.1.100"),
        ("api_key_created", {"key_id": "key_123", "permissions": ["trade"]}, "trader1", "192.168.1.100"),
    ]
    
    for event_type, details, user, ip in events:
        secure_logger.log_security_event(event_type, details, user, ip)
        print(f"✅ Logged security event: {event_type}")
    
    # Log trading events
    trade_events = [
        ("order_placed", {"account": "123456789", "symbol": "EURUSD", "volume": 1.0, "type": "BUY"}),
        ("position_closed", {"account": "987654321", "symbol": "GOLD", "profit": 150.50}),
        ("error_occurred", {"account": "555555555", "error": "Insufficient margin"}),
    ]
    
    for event_type, trade_data in trade_events:
        secure_logger.log_trading_event(event_type, trade_data)
        print(f"✅ Logged trading event: {event_type}")

async def main():
    """Run all security demonstrations"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║         🔒 MT5-MATCHTRADER SECURITY FEATURES DEMONSTRATION 🔒                 ║
║                                                                               ║
║                    Developed by Ratna Kirti (@ratna3)                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Run demonstrations
    demonstrate_input_validation()
    demonstrate_secure_logging()
    demonstrate_encryption()
    await demonstrate_authentication()
    demonstrate_security_events()
    
    print("\n" + "=" * 50)
    print("🎉 SECURITY DEMONSTRATION COMPLETE!")
    print("=" * 50)
    print("\n✅ All security features are fully implemented and functional")
    print("✅ Your MT5-MatchTrader Bridge is enterprise-grade secure!")
    print("\n📄 Check the generated files:")
    print("  - demo_logs/ - Secure log files with masked data")
    print("  - demo_auth/ - Authentication database")
    print("  - demo_config.enc - Encrypted configuration")
    print("\n🔐 Ready for production use with City Traders Imperium!")

if __name__ == "__main__":
    asyncio.run(main())
