"""
MatchTrade Authentication Module

Handles username/password authentication for MatchTrade accounts.
This module implements the authentication flow to obtain access tokens
without requiring API keys.
"""

import requests
import json
import logging
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import jwt


class MatchTradeAuthenticator:
    """Handles authentication with MatchTrade API using username/password"""
    
    def __init__(self, broker_id: str, base_url: str):
        self.broker_id = broker_id
        self.base_url = base_url.replace("wss://", "https://").replace("/ws", "")
        self.logger = logging.getLogger(__name__)
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        
    def authenticate(self, username: str, password: str, account_number: str) -> Tuple[bool, Optional[str]]:
        """
        Authenticate with MatchTrade using username and password
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            # Step 1: Login with username and password
            login_url = f"{self.base_url}/api/auth/login"
            login_data = {
                "username": username,
                "password": password,
                "broker": self.broker_id
            }
            
            self.logger.info(f"Attempting login for user: {username}")
            response = requests.post(login_url, json=login_data)
            
            if response.status_code != 200:
                error_msg = f"Login failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return False, error_msg
                
            auth_data = response.json()
            
            # Extract tokens from response
            self.access_token = auth_data.get("access_token")
            self.refresh_token = auth_data.get("refresh_token")
            
            if not self.access_token:
                error_msg = "No access token received from authentication"
                self.logger.error(error_msg)
                return False, error_msg
                
            # Calculate token expiry
            expires_in = auth_data.get("expires_in", 3600)  # Default 1 hour
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            # Step 2: Select trading account
            if not self._select_account(account_number):
                error_msg = f"Failed to select account: {account_number}"
                return False, error_msg
                
            self.logger.info(f"Successfully authenticated for account: {account_number}")
            return True, None
            
        except Exception as e:
            error_msg = f"Authentication error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
            
    def _select_account(self, account_number: str) -> bool:
        """Select the trading account after authentication"""
        try:
            # Get list of available accounts
            accounts_url = f"{self.base_url}/api/accounts"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.get(accounts_url, headers=headers)
            if response.status_code != 200:
                self.logger.error(f"Failed to get accounts: {response.status_code}")
                return False
                
            accounts = response.json()
            
            # Find the requested account
            target_account = None
            for account in accounts:
                if account.get("account_number") == account_number:
                    target_account = account
                    break
                    
            if not target_account:
                self.logger.error(f"Account {account_number} not found")
                return False
                
            # Select the account
            select_url = f"{self.base_url}/api/accounts/{target_account['id']}/select"
            response = requests.post(select_url, headers=headers)
            
            if response.status_code != 200:
                self.logger.error(f"Failed to select account: {response.status_code}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error selecting account: {str(e)}")
            return False
            
    def refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token"""
        if not self.refresh_token:
            self.logger.error("No refresh token available")
            return False
            
        try:
            refresh_url = f"{self.base_url}/api/auth/refresh"
            data = {"refresh_token": self.refresh_token}
            
            response = requests.post(refresh_url, json=data)
            
            if response.status_code != 200:
                self.logger.error(f"Token refresh failed: {response.status_code}")
                return False
                
            auth_data = response.json()
            self.access_token = auth_data.get("access_token")
            
            # Update expiry
            expires_in = auth_data.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            self.logger.info("Successfully refreshed access token")
            return True
            
        except Exception as e:
            self.logger.error(f"Error refreshing token: {str(e)}")
            return False
            
    def is_token_valid(self) -> bool:
        """Check if the current access token is still valid"""
        if not self.access_token or not self.token_expiry:
            return False
            
        # Check if token will expire in the next 5 minutes
        return datetime.now() < (self.token_expiry - timedelta(minutes=5))
        
    def get_websocket_auth_params(self) -> Dict[str, str]:
        """Get authentication parameters for WebSocket connection"""
        if not self.is_token_valid():
            if not self.refresh_access_token():
                raise RuntimeError("Failed to refresh access token")
                
        return {
            "authorization": f"Bearer {self.access_token}",
            "broker": self.broker_id
        }
        
    def logout(self):
        """Logout and invalidate tokens"""
        if self.access_token:
            try:
                logout_url = f"{self.base_url}/api/auth/logout"
                headers = {"Authorization": f"Bearer {self.access_token}"}
                requests.post(logout_url, headers=headers)
            except Exception as e:
                self.logger.error(f"Error during logout: {str(e)}")
                
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
