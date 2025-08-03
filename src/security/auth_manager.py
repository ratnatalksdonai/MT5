"""
Authentication and Session Manager
Handles user authentication, MFA, and secure session management
"""

import os
import jwt
import pyotp
import qrcode
import hashlib
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
import bcrypt
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class AuthManager:
    """Manages authentication, MFA, and secure sessions"""
    
    def __init__(self, data_dir: str = "data/auth"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True, parents=True)
        self.users_file = self.data_dir / "users.json"
        self.sessions_file = self.data_dir / "sessions.json"
        self.jwt_secret = os.environ.get('JWT_SECRET', secrets.token_urlsafe(32))
        self._load_data()
        
    def _load_data(self) -> None:
        """Load users and sessions from files"""
        # Load users
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        else:
            self.users = {}
            
        # Load sessions
        if self.sessions_file.exists():
            with open(self.sessions_file, 'r') as f:
                self.sessions = json.load(f)
        else:
            self.sessions = {}
            
    def _save_data(self) -> None:
        """Save users and sessions to files"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
            
        with open(self.sessions_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def create_user(self, username: str, password: str, email: str, 
                   enable_mfa: bool = True) -> Dict[str, any]:
        """Create a new user with secure password storage"""
        if username in self.users:
            raise ValueError(f"User {username} already exists")
        
        # Validate password strength
        if not self._validate_password_strength(password):
            raise ValueError("Password does not meet security requirements")
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Generate MFA secret if enabled
        mfa_secret = None
        if enable_mfa:
            mfa_secret = pyotp.random_base32()
        
        # Create user record
        user = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'mfa_enabled': enable_mfa,
            'mfa_secret': mfa_secret,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'last_login': None,
            'failed_attempts': 0,
            'locked_until': None,
            'permissions': ['trade_copy', 'view_positions']  # Default permissions
        }
        
        self.users[username] = user
        self._save_data()
        
        logger.info(f"User {username} created successfully")
        return {'username': username, 'mfa_enabled': enable_mfa}
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password meets security requirements"""
        if len(password) < 12:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        return all([has_upper, has_lower, has_digit, has_special])
    
    def authenticate(self, username: str, password: str, mfa_code: Optional[str] = None) -> Optional[str]:
        """Authenticate user and return session token"""
        if username not in self.users:
            logger.warning(f"Authentication failed: User {username} not found")
            return None
        
        user = self.users[username]
        
        # Check if account is locked
        if user.get('locked_until'):
            locked_until = datetime.fromisoformat(user['locked_until'])
            if datetime.now(timezone.utc) < locked_until:
                logger.warning(f"Authentication failed: Account {username} is locked")
                return None
            else:
                # Unlock account
                user['locked_until'] = None
                user['failed_attempts'] = 0
        
        # Verify password
        if not self.verify_password(password, user['password_hash']):
            user['failed_attempts'] = user.get('failed_attempts', 0) + 1
            
            # Lock account after 5 failed attempts
            if user['failed_attempts'] >= 5:
                user['locked_until'] = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
                logger.warning(f"Account {username} locked due to multiple failed attempts")
            
            self._save_data()
            logger.warning(f"Authentication failed: Invalid password for {username}")
            return None
        
        # Verify MFA if enabled
        if user.get('mfa_enabled') and user.get('mfa_secret'):
            if not mfa_code:
                logger.warning(f"Authentication failed: MFA code required for {username}")
                return None
                
            totp = pyotp.TOTP(user['mfa_secret'])
            if not totp.verify(mfa_code, valid_window=1):
                logger.warning(f"Authentication failed: Invalid MFA code for {username}")
                return None
        
        # Reset failed attempts
        user['failed_attempts'] = 0
        user['last_login'] = datetime.now(timezone.utc).isoformat()
        
        # Create session token
        session_token = self.create_session(username)
        
        self._save_data()
        logger.info(f"User {username} authenticated successfully")
        return session_token
    
    def create_session(self, username: str) -> str:
        """Create a secure session token"""
        # Generate session ID
        session_id = secrets.token_urlsafe(32)
        
        # Create JWT token
        payload = {
            'session_id': session_id,
            'username': username,
            'permissions': self.users[username].get('permissions', []),
            'exp': datetime.now(timezone.utc) + timedelta(hours=8),  # 8 hour expiry
            'iat': datetime.now(timezone.utc)
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        
        # Store session
        self.sessions[session_id] = {
            'username': username,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'last_activity': datetime.now(timezone.utc).isoformat(),
            'ip_address': None,  # Would be set from request
            'user_agent': None   # Would be set from request
        }
        
        self._save_data()
        return token
    
    def verify_session(self, token: str) -> Optional[Dict[str, any]]:
        """Verify and decode session token"""
        try:
            # Decode JWT
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            session_id = payload.get('session_id')
            if session_id not in self.sessions:
                logger.warning("Session not found")
                return None
            
            # Update last activity
            self.sessions[session_id]['last_activity'] = datetime.now(timezone.utc).isoformat()
            self._save_data()
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Session token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid session token: {e}")
            return None
    
    def revoke_session(self, token: str) -> bool:
        """Revoke a session token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            session_id = payload.get('session_id')
            
            if session_id in self.sessions:
                del self.sessions[session_id]
                self._save_data()
                logger.info(f"Session {session_id} revoked")
                return True
                
        except Exception as e:
            logger.error(f"Error revoking session: {e}")
            
        return False
    
    def generate_mfa_qr_code(self, username: str) -> Optional[str]:
        """Generate QR code for MFA setup"""
        if username not in self.users:
            return None
            
        user = self.users[username]
        if not user.get('mfa_secret'):
            return None
        
        # Generate provisioning URI
        totp = pyotp.TOTP(user['mfa_secret'])
        provisioning_uri = totp.provisioning_uri(
            name=user['email'],
            issuer_name='MT5-MatchTrader'
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Save QR code
        qr_path = self.data_dir / f"mfa_qr_{username}.png"
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(qr_path)
        
        return str(qr_path)
    
    def check_permission(self, username: str, permission: str) -> bool:
        """Check if user has specific permission"""
        if username not in self.users:
            return False
            
        user_permissions = self.users[username].get('permissions', [])
        return permission in user_permissions or 'admin' in user_permissions
    
    def update_user_permissions(self, username: str, permissions: list) -> bool:
        """Update user permissions"""
        if username not in self.users:
            return False
            
        self.users[username]['permissions'] = permissions
        self._save_data()
        logger.info(f"Updated permissions for user {username}")
        return True
