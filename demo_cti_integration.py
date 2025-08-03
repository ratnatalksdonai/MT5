#!/usr/bin/env python3
"""
🔬 MT5 to CTI Integration Demo Script

This script demonstrates what happens when you attempt to connect to:
1. MT5 GNTCapital Demo Account (200374)
2. City Traders Imperium Account (16609)

Usage: python demo_cti_integration.py
"""

import asyncio
import logging
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.trade_copier_mvp import TradeCopierMVP
from src.mt5_connector import MT5Connector
from src.tradelocker_client import TradeLockerClient

# Setup enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/cti_integration_demo.log')
    ]
)

logger = logging.getLogger(__name__)

async def demo_mt5_connection():
    """Demonstrate MT5 connection with GNTCapital Demo"""
    print("\n🔌 Testing MT5 Connection...")
    print("=" * 50)
    
    mt5_config = {
        "login": 200374,
        "password": "C!0wcaa6",
        "server": "GNTCapital-Demo"
    }
    
    connector = MT5Connector(mt5_config)
    
    try:
        # Test connection
        logger.info("Attempting MT5 connection...")
        success = await connector.connect_with_retry()
        
        if success:
            print("✅ MT5 Connection: SUCCESS")
            
            # Get account info
            account_info = connector.get_account_info()
            print(f"📊 Account Balance: ${account_info.get('balance', 'N/A')}")
            print(f"📊 Account Equity: ${account_info.get('equity', 'N/A')}")
            print(f"📊 Free Margin: ${account_info.get('free_margin', 'N/A')}")
            
            # Get positions
            positions = connector.get_positions()
            print(f"📈 Open Positions: {len(positions)}")
            
            if positions:
                for pos in positions[:3]:  # Show first 3 positions
                    print(f"   • {pos['symbol']} {pos['type']} {pos['volume']} lots")
        else:
            print("❌ MT5 Connection: FAILED")
            print("   Possible issues:")
            print("   - MT5 terminal not running")
            print("   - Invalid credentials")
            print("   - Server connection issues")
            
    except Exception as e:
        print(f"❌ MT5 Connection Error: {e}")
    finally:
        connector.shutdown()

async def demo_cti_connection():
    """Demonstrate CTI connection attempt"""
    print("\n🔌 Testing City Traders Imperium Connection...")
    print("=" * 50)
    
    client = TradeLockerClient(
        username="dparkmit@gmail.com",
        password="Hwr0^u{vz_",
        account_number="16609"
    )
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            logger.info("Attempting CTI authentication...")
            success = await client.authenticate(session)
            
            if success:
                print("✅ CTI Authentication: SUCCESS")
                print(f"🎯 Account ID: {client.account_id}")
                
                # Try to get account info
                account_info = await client.get_account_info(session)
                if account_info:
                    print("📊 Account Info Retrieved")
                    # Don't print sensitive info, just confirm access
                else:
                    print("⚠️ Account info not accessible")
                    
                # Try to get positions
                positions = await client.get_positions(session)
                print(f"📈 Open Positions: {len(positions)}")
                
            else:
                print("❌ CTI Authentication: FAILED")
                print("   Possible issues:")
                print("   - Incorrect server configuration")
                print("   - API access not enabled")
                print("   - Invalid credentials")
                print("   - TradeLocker API changes")
                
    except ImportError:
        print("❌ Missing aiohttp dependency")
        print("   Run: pip install aiohttp")
    except Exception as e:
        print(f"❌ CTI Connection Error: {e}")

async def demo_trade_replication():
    """Demonstrate what would happen during trade replication"""
    print("\n📋 Trade Replication Simulation...")
    print("=" * 50)
    
    # Simulate an MT5 trade
    simulated_trade = {
        "symbol": "EURUSD.z",
        "type": "BUY",
        "volume": 0.1,
        "price": 1.0850,
        "sl": 1.0800,
        "tp": 1.0950
    }
    
    print("🎯 Simulated MT5 Trade:")
    print(f"   Symbol: {simulated_trade['symbol']}")
    print(f"   Type: {simulated_trade['type']}")
    print(f"   Volume: {simulated_trade['volume']} lots")
    print(f"   Price: {simulated_trade['price']}")
    
    # Show symbol mapping
    from src.symbol_mapper import SymbolMapper
    mapper = SymbolMapper()
    mapped_symbol = mapper.map_symbol(simulated_trade['symbol'])
    print(f"🔄 Mapped Symbol: {mapped_symbol}")
    
    # Show what would be sent to CTI
    cti_order = {
        "accNum": "16609",
        "tradeSide": 1,  # BUY
        "qty": simulated_trade['volume'],
        "instrId": "EUR/USD",  # Would be resolved from API
        "orderType": 1,  # Market order
        "timeInForce": 1  # GTC
    }
    
    print("📤 CTI Order Format:")
    for key, value in cti_order.items():
        print(f"   {key}: {value}")
    
    print("\n⚠️ Current Status: Authentication Required")
    print("   Once CTI authentication works, this trade would be replicated automatically.")

async def main():
    """Run the complete integration demo"""
    print("🚀 MT5 to City Traders Imperium Integration Demo")
    print("=" * 60)
    print("This demo shows what happens when connecting with provided credentials:")
    print("• MT5: login 200374, server GNTCapital-Demo")
    print("• CTI: account 16609, email dparkmit@gmail.com")
    print("=" * 60)
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    try:
        # Test MT5 connection
        await demo_mt5_connection()
        
        # Test CTI connection  
        await demo_cti_connection()
        
        # Show trade replication process
        await demo_trade_replication()
        
        print("\n📋 Summary")
        print("=" * 50)
        print("✅ MT5 connection should work with proper MT5 terminal setup")
        print("⚠️ CTI connection requires API access configuration")
        print("🔄 Trade replication will work once both connections are established")
        print("\nSee INTEGRATION_GUIDE.md for detailed troubleshooting steps.")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        logger.exception("Demo failed with unexpected error")
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Failed to start demo: {e}")
