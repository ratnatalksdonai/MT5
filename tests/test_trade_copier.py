import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.trade_copier_mvp import TradeCopierMVP

class TestTradeCopierMVP:
    """Test suite for the main Trade Copier MVP functionality"""

    @pytest.fixture
    def copier(self):
        """Instantiate TradeCopierMVP for testing"""
        return TradeCopierMVP("config_mvp.json")

    # Test 31: Test start copying method
    @pytest.mark.asyncio
    async def test_start_copying(self, copier):
        with patch.object(copier, 'authenticate_all_accounts', new_callable=AsyncMock) as mock_auth, \
             patch.object(copier, 'monitor_mt5_positions', new_callable=AsyncMock) as mock_monitor:
            await copier.start_copying()
            mock_auth.assert_called_once()
            mock_monitor.assert_called_once()

    # Test 32: Test stop copying method
    @pytest.mark.asyncio
    async def test_stop_copying(self, copier):
        with patch('src.trade_copier_mvp.asyncio.sleep', new_callable=AsyncMock):
            await copier.stop_copying()

    # Test 33: Test authenticate all accounts method
    @pytest.mark.asyncio
    async def test_authenticate_all_accounts(self, copier):
        with patch('src.matchtrade_client.MatchTraderClient.authenticate', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = True
            import aiohttp
            async with aiohttp.ClientSession() as session:
                result = await copier.authenticate_all_accounts(session)
            assert result == True

    # Test 34: Test replicate trade logic
    @pytest.mark.asyncio
    async def test_replicate_trade(self, copier):
        trade_signal = {
            'symbol': 'EURUSD',
            'volume': 0.1,
            'type': 'buy'
        }
        with patch.object(copier.symbol_mapper, 'map_symbol', return_value='EURUSD'), \
             patch('src.matchtrade_client.MatchTraderClient.place_order', new_callable=AsyncMock) as mock_place_order:
            mock_place_order.return_value = {'status': 'success'}
            import aiohttp
            async with aiohttp.ClientSession() as session:
                result = await copier.replicate_trade(trade_signal, copier.match_trader_clients, session=session)
            assert result is not None

    # Test 35: Test handle connection errors method
    @pytest.mark.asyncio
    async def test_handle_connection_errors(self, copier):
        with patch('src.trade_copier_mvp.asyncio.sleep', new_callable=AsyncMock):
            await copier.handle_connection_errors()
