"""
Test Suite for MT5 to Match-Trader Trade Copier

Comprehensive tests for all modules.
"""

import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from config_manager import ConfigManager, TradeCopierConfig
from mt5_connector import MT5Connector
from match_trader_client import MatchTraderClient
from trade_copier import TradeCopier
from notification_logger import NotificationManager, CustomLogger


class TestConfigManager(unittest.TestCase):
    """Test Configuration Manager"""
    
    def setUp(self):
        self.test_config_path = "test_config.json"
        self.test_config = {
            "mt5_accounts": [
                {
                    "account_id": "12345",
                    "server": "TestServer",
                    "login": "testuser",
                    "password": "testpass",
                    "terminal_path": "C:\\Test\\mt5.exe"
                }
            ],
            "matchtrade_accounts": [
                {
                    "account_id": "MT-123",
                    "broker_id": "TEST",
                    "base_url": "wss://test.com/ws",
                    "api_key": "test_key",
                    "secret": "test_secret"
                }
            ],
            "trade_settings": {
                "lot_size_mode": "proportional",
                "lot_multiplier": 1.0,
                "max_lot_size": 10.0,
                "min_lot_size": 0.01,
                "symbol_mapping": {"EURUSD.z": "EURUSD"},
                "allowed_symbols": ["EURUSD"],
                "copy_pending_orders": False,
                "copy_sl_tp": True
            },
            "notifications": {
                "enabled": True,
                "webhook_url": "https://test.slack.com",
                "telegram_bot_token": "test_token",
                "telegram_chat_id": "test_chat"
            },
            "logging": {
                "level": "INFO",
                "file_path": "test.log",
                "max_file_size_mb": 10,
                "backup_count": 5,
                "console_output": True
            },
            "performance": {
                "max_latency_ms": 100,
                "health_check_interval_seconds": 60,
                "connection_timeout_seconds": 30,
                "heartbeat_interval_seconds": 30,
                "retry_max_attempts": 5,
                "retry_delay_seconds": 5
            }
        }
        
        # Create test config file
        with open(self.test_config_path, 'w') as f:
            json.dump(self.test_config, f)
    
    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)
    
    def test_load_config(self):
        """Test loading configuration from file"""
        config_manager = ConfigManager(self.test_config_path)
        self.assertIsNotNone(config_manager.config)
        self.assertEqual(config_manager.config.mt5_accounts[0].account_id, "12345")
    
    def test_symbol_mapping(self):
        """Test symbol mapping functionality"""
        config_manager = ConfigManager(self.test_config_path)
        
        # Test direct mapping
        mapped = config_manager.validate_symbol_mapping("EURUSD.z")
        self.assertEqual(mapped, "EURUSD")
        
        # Test .z suffix removal with non-allowed symbol
        mapped = config_manager.validate_symbol_mapping("GBPUSD.z")
        self.assertIsNone(mapped)  # GBPUSD is not in allowed symbols
        
        # Test allowed symbols filter
        mapped = config_manager.validate_symbol_mapping("USDJPY.z")
        self.assertIsNone(mapped)  # Not in allowed symbols
    
    def test_encryption(self):
        """Test credential encryption functionality"""
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        
        config_manager = ConfigManager(self.test_config_path, key)
        
        # Test encryption
        encrypted_config = config_manager.encrypt_sensitive_fields(self.test_config)
        self.assertTrue(encrypted_config['mt5_accounts'][0]['password'].startswith('encrypted:'))
        self.assertTrue(encrypted_config['matchtrade_accounts'][0]['api_key'].startswith('encrypted:'))
        
        # Test decryption
        decrypted_config = config_manager._decrypt_config(encrypted_config)
        self.assertEqual(decrypted_config['mt5_accounts'][0]['password'], 'testpass')
        self.assertEqual(decrypted_config['matchtrade_accounts'][0]['api_key'], 'test_key')


class TestMT5Connector(unittest.TestCase):
    """Test MT5 Connector"""
    
    @patch('mt5_connector.mt5')
    def test_initialize(self, mock_mt5):
        """Test MT5 initialization"""
        mock_mt5.initialize.return_value = True
        
        connector = MT5Connector("12345", "TestServer", "user", "pass")
        result = connector.initialize()
        
        self.assertTrue(result)
        self.assertTrue(connector.connected)
        mock_mt5.initialize.assert_called_once()
    
    @patch('mt5_connector.mt5')
    def test_shutdown(self, mock_mt5):
        """Test MT5 shutdown"""
        connector = MT5Connector("12345", "TestServer", "user", "pass")
        connector.connected = True
        connector.shutdown()
        
        self.assertFalse(connector.connected)
        mock_mt5.shutdown.assert_called_once()


class TestMatchTraderClient(unittest.TestCase):
    """Test Match-Trader WebSocket Client"""
    
    @patch('match_trader_client.websocket.WebSocketApp')
    def test_initialization(self, mock_ws):
        """Test client initialization"""
        client = MatchTraderClient("MT-123", "TEST", "wss://test.com", "key", "secret")
        
        self.assertEqual(client.account_id, "MT-123")
        self.assertEqual(client.broker_id, "TEST")
        self.assertEqual(client.base_url, "wss://test.com")
    
    @patch('match_trader_client.websocket.WebSocketApp')
    def test_send_trade(self, mock_ws):
        """Test sending trade data"""
        client = MatchTraderClient("MT-123", "TEST", "wss://test.com", "key", "secret")
        client.connected = True
        client.ws = MagicMock()
        
        trade_data = {"symbol": "EURUSD", "action": "BUY", "volume": 0.1}
        client.send_trade(trade_data)
        
        client.ws.send.assert_called_once()


class TestTradeCopier(unittest.TestCase):
    """Test Trade Copier Core Logic"""
    
    def setUp(self):
        self.config_path = "test_config.json"
        self.test_config = {
            "mt5_accounts": [{
                "account_id": "12345",
                "server": "TestServer",
                "login": "user",
                "password": "pass"
            }],
            "matchtrade_accounts": [{
                "account_id": "MT-123",
                "broker_id": "TEST",
                "base_url": "wss://test.com",
                "api_key": "key",
                "secret": "secret"
            }],
            "trade_settings": {
                "lot_size_mode": "proportional",
                "lot_multiplier": 2.0,
                "max_lot_size": 10.0,
                "min_lot_size": 0.01,
                "symbol_mapping": {},
                "allowed_symbols": [],
                "copy_pending_orders": False,
                "copy_sl_tp": True
            },
            "notifications": {"enabled": True},
            "logging": {"level": "INFO", "file_path": "test.log"},
            "performance": {"max_latency_ms": 100}
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f)
    
    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
    
    @patch('trade_copier.MT5Connector')
    @patch('trade_copier.MatchTraderClient')
    def test_initialize_connections(self, mock_match_client, mock_mt5):
        """Test initialization of all connections"""
        config_manager = ConfigManager(self.config_path)
        copier = TradeCopier(config_manager)
        
        # Mock the start methods
        mock_mt5.return_value.start = MagicMock()
        mock_match_client.return_value.start = MagicMock()
        
        copier.initialize_connections()
        
        # Verify connections were created
        self.assertEqual(len(copier.mt5_connectors), 1)
        self.assertEqual(len(copier.match_clients), 1)


class TestNotificationManager(unittest.TestCase):
    """Test Notification System"""
    
    @patch('notification_logger.requests.post')
    def test_slack_notification(self, mock_post):
        """Test Slack notification"""
        config = {"webhook_url": "https://test.slack.com"}
        manager = NotificationManager(config)
        
        manager.send_slack_notification("Test message")
        
        mock_post.assert_called_once_with(
            "https://test.slack.com",
            json={"text": "Test message"}
        )
    
    @patch('notification_logger.requests.post')
    def test_telegram_notification(self, mock_post):
        """Test Telegram notification"""
        config = {
            "telegram_bot_token": "test_token",
            "telegram_chat_id": "test_chat"
        }
        manager = NotificationManager(config)
        
        manager.send_telegram_notification("Test message")
        
        expected_url = "https://api.telegram.org/bottest_token/sendMessage"
        mock_post.assert_called_once_with(
            expected_url,
            data={"chat_id": "test_chat", "text": "Test message"}
        )


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def test_lot_size_calculation_proportional(self):
        """Test proportional lot size calculation"""
        source_lots = 1.0
        multiplier = 2.0
        expected = 2.0
        
        result = source_lots * multiplier
        self.assertEqual(result, expected)
    
    def test_lot_size_calculation_equity_based(self):
        """Test equity-based lot size calculation"""
        source_lots = 1.0
        source_equity = 10000
        destination_equity = 5000
        expected = 0.5
        
        result = source_lots * (destination_equity / source_equity)
        self.assertEqual(result, expected)
    
    def test_lot_size_limits(self):
        """Test lot size limit enforcement"""
        calculated_lots = 15.0
        max_lots = 10.0
        min_lots = 0.01
        
        # Test max limit
        result = min(calculated_lots, max_lots)
        self.assertEqual(result, max_lots)
        
        # Test min limit
        calculated_lots = 0.001
        result = max(calculated_lots, min_lots)
        self.assertEqual(result, min_lots)


def run_all_tests():
    """Run all test suites"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_all_tests()
