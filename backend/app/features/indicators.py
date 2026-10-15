"""
backend/app/features/indicators.py - Deterministic Technical & Portfolio Indicator Calculations
"""

import math
import numpy as np
import pandas as pd
from typing import Any

def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Computes Relative Strength Index (RSI).
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Exponential moving average / Wilder smoothing
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)

def compute_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal_period: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Computes MACD line, signal line, and MACD histogram.
    """
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    macd_hist = macd_line - signal_line
    return macd_line, signal_line, macd_hist

def compute_smas(series: pd.Series, windows: list[int] = [20, 50, 200]) -> dict[str, pd.Series]:
    """
    Computes Simple Moving Averages.
    """
    result = {}
    for w in windows:
        result[f"SMA{w}"] = series.rolling(window=w, min_periods=1).mean()
    return result

def compute_technical_features(df: pd.DataFrame) -> dict[str, float]:
    """
    Computes all deterministic technical metrics from OHLCV dataframe.
    """
    if df.empty or len(df) < 5:
        return {
            "rsi": 50.0,
            "macd": 0.0,
            "macd_signal": 0.0,
            "macd_hist": 0.0,
            "macd_hist_rising": False,
            "sma20": 0.0,
            "sma50": 0.0,
            "sma200": 0.0,
            "return_20d": 0.0,
            "return_60d": 0.0,
            "dist_52w_high": 0.0,
            "volatility_60d": 0.0,
            "volume_zscore": 0.0,
            "volume_ratio_20d": 1.0,
            "latest_close": 0.0,
            "latest_volume": 0
        }

    close = df['Close']
    volume = df['Volume']

    rsi_series = compute_rsi(close, 14)
    macd_line, macd_sig, macd_hist = compute_macd(close, 12, 26, 9)
    smas = compute_smas(close, [20, 50, 200])

    latest_close = float(close.iloc[-1])
    latest_volume = int(volume.iloc[-1])

    # 20d and 60d returns
    ret_20d = float((latest_close - close.iloc[-21]) / close.iloc[-21]) if len(close) > 21 else 0.0
    ret_60d = float((latest_close - close.iloc[-61]) / close.iloc[-61]) if len(close) > 61 else 0.0

    # Distance from 52-week (252 days) high
    rolling_252 = close.iloc[-252:] if len(close) >= 252 else close
    high_52w = float(rolling_252.max())
    dist_52w_high = float((latest_close - high_52w) / high_52w) if high_52w > 0 else 0.0

    # 60d Annualized Volatility
    daily_returns = close.pct_change().dropna()
    rolling_returns = daily_returns.iloc[-60:] if len(daily_returns) >= 60 else daily_returns
    volatility_60d = float(rolling_returns.std() * math.sqrt(252)) if len(rolling_returns) > 5 else 0.20

    # Volume Anomaly (20-day mean/std z-score)
    vol_20d_window = volume.iloc[-21:-1] if len(volume) > 21 else volume
    vol_mean = float(vol_20d_window.mean())
    vol_std = float(vol_20d_window.std()) if len(vol_20d_window) > 1 else 1.0
    if vol_std <= 0:
        vol_std = 1.0
    vol_zscore = float((latest_volume - vol_mean) / vol_std)
    vol_ratio = float(latest_volume / vol_mean) if vol_mean > 0 else 1.0

    # MACD hist trend (rising vs falling)
    hist_rising = False
    if len(macd_hist) >= 2:
        hist_rising = bool(macd_hist.iloc[-1] > macd_hist.iloc[-2])

    return {
        "rsi": round(float(rsi_series.iloc[-1]), 2),
        "macd": round(float(macd_line.iloc[-1]), 2),
        "macd_signal": round(float(macd_sig.iloc[-1]), 2),
        "macd_hist": round(float(macd_hist.iloc[-1]), 2),
        "macd_hist_rising": hist_rising,
        "sma20": round(float(smas["SMA20"].iloc[-1]), 2),
        "sma50": round(float(smas["SMA50"].iloc[-1]), 2),
        "sma200": round(float(smas["SMA200"].iloc[-1]), 2),
        "return_20d": round(ret_20d * 100, 2), # percentage
        "return_60d": round(ret_60d * 100, 2), # percentage
        "dist_52w_high": round(dist_52w_high * 100, 2), # percentage
        "volatility_60d": round(volatility_60d * 100, 2), # percentage annualized
        "volume_zscore": round(vol_zscore, 2),
        "volume_ratio_20d": round(vol_ratio, 2),
        "latest_close": round(latest_close, 2),
        "latest_volume": latest_volume
    }

def compute_portfolio_metrics(holdings: list[dict], current_prices: dict[str, float]) -> dict[str, Any]:
    """
    Computes portfolio values, weights, sector breakdown, and HHI.
    holdings: list of dicts with keys {'ticker', 'qty', 'avg_price', 'sector'}
    """
    if not holdings:
        return {
            "total_value": 0.0,
            "total_cost": 0.0,
            "total_pnl": 0.0,
            "total_pnl_pct": 0.0,
            "hhi": 0.0,
            "sector_exposure": {},
            "top_holding_pct": 0.0,
            "weights": {}
        }

    total_value = 0.0
    total_cost = 0.0
    item_values = {}
    sector_values = {}

    for h in holdings:
        ticker = h["ticker"]
        qty = float(h["qty"])
        avg_price = float(h["avg_price"])
        sector = h.get("sector", "Other")
        curr_price = float(current_prices.get(ticker, avg_price))

        val = qty * curr_price
        cost = qty * avg_price
        total_value += val
        total_cost += cost

        item_values[ticker] = val
        sector_values[sector] = sector_values.get(sector, 0.0) + val

    weights = {}
    hhi = 0.0
    top_holding_pct = 0.0

    if total_value > 0:
        for ticker, val in item_values.items():
            w = val / total_value
            weights[ticker] = round(w * 100, 2)
            hhi += (w ** 2)
            if w > top_holding_pct:
                top_holding_pct = w
        
        sector_exposure = {sec: round((v / total_value) * 100, 2) for sec, v in sector_values.items()}
    else:
        sector_exposure = {}

    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0.0

    return {
        "total_value": round(total_value, 2),
        "total_cost": round(total_cost, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl_pct, 2),
        "hhi": round(hhi, 4), # Herfindahl-Hirschman Index between 0 and 1.0
        "sector_exposure": sector_exposure,
        "top_holding_pct": round(top_holding_pct * 100, 2),
        "weights": weights
    }

