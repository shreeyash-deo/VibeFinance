"""
tests/test_indicators.py - Unit Tests for Deterministic Quantitative Features
"""

import pytest
import pandas as pd
import numpy as np
from backend.app.features.indicators import (
    compute_rsi, compute_macd, compute_smas,
    compute_technical_features, compute_portfolio_metrics
)

def test_rsi_bounds():
    prices = pd.Series([100, 102, 101, 105, 107, 106, 110, 112, 115, 114, 118, 120, 122, 125, 127, 130])
    rsi = compute_rsi(prices, 14)
    assert len(rsi) == len(prices)
    assert 0 <= rsi.iloc[-1] <= 100
    assert rsi.iloc[-1] > 50  # Steady upward trend should have RSI > 50

def test_macd_calculation():
    prices = pd.Series(np.linspace(100, 200, 50))
    macd_line, sig_line, hist = compute_macd(prices, 12, 26, 9)
    assert len(macd_line) == 50
    assert len(sig_line) == 50
    assert len(hist) == 50
    # In a linear upward ramp, macd line should be positive
    assert macd_line.iloc[-1] > 0

def test_smas_calculation():
    prices = pd.Series(np.ones(250) * 100.0)
    smas = compute_smas(prices, [20, 50, 200])
    assert "SMA20" in smas and "SMA50" in smas and "SMA200" in smas
    assert smas["SMA20"].iloc[-1] == 100.0
    assert smas["SMA200"].iloc[-1] == 100.0

def test_portfolio_metrics_and_hhi():
    holdings = [
        {"ticker": "TCS", "qty": 10, "avg_price": 4000.0, "sector": "IT"},
        {"ticker": "INFY", "qty": 20, "avg_price": 2000.0, "sector": "IT"}
    ]
    current_prices = {"TCS": 4000.0, "INFY": 2000.0}
    metrics = compute_portfolio_metrics(holdings, current_prices)

    assert metrics["total_value"] == 80000.0
    assert metrics["total_cost"] == 80000.0
    assert metrics["total_pnl"] == 0.0
    # Equal 50/50 weighting -> HHI should be 0.5^2 + 0.5^2 = 0.50
    assert abs(metrics["hhi"] - 0.50) < 0.01
    assert metrics["sector_exposure"]["IT"] == 100.0

