"""
backend/app/data/live.py - Best-effort Live Data Provider
"""

from datetime import datetime
import pandas as pd
from backend.app.data.provider import DataResult

class LiveProvider:
    def get_prices(self, ticker: str, period: str = '1y') -> DataResult:
        try:
            import yfinance as yf
            yf_ticker = f"{ticker}.NS" if not ticker.endswith(".NS") else ticker
            t = yf.Ticker(yf_ticker)
            df = t.history(period=period, timeout=5)
            if df.empty:
                return DataResult(
                    data=pd.DataFrame(),
                    source='live',
                    as_of=datetime.utcnow(),
                    stale=True,
                    error=f"No live price data returned for {ticker}"
                )
            df = df.reset_index()
            # Standardize columns
            col_map = {'Date': 'Date', 'Open': 'Open', 'High': 'High', 'Low': 'Low', 'Close': 'Close', 'Volume': 'Volume'}
            df = df[[c for c in col_map if c in df.columns]]
            last_date = df['Date'].iloc[-1].to_pydatetime() if len(df) > 0 else datetime.utcnow()
            return DataResult(
                data=df,
                source='live',
                as_of=last_date,
                stale=False,
                error=None
            )
        except Exception as e:
            return DataResult(
                data=pd.DataFrame(),
                source='live',
                as_of=datetime.utcnow(),
                stale=True,
                error=f"yfinance error: {str(e)}"
            )

    def get_news(self, ticker: str, days: int = 14) -> DataResult:
        try:
            import feedparser
            # Search Google News RSS
            query = f"{ticker}+stock+India"
            rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
            feed = feedparser.parse(rss_url)
            entries = []
            for item in feed.entries[:15]:
                entries.append({
                    "id": item.get("id", item.get("link", "")),
                    "ticker": ticker,
                    "title": item.get("title", ""),
                    "publisher": item.get("source", {}).get("title", "Google News RSS"),
                    "published_at": item.get("published", datetime.utcnow().isoformat()),
                    "url": item.get("link", ""),
                    "sentiment_label": "neutral",
                    "relevance": 0.8
                })
            return DataResult(
                data=entries,
                source='live',
                as_of=datetime.utcnow(),
                stale=False,
                error=None
            )
        except Exception as e:
            return DataResult(
                data=[],
                source='live',
                as_of=datetime.utcnow(),
                stale=True,
                error=f"News RSS error: {str(e)}"
            )

    def get_flows(self, days: int = 30) -> DataResult:
        # Institutional flows live scraping is best-effort fallback
        return DataResult(
            data=pd.DataFrame(),
            source='live',
            as_of=datetime.utcnow(),
            stale=True,
            error="Live institutional flow requires proprietary NSE clearing feed; use snapshot."
        )

