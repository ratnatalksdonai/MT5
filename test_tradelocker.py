#!/usr/bin/env python3
"""
Test TradeLocker authentication for City Traders Imperium
"""

import asyncio
import logging
from src.tradelocker_client import TradeLockerClient
import aiohttp

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# CTI credentials
CTI_USERNAME = "dparkmit@gmail.com"
CTI_PASSWORD = "Hwr0^u{vz_"
CTI_ACCOUNT = "16609"

async def test_tradelocker_auth():
    """Test TradeLocker authentication for CTI"""
    
    print("🔍 Testing TradeLocker Authentication for City Traders Imperium")
    print("=" * 65)
    
    client = TradeLockerClient(
        username=CTI_USERNAME,
        password=CTI_PASSWORD,
        account_number=CTI_ACCOUNT
    )
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        
        print("\n🔐 Step 1: Attempting authentication...")
        auth_success = await client.authenticate(session)
        
        if auth_success:
            print("✅ Authentication successful!")
            print(f"   Token: {client.token[:20]}..." if client.token else "None")
            print(f"   Account ID: {client.account_id}")
            
            print("\n📊 Step 2: Getting account information...")
            accounts = await client.get_positions(session)
            print(f"   Found {len(accounts)} positions")
            
            print("\n🔍 Step 3: Testing instrument lookup...")
            instrument_id = await client.get_instrument_id(session, "EURUSD")
            print(f"   EURUSD instrument ID: {instrument_id}")
            
            # Test order placement (simulation)
            print("\n📈 Step 4: Testing order placement (simulation)...")
            test_order = {
                "symbol": "EURUSD",
                "type": "BUY",
                "volume": 0.01  # Very small test size
            }
            
            # Note: Comment out the actual order placement for safety
            # order_result = await client.place_order(session, test_order)
            print("   Order placement test skipped for safety")
            print("   (Uncomment in code to test actual order placement)")
            
            print("\n🎉 All tests completed successfully!")
            return True
            
        else:
            print("❌ Authentication failed!")
            return False

if __name__ == "__main__":
    print("Starting TradeLocker Authentication Test...")
    success = asyncio.run(test_tradelocker_auth())
    
    if success:
        print("\n✅ TradeLocker integration is ready!")
    else:
        print("\n❌ TradeLocker integration needs debugging")
