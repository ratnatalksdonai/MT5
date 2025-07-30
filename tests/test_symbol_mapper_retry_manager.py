"""
Test Suite for SymbolMapper and RetryManager modules
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import time
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from symbol_mapper import SymbolMapper
from retry_manager import RetryManager, CircuitState


class TestSymbolMapper(unittest.TestCase):
    """Test Symbol Mapper Module"""
    
    def setUp(self):
        """Set up test data"""
        self.symbol_mapping = {
            "EURUSD.z": "EURUSD",
            "GBPUSD.z": "GBPUSD",
            "XAUUSD": "GOLD"
        }
        self.allowed_symbols = {"EURUSD", "GBPUSD", "GOLD", "USDJPY"}
        self.mapper = SymbolMapper(self.symbol_mapping, self.allowed_symbols)
    
    def test_direct_mapping(self):
        """Test direct symbol mapping"""
        # Test existing mapping
        mapped = self.mapper.map_symbol("EURUSD.z")
        self.assertEqual(mapped, "EURUSD")
        
        # Test custom mapping
        mapped = self.mapper.map_symbol("XAUUSD")
        self.assertEqual(mapped, "GOLD")
    
    def test_suffix_removal(self):
        """Test automatic suffix removal"""
        # Test .z suffix removal
        mapped = self.mapper.map_symbol("USDJPY.z")
        self.assertEqual(mapped, "USDJPY")
        
        # Test other suffixes
        test_suffixes = [".a", ".m", ".pro", ".ecn", ".raw"]
        for suffix in test_suffixes:
            with self.subTest(suffix=suffix):
                mapped = self.mapper.map_symbol(f"EURUSD{suffix}")
                self.assertEqual(mapped, "EURUSD")
    
    def test_allowed_symbols_filter(self):
        """Test allowed symbols filtering"""
        # Test allowed symbol
        mapped = self.mapper.map_symbol("USDJPY.z")
        self.assertIsNotNone(mapped)
        
        # Test not allowed symbol
        mapped = self.mapper.map_symbol("EURAUD.z")
        self.assertIsNone(mapped)
    
    def test_reverse_mapping(self):
        """Test reverse symbol mapping"""
        # Test existing reverse mapping
        original = self.mapper.reverse_map_symbol("EURUSD")
        self.assertEqual(original, "EURUSD.z")
        
        # Test custom reverse mapping
        original = self.mapper.reverse_map_symbol("GOLD")
        self.assertEqual(original, "XAUUSD")
        
        # Test non-existing mapping
        original = self.mapper.reverse_map_symbol("USDJPY")
        self.assertEqual(original, "USDJPY")
    
    def test_add_remove_mapping(self):
        """Test adding and removing mappings"""
        # First update allowed symbols to include EURJPY
        new_allowed = self.allowed_symbols.copy()
        new_allowed.add("EURJPY")
        self.mapper.update_allowed_symbols(new_allowed)
        
        # Add new mapping
        self.mapper.add_mapping("EURJPY.z", "EURJPY")
        mapped = self.mapper.map_symbol("EURJPY.z")
        self.assertEqual(mapped, "EURJPY")
        
        # Remove mapping
        self.mapper.remove_mapping("EURJPY.z")
        mapped = self.mapper.map_symbol("EURJPY.z")
        self.assertEqual(mapped, "EURJPY")  # Should use suffix removal now
    
    def test_invalid_symbol_format(self):
        """Test invalid symbol formats"""
        invalid_symbols = ["", "123", "EUR USD", "EUR/USD", "@EURUSD"]
        
        for symbol in invalid_symbols:
            with self.subTest(symbol=symbol):
                mapped = self.mapper.map_symbol(symbol)
                self.assertIsNone(mapped)
    
    def test_no_allowed_symbols_restriction(self):
        """Test mapper without allowed symbols restriction"""
        mapper_no_restriction = SymbolMapper(self.symbol_mapping, None)
        
        # Any valid symbol should be allowed
        mapped = mapper_no_restriction.map_symbol("EURAUD.z")
        self.assertEqual(mapped, "EURAUD")


class TestRetryManager(unittest.TestCase):
    """Test Retry Manager Module"""
    
    def setUp(self):
        """Set up test data"""
        self.retry_manager = RetryManager(
            max_attempts=3,
            initial_delay=0.1,
            max_delay=1.0,
            exponential_base=2.0,
            jitter=False,
            circuit_failure_threshold=3,
            circuit_recovery_timeout=1
        )
    
    def test_successful_function_call(self):
        """Test successful function execution"""
        def successful_func():
            return "success"
        
        result = self.retry_manager.retry_with_backoff(successful_func)
        self.assertEqual(result, "success")
    
    def test_retry_on_failure(self):
        """Test retry mechanism on failure"""
        call_count = 0
        
        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = self.retry_manager.retry_with_backoff(failing_func)
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)
    
    def test_all_retries_exhausted(self):
        """Test when all retries are exhausted"""
        def always_failing_func():
            raise Exception("Permanent failure")
        
        with self.assertRaises(Exception) as context:
            self.retry_manager.retry_with_backoff(always_failing_func)
        
        self.assertEqual(str(context.exception), "Permanent failure")
    
    def test_exponential_backoff(self):
        """Test exponential backoff calculation"""
        delays = []
        for attempt in range(5):
            delay = self.retry_manager.calculate_delay(attempt)
            delays.append(delay)
        
        # Check that delays increase exponentially
        self.assertAlmostEqual(delays[0], 0.1, places=2)
        self.assertAlmostEqual(delays[1], 0.2, places=2)
        self.assertAlmostEqual(delays[2], 0.4, places=2)
        self.assertAlmostEqual(delays[3], 0.8, places=2)
        self.assertAlmostEqual(delays[4], 1.0, places=2)  # Max delay
    
    def test_circuit_breaker_opens(self):
        """Test circuit breaker opening after threshold"""
        def always_failing_func():
            raise Exception("Failure")
        
        # Exhaust retries multiple times to trigger circuit breaker
        for _ in range(3):
            try:
                self.retry_manager.retry_with_backoff(always_failing_func)
            except:
                pass
        
        # Check circuit is open
        status = self.retry_manager.get_circuit_status()
        self.assertIn("always_failing_func", status)
        self.assertEqual(status["always_failing_func"]["state"], CircuitState.OPEN.value)
        
        # Subsequent calls should fail immediately
        with self.assertRaises(Exception) as context:
            self.retry_manager.retry_with_backoff(always_failing_func)
        
        self.assertIn("Circuit breaker is OPEN", str(context.exception))
    
    def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery"""
        call_count = 0
        
        def recovering_func():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise Exception("Still failing")
            return "recovered"
        
        # Trigger circuit breaker
        for _ in range(3):
            try:
                self.retry_manager.retry_with_backoff(recovering_func)
            except:
                pass
        
        # Wait for recovery timeout
        time.sleep(1.1)
        
        # Should work now
        result = self.retry_manager.retry_with_backoff(recovering_func)
        self.assertEqual(result, "recovered")
    
    def test_retry_decorator(self):
        """Test retry decorator functionality"""
        call_count = 0
        
        @self.retry_manager.retry_decorator(max_attempts=2)
        def decorated_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return "success"
        
        result = decorated_func()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 2)
    
    def test_jitter_enabled(self):
        """Test jitter functionality"""
        retry_manager_with_jitter = RetryManager(
            initial_delay=1.0,
            jitter=True
        )
        
        # Get multiple delay calculations
        delays = []
        for _ in range(10):
            delay = retry_manager_with_jitter.calculate_delay(0)
            delays.append(delay)
        
        # Check that delays vary due to jitter
        unique_delays = set(delays)
        self.assertGreater(len(unique_delays), 1)
        
        # Check delays are within expected range (±25%)
        for delay in delays:
            self.assertGreaterEqual(delay, 0.75)
            self.assertLessEqual(delay, 1.25)


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
