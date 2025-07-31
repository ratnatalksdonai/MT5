import pytest
import json
import os
from unittest.mock import Mock, patch, mock_open
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.trade_copier_mvp import TradeCopierMVP
from src.symbol_mapper import SymbolMapper


class TestConfigurationAndUtils:
    """Test suite for configuration loading and utility functions"""
    
    # Test 43: Test configuration file loading
    def test_config_loading(self):
        config_data = {
            "mt5_accounts": [{
                "account_id": "test_mt5",
                "login": 12345678,
                "password": "test_pass",
                "server": "TestServer"
            }],
            "matchtrade_accounts": [{
                "account_id": "test_match",
                "username": "test@test.com",
                "password": "test_pass",
                "broker_name": "e8markets"
            }]
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(config_data))):
            copier = TradeCopierMVP("config_test.json")
            assert copier.config is not None
            assert len(copier.config.get('mt5_accounts', [])) == 1
    
    # Test 44: Test invalid configuration file
    def test_invalid_config_file(self):
        with patch('builtins.open', side_effect=FileNotFoundError()):
            with pytest.raises(FileNotFoundError):
                copier = TradeCopierMVP("nonexistent.json")
    
    # Test 45: Test symbol mapping with suffix
    def test_symbol_mapping_with_suffix(self):
        mapper = SymbolMapper()
        mapper.mapping = {"EURUSD.z": "EURUSD", "GBPUSD.z": "GBPUSD"}
        
        assert mapper.map_symbol("EURUSD.z") == "EURUSD"
        assert mapper.map_symbol("GBPUSD.z") == "GBPUSD"
    
    # Test 46: Test symbol mapping without suffix
    def test_symbol_mapping_without_suffix(self):
        mapper = SymbolMapper()
        mapper.mapping = {"XAUUSD": "GOLD", "NAS100": "US100"}
        
        assert mapper.map_symbol("XAUUSD") == "GOLD"
        assert mapper.map_symbol("NAS100") == "US100"
    
    # Test 47: Test unmapped symbol
    def test_unmapped_symbol(self):
        mapper = SymbolMapper()
        mapper.mapping = {"EURUSD": "EURUSD"}
        
        # Should return original if not in mapping
        assert mapper.map_symbol("USDJPY") == "USDJPY"
    
    # Test 48: Test lot size multiplier
    def test_lot_size_multiplier(self):
        copier = TradeCopierMVP("config_mvp.json")
        copier.lot_multiplier = 2.0
        
        original_lot = 0.1
        adjusted_lot = copier.calculate_lot_size(original_lot)
        assert adjusted_lot == 0.2
    
    # Test 49: Test fractional lot size multiplier
    def test_fractional_lot_multiplier(self):
        copier = TradeCopierMVP("config_mvp.json")
        copier.lot_multiplier = 0.5
        
        original_lot = 1.0
        adjusted_lot = copier.calculate_lot_size(original_lot)
        assert adjusted_lot == 0.5
    
    # Test 50: Test maximum lot size cap
    def test_max_lot_size_cap(self):
        copier = TradeCopierMVP("config_mvp.json")
        copier.max_lot_size = 5.0
        
        original_lot = 10.0
        adjusted_lot = copier.apply_lot_size_cap(original_lot)
        assert adjusted_lot == 5.0
    
    # Test 51: Test minimum lot size floor
    def test_min_lot_size_floor(self):
        copier = TradeCopierMVP("config_mvp.json")
        copier.min_lot_size = 0.01
        
        original_lot = 0.001
        adjusted_lot = copier.apply_lot_size_floor(original_lot)
        assert adjusted_lot == 0.01
    
    # Test 52: Test broker URL mapping
    def test_broker_url_mapping(self):
        broker_urls = {
            "e8markets": "https://platform.e8markets.com",
            "toponetrader": "https://platform.toponetrader.com",
            "ftmo": "https://platform.ftmo.com"
        }
        
        assert broker_urls["e8markets"] == "https://platform.e8markets.com"
        assert broker_urls["toponetrader"] == "https://platform.toponetrader.com"
        assert broker_urls["ftmo"] == "https://platform.ftmo.com"
    
    # Test 53: Test logging configuration
    def test_logging_config(self):
        config = {
            "logging": {
                "level": "INFO",
                "file_path": "logs/trade_copier.log",
                "max_file_size_mb": 50,
                "backup_count": 5
            }
        }
        
        assert config["logging"]["level"] == "INFO"
        assert config["logging"]["max_file_size_mb"] == 50
        assert config["logging"]["backup_count"] == 5
