#!/usr/bin/env python3
"""
Research City Traders Imperium platform
Check what trading platform they actually use
"""

import asyncio
import aiohttp
import re
from urllib.parse import urljoin

async def research_cti_platform():
    """Research CTI's trading platform"""
    
    print("🔍 Researching City Traders Imperium Platform")
    print("=" * 50)
    
    base_urls = [
        "https://citytradersimperium.com",
        "https://www.citytradersimperium.com",
        "https://platform.citytradersimperium.com",
        "https://app.citytradersimperium.com"
    ]
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
        for url in base_urls:
            print(f"\n🌐 Analyzing: {url}")
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        await analyze_platform(html, url)
                    else:
                        print(f"   Status: {response.status}")
            except Exception as e:
                print(f"   Error: {e}")

async def analyze_platform(html, base_url):
    """Analyze HTML to identify trading platform"""
    
    # Look for common trading platform indicators
    platform_indicators = {
        "TradeLocker": ["tradelocker", "trade-locker", "TL."],
        "cTrader": ["ctrader", "spotware", "cbot"],  
        "MetaTrader": ["metatrader", "mt4", "mt5", "metaquotes"],
        "DXTrade": ["dxtrade", "devexperts"],
        "Match-Trader": ["matchtrade", "match-trader", "matchtrader"],
        "TradingView": ["tradingview", "charting_library"],
        "PropriFirm": ["proprietary", "prop-firm", "propfirm"],
        "Custom": ["login", "dashboard", "trading"]
    }
    
    found_platforms = []
    
    for platform, keywords in platform_indicators.items():
        for keyword in keywords:
            if keyword.lower() in html.lower():
                found_platforms.append(platform)
                break
    
    if found_platforms:
        print(f"   📊 Detected platforms: {', '.join(set(found_platforms))}")
    else:
        print("   ❓ No specific platform detected")
    
    # Look for login forms and API endpoints
    login_patterns = [
        r'action=["\']([^"\']*login[^"\']*)["\']',
        r'href=["\']([^"\']*login[^"\']*)["\']',
        r'fetch\(["\']([^"\']*api[^"\']*)["\']',
        r'"api":\s*"([^"]*)"',
        r'baseURL:\s*["\']([^"\']*)["\']'
    ]
    
    endpoints = []
    for pattern in login_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        endpoints.extend(matches)
    
    if endpoints:
        print(f"   🔗 Found potential endpoints:")
        for endpoint in set(endpoints[:5]):  # Show first 5 unique endpoints
            if not endpoint.startswith('http'):
                endpoint = urljoin(base_url, endpoint)
            print(f"      - {endpoint}")
    
    # Look for JavaScript files that might contain API info
    js_files = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', html)
    if js_files:
        print(f"   📜 JavaScript files found: {len(js_files)}")
        # Show a few important looking ones
        important_js = [js for js in js_files if any(word in js.lower() for word in ['api', 'auth', 'login', 'main', 'app'])]
        for js_file in important_js[:3]:
            if not js_file.startswith('http'):
                js_file = urljoin(base_url, js_file)
            print(f"      - {js_file}")

if __name__ == "__main__":
    print("Researching CTI Platform...")
    asyncio.run(research_cti_platform())
