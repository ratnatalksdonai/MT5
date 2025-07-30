"""
Retry Manager Module

Implements retry logic with exponential backoff and circuit breaker pattern.
- Exponential backoff for failed operations
- Circuit breaker to prevent cascading failures
- Configurable retry strategies
"""

import logging
import time
import functools
from typing import Callable, Any, Optional, Dict, Tuple
from datetime import datetime, timedelta
from enum import Enum
import random


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject all calls
    HALF_OPEN = "half_open"  # Testing if service recovered


class RetryManager:
    """Manages retry logic with exponential backoff and circuit breaker"""
    
    def __init__(self, 
                 max_attempts: int = 5,
                 initial_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True,
                 circuit_failure_threshold: int = 5,
                 circuit_recovery_timeout: int = 60):
        """
        Initialize Retry Manager
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            exponential_base: Base for exponential backoff calculation
            jitter: Add random jitter to prevent thundering herd
            circuit_failure_threshold: Failures before circuit opens
            circuit_recovery_timeout: Seconds before circuit attempts recovery
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.circuit_failure_threshold = circuit_failure_threshold
        self.circuit_recovery_timeout = circuit_recovery_timeout
        
        self.logger = logging.getLogger(__name__)
        
        # Circuit breaker state tracking
        self.circuit_states: Dict[str, Tuple[CircuitState, datetime, int]] = {}
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for next retry attempt
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds before next retry
        """
        # Exponential backoff
        delay = min(self.initial_delay * (self.exponential_base ** attempt), self.max_delay)
        
        # Add jitter if enabled (±25% of delay)
        if self.jitter:
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)  # Ensure non-negative
    
    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result if successful
            
        Raises:
            Last exception if all retries failed
        """
        func_name = func.__name__
        
        # Check circuit breaker state
        if self._is_circuit_open(func_name):
            raise Exception(f"Circuit breaker is OPEN for {func_name}")
        
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                self.logger.debug(f"Attempting {func_name} (attempt {attempt + 1}/{self.max_attempts})")
                
                result = func(*args, **kwargs)
                
                # Success - reset circuit breaker
                self._on_success(func_name)
                
                if attempt > 0:
                    self.logger.info(f"{func_name} succeeded after {attempt + 1} attempts")
                
                return result
                
            except Exception as e:
                last_exception = e
                self.logger.warning(f"{func_name} failed (attempt {attempt + 1}/{self.max_attempts}): {str(e)}")
                
                # Record failure for circuit breaker
                self._on_failure(func_name)
                
                # Don't retry if this was the last attempt
                if attempt < self.max_attempts - 1:
                    delay = self.calculate_delay(attempt)
                    self.logger.info(f"Retrying {func_name} in {delay:.2f} seconds...")
                    time.sleep(delay)
        
        # All retries failed
        self.logger.error(f"{func_name} failed after {self.max_attempts} attempts")
        raise last_exception
    
    def retry_decorator(self, max_attempts: Optional[int] = None):
        """
        Decorator for adding retry logic to functions
        
        Args:
            max_attempts: Override default max attempts for this function
            
        Returns:
            Decorated function with retry logic
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Create a new instance with custom max_attempts if provided
                if max_attempts is not None:
                    retry_manager = RetryManager(
                        max_attempts=max_attempts,
                        initial_delay=self.initial_delay,
                        max_delay=self.max_delay,
                        exponential_base=self.exponential_base,
                        jitter=self.jitter,
                        circuit_failure_threshold=self.circuit_failure_threshold,
                        circuit_recovery_timeout=self.circuit_recovery_timeout
                    )
                    return retry_manager.retry_with_backoff(func, *args, **kwargs)
                else:
                    return self.retry_with_backoff(func, *args, **kwargs)
            
            return wrapper
        return decorator
    
    def _is_circuit_open(self, func_name: str) -> bool:
        """
        Check if circuit breaker is open for a function
        
        Args:
            func_name: Name of the function
            
        Returns:
            True if circuit is open, False otherwise
        """
        if func_name not in self.circuit_states:
            return False
        
        state, last_failure_time, failure_count = self.circuit_states[func_name]
        
        if state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if datetime.now() - last_failure_time > timedelta(seconds=self.circuit_recovery_timeout):
                # Move to half-open state
                self.circuit_states[func_name] = (CircuitState.HALF_OPEN, last_failure_time, failure_count)
                self.logger.info(f"Circuit breaker for {func_name} moved to HALF_OPEN state")
                return False
            else:
                return True
        
        return False
    
    def _on_success(self, func_name: str):
        """
        Handle successful execution for circuit breaker
        
        Args:
            func_name: Name of the function
        """
        if func_name in self.circuit_states:
            state, _, _ = self.circuit_states[func_name]
            if state == CircuitState.HALF_OPEN:
                # Recovery successful, close circuit
                del self.circuit_states[func_name]
                self.logger.info(f"Circuit breaker for {func_name} CLOSED (recovered)")
    
    def _on_failure(self, func_name: str):
        """
        Handle failed execution for circuit breaker
        
        Args:
            func_name: Name of the function
        """
        if func_name not in self.circuit_states:
            # First failure
            self.circuit_states[func_name] = (CircuitState.CLOSED, datetime.now(), 1)
        else:
            state, last_failure_time, failure_count = self.circuit_states[func_name]
            
            if state == CircuitState.HALF_OPEN:
                # Recovery failed, reopen circuit
                self.circuit_states[func_name] = (CircuitState.OPEN, datetime.now(), failure_count + 1)
                self.logger.warning(f"Circuit breaker for {func_name} REOPENED")
            else:
                # Increment failure count
                new_count = failure_count + 1
                self.circuit_states[func_name] = (state, datetime.now(), new_count)
                
                # Check if threshold reached
                if new_count >= self.circuit_failure_threshold and state == CircuitState.CLOSED:
                    self.circuit_states[func_name] = (CircuitState.OPEN, datetime.now(), new_count)
                    self.logger.warning(f"Circuit breaker for {func_name} OPENED after {new_count} failures")
    
    def get_circuit_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get current status of all circuit breakers
        
        Returns:
            Dictionary with circuit breaker status for each function
        """
        status = {}
        for func_name, (state, last_failure_time, failure_count) in self.circuit_states.items():
            status[func_name] = {
                "state": state.value,
                "failure_count": failure_count,
                "last_failure": last_failure_time.isoformat(),
                "time_since_failure": (datetime.now() - last_failure_time).total_seconds()
            }
        return status
    
    def reset_circuit(self, func_name: str):
        """
        Manually reset circuit breaker for a function
        
        Args:
            func_name: Name of the function
        """
        if func_name in self.circuit_states:
            del self.circuit_states[func_name]
            self.logger.info(f"Circuit breaker for {func_name} manually reset")
    
    def reset_all_circuits(self):
        """Reset all circuit breakers"""
        self.circuit_states.clear()
        self.logger.info("All circuit breakers reset")
