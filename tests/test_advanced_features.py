"""
Test Suite for Advanced Features in MT5 to Match-Trader Trade Copier
"""

import unittest
from unittest.mock import MagicMock
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from trade_analytics import TradeAnalytics
from health_monitor import HealthMonitor


class TestTradeAnalytics(unittest.TestCase):
    """Test Trade Analytics Module"""

    def setUp(self):
        self.analytics = TradeAnalytics()
        
    def test_add_trade(self):
        """Test adding a trade to analytics"""
        trade_data = {'symbol': 'EURUSD', 'profit': 100.50}
        self.analytics.add_trade(trade_data)
        self.assertEqual(len(self.analytics.trades_history), 1)
        
    def test_calculate_win_rate(self):
        """Test win rate calculation"""
        self.analytics.trades_history = [
            {'profit': 100.50},
            {'profit': -50.00},
            {'profit': 75.00}
        ]
        win_rate = self.analytics.calculate_win_rate()
        self.assertAlmostEqual(win_rate, 66.67, places=2)
        
    def test_performance_summary(self):
        """Test performance summary output"""
        self.analytics.trades_history = [
            {'profit': 100.50},
            {'profit': -50.00},
            {'profit': 75.00},
            {'profit': -20.00}
        ]
        summary = self.analytics.get_performance_summary()
        self.assertEqual(summary['total_trades'], 4)
        self.assertAlmostEqual(summary['win_rate'], 50.0, places=1)


class TestHealthMonitor(unittest.TestCase):
    """Test Health Monitoring System"""

    def setUp(self):
        self.monitor = HealthMonitor()

    def test_get_system_metrics(self):
        """Test system metrics retrieval"""
        metrics = self.monitor.get_system_metrics()
        self.assertIn('cpu_percent', metrics)
        self.assertIn('memory_percent', metrics)
        
    def test_health_status(self):
        """Test health status check"""
        status = self.monitor.check_health_status()
        self.assertIn('status', status)
        self.assertIn('metrics', status)


def run_advanced_tests():
    """Run tests for advanced features"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_advanced_tests()
