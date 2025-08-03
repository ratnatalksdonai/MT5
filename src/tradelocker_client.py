import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List

class TradeLockerClient:
    """Specialized client for TradeLocker platform (used by City Traders Imperium)"""
    
    def __init__(self, username: str, password: str, account_number: str = None):
        self.username = username
        self.password = password
        self.account_number = account_number
        self.base_url = "https://live.tradelocker.com"
        self.token = None
        self.token_expiry = None
        self.account_id = None
        
    async def authenticate(self, session: aiohttp.ClientSession) -> bool:
        """Authenticate with TradeLocker platform"""
        try:
            # TradeLocker authentication endpoint
            url = f"{self.base_url}/backend-api/auth/jwt/token"
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'MT5-MatchTrader-MVP/1.0',
                'Accept': 'application/json',
                'Origin': 'https://live.tradelocker.com',
                'Referer': 'https://live.tradelocker.com/'
            }
            
            logging.info(f"Attempting TradeLocker authentication for: {self.username}")
            
            # Try different TradeLocker server configurations for CTI
            server_configs = [
                "citytradersimperium",
                "cti", 
                "city-traders-imperium",
                "live",
                "demo",
                "real"
            ]
            
            for server in server_configs:
                data = {
                    "email": self.username,
                    "password": self.password,
                    "server": server
                }
                
                logging.info(f"Trying server config: {server}")
                
                response = await session.post(url, json=data, headers=headers)
                
                logging.info(f"TradeLocker response status for {server}: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    logging.info(f"TradeLocker response: {result}")
                    
                    if "accessToken" in result:
                        self.token = result["accessToken"]
                        # Set expiry time (usually 1 hour for TradeLocker)
                        expires_in = result.get("expiresIn", 3600)
                        self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                        
                        # Get account info to find the correct account ID
                        if await self.get_account_info(session):
                            logging.info(f"TradeLocker authentication successful with server: {server}")
                            return True
                else:
                    error_body = await response.text()
                    logging.info(f"Server {server} failed: {error_body}")
            
            logging.error("All server configurations failed")
            return False
                
        except Exception as e:
            logging.error(f"TradeLocker authentication error: {e}")
            return False
    
    async def get_account_info(self, session: aiohttp.ClientSession) -> bool:
        """Get account information and find the correct account ID"""
        if not self.token:
            return False
            
        try:
            url = f"{self.base_url}/backend-api/trade/accounts"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = await session.get(url, headers=headers)
            
            if response.status == 200:
                accounts = await response.json()
                logging.info(f"Available accounts: {accounts}")
                
                # Find account matching our account number
                if self.account_number:
                    for account in accounts.get("accounts", []):
                        if str(account.get("accountNum")) == str(self.account_number):
                            self.account_id = account.get("accNum")
                            logging.info(f"Found matching account ID: {self.account_id}")
                            return True
                else:
                    # Use first available account if no specific account number
                    if accounts.get("accounts"):
                        account = accounts["accounts"][0]
                        self.account_id = account.get("accNum")
                        logging.info(f"Using first available account: {self.account_id}")
                        return True
                        
                logging.error(f"Account {self.account_number} not found in available accounts")
                return False
                
        except Exception as e:
            logging.error(f"Error getting account info: {e}")
            return False
    
    async def place_order(self, session: aiohttp.ClientSession, order_details: Dict) -> Optional[Dict]:
        """Place an order on TradeLocker"""
        if not self.token or not self.account_id:
            logging.error("Not authenticated or no account ID")
            return None
            
        try:
            url = f"{self.base_url}/backend-api/trade/orders"
            
            # Convert our order format to TradeLocker format
            tl_order = {
                "accNum": self.account_id,
                "tradeSide": 1 if order_details["type"].upper() == "BUY" else 2,
                "qty": order_details["volume"],
                "instrId": await self.get_instrument_id(session, order_details["symbol"]),
                "orderType": 1,  # Market order
                "timeInForce": 1  # GTC
            }
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = await session.post(url, json=tl_order, headers=headers)
            
            if response.status == 200:
                result = await response.json()
                logging.info(f"Order placed successfully: {result}")
                return result
            else:
                error_body = await response.text()
                logging.error(f"Order placement failed: {response.status}")
                logging.error(f"Error: {error_body}")
                return None
                
        except Exception as e:
            logging.error(f"Error placing order: {e}")
            return None
    
    async def get_instrument_id(self, session: aiohttp.ClientSession, symbol: str) -> int:
        """Get TradeLocker instrument ID for a symbol"""
        try:
            url = f"{self.base_url}/backend-api/trade/instruments"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = await session.get(url, headers=headers)
            
            if response.status == 200:
                instruments = await response.json()
                
                for instrument in instruments.get("instruments", []):
                    if instrument.get("tradableInstrumentName") == symbol:
                        return instrument.get("tradableInstrumentId")
                        
                # If exact match not found, try common symbol mappings
                symbol_mappings = {
                    "EURUSD": "EUR/USD",
                    "GBPUSD": "GBP/USD", 
                    "XAUUSD": "XAU/USD",
                    "US30": "US30"
                }
                
                mapped_symbol = symbol_mappings.get(symbol, symbol)
                for instrument in instruments.get("instruments", []):
                    if instrument.get("tradableInstrumentName") == mapped_symbol:
                        return instrument.get("tradableInstrumentId")
                        
        except Exception as e:
            logging.error(f"Error getting instrument ID: {e}")
            
        return 1  # Default to instrument ID 1 if not found
    
    async def get_positions(self, session: aiohttp.ClientSession) -> List[Dict]:
        """Get open positions"""
        if not self.token or not self.account_id:
            return []
            
        try:
            url = f"{self.base_url}/backend-api/trade/positions"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = await session.get(url, headers=headers)
            
            if response.status == 200:
                result = await response.json()
                return result.get("positions", [])
                
        except Exception as e:
            logging.error(f"Error getting positions: {e}")
            
        return []
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.token is not None and self.account_id is not None
    
    def needs_refresh(self) -> bool:
        """Check if token needs refresh"""
        if not self.token_expiry:
            return False
        return datetime.now() >= self.token_expiry
