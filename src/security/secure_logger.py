"""
Secure Logging Module
Handles logging with automatic sensitive data masking and secure log storage
"""

import os
import re
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Pattern
import hashlib
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class SensitiveDataFilter(logging.Filter):
    """Filter to mask sensitive data in log messages"""
    
    # Patterns for sensitive data
    SENSITIVE_PATTERNS: List[Pattern] = [
        # API Keys and tokens
        re.compile(r'(api[_-]?key|token|bearer|authorization)[\s:=]+[\'\"]?([^\s\'\"]+)[\'\"]?', re.IGNORECASE),
        
        # Passwords
        re.compile(r'(password|passwd|pwd)[\s:=]+[\'\"]?([^\s\'\"]+)[\'\"]?', re.IGNORECASE),
        
        # Credit card numbers
        re.compile(r'\b(?:\d{4}[\s-]?){3}\d{4}\b'),
        
        # Email addresses (partial masking)
        re.compile(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'),
        
        # IP addresses (partial masking)
        re.compile(r'\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b'),
        
        # Account numbers
        re.compile(r'(account|acct)[\s:=]+[\'\"]?([0-9]{4,})[\'\"]?', re.IGNORECASE),
        
        # Session IDs
        re.compile(r'(session[_-]?id|sess[_-]?id)[\s:=]+[\'\"]?([^\s\'\"]+)[\'\"]?', re.IGNORECASE),
        
        # MT5 login numbers
        re.compile(r'(login|mt5[_-]?login)[\s:=]+[\'\"]?(\d{5,})[\'\"]?', re.IGNORECASE),
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter and mask sensitive data in log records"""
        # Mask message
        if hasattr(record, 'msg'):
            record.msg = self._mask_sensitive_data(str(record.msg))
        
        # Mask arguments
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, dict):
                record.args = {k: self._mask_sensitive_data(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self._mask_sensitive_data(str(arg)) for arg in record.args)
        
        return True
    
    def _mask_sensitive_data(self, text: str) -> str:
        """Mask sensitive data in text"""
        if not text:
            return text
        
        masked_text = text
        
        # Apply all sensitive patterns
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern.pattern.startswith(r'([a-zA-Z0-9._%+-]+)@'):
                # Email masking
                masked_text = pattern.sub(lambda m: f"{m.group(1)[:3]}***@{m.group(2)}", masked_text)
            elif pattern.pattern.startswith(r'\b(\d{1,3})'):
                # IP address masking
                masked_text = pattern.sub(lambda m: f"{m.group(1)}.{m.group(2)}.XXX.XXX", masked_text)
            elif 'password' in pattern.pattern.lower():
                # Password complete masking
                masked_text = pattern.sub(lambda m: f"{m.group(1)}=********", masked_text)
            elif any(key in pattern.pattern.lower() for key in ['api', 'token', 'bearer']):
                # API key partial masking
                masked_text = pattern.sub(lambda m: f"{m.group(1)}={m.group(2)[:8]}...{m.group(2)[-4:]}" 
                                        if len(m.group(2)) > 12 else f"{m.group(1)}=****", masked_text)
            else:
                # Default masking
                masked_text = pattern.sub(lambda m: re.sub(r'\d', '*', m.group(0)), masked_text)
        
        return masked_text

class SecureLogger:
    """Secure logging configuration and management"""
    
    def __init__(self, 
                 log_dir: str = "logs",
                 log_level: str = "INFO",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 10,
                 enable_encryption: bool = False):
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True, parents=True)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_encryption = enable_encryption
        
        # Separate log files for different purposes
        self.log_files = {
            'main': self.log_dir / 'mt5_copier.log',
            'security': self.log_dir / 'security.log',
            'trading': self.log_dir / 'trading.log',
            'error': self.log_dir / 'error.log',
            'audit': self.log_dir / 'audit.log'
        }
        
        self._setup_loggers()
    
    def _setup_loggers(self):
        """Setup different loggers with appropriate handlers"""
        # Main logger
        self._setup_logger(
            'main',
            self.log_files['main'],
            self.log_level,
            include_console=True
        )
        
        # Security logger - for authentication, authorization events
        self._setup_logger(
            'security',
            self.log_files['security'],
            logging.INFO,
            include_console=False
        )
        
        # Trading logger - for trade operations
        self._setup_logger(
            'trading',
            self.log_files['trading'],
            logging.INFO,
            include_console=False
        )
        
        # Error logger - for errors only
        self._setup_logger(
            'error',
            self.log_files['error'],
            logging.ERROR,
            include_console=True
        )
        
        # Audit logger - for compliance and audit trail
        self._setup_logger(
            'audit',
            self.log_files['audit'],
            logging.INFO,
            include_console=False,
            use_json=True
        )
    
    def _setup_logger(self, 
                     name: str, 
                     log_file: Path,
                     level: int,
                     include_console: bool = False,
                     use_json: bool = False):
        """Setup individual logger"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.handlers.clear()
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        
        # Format
        if use_json:
            formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(formatter)
        
        # Add sensitive data filter
        file_handler.addFilter(SensitiveDataFilter())
        
        logger.addHandler(file_handler)
        
        # Console handler
        if include_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            console_handler.addFilter(SensitiveDataFilter())
            logger.addHandler(console_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance"""
        return logging.getLogger(name)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], 
                          user: str = None, ip: str = None):
        """Log security-related events"""
        security_logger = self.get_logger('security')
        audit_logger = self.get_logger('audit')
        
        event_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user': user,
            'ip_address': ip,
            'details': details
        }
        
        # Log to security log
        security_logger.info(f"Security Event: {event_type} - User: {user} - IP: {ip}")
        
        # Log to audit trail
        audit_logger.info(json.dumps(event_data))
    
    def log_trading_event(self, event_type: str, trade_data: Dict[str, Any]):
        """Log trading-related events"""
        trading_logger = self.get_logger('trading')
        audit_logger = self.get_logger('audit')
        
        # Mask sensitive trading data
        safe_trade_data = self._mask_trading_data(trade_data)
        
        event_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'trade_data': safe_trade_data
        }
        
        trading_logger.info(f"Trading Event: {event_type} - {safe_trade_data}")
        audit_logger.info(json.dumps(event_data))
    
    def _mask_trading_data(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive trading information"""
        masked_data = trade_data.copy()
        
        # Mask account numbers (show last 4 digits)
        if 'account' in masked_data:
            account = str(masked_data['account'])
            if len(account) > 4:
                masked_data['account'] = '*' * (len(account) - 4) + account[-4:]
        
        # Don't mask symbols, volumes, or trade types - these are needed for debugging
        # But remove any API keys or tokens if present
        sensitive_keys = ['api_key', 'token', 'password', 'secret']
        for key in sensitive_keys:
            if key in masked_data:
                masked_data[key] = '***MASKED***'
        
        return masked_data
    
    def rotate_logs(self):
        """Manually rotate all log files"""
        for logger_name in ['main', 'security', 'trading', 'error', 'audit']:
            logger = self.get_logger(logger_name)
            for handler in logger.handlers:
                if isinstance(handler, RotatingFileHandler):
                    handler.doRollover()
    
    def cleanup_old_logs(self, days: int = 30):
        """Remove log files older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for log_file in self.log_dir.glob('*.log*'):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                try:
                    log_file.unlink()
                    logging.info(f"Removed old log file: {log_file}")
                except Exception as e:
                    logging.error(f"Failed to remove log file {log_file}: {e}")

class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'thread': record.thread,
            'thread_name': record.threadName,
            'process': record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'pathname', 'process', 'processName', 'relativeCreated',
                          'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info']:
                log_data[key] = value
        
        return json.dumps(log_data)
