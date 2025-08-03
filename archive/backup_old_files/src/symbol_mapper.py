"""
Symbol Mapper Module

Handles symbol conversions between MT5 and Match-Trader platforms.
- Automatic suffix removal (.z, .a, etc.)
- Custom symbol mapping
- Symbol validation
"""

import logging
from typing import Dict, Optional, Set
import re


class SymbolMapper:
    """Handles symbol mapping and conversion between platforms"""
    
    def __init__(self, symbol_mapping: Dict[str, str], allowed_symbols: Optional[Set[str]] = None):
        """
        Initialize Symbol Mapper
        
        Args:
            symbol_mapping: Dictionary mapping source symbols to destination symbols
            allowed_symbols: Set of allowed symbols for trading (None allows all)
        """
        self.symbol_mapping = symbol_mapping
        self.allowed_symbols = allowed_symbols
        self.logger = logging.getLogger(__name__)
        
        # Common MT5 suffixes to remove
        self.suffix_pattern = re.compile(r'\.(z|a|m|pro|ecn|raw)$', re.IGNORECASE)
        
        # Symbol validation pattern (alphanumeric with possible dots/dashes)
        self.symbol_pattern = re.compile(r'^[A-Z0-9\.\-]+$', re.IGNORECASE)
        
        self.logger.info(f"Symbol mapper initialized with {len(symbol_mapping)} custom mappings")
        if allowed_symbols:
            self.logger.info(f"Symbol filter enabled with {len(allowed_symbols)} allowed symbols")
    
    def map_symbol(self, mt5_symbol: str) -> Optional[str]:
        """
        Map MT5 symbol to Match-Trader symbol
        
        Args:
            mt5_symbol: Symbol from MT5 platform
            
        Returns:
            Mapped symbol for Match-Trader or None if not allowed
        """
        if not mt5_symbol:
            return None
            
        # First check if there's a direct mapping
        if mt5_symbol in self.symbol_mapping:
            mapped = self.symbol_mapping[mt5_symbol]
            self.logger.debug(f"Direct mapping: {mt5_symbol} -> {mapped}")
            return self._validate_symbol(mapped)
        
        # Remove common suffixes
        cleaned_symbol = self.suffix_pattern.sub('', mt5_symbol)
        
        # Check if cleaned symbol has a mapping
        if cleaned_symbol in self.symbol_mapping:
            mapped = self.symbol_mapping[cleaned_symbol]
            self.logger.debug(f"Mapped after cleaning: {mt5_symbol} -> {mapped}")
            return self._validate_symbol(mapped)
        
        # If no mapping found, use cleaned symbol
        self.logger.debug(f"No mapping found, using cleaned: {mt5_symbol} -> {cleaned_symbol}")
        return self._validate_symbol(cleaned_symbol)
    
    def _validate_symbol(self, symbol: str) -> Optional[str]:
        """
        Validate symbol against allowed list and format
        
        Args:
            symbol: Symbol to validate
            
        Returns:
            Symbol if valid and allowed, None otherwise
        """
        # Check symbol format
        if not self.symbol_pattern.match(symbol):
            self.logger.warning(f"Invalid symbol format: {symbol}")
            return None
        
        # Check if symbol is in allowed list
        if self.allowed_symbols and symbol not in self.allowed_symbols:
            self.logger.warning(f"Symbol not in allowed list: {symbol}")
            return None
        
        return symbol
    
    def reverse_map_symbol(self, match_trader_symbol: str) -> Optional[str]:
        """
        Reverse map Match-Trader symbol to MT5 symbol
        
        Args:
            match_trader_symbol: Symbol from Match-Trader platform
            
        Returns:
            Original MT5 symbol or None if not found
        """
        # Search for the original symbol in mapping
        for mt5_symbol, mapped_symbol in self.symbol_mapping.items():
            if mapped_symbol == match_trader_symbol:
                return mt5_symbol
        
        # If not found in mapping, return as is (might need suffix added manually)
        return match_trader_symbol
    
    def add_mapping(self, mt5_symbol: str, match_trader_symbol: str):
        """
        Add or update a symbol mapping
        
        Args:
            mt5_symbol: MT5 symbol
            match_trader_symbol: Corresponding Match-Trader symbol
        """
        self.symbol_mapping[mt5_symbol] = match_trader_symbol
        self.logger.info(f"Added symbol mapping: {mt5_symbol} -> {match_trader_symbol}")
    
    def remove_mapping(self, mt5_symbol: str):
        """
        Remove a symbol mapping
        
        Args:
            mt5_symbol: MT5 symbol to remove from mapping
        """
        if mt5_symbol in self.symbol_mapping:
            del self.symbol_mapping[mt5_symbol]
            self.logger.info(f"Removed symbol mapping for: {mt5_symbol}")
    
    def update_allowed_symbols(self, allowed_symbols: Set[str]):
        """
        Update the list of allowed symbols
        
        Args:
            allowed_symbols: New set of allowed symbols
        """
        self.allowed_symbols = allowed_symbols
        self.logger.info(f"Updated allowed symbols list with {len(allowed_symbols)} symbols")
    
    def is_symbol_allowed(self, symbol: str) -> bool:
        """
        Check if a symbol is allowed for trading
        
        Args:
            symbol: Symbol to check
            
        Returns:
            True if allowed, False otherwise
        """
        if not self.allowed_symbols:
            return True  # No restrictions
        
        # Check both original and mapped symbol
        mapped = self.map_symbol(symbol)
        return mapped is not None
    
    def get_all_mappings(self) -> Dict[str, str]:
        """
        Get all current symbol mappings
        
        Returns:
            Dictionary of all symbol mappings
        """
        return self.symbol_mapping.copy()
    
    def get_allowed_symbols(self) -> Optional[Set[str]]:
        """
        Get set of allowed symbols
        
        Returns:
            Set of allowed symbols or None if no restrictions
        """
        return self.allowed_symbols.copy() if self.allowed_symbols else None
