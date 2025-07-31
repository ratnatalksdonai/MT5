#!/usr/bin/env python3
"""Test connections to MT5 and MatchTrader accounts"""

import asyncio
import json
from src.trade_copier_mvp import TradeCopierMVP

async def test_connections():
    print("🧪 Testing MT5 and MatchTrader connections...")
    
    copier = TradeCopierMVP("config_mvp.json")
    
    # Test MT5 connection
    mt5_success = await copier.test_mt5_connection()
    print(f"MT5 Connection: {'✅ Success' if mt5_success else '❌ Failed'}")
    
    # Test MatchTrader connections
    mt_results = await copier.test_matchtrade_connections()
    for account_id, success in mt_results.items():
        print(f"MatchTrader {account_id}: {'✅ Success' if success else '❌ Failed'}")

if __name__ == "__main__":
    asyncio.run(test_connections())
