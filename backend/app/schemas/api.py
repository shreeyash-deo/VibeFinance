"""
backend/app/schemas/api.py - REST Request and Response Schemas
"""

from typing import Literal
from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    ticker: str
    user_id: str | None = None
    data_mode: Literal['cached', 'live'] = 'cached'
    simulate_feed_down: bool = False
    simulate_missing_filing: bool = False

class StockItemSchema(BaseModel):
    ticker: str
    name: str
    sector: str
    yf_symbol: str
    latest_price: float
    change_24h: float
    change_pct: float
    volume_24h: int

class PriceCandleSchema(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class BacktestResultSchema(BaseModel):
    agent: str
    ticker: str
    horizon_days: int
    n_signals: int
    hit_rate: float
    avg_fwd_return: float
    run_at: str

class DocumentChunkDetailSchema(BaseModel):
    chunk_id: str
    ticker: str
    title: str
    doc_type: str
    doc_date: str
    source_label: str
    page: int | None
    snippet: str
    url: str | None

