import re
from typing import Dict, Optional, Set

class SymbolMapper:
    """Handles symbol conversion between MT5 and MatchTrader platforms"""

    def __init__(self):
        self.mapping = {
            # Forex pairs with MT5 suffixes
            "EURUSD.z": "EURUSD",
            "GBPUSD.z": "GBPUSD", 
            "USDJPY.z": "USDJPY",
            "AUDUSD.z": "AUDUSD",
            "USDCAD.z": "USDCAD",
            "USDCHF.z": "USDCHF",
            "NZDUSD.z": "NZDUSD",
            "EURJPY.z": "EURJPY",
            "GBPJPY.z": "GBPJPY",
            "EURGBP.z": "EURGBP",
            
            # Metals
            "XAUUSD": "GOLD",
            "XAUUSD.z": "GOLD",
            "XAGUSD": "SILVER",
            "XAGUSD.z": "SILVER",
            
            # Indices
            "US30": "US30",
            "US500": "US500", 
            "USTEC": "NAS100",
            "GER40": "GER40",
            "UK100": "UK100",
            "JPN225": "JPN225",
            
            # Crypto (if supported)
            "BTCUSD": "BTCUSD",
            "ETHUSD": "ETHUSD"
        }
        
        # Common MT5 suffixes to remove
        self.suffix_pattern = re.compile(r'\.(z|a|b|c|m|e|f|pro|ecn|raw)$', re.IGNORECASE)
        
    def map_symbol(self, mt5_symbol: str) -> Optional[str]:
        """Map MT5 symbol to MatchTrader symbol"""
        if not mt5_symbol:
            return None
            
        # First check direct mapping
        if mt5_symbol in self.mapping:
            return self.mapping[mt5_symbol]
        
        # Try removing common suffixes
        clean_symbol = self.suffix_pattern.sub('', mt5_symbol)
        if clean_symbol in self.mapping:
            return self.mapping[clean_symbol]
            
        # Return cleaned symbol if no mapping found
        return clean_symbol
        
    def reverse_map_symbol(self, match_trader_symbol: str) -> Optional[str]:
        """Map MatchTrader symbol back to MT5 symbol"""
        for mt5_sym, mt_sym in self.mapping.items():
            if mt_sym == match_trader_symbol:
                return mt5_sym
        return match_trader_symbol
        
    def add_mapping(self, mt5_symbol: str, match_trader_symbol: str):
        """Add custom symbol mapping"""
        self.mapping[mt5_symbol] = match_trader_symbol
        
    def get_supported_symbols(self) -> Set[str]:
        """Get all supported symbols"""
        return set(self.mapping.values())
