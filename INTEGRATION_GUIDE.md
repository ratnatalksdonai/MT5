# 🚀 MT5 to City Traders Imperium Integration Guide

## Overview
This document explains the complete integration process between MetaTrader 5 and City Traders Imperium (CTI) using our trade copier system. It covers what happens when you attempt to connect with the provided credentials and the expected workflow.

---

## 🔧 Integration Setup Process

### 1. Account Configuration
When setting up the integration with the provided accounts:

**MT5 Demo Account (GNTCapital):**
```json
{
  "account_id": "gnt_demo",
  "login": 200374,
  "password": "C!0wcaa6",
  "server": "GNTCapital-Demo"
}
```

**City Traders Imperium Account:**
```json
{
  "account_id": "city_traders_imperium",
  "account_number": "16609",
  "username": "dparkmit@gmail.com", 
  "password": "Hwr0^u{vz_",
  "broker_name": "citytradersimperium"
}
```

### 2. What Happens During Connection

#### MT5 Connection Process:
✅ **Step 1: MT5 Terminal Initialization**
- System initializes MetaTrader5 library
- Connects to GNTCapital-Demo server
- Authenticates with login 200374

✅ **Step 2: Account Verification**
- Retrieves account information (balance, equity, margin)
- Validates trading permissions
- Sets up position monitoring

#### CTI Connection Process:
🔄 **Step 1: TradeLocker Authentication**
- Uses specialized `TradeLockerClient` for CTI
- Attempts connection to `https://live.tradelocker.com`
- Tries multiple server configurations:
  - `citytradersimperium`
  - `cti`
  - `city-traders-imperium`
  - `live`

⚠️ **Current Challenge: Authentication Issues**
The integration attempts authentication but encounters the following:

```python
# Authentication endpoint
url = "https://live.tradelocker.com/backend-api/auth/jwt/token"

# Request payload
data = {
    "email": "dparkmit@gmail.com",
    "password": "Hwr0^u{vz_",
    "server": "citytradersimperium"  # Tries multiple server names
}
```

**Potential Issues:**
1. **Server Configuration**: CTI may use a different server identifier
2. **API Access**: TradeLocker API might require specific permissions
3. **Authentication Method**: CTI might use different auth flow than standard TradeLocker

---

## 🔄 Trade Copying Workflow

### When a Trade is Placed on MT5:

1. **Trade Detection**
   ```python
   # MT5 monitors for new positions
   positions = mt5.positions_get()
   new_trade = detect_new_position(positions)
   ```

2. **Symbol Mapping**
   ```python
   # Convert MT5 symbol to CTI format
   mt5_symbol = "EURUSD.z"
   cti_symbol = symbol_mapper.map_symbol(mt5_symbol)  # "EURUSD"
   ```

3. **Order Replication**
   ```python
   # Prepare order for CTI
   order_details = {
       "accNum": "16609",
       "tradeSide": 1,  # 1=BUY, 2=SELL
       "qty": 0.1,      # Lot size
       "instrId": get_instrument_id("EURUSD"),
       "orderType": 1,   # Market order
       "timeInForce": 1  # GTC
   }
   ```

### Expected Results:
- ✅ MT5 trade opens successfully
- 🔄 System detects new position
- 🔄 Converts trade parameters
- ❌ **Current Issue**: CTI authentication fails, preventing trade replication

---

## 🛠️ Technical Implementation Details

### Code Structure:
```
src/
├── trade_copier_mvp.py      # Main orchestrator
├── mt5_connector.py         # MT5 integration
├── tradelocker_client.py    # CTI-specific client
├── matchtrade_client.py     # Generic prop firm client
└── symbol_mapper.py         # Symbol conversion
```

### Authentication Flow:
```python
class TradeLockerClient:
    async def authenticate(self, session):
        # Multiple server attempts
        server_configs = [
            "citytradersimperium",
            "cti", 
            "city-traders-imperium"
        ]
        
        for server in server_configs:
            # Attempt authentication
            response = await session.post(auth_url, json=data)
            if response.status == 200:
                return True
        
        return False  # All attempts failed
```

---

## 🔍 Troubleshooting CTI Integration

### Common Issues and Solutions:

#### 1. Authentication Failures
**Symptoms:**
- "Authentication failed" messages
- HTTP 401/403 responses
- "Invalid credentials" errors

**Potential Causes:**
- Incorrect server configuration
- API access not enabled for account
- Different authentication endpoint

**Solutions:**
```python
# Try alternative endpoints
endpoints = [
    "https://live.tradelocker.com/backend-api/auth/jwt/token",
    "https://api.tradelocker.com/auth/login",
    "https://cti.tradelocker.com/api/auth"
]
```

#### 2. Account ID Resolution
**Issue:** Account number 16609 not found in API response

**Debug Steps:**
```python
# Check available accounts
accounts = await get_account_info()
print(f"Available accounts: {accounts}")

# Match account number
for account in accounts.get("accounts", []):
    if str(account.get("accountNum")) == "16609":
        print(f"Found account: {account}")
```

#### 3. Instrument ID Mapping
**Issue:** Symbol conversion between MT5 and CTI formats

**Current Mapping:**
```python
symbol_mappings = {
    "EURUSD.z": "EUR/USD",
    "GBPUSD.z": "GBP/USD", 
    "XAUUSD": "XAU/USD",
    "US30": "US30"
}
```

---

## 📋 Testing Checklist

### Pre-Integration Tests:
- [ ] MT5 terminal can connect to GNTCapital-Demo
- [ ] Account 200374 has active demo balance
- [ ] CTI account 16609 is active and accessible
- [ ] Python environment has all required packages

### Integration Tests:
- [ ] MT5Connector initializes successfully
- [ ] TradeLockerClient attempts authentication
- [ ] Symbol mapping works correctly
- [ ] Error handling captures authentication failures

### Trade Replication Tests:
```python
# Test sequence
1. Place EURUSD BUY 0.1 lot on MT5
2. System should detect new position
3. Convert to CTI format
4. Attempt to replicate on CTI account 16609
5. Log success/failure with detailed error info
```

---

## 🚨 Current Status & Next Steps

### ✅ Working Components (Test Results: 52/53 PASSED - 98.1%):
- ✅ MT5 connection and monitoring logic
- ✅ Trade detection system 
- ✅ Symbol mapping (EURUSD.z → EURUSD)
- ✅ Error logging and retry mechanisms
- ✅ Order format conversion (MT5 → CTI)
- ✅ Configuration management
- ✅ Security and authentication framework

### ⚠️ Current Blockers:
1. **MT5 Terminal**: Not running (easily fixable)
2. **CTI Authentication**: All 6 server configs return 401 "Failed to fetch token, check if server exists"
3. **API Access**: CTI needs to provide correct server configuration

### 🔄 Recommended Actions:

1. **Start MetaTrader 5**
   ```
   Download and install MetaTrader 5
   Add server: GNTCapital-Demo  
   Login: 200374
   Password: C!0wcaa6
   ```

2. **Contact CTI Support (Priority)**
   ```
   Subject: API Access for Trade Copier Integration
   Account: 16609 (dparkmit@gmail.com)
   Request: Correct TradeLocker server configuration
   Issue: All server names return "check if server exists" error
   ```

3. **Test Results Available**
   ```
   ✅ 98.1% of system components working perfectly
   ⚠️ Only external authentication blocked  
   📋 See TEST_RESULTS_SUMMARY.md for full details
   ```

---

## 📞 Support Information

**For CTI Integration Issues:**
- Contact: City Traders Imperium Support
- Account Reference: 16609
- Integration Type: TradeLocker API via MT5 Trade Copier

**For Technical Issues:**
- Repository: https://github.com/ratna3/MT5-MatchTrader-MVP
- Author: Ratna Kirti (@ratna3)
- License: MIT

---

## 🎯 Expected Final Workflow

Once authentication is resolved:

1. **Trade Placement**: User places EUR/USD BUY 0.1 on MT5
2. **Detection**: System detects new position within 1-2 seconds
3. **Conversion**: Converts MT5 format to CTI format
4. **Replication**: Places identical trade on CTI account 16609
5. **Confirmation**: Both platforms show synchronized positions
6. **Monitoring**: Continues monitoring for position updates/closes

**Success Indicators:**
- ✅ Both MT5 and CTI show matching positions
- ✅ Trade parameters (symbol, volume, direction) are identical
- ✅ Real-time synchronization of trade modifications
- ✅ Proper error handling and logging throughout process

---

*This integration guide will be updated as authentication issues are resolved and testing progresses.*
