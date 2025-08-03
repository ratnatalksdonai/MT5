#!/usr/bin/env python3
"""
Simplified debug script for City Traders Imperium
Focuses on finding the correct authentication method
"""

import asyncio
import aiohttp
import json

# CTI credentials
CTI_USERNAME = "dparkmit@gmail.com"
CTI_PASSWORD = "Hwr0^u{vz_"
CTI_ACCOUNT = "16609"

async def test_cti_authentication():
    """Test different CTI authentication approaches"""
    
    print("🔍 City Traders Imperium Authentication Test")
    print("=" * 50)
    
    # Common prop firm platforms that CTI might use
    test_urls = [
        # Direct CTI URLs
        "https://platform.citytradersimperium.com",
        "https://app.citytradersimperium.com",
        "https://trading.citytradersimperium.com",
        "https://client.citytradersimperium.com",
        
        # Common trading platforms
        "https://live.tradelocker.com",
        "https://platform.tradelocker.com",
        "https://api.tradelocker.com",
        
        # MetaTrader Web API
        "https://mt5.citytradersimperium.com",
        "https://webapi.citytradersimperium.com",
        
        # cTrader
        "https://ct.citytradersimperium.com",
        "https://ctrader.citytradersimperium.com"
    ]
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        for base_url in test_urls:
            print(f"\n🔗 Testing: {base_url}")
            
            # First check if URL exists
            accessible = await check_url_exists(session, base_url)
            if not accessible:
                print("   ❌ URL not accessible")
                continue
            
            print("   ✅ URL accessible")
            
            # Try common authentication endpoints
            auth_endpoints = [
                "/api/auth/login",
                "/api/login", 
                "/auth/login",
                "/login",
                "/api/v1/login",
                "/connect/token",
                "/oauth/token"
            ]
            
            for endpoint in auth_endpoints:
                full_url = base_url + endpoint
                result = await test_auth_endpoint(session, full_url)
                if result:
                    print(f"   🎉 FOUND WORKING ENDPOINT: {endpoint}")
                    return True
    
    print("\n❌ No working authentication endpoint found")
    return False

async def check_url_exists(session, url):
    """Check if a URL is accessible"""
    try:
        async with session.get(url, timeout=5) as response:
            return response.status < 500
    except:
        return False

async def test_auth_endpoint(session, url):
    """Test authentication at a specific endpoint"""
    payloads = [
        # Standard formats
        {"username": CTI_USERNAME, "password": CTI_PASSWORD, "account": CTI_ACCOUNT},
        {"email": CTI_USERNAME, "password": CTI_PASSWORD, "account_id": CTI_ACCOUNT},
        {"login": CTI_USERNAME, "password": CTI_PASSWORD},
        
        # OAuth-style
        {"grant_type": "password", "username": CTI_USERNAME, "password": CTI_PASSWORD, "client_id": "web"},
        
        # Form data style
        {"user": CTI_USERNAME, "pass": CTI_PASSWORD}
    ]
    
    for i, payload in enumerate(payloads):
        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            async with session.post(url, json=payload, headers=headers, timeout=8) as response:
                status = response.status
                
                # Check for successful authentication indicators
                if status == 200:
                    try:
                        body = await response.json()
                        if any(key in body for key in ['token', 'access_token', 'jwt', 'sessionId']):
                            print(f"      ✅ SUCCESS with payload {i+1}: {list(payload.keys())}")
                            print(f"         Response: {body}")
                            return True
                    except:
                        pass
                
                # Check for different error types
                if status == 401:
                    print(f"      🔐 Payload {i+1}: Unauthorized (401)")
                elif status == 400:
                    try:
                        error_body = await response.text()
                        if "invalid" in error_body.lower() or "error" in error_body.lower():
                            print(f"      ❌ Payload {i+1}: Bad Request - {error_body[:100]}")
                    except:
                        print(f"      ❌ Payload {i+1}: Bad Request (400)")
                elif status == 404:
                    return False  # Endpoint doesn't exist
                elif status == 405:
                    return False  # Method not allowed
                
        except asyncio.TimeoutError:
            print(f"      ⏰ Payload {i+1}: Timeout")
        except Exception as e:
            print(f"      💥 Payload {i+1}: Error - {str(e)[:50]}")
    
    return False

if __name__ == "__main__":
    print("Starting CTI Simple Authentication Test...")
    asyncio.run(test_cti_authentication())
