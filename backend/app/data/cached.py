"""
backend/app/data/cached.py - Cached Snapshot Data Provider
"""

import os
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
from backend.app.config import settings
from backend.app.data.provider import DataResult

class CachedProvider:
    def __init__(self, snapshot_dir: Path | None = None):
        self.snapshot_dir = Path(snapshot_dir) if snapshot_dir else settings.SNAPSHOT_DIR
        self.prices_dir = self.snapshot_dir / "prices"
        self.news_dir = self.snapshot_dir / "news"
        self.flows_file = self.snapshot_dir / "flows.csv"

    def get_prices(self, ticker: str, period: str = '1y') -> DataResult:
        csv_path = self.prices_dir / f"{ticker.upper()}.csv"
        if not csv_path.exists():
            return DataResult(
                data=pd.DataFrame(),
                source='cache',
                as_of=datetime.utcnow(),
                stale=True,
                error=f"Price snapshot not found for {ticker} at {csv_path}"
            )
        try:
            df = pd.read_csv(csv_path)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date').reset_index(drop=True)
            
            # Slice period
            if period == '1y' and len(df) > 252:
                df = df.iloc[-252:].reset_index(drop=True)
            elif period == '6m' and len(df) > 126:
                df = df.iloc[-126:].reset_index(drop=True)
                
            last_date = df['Date'].iloc[-1].to_pydatetime() if len(df) > 0 else datetime.utcnow()
            return DataResult(
                data=df,
                source='cache',
                as_of=last_date,
                stale=False,
                error=None
            )
        except Exception as e:
            return DataResult(
                data=pd.DataFrame(),
                source='cache',
                as_of=datetime.utcnow(),
                stale=True,
                error=str(e)
            )

    def get_news(self, ticker: str, days: int = 14) -> DataResult:
        json_path = self.news_dir / f"{ticker.upper()}.json"
        if not json_path.exists():
            return DataResult(
                data=[],
                source='cache',
                as_of=datetime.utcnow(),
                stale=True,
                error=f"News snapshot not found for {ticker}"
            )
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                news = json.load(f)
            return DataResult(
                data=news,
                source='cache',
                as_of=datetime.utcnow(),
                stale=False,
                error=None
            )
        except Exception as e:
            return DataResult(
                data=[],
                source='cache',
                as_of=datetime.utcnow(),
                stale=True,
                error=str(e)
            )

    def get_flows(self, days: int = 30) -> DataResult:
        if not self.flows_file.exists():
            return DataResult(
                data=pd.DataFrame(),
                source='cache',
                as_of=datetime.utcnow(),
                stale=True,
                error="Flows snapshot not found"
            )
        try:
            df = pd.read_csv(self.flows_file)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date').reset_index(drop=True)
            if len(df) > days:
                df = df.iloc[-days:].reset_index(drop=True)
            last_date = df['Date'].iloc[-1].to_pydatetime() if len(df) > 0 else datetime.utcnow()
            return DataResult(
                data=df,
                source='cache',
                as_of=last_date,
                stale=False,
                error=None
            )
        except Exception as e:
            return DataResult(
                data=pd.DataFrame(),
                source='cache',
                as_of=datetime.utcnow(),
                stale=True,
                error=str(e)
            )

