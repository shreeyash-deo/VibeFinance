"""
backend/app/data/provider.py - DataProvider Protocol & ResilientProvider
"""

from typing import Protocol, Literal, Any, runtime_checkable
from datetime import datetime
import pandas as pd
from pydantic import BaseModel

class DataResult(BaseModel):
    data: Any
    source: Literal['live', 'cache', 'synthetic']
    as_of: datetime
    stale: bool = False
    error: str | None = None

    class Config:
        arbitrary_types_allowed = True

@runtime_checkable
class DataProvider(Protocol):
    def get_prices(self, ticker: str, period: str = '1y') -> DataResult:
        ...
    def get_news(self, ticker: str, days: int = 14) -> DataResult:
        ...
    def get_flows(self, days: int = 30) -> DataResult:
        ...

class ResilientProvider:
    """
    Wraps Live and Cached providers.
    In 'cached' mode, reads directly from frozen snapshot.
    In 'live' mode, attempts live fetch with timeout; on exception or feed down flag,
    falls back cleanly to cached snapshot with stale=True.
    """
    def __init__(self, live_provider: DataProvider, cached_provider: DataProvider):
        self.live = live_provider
        self.cached = cached_provider

    def get_prices(self, ticker: str, period: str = '1y', data_mode: str = 'cached', simulate_feed_down: bool = False) -> DataResult:
        if simulate_feed_down:
            cached_res = self.cached.get_prices(ticker, period)
            return DataResult(
                data=cached_res.data,
                source='cache',
                as_of=cached_res.as_of,
                stale=True,
                error="Feed connection simulated down: graceful fallback to cached snapshot."
            )

        if data_mode == 'live':
            try:
                live_res = self.live.get_prices(ticker, period)
                if live_res.error:
                    cached_res = self.cached.get_prices(ticker, period)
                    return DataResult(
                        data=cached_res.data,
                        source='cache',
                        as_of=cached_res.as_of,
                        stale=True,
                        error=f"Live feed failed ({live_res.error}); used cached snapshot."
                    )
                return live_res
            except Exception as e:
                cached_res = self.cached.get_prices(ticker, period)
                return DataResult(
                    data=cached_res.data,
                    source='cache',
                    as_of=cached_res.as_of,
                    stale=True,
                    error=f"Live feed exception: {str(e)}; fallback to cached snapshot."
                )

        # Default to cached snapshot
        return self.cached.get_prices(ticker, period)

    def get_news(self, ticker: str, days: int = 14, data_mode: str = 'cached', simulate_feed_down: bool = False) -> DataResult:
        if simulate_feed_down:
            cached_res = self.cached.get_news(ticker, days)
            return DataResult(
                data=cached_res.data,
                source='cache',
                as_of=cached_res.as_of,
                stale=True,
                error="Simulated news feed down: returned cached headlines."
            )

        if data_mode == 'live':
            try:
                live_res = self.live.get_news(ticker, days)
                if not live_res.error and len(live_res.data) > 0:
                    return live_res
            except Exception as e:
                pass
        return self.cached.get_news(ticker, days)

    def get_flows(self, days: int = 30, data_mode: str = 'cached', simulate_feed_down: bool = False) -> DataResult:
        if simulate_feed_down:
            cached_res = self.cached.get_flows(days)
            return DataResult(
                data=cached_res.data,
                source='cache',
                as_of=cached_res.as_of,
                stale=True,
                error="Simulated institutional flow feed down: returned cached flows."
            )
        return self.cached.get_flows(days)

