import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import aiohttp
import json
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.matchtrade_client import MatchTraderClient


class TestMatchTraderClient:
    """Test suite for MatchTrader client functionality"""
    
    @pytest.fixture
    def client(self):
        """Create MatchTrader client instance for testing"""
        return MatchTraderClient(
            base_url="https://platform.e8markets.com",
            username="test@example.com",
            password="test_password",
            account_number="E8-123456"
        )
    
    # Test 16: Test successful authentication
    @pytest.mark.asyncio
    async def test_authentication_success(self, client):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'access_token': 'test_token_123',
            'expires_in': 3600
        })
        mock_response.__aenter__.return_value = mock_response
        
        mock_post = AsyncMock(return_value=mock_response)
        
        with patch('aiohttp.ClientSession.post', mock_post):
            async with aiohttp.ClientSession() as session:
                result = await client.authenticate(session)
                assert result == True
                assert client.token == 'test_token_123'
    
    # Test 17: Test authentication failure
    @pytest.mark.asyncio
    async def test_authentication_failure(self, client):
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.json = AsyncMock(return_value={'error': 'Invalid credentials'})
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            async with aiohttp.ClientSession() as session:
                result = await client.authenticate(session)
                assert result == False
                assert client.token is None
    
    # Test 18: Test token refresh
    @pytest.mark.asyncio
    async def test_token_refresh(self, client):
        client.token = 'old_token'
        client.token_expiry = datetime.now() - timedelta(minutes=1)  # Expired
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'access_token': 'new_token_456',
            'expires_in': 3600
        })
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            async with aiohttp.ClientSession() as session:
                result = await client.refresh_token(session)
                assert result == True
                assert client.token == 'new_token_456'
    
    # Test 19: Test place buy order
    @pytest.mark.asyncio
    async def test_place_buy_order(self, client):
        client.token = 'valid_token'
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'order_id': '12345',
            'status': 'filled',
            'symbol': 'EURUSD',
            'side': 'buy',
            'volume': 0.1
        })
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            async with aiohttp.ClientSession() as session:
                result = await client.place_order(session, {
                    'symbol': 'EURUSD',
                    'side': 'buy',
                    'volume': 0.1,
                    'type': 'market'
                })
                assert result['order_id'] == '12345'
                assert result['status'] == 'filled'
    
    # Test 20: Test place sell order
    @pytest.mark.asyncio
    async def test_place_sell_order(self, client):
        client.token = 'valid_token'
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'order_id': '67890',
            'status': 'filled',
            'symbol': 'GBPUSD',
            'side': 'sell',
            'volume': 0.2
        })
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            async with aiohttp.ClientSession() as session:
                result = await client.place_order(session, {
                    'symbol': 'GBPUSD',
                    'side': 'sell',
                    'volume': 0.2,
                    'type': 'market'
                })
                assert result['order_id'] == '67890'
                assert result['side'] == 'sell'
    
    # Test 21: Test order placement with invalid token
    @pytest.mark.asyncio
    async def test_place_order_invalid_token(self, client):
        client.token = 'invalid_token'
        
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.json = AsyncMock(return_value={'error': 'Unauthorized'})
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            async with aiohttp.ClientSession() as session:
                result = await client.place_order(session, {
                    'symbol': 'EURUSD',
                    'side': 'buy',
                    'volume': 0.1
                })
                assert result is None
    
    # Test 22: Test get account info
    @pytest.mark.asyncio
    async def test_get_account_info(self, client):
        client.token = 'valid_token'
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'account_number': 'E8-123456',
            'balance': 10000.0,
            'equity': 10500.0,
            'margin': 1000.0
        })
        
        with patch('aiohttp.ClientSession.get', return_value=mock_response):
            async with aiohttp.ClientSession() as session:
                info = await client.get_account_info(session)
                assert info['account_number'] == 'E8-123456'
                assert info['balance'] == 10000.0
    
    # Test 23: Test get positions
    @pytest.mark.asyncio
    async def test_get_positions(self, client):
        client.token = 'valid_token'
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'positions': [
                {
                    'id': '123',
                    'symbol': 'EURUSD',
                    'side': 'buy',
                    'volume': 0.1,
                    'profit': 50.0
                }
            ]
        })
        
        with patch('aiohttp.ClientSession.get', return_value=mock_response):
            async with aiohttp.ClientSession() as session:
                positions = await client.get_positions(session)
                assert len(positions) == 1
                assert positions[0]['symbol'] == 'EURUSD'
    
    # Test 24: Test close position
    @pytest.mark.asyncio
    async def test_close_position(self, client):
        client.token = 'valid_token'
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'order_id': '99999',
            'status': 'closed',
            'position_id': '123'
        })
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            async with aiohttp.ClientSession() as session:
                result = await client.close_position(session, '123')
                assert result['status'] == 'closed'
                assert result['position_id'] == '123'
    
    # Test 25: Test connection timeout handling
    @pytest.mark.asyncio
    async def test_connection_timeout(self, client):
        with patch('aiohttp.ClientSession.post', side_effect=asyncio.TimeoutError()):
            async with aiohttp.ClientSession() as session:
                result = await client.authenticate(session)
                assert result == False
    
    # Test 26: Test network error handling
    @pytest.mark.asyncio
    async def test_network_error(self, client):
        with patch('aiohttp.ClientSession.post', side_effect=aiohttp.ClientError()):
            async with aiohttp.ClientSession() as session:
                result = await client.authenticate(session)
                assert result == False
    
    # Test 27: Test rate limit handling
    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, client):
        mock_response = AsyncMock()
        mock_response.status = 429
        mock_response.headers = {'Retry-After': '60'}
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            async with aiohttp.ClientSession() as session:
                result = await client.place_order(session, {
                    'symbol': 'EURUSD',
                    'side': 'buy',
                    'volume': 0.1
                })
                assert result is None
    
    # Test 28: Test different broker endpoints
    def test_broker_endpoints(self):
        e8_client = MatchTraderClient(
            base_url="https://platform.e8markets.com",
            username="test@example.com",
            password="test_password",
            account_number="E8-123456"
        )
        assert e8_client.base_url == "https://platform.e8markets.com"
        
        topone_client = MatchTraderClient(
            base_url="https://platform.toponetrader.com",
            username="test@example.com",
            password="test_password",
            account_number="TOP-123456"
        )
        assert topone_client.base_url == "https://platform.toponetrader.com"
    
    # Test 29: Test session persistence
    @pytest.mark.asyncio
    async def test_session_persistence(self, client):
        client.token = 'valid_token'
        client.token_expiry = datetime.now() + timedelta(hours=1)
        
        assert client.is_authenticated() == True
        assert client.needs_refresh() == False
    
    # Test 30: Test token expiry check
    def test_token_expiry_check(self, client):
        client.token = 'valid_token'
        client.token_expiry = datetime.now() - timedelta(minutes=1)
        
        assert client.is_authenticated() == True
        assert client.needs_refresh() == True
