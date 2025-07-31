class SymbolMapper:
    """Handles symbol conversion between MT5 and MatchTrader"""

    def __init__(self):
        self.mapping = {
            "EURUSD.z": "EURUSD",
            "GBPUSD.z": "GBPUSD",
            "XAUUSD": "GOLD",
            "US30": "US30"
        }

    def map_symbol(self, mt5_symbol):
        """Map MT5 symbol to MatchTrader symbol"""
        return self.mapping.get(mt5_symbol, mt5_symbol)
