import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List

class MatchTraderClient:
    def __init__(self, base_url: str, username: str, password: str, account_number: str = None):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.account_number = account_number
        self.token = None
        self.token_expiry = None
        
    async def authenticate(self, session: aiohttp.ClientSession) -> bool:
        """Authenticate with the MatchTrader platform"""
        try:
            url = f"{self.base_url}/api/auth/login"
            data = {"username": self.username, "password": self.password}
            if self.account_number:
                data["account_number"] = self.account_number
                
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.token = result.get("access_token") or result.get("token")
                    expires_in = result.get("expires_in", 3600)
                    self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                    logging.info(f"Authenticated with {self.base_url} successfully")
                    return True
                else:
                    logging.error(f"Authentication failed: {response.status}")
                    return False
        except asyncio.TimeoutError:
            logging.error("Authentication timeout")
            return False
        except aiohttp.ClientError as e:
            logging.error(f"Network error during authentication: {e}")
            return False
            
    async def login(self, session):
        """Legacy login method for compatibility"""
        return await self.authenticate(session)
    
    async def refresh_token(self, session: aiohttp.ClientSession) -> bool:
        """Refresh the authentication token"""
        return await self.authenticate(session)
    
    async def place_order(self, session: aiohttp.ClientSession, order_details: Dict) -> Optional[Dict]:
        """Place an order on the MatchTrader platform"""
        if not self.token:
            return None
            
        url = f"{self.base_url}/api/orders"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            async with session.post(url, json=order_details, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    logging.error("Unauthorized - token may be invalid")
                    return None
                elif response.status == 429:
                    logging.error("Rate limit exceeded")
                    return None
                else:
                    return None
        except Exception as e:
            logging.error(f"Error placing order: {e}")
            return None
    
    async def get_account_info(self, session: aiohttp.ClientSession) -> Optional[Dict]:
        """Get account information"""
        if not self.token:
            return None
            
        url = f"{self.base_url}/api/account/info"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logging.error(f"Error getting account info: {e}")
            return None
    
    async def get_positions(self, session: aiohttp.ClientSession) -> List[Dict]:
        """Get open positions"""
        if not self.token:
            return []
            
        url = f"{self.base_url}/api/positions"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('positions', [])
                return []
        except Exception as e:
            logging.error(f"Error getting positions: {e}")
            return []
    
    async def close_position(self, session: aiohttp.ClientSession, position_id: str) -> Optional[Dict]:
        """Close a specific position"""
        if not self.token:
            return None
            
        url = f"{self.base_url}/api/positions/{position_id}/close"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            async with session.post(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logging.error(f"Error closing position: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.token is not None
    
    def needs_refresh(self) -> bool:
        """Check if token needs refresh"""
        if not self.token_expiry:
            return False
        return datetime.now() >= self.token_expiry
