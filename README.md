```
 ██████╗  █████╗ ████████╗███╗   ██╗ █████╗      ██╗  ██╗██╗██████╗ ████████╗██╗
██╔══██╗██╔══██╗╚══██╔══╝████╗  ██║██╔══██╗     ██║ ██╔╝██║██╔══██╗╚══██╔══╝██║
██████╔╝███████║   ██║   ██╔██╗ ██║███████║     █████╔╝ ██║██████╔╝   ██║   ██║
██╔══██╗██╔══██║   ██║   ██║╚██╗██║██╔══██║     ██╔═██╗ ██║██╔══██╗   ██║   ██║
██║  ██║██║  ██║   ██║   ██║ ╚████║██║  ██║     ██║  ██╗██║██║  ██║   ██║   ██║
╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝

███╗   ███╗████████╗███████╗    ████████╗██████╗  █████╗ ██████╗ ███████╗██████╗ 
████╗ ████║╚══██╔══╝██╔════╝    ╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
██╔████╔██║   ██║   ███████╗       ██║   ██████╔╝███████║██║  ██║█████╗  ██████╔╝
██║╚██╔╝██║   ██║   ╚════██║       ██║   ██╔══██╗██╔══██║██║  ██║██╔══╝  ██╔══██╗
██║ ╚═╝ ██║   ██║   ███████║       ██║   ██║  ██║██║  ██║██████╔╝███████╗██║  ██║
╚═╝     ╚═╝   ╚═╝   ╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
```

<div align="center">

# 🚀 **Professional MT5 to MatchTrader Bridge** 🚀

*Engineered by [Ratna Kirti](https://github.com/ratna3) - Software Engineer & Trading Technology Specialist*

[![GitHub](https://img.shields.io/badge/GitHub-ratna3-181717?style=for-the-badge&logo=github)](https://github.com/ratna3)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)]()

</div>

---

## 🎯 **Enterprise-Grade Trade Replication System**

A sophisticated, asynchronous trading bridge that seamlessly replicates MetaTrader 5 positions to MatchTrader prop firm platforms. Built with modern Python architecture, comprehensive error handling, and institutional-grade security protocols.

### ✨ **Key Features**
- 🔄 **Real-time Position Monitoring** - Instant trade detection and replication
- 🛡️ **Enterprise Security** - Encrypted credentials and secure API communication
- 📊 **Multi-Account Support** - Manage multiple MT5 and prop firm accounts
- 🎯 **Smart Symbol Mapping** - Automatic conversion between platform symbols
- 📈 **Risk Management Tools** - Configurable lot sizing and position limits
- 🔧 **Professional Logging** - Comprehensive audit trails and monitoring

## 📋 **System Requirements**

- Windows OS (required for MT5)
- Python 3.8 or higher
- MetaTrader 5 terminal installed
- MT5 trading account
- MatchTrader prop firm account(s)

## Installation

1. **Download the project:**
   ```
   git clone https://github.com/ratna3/MT5-MatchTrader-MVP.git
   cd MT5-MatchTrader-MVP
   ```

2. **Install dependencies:**
   ```
   install_mvp.bat
   ```
   This will create a virtual environment and install all required packages.

## Configuration

1. **Open the configuration file:**
   ```
   notepad config_mvp.json
   ```

2. **Enter your account details:**

   ```json
   {
     "mt5_accounts": [
       {
         "account_id": "my_mt5",
         "login": 12345678,
         "password": "your_mt5_password",
         "server": "Your-Broker-Server"
       }
     ],
     "matchtrade_accounts": [
       {
         "account_id": "my_e8_account",
         "account_number": "E8-123456",
         "username": "your_email@example.com",
         "password": "your_matchtrade_password",
         "broker_name": "e8markets"
       }
     ]
   }
   ```

   **For each MatchTrader account, you need:**
   - **account_number**: Your prop firm account number (e.g., "E8-123456")
   - **username**: Your login email/username
   - **password**: Your account password
   - **broker_name**: One of: "e8markets", "toponetrader", "ftmo"

## Usage

1. **Test your connections:**
   ```
   python test_connection.py
   ```
   You should see:
   ```
   🧪 Testing MT5 and MatchTrader connections...
   MT5 Connection: ✅ Success
   MatchTrader https://platform.e8markets.com: ✅ Success
   ```

2. **Start the trade copier:**
   ```
   python run_mvp.py
   ```

3. **Stop the copier:**
   Press `Ctrl+C` to stop gracefully.

## Supported Prop Firms

- **E8 Markets** (broker_name: "e8markets")
- **Top One Trader** (broker_name: "toponetrader")
- **FTMO** (broker_name: "ftmo")

## How It Works

1. Monitors your MT5 account for new positions
2. Automatically maps MT5 symbols to MatchTrader symbols
3. Authenticates with your prop firm accounts
4. Replicates trades on MatchTrader platforms
5. Handles errors and reconnects automatically

## Troubleshooting

**MT5 Connection Failed:**
- Ensure MT5 terminal is running
- Check your login number is correct
- Verify server name matches exactly

**MatchTrader Authentication Failed:**
- Double-check your email/username
- Verify password is correct
- Confirm account number format

## 📞 **Support & Contact**

<div align="center">

### **Professional Support Available**

📧 **Technical Support**: Open a [GitHub Issue](https://github.com/ratna3/MT5-MatchTrader-MVP/issues)  
👤 **Developer Contact**: [Ratna Kirti (@ratna3)](https://github.com/ratna3)  
📈 **Professional Consulting**: Available for custom implementations  

[![GitHub Issues](https://img.shields.io/github/issues/ratna3/MT5-MatchTrader-MVP?style=for-the-badge)](https://github.com/ratna3/MT5-MatchTrader-MVP/issues)
[![GitHub Stars](https://img.shields.io/github/stars/ratna3/MT5-MatchTrader-MVP?style=for-the-badge)](https://github.com/ratna3/MT5-MatchTrader-MVP/stargazers)

</div>

---

<div align="center">

**🎆 Engineered with Excellence by Ratna Kirti 🎆**

*Professional Software Engineer & Trading Technology Specialist*

*“Building enterprise-grade solutions that traders trust”*

</div>
