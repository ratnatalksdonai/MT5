#!/usr/bin/env python3
"""
MT5 to MatchTrader MVP Runner
Usage: python run_mvp.py
"""

import asyncio
import signal
import sys
from src.trade_copier_mvp import TradeCopierMVP

async def main():
    copier = TradeCopierMVP("config_mvp.json")
    
    # Setup signal handlers
    def signal_handler(sig, frame):
        print("\n🛑 Stopping trade copier...")
        asyncio.create_task(copier.stop_copying())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the trade copier
    print("🚀 Starting MT5 to MatchTrader MVP...")
    await copier.start_copying()

if __name__ == "__main__":
    asyncio.run(main())
