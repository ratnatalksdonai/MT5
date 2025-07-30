"""
Match-Trader WebSocket Client Module for WebSocket communication.

- Manages persistent and secure WebSocket connections.
- Sends and receives trade data in real-time.
"""

import websocket
import threading
import json
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime


class MatchTraderClient:
    """WebSocket client for Match-Trader API"""

    def __init__(self, account_id: str, broker_id: str, base_url: str, api_key: str, secret: str):
        self.account_id = account_id
        self.broker_id = broker_id
        self.base_url = base_url
        self.api_key = api_key
        self.secret = secret
        self.ws = None
        self.connected = False
        self.logger = logging.getLogger(__name__)

    def _on_message(self, message):
        self.logger.info(f"Received message: {message}")
        # Parse and handle the message

    def _on_error(self, error):
        self.logger.error(f"WebSocket error: {error}")

    def _on_close(self):
        self.logger.info("WebSocket connection closed")
        self.connected = False

    def _on_open(self):
        self.logger.info("WebSocket connection opened")
        self.connected = True

    def connect(self):
        self.ws = websocket.WebSocketApp(
            self.base_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self.ws.on_open = self._on_open
        self.ws.run_forever()

    def send_trade(self, trade_data: Dict[str, Any]):
        """Send trade data to Match-Trader API"""
        if not self.connected:
            self.logger.error("Can't send trade, WebSocket is not connected")
            return
        message = json.dumps(trade_data)
        self.ws.send(message)
        self.logger.info(f"Sent trade: {message}")

    def start(self):
        """Start WebSocket connection in a separate thread"""
        connection_thread = threading.Thread(target=self.connect)
        connection_thread.start()

    def close(self):
        if self.ws:
            self.ws.close()
            self.connected = False
            self.logger.info("WebSocket connection closed manually")
