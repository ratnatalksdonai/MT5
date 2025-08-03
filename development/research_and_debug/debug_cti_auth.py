#!/usr/bin/env python3
"""
Debug script for City Traders Imperium authentication
Tests different endpoints and authentication methods
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CTI credentials from config
CTI_USERNAME = "dparkmit@gmail.com"
CTI_PASSWORD = "Hwr0^u{vz_"
CTI_ACCOUNT = "16609"

async def test_cti_endpoints():
    """Test different CTI endpoints and authentication methods"""
    
    print("🔍 City Traders Imperium Authentication Debug")
    print("=" * 60)
    
    # Different possible base URLs for CTI
    possible_urls = [
        "https://platform.citytradersimperium.com",
        "https://app.citytradersimperium.com", 
        "https://api.citytradersimperium.com",
        "https://trading.citytradersimperium.com",
        "https://client.citytradersimperium.com",
        "https://portal.citytradersimperium.com"
    ]
    
    # Different possible endpoints
    endpoints = [
        "/api/auth/login",
        "/api/login",
        "/auth/login",
        "/login",
        "/api/v1/auth/login",
        "/api/v1/login"
    ]
    
    # Different payload formats
    payloads = [
        {"username": CTI_USERNAME, "password": CTI_PASSWORD, "account_number": CTI_ACCOUNT},
        {"email": CTI_USERNAME, "password": CTI_PASSWORD, "account": CTI_ACCOUNT},
        {"login": CTI_USERNAME, "password": CTI_PASSWORD, "account_id": CTI_ACCOUNT},
        {"username": CTI_USERNAME, "password": CTI_PASSWORD},
        {"email": CTI_USERNAME, "password": CTI_PASSWORD},
        {"user": CTI_USERNAME, "pass": CTI_PASSWORD, "account": CTI_ACCOUNT}
    ]
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        
        # First, check if the main website is accessible
        print("\n🌐 Testing website accessibility...")
        await test_website_access(session, "https://citytradersimperium.com")
        
        # Test different combinations
        for base_url in possible_urls:
            print(f"\n🔗 Testing base URL: {base_url}")
            
            # Test if the base URL is accessible
            accessible = await test_url_access(session, base_url)
            if not accessible:
                print(f"   ❌ Base URL not accessible")
                continue
            
            for endpoint in endpoints:
                full_url = base_url + endpoint
                print(f"\n   📡 Testing endpoint: {endpoint}")
                
                for i, payload in enumerate(payloads):
                    print(f"      🔑 Payload format {i+1}: {list(payload.keys())}")
                    await test_authentication(session, full_url, payload)

async def test_website_access(session, url):
    """Test if the main website is accessible"""
    try:
        async with session.get(url, timeout=10) as response:
            print(f"   ✅ Main website accessible: {response.status}")
            return True
    except Exception as e:
        print(f"   ❌ Main website not accessible: {e}")
        return False

async def test_url_access(session, url):
    """Test if a URL is accessible"""
    try:
        async with session.get(url, timeout=10) as response:
            print(f"   Status: {response.status}")
            if response.status < 500:  # Consider anything below 500 as accessible
                return True
    except Exception as e:
        print(f"   Error: {e}")
    return False

async def test_authentication(session, url, payload):
    """Test authentication with specific URL and payload"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MT5-MatchTrader-MVP/1.0',
            'Accept': 'application/json'
        }
        
        async with session.post(url, json=payload, headers=headers, timeout=15) as response:
            status = response.status
            headers_dict = dict(response.headers)
            
            try:
                if response.content_type == 'application/json':
                    body = await response.json()
                else:
                    body = await response.text()
            except:
                body = "Could not read response body"
            
            print(f"         Status: {status}")
            
            if status == 200:
                print(f"         ✅ SUCCESS! Response: {body}")
            elif status == 401:
                print(f"         🔐 Unauthorized - Invalid credentials")
            elif status == 403:
                print(f"         🚫 Forbidden - Access denied")
            elif status == 404:
                print(f"         🔍 Not Found - Endpoint doesn't exist")
            elif status == 405:
                print(f"         ❌ Method Not Allowed")
            else:
                print(f"         ❓ Other error: {body}")
                
    except asyncio.TimeoutError:
        print(f"         ⏰ Timeout")
    except Exception as e:
        print(f"         💥 Error: {e}")

async def test_common_trading_platforms():
    """Test if CTI uses a common trading platform"""
    
    print("\n🎯 Testing Common Trading Platform URLs...")
    
    # Common prop firm platforms
    common_platforms = {
        "TradeLocker": "https://live.tradelocker.com",
        "cTrader": "https://ct.citytradersimperium.com", 
        "MetaTrader": "https://mt.citytradersimperium.com",
        "DXTrade": "https://dx.citytradersimperium.com",
        "Custom Platform": "https://trade.citytradersimperium.com"
    }
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
        for platform_name, url in common_platforms.items():
            print(f"\n   Testing {platform_name}: {url}")
            accessible = await test_url_access(session, url)
            
            if accessible:
                # Try common login endpoints
                login_endpoints = ["/api/login", "/login", "/auth/login"]
                for endpoint in login_endpoints:
                    full_url = url + endpoint
                    payload = {"username": CTI_USERNAME, "password": CTI_PASSWORD}
                    print(f"      Testing login at: {endpoint}")
                    await test_authentication(session, full_url, payload)

if __name__ == "__main__":
    print("Starting City Traders Imperium authentication debug...")
    asyncio.run(test_cti_endpoints())
    asyncio.run(test_common_trading_platforms())
