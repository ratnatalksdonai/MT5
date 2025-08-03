"""
Input Validation and Sanitization Module
Protects against injection attacks and validates all user inputs
"""

import re
import logging
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

class InputValidator:
    """Validates and sanitizes all inputs to prevent security vulnerabilities"""
    
    # Regular expressions for validation
    SYMBOL_PATTERN = re.compile(r'^[A-Z]{3,10}$')  # Trading symbols
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    NUMERIC_PATTERN = re.compile(r'^[0-9]+(\.[0-9]+)?$')
    SERVER_PATTERN = re.compile(r'^[a-zA-Z0-9.-]+$')
    
    # SQL injection patterns to detect
    SQL_INJECTION_PATTERNS = [
        r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
        r"(--|#|\/\*|\*\/)",
        r"(\bor\b\s*\d+\s*=\s*\d+)",
        r"(\band\b\s*\d+\s*=\s*\d+)",
        r"(;|\||&&)"
    ]
    
    # XSS patterns to detect
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed"
    ]
    
    @classmethod
    def validate_trading_symbol(cls, symbol: str) -> Optional[str]:
        """Validate and sanitize trading symbol"""
        if not symbol:
            return None
            
        # Convert to uppercase
        symbol = symbol.upper().strip()
        
        # Check pattern
        if not cls.SYMBOL_PATTERN.match(symbol):
            logger.warning(f"Invalid trading symbol format: {symbol}")
            return None
            
        # Check against allowed symbols (configurable)
        allowed_symbols = [
            'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF',
            'XAUUSD', 'XAGUSD', 'US30', 'US500', 'USTEC', 'UK100', 'GER40',
            'BTCUSD', 'ETHUSD'
        ]
        
        if symbol not in allowed_symbols:
            logger.warning(f"Symbol not in allowed list: {symbol}")
            return None
            
        return symbol
    
    @classmethod
    def validate_volume(cls, volume: Union[str, float, Decimal], 
                       min_volume: float = 0.01, 
                       max_volume: float = 100.0) -> Optional[Decimal]:
        """Validate trading volume"""
        try:
            # Convert to Decimal for precision
            volume_decimal = Decimal(str(volume))
            
            # Check range
            if volume_decimal < Decimal(str(min_volume)):
                logger.warning(f"Volume too small: {volume}")
                return None
                
            if volume_decimal > Decimal(str(max_volume)):
                logger.warning(f"Volume too large: {volume}")
                return None
                
            # Round to standard lot precision (2 decimal places)
            return volume_decimal.quantize(Decimal('0.01'))
            
        except (InvalidOperation, ValueError) as e:
            logger.error(f"Invalid volume format: {volume} - {e}")
            return None
    
    @classmethod
    def validate_price(cls, price: Union[str, float, Decimal], 
                      min_price: float = 0.00001,
                      max_price: float = 999999.99999) -> Optional[Decimal]:
        """Validate price value"""
        try:
            price_decimal = Decimal(str(price))
            
            if price_decimal <= 0:
                logger.warning(f"Price must be positive: {price}")
                return None
                
            if price_decimal < Decimal(str(min_price)):
                logger.warning(f"Price too small: {price}")
                return None
                
            if price_decimal > Decimal(str(max_price)):
                logger.warning(f"Price too large: {price}")
                return None
                
            return price_decimal
            
        except (InvalidOperation, ValueError) as e:
            logger.error(f"Invalid price format: {price} - {e}")
            return None
    
    @classmethod
    def validate_email(cls, email: str) -> Optional[str]:
        """Validate email address"""
        if not email:
            return None
            
        email = email.strip().lower()
        
        if not cls.EMAIL_PATTERN.match(email):
            logger.warning(f"Invalid email format: {email}")
            return None
            
        # Check for SQL injection attempts
        if cls._contains_sql_injection(email):
            logger.error(f"Potential SQL injection in email: {email}")
            return None
            
        return email
    
    @classmethod
    def validate_username(cls, username: str, min_length: int = 3, max_length: int = 50) -> Optional[str]:
        """Validate username"""
        if not username:
            return None
            
        username = username.strip()
        
        # Check length
        if len(username) < min_length or len(username) > max_length:
            logger.warning(f"Username length invalid: {len(username)}")
            return None
            
        # Check pattern
        if not cls.ALPHANUMERIC_PATTERN.match(username):
            logger.warning(f"Username contains invalid characters: {username}")
            return None
            
        # Check for injection attempts
        if cls._contains_injection(username):
            logger.error(f"Potential injection in username: {username}")
            return None
            
        return username
    
    @classmethod
    def validate_server_name(cls, server: str) -> Optional[str]:
        """Validate MT5 server name"""
        if not server:
            return None
            
        server = server.strip()
        
        # Check pattern
        if not cls.SERVER_PATTERN.match(server):
            logger.warning(f"Invalid server name format: {server}")
            return None
            
        # Check for injection attempts
        if cls._contains_injection(server):
            logger.error(f"Potential injection in server name: {server}")
            return None
            
        return server
    
    @classmethod
    def validate_order_type(cls, order_type: str) -> Optional[str]:
        """Validate order type"""
        allowed_types = ['BUY', 'SELL', 'BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP']
        
        if not order_type:
            return None
            
        order_type = order_type.upper().strip()
        
        if order_type not in allowed_types:
            logger.warning(f"Invalid order type: {order_type}")
            return None
            
        return order_type
    
    @classmethod
    def validate_broker_name(cls, broker: str) -> Optional[str]:
        """Validate broker name"""
        allowed_brokers = [
            'e8markets', 'ftmo', 'toponetrader', 'citytradersimperium',
            'fundednext', 'trueforexfunds', 'thefundedtrader'
        ]
        
        if not broker:
            return None
            
        broker = broker.lower().strip()
        
        if broker not in allowed_brokers:
            logger.warning(f"Unknown broker: {broker}")
            return None
            
        return broker
    
    @classmethod
    def sanitize_string(cls, text: str, max_length: int = 1000) -> str:
        """General string sanitization"""
        if not text:
            return ""
            
        # Truncate to max length
        text = text[:max_length]
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Escape special characters for logging
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        
        return text.strip()
    
    @classmethod
    def validate_api_response(cls, response: Dict[str, Any]) -> bool:
        """Validate API response structure"""
        try:
            # Check for expected fields
            if not isinstance(response, dict):
                logger.error("API response is not a dictionary")
                return False
                
            # Recursively validate nested structures
            return cls._validate_nested_structure(response)
            
        except Exception as e:
            logger.error(f"Error validating API response: {e}")
            return False
    
    @classmethod
    def _contains_sql_injection(cls, text: str) -> bool:
        """Check for SQL injection patterns"""
        text_lower = text.lower()
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
                
        return False
    
    @classmethod
    def _contains_xss(cls, text: str) -> bool:
        """Check for XSS patterns"""
        text_lower = text.lower()
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
                
        return False
    
    @classmethod
    def _contains_injection(cls, text: str) -> bool:
        """Check for any injection attempts"""
        return cls._contains_sql_injection(text) or cls._contains_xss(text)
    
    @classmethod
    def _validate_nested_structure(cls, obj: Any, depth: int = 0, max_depth: int = 10) -> bool:
        """Recursively validate nested data structures"""
        if depth > max_depth:
            logger.warning("Maximum nesting depth exceeded")
            return False
            
        if isinstance(obj, dict):
            for key, value in obj.items():
                if not isinstance(key, str):
                    logger.warning(f"Non-string key found: {type(key)}")
                    return False
                    
                if cls._contains_injection(key):
                    logger.error(f"Potential injection in key: {key}")
                    return False
                    
                if not cls._validate_nested_structure(value, depth + 1, max_depth):
                    return False
                    
        elif isinstance(obj, list):
            for item in obj:
                if not cls._validate_nested_structure(item, depth + 1, max_depth):
                    return False
                    
        elif isinstance(obj, str):
            # Check string values for injection
            if len(obj) > 10000:  # Prevent extremely long strings
                logger.warning("String value too long")
                return False
                
        return True
    
    @classmethod
    def create_safe_error_message(cls, error: Exception, include_type: bool = True) -> str:
        """Create safe error message without exposing sensitive information"""
        error_type = type(error).__name__ if include_type else "Error"
        
        # Define safe error messages
        safe_messages = {
            'FileNotFoundError': 'Configuration file not found',
            'PermissionError': 'Permission denied',
            'ConnectionError': 'Connection failed',
            'TimeoutError': 'Operation timed out',
            'ValueError': 'Invalid input provided',
            'KeyError': 'Required configuration missing',
            'AuthenticationError': 'Authentication failed',
            'APIError': 'API request failed'
        }
        
        # Return safe message
        return safe_messages.get(error_type, 'An error occurred. Please check logs.')
