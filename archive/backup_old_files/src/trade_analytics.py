"""
Trade Analytics Module providing comprehensive statistical analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import logging


class TradeAnalytics:
    """Provides advanced trade analytics and performance metrics."""

    def __init__(self):
        self.trades_history = []
        self.logger = logging.getLogger(__name__)

    def add_trade(self, trade_data: Dict[str, Any]):
        """Add a trade to analytics history."""
        trade_data["timestamp"] = datetime.now().isoformat()
        self.trades_history.append(trade_data)

    def calculate_win_rate(self) -> float:
        """Calculate overall win rate percentage."""
        if not self.trades_history:
            return 0.0

        winning_trades = sum(1 for trade in self.trades_history if trade.get("profit", 0) > 0)
        return (winning_trades / len(self.trades_history)) * 100

    def calculate_profit_factor(self) -> float:
        """Calculate profit factor (gross profit / gross loss)."""
        gross_profit = sum(trade.get("profit", 0) for trade in self.trades_history if trade.get("profit", 0) > 0)
        gross_loss = abs(sum(trade.get("profit", 0) for trade in self.trades_history if trade.get("profit", 0) < 0))

        return gross_profit / gross_loss if gross_loss > 0 else float("inf")

    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio for risk-adjusted returns."""
        if len(self.trades_history) < 2:
            return 0.0

        returns = [trade.get("profit", 0) for trade in self.trades_history]
        mean_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0.0

        return (mean_return - risk_free_rate) / std_return

    def calculate_max_drawdown(self) -> Dict[str, float]:
        """Calculate maximum drawdown metrics."""
        if not self.trades_history:
            return {"max_drawdown": 0.0, "max_drawdown_percentage": 0.0}

        cumulative_profit = 0
        peak = 0
        max_drawdown = 0

        for trade in self.trades_history:
            cumulative_profit += trade.get("profit", 0)
            if cumulative_profit > peak:
                peak = cumulative_profit
            drawdown = peak - cumulative_profit
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        max_drawdown_percentage = (max_drawdown / peak * 100) if peak > 0 else 0

        return {"max_drawdown": max_drawdown, "max_drawdown_percentage": max_drawdown_percentage}

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        if not self.trades_history:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "total_profit": 0.0,
            }

        total_profit = sum(trade.get("profit", 0) for trade in self.trades_history)

        return {
            "total_trades": len(self.trades_history),
            "win_rate": self.calculate_win_rate(),
            "profit_factor": self.calculate_profit_factor(),
            "sharpe_ratio": self.calculate_sharpe_ratio(),
            "max_drawdown": self.calculate_max_drawdown(),
            "total_profit": total_profit,
            "average_profit": total_profit / len(self.trades_history) if self.trades_history else 0,
        }

    def export_to_csv(self, filename: str = "trade_analytics.csv"):
        """Export trade history to CSV for further analysis."""
        if self.trades_history:
            df = pd.DataFrame(self.trades_history)
            df.to_csv(filename, index=False)
            self.logger.info(f"Trade analytics exported to {filename}")
        else:
            self.logger.warning("No trades to export")

    def get_daily_summary(self) -> Dict[str, Any]:
        """Get today's trading summary."""
        today = datetime.now().date()
        today_trades = [
            trade for trade in self.trades_history if datetime.fromisoformat(trade["timestamp"]).date() == today
        ]

        if not today_trades:
            return {"trades_today": 0, "profit_today": 0.0}

        return {
            "trades_today": len(today_trades),
            "profit_today": sum(trade.get("profit", 0) for trade in today_trades),
            "win_rate_today": (sum(1 for trade in today_trades if trade.get("profit", 0) > 0) / len(today_trades))
            * 100,
        }
