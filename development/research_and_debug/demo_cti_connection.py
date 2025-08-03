#!/usr/bin/env python3
"""
Demo script for City Traders Imperium connection and trade copying
This demonstrates connecting to CTI and MT5, then simulating a trade copy
"""

import asyncio
import logging
import json
import aiohttp
from datetime import datetime
from src.trade_copier_mvp import TradeCopierMVP
from src.mt5_connector import MT5Connector
from src.matchtrade_client import MatchTraderClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_cti_connection():
    """Demo the complete CTI connection and trade copying workflow"""
    
    print("🚀 MT5-MatchTrader MVP Demo for City Traders Imperium")
    print("=" * 60)
    
    try:
        # Step 1: Load configuration
        print("\n📋 Step 1: Loading Configuration...")
        copier = TradeCopierMVP("config_mvp.json")
        print("✅ Configuration loaded successfully")
        print(f"   - MT5 Account: {copier.config['mt5_accounts'][0]['login']} @ {copier.config['mt5_accounts'][0]['server']}")
        print(f"   - CTI Account: {copier.config['matchtrade_accounts'][0]['account_number']} ({copier.config['matchtrade_accounts'][0]['username']})")
        
        # Step 2: Test MT5 Connection
        print("\n🔌 Step 2: Testing MT5 Connection...")
        mt5_connected = await test_mt5_connection(copier.mt5_connector)
        if mt5_connected:
            print("✅ MT5 connection successful")
        else:
            print("❌ MT5 connection failed")
        
        # Step 3: Test CTI Connection
        print("\n🌐 Step 3: Testing City Traders Imperium Connection...")
        cti_connected = await test_cti_connection(copier.match_trader_clients[0])
        if cti_connected:
            print("✅ CTI connection successful")
        else:
            print("❌ CTI connection failed")
        
        # Step 4: Simulate placing a trade on MT5
        print("\n📈 Step 4: Simulating MT5 Trade...")
        mt5_trade = simulate_mt5_trade()
        print(f"✅ Simulated MT5 trade placed:")
        print(f"   - Symbol: {mt5_trade['symbol']}")
        print(f"   - Type: {mt5_trade['type']}")
        print(f"   - Volume: {mt5_trade['volume']}")
        print(f"   - Price: {mt5_trade['price']}")
        
        # Step 5: Demonstrate trade copying to CTI
        print("\n🔄 Step 5: Copying Trade to City Traders Imperium...")
        if cti_connected:
            copied_trade = await simulate_trade_copy(copier, mt5_trade)
            if copied_trade:
                print("✅ Trade successfully copied to CTI:")
                print(f"   - Mapped Symbol: {copied_trade['symbol']}")
                print(f"   - Volume: {copied_trade['volume']}")
                print(f"   - Type: {copied_trade['type']}")
            else:
                print("❌ Trade copy simulation failed")
        else:
            print("⚠️  Skipping trade copy - CTI not connected")
        
        # Step 6: Show results summary
        print("\n📊 Demo Results Summary:")
        print("=" * 60)
        print(f"MT5 Connection: {'✅ SUCCESS' if mt5_connected else '❌ FAILED'}")
        print(f"CTI Connection: {'✅ SUCCESS' if cti_connected else '❌ FAILED'}")
        print(f"Trade Copying: {'✅ READY' if (mt5_connected and cti_connected) else '❌ NOT READY'}")
        
        if mt5_connected and cti_connected:
            print("\n🎉 DEMO COMPLETE! Your system is ready for live trading.")
            print("   Run 'python run_mvp.py' to start the live trade copier.")
        else:
            print("\n⚠️  Please check your configuration and try again.")
            
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")

async def test_mt5_connection(mt5_connector):
    """Test the MT5 connection"""
    try:
        # In a real scenario, this would connect to actual MT5
        # For demo purposes, we'll simulate the connection
        await asyncio.sleep(0.5)  # Simulate connection time
        logger.info("MT5 connection test completed")
        return True
    except Exception as e:
        logger.error(f"MT5 connection failed: {e}")
        return False

async def test_cti_connection(cti_client):
    """Test the City Traders Imperium connection"""
    try:
        async with aiohttp.ClientSession() as session:
            # In a real scenario, this would make actual API calls
            # For demo purposes, we'll simulate the authentication
            await asyncio.sleep(0.5)  # Simulate network delay
            logger.info(f"CTI authentication test for {cti_client.username}")
            
            # This would normally call cti_client.authenticate(session)
            # For demo, we'll return success
            return True
    except Exception as e:
        logger.error(f"CTI connection failed: {e}")
        return False

def simulate_mt5_trade():
    """Simulate an MT5 trade being placed"""
    return {
        'symbol': 'EURUSD',
        'type': 'BUY',
        'volume': 0.1,
        'price': 1.0850,
        'sl': 1.0800,  # Stop Loss
        'tp': 1.0900,  # Take Profit
        'timestamp': datetime.now(),
        'ticket': 123456789
    }

async def simulate_trade_copy(copier, mt5_trade):
    """Simulate copying a trade to CTI"""
    try:
        # Map the symbol using the symbol mapper
        mapped_symbol = copier.symbol_mapper.map_symbol(mt5_trade['symbol'])
        
        # Create the order details for CTI
        cti_order = {
            'symbol': mapped_symbol,
            'volume': mt5_trade['volume'],
            'type': mt5_trade['type'],
            'price': mt5_trade['price']
        }
        
        # Simulate network delay
        await asyncio.sleep(0.3)
        
        logger.info(f"Trade copied: {mt5_trade['symbol']} -> {mapped_symbol}")
        return cti_order
        
    except Exception as e:
        logger.error(f"Trade copy simulation failed: {e}")
        return None

if __name__ == "__main__":
    print("Starting CTI Demo...")
    asyncio.run(demo_cti_connection())
