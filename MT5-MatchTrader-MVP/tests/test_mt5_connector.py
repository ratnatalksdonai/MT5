import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import MetaTrader5 as mt5
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mt5_connector import MT5Connector


class TestMT5Connector:
    """Test suite for MT5 connector functionality"""
    
    @pytest.fixture
    def mt5_connector(self):
        """Create MT5 connector instance for testing"""
        return MT5Connector({
            'login': 12345678,
            'password': 'test_password',
            'server': 'TestBroker-Server'
        })
    
    # Test 1: Test successful MT5 initialization
    @patch('MetaTrader5.initialize')
    def test_mt5_initialize_success(self, mock_initialize, mt5_connector):
        mock_initialize.return_value = True
        result = mt5_connector.initialize()
        assert result == True
        mock_initialize.assert_called_once()
    
    # Test 2: Test failed MT5 initialization
    @patch('MetaTrader5.initialize')
    def test_mt5_initialize_failure(self, mock_initialize, mt5_connector):
        mock_initialize.return_value = False
        result = mt5_connector.initialize()
        assert result == False
    
    # Test 3: Test successful login
    @patch('MetaTrader5.login')
    @patch('MetaTrader5.initialize')
    def test_mt5_login_success(self, mock_initialize, mock_login, mt5_connector):
        mock_initialize.return_value = True
        mock_login.return_value = True
        result = mt5_connector.connect()
        assert result == True
        mock_login.assert_called_with(12345678, 'test_password', 'TestBroker-Server')
    
    # Test 4: Test failed login
    @patch('MetaTrader5.login')
    @patch('MetaTrader5.initialize')
    def test_mt5_login_failure(self, mock_initialize, mock_login, mt5_connector):
        mock_initialize.return_value = True
        mock_login.return_value = False
        result = mt5_connector.connect()
        assert result == False
    
    # Test 5: Test getting account info
    @patch('MetaTrader5.account_info')
    def test_get_account_info(self, mock_account_info, mt5_connector):
        mock_info = Mock()
        mock_info.balance = 10000.0
        mock_info.equity = 10500.0
        mock_info.margin = 1000.0
        mock_account_info.return_value = mock_info
        
        info = mt5_connector.get_account_info()
        assert info['balance'] == 10000.0
        assert info['equity'] == 10500.0
        assert info['margin'] == 1000.0
    
    # Test 6: Test getting positions
    @patch('MetaTrader5.positions_get')
    def test_get_positions_empty(self, mock_positions, mt5_connector):
        mock_positions.return_value = []
        positions = mt5_connector.get_positions()
        assert positions == []
    
    # Test 7: Test getting positions with data
    @patch('MetaTrader5.positions_get')
    def test_get_positions_with_data(self, mock_positions, mt5_connector):
        mock_position = Mock()
        mock_position.ticket = 123456
        mock_position.symbol = 'EURUSD'
        mock_position.volume = 0.1
        mock_position.type = 0  # Buy
        mock_positions.return_value = [mock_position]
        
        positions = mt5_connector.get_positions()
        assert len(positions) == 1
        assert positions[0]['ticket'] == 123456
        assert positions[0]['symbol'] == 'EURUSD'
    
    # Test 8: Test position type conversion (buy)
    def test_position_type_buy(self, mt5_connector):
        assert mt5_connector.get_position_type(0) == 'BUY'
    
    # Test 9: Test position type conversion (sell)
    def test_position_type_sell(self, mt5_connector):
        assert mt5_connector.get_position_type(1) == 'SELL'
    
    # Test 10: Test shutdown
    @patch('MetaTrader5.shutdown')
    def test_shutdown(self, mock_shutdown, mt5_connector):
        mt5_connector.shutdown()
        mock_shutdown.assert_called_once()
    
    # Test 11: Test connection retry on failure
    @patch('MetaTrader5.login')
    @patch('MetaTrader5.initialize')
    def test_connection_retry(self, mock_initialize, mock_login, mt5_connector):
        mock_initialize.return_value = True
        mock_login.side_effect = [False, False, True]  # Fail twice, then succeed
        
        mt5_connector.max_retries = 3
        result = mt5_connector.connect_with_retry()
        assert result == True
        assert mock_login.call_count == 3
    
    # Test 12: Test max retries exceeded
    @patch('MetaTrader5.login')
    @patch('MetaTrader5.initialize')
    def test_max_retries_exceeded(self, mock_initialize, mock_login, mt5_connector):
        mock_initialize.return_value = True
        mock_login.return_value = False
        
        mt5_connector.max_retries = 3
        result = mt5_connector.connect_with_retry()
        assert result == False
        assert mock_login.call_count == 3
    
    # Test 13: Test symbol info retrieval
    @patch('MetaTrader5.symbol_info')
    def test_get_symbol_info(self, mock_symbol_info, mt5_connector):
        mock_info = Mock()
        mock_info.bid = 1.12345
        mock_info.ask = 1.12355
        mock_info.digits = 5
        mock_symbol_info.return_value = mock_info
        
        info = mt5_connector.get_symbol_info('EURUSD')
        assert info['bid'] == 1.12345
        assert info['ask'] == 1.12355
        assert info['digits'] == 5
    
    # Test 14: Test invalid symbol info
    @patch('MetaTrader5.symbol_info')
    def test_get_invalid_symbol_info(self, mock_symbol_info, mt5_connector):
        mock_symbol_info.return_value = None
        info = mt5_connector.get_symbol_info('INVALID')
        assert info is None
    
    # Test 15: Test position history
    @patch('MetaTrader5.history_positions_get')
    def test_get_position_history(self, mock_history, mt5_connector):
        mock_position = Mock()
        mock_position.ticket = 789012
        mock_position.profit = 50.0
        mock_history.return_value = [mock_position]
        
        history = mt5_connector.get_position_history(datetime.now(), datetime.now())
        assert len(history) == 1
        assert history[0]['ticket'] == 789012
        assert history[0]['profit'] == 50.0
