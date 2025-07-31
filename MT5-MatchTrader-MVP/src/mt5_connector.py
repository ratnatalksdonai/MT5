import MetaTrader5 as mt5
import logging
from datetime import datetime
import asyncio
from typing import Dict, List, Optional

class MT5Connector:
    """Handles connection and operations with MetaTrader 5"""
    
    def __init__(self, config: Dict):
        self.login = config.get('login')
        self.password = config.get('password')
        self.server = config.get('server')
        self.max_retries = 3
        self.connected = False
        
    def initialize(self) -> bool:
        """Initialize MT5 terminal"""
        try:
            return mt5.initialize()
        except Exception as e:
            logging.error(f"Failed to initialize MT5: {e}")
            return False
    
    def connect(self) -> bool:
        """Connect to MT5 account"""
        if not self.initialize():
            return False
            
        try:
            return mt5.login(self.login, self.password, self.server)
        except Exception as e:
            logging.error(f"Failed to connect to MT5: {e}")
            return False
    
    async def connect_with_retry(self) -> bool:
        """Connect with retry logic"""
        for attempt in range(self.max_retries):
            if self.connect():
                self.connected = True
                return True
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        return False
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        info = mt5.account_info()
        if info:
            return {
                'balance': info.balance,
                'equity': info.equity,
                'margin': info.margin,
                'free_margin': info.margin_free,
                'leverage': info.leverage
            }
        return {}
    
    def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        positions = mt5.positions_get()
        if positions is None:
            return []
            
        return [{
            'ticket': pos.ticket,
            'symbol': pos.symbol,
            'volume': pos.volume,
            'type': self.get_position_type(pos.type),
            'price': pos.price_open,
            'sl': pos.sl,
            'tp': pos.tp,
            'profit': pos.profit,
            'comment': pos.comment
        } for pos in positions]
    
    def get_position_type(self, position_type: int) -> str:
        """Convert MT5 position type to string"""
        return 'BUY' if position_type == 0 else 'SELL'
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information"""
        info = mt5.symbol_info(symbol)
        if info:
            return {
                'bid': info.bid,
                'ask': info.ask,
                'digits': info.digits,
                'spread': info.spread,
                'volume_min': info.volume_min,
                'volume_max': info.volume_max,
                'volume_step': info.volume_step
            }
        return None
    
    def get_position_history(self, from_date: datetime, to_date: datetime) -> List[Dict]:
        """Get position history within date range"""
        positions = mt5.history_positions_get(from_date, to_date)
        if positions is None:
            return []
            
        return [{
            'ticket': pos.ticket,
            'symbol': pos.symbol,
            'volume': pos.volume,
            'profit': pos.profit,
            'time_open': datetime.fromtimestamp(pos.time),
            'time_close': datetime.fromtimestamp(pos.time_msc // 1000)
        } for pos in positions]
    
    def shutdown(self):
        """Shutdown MT5 connection"""
        mt5.shutdown()
        self.connected = False
