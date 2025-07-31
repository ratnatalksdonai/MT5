# MT5 to MatchTrader Trade Copier

Automatically copy trades from MetaTrader 5 to MatchTrader prop firm accounts.

## Requirements

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

## Support

For support, please contact:
- Email: ratnakirtiscr@gmail.com
- LinkedIn: [linkedin.com/in/ratna-kirti](https://www.linkedin.com/in/ratna-kirti/)
- GitHub Issues: [github.com/ratna3/MT5-MatchTrader-MVP/issues](https://github.com/ratna3/MT5-MatchTrader-MVP/issues)
