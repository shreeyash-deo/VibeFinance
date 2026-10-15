"""
backend/app/schemas/profile.py - User Profile, Portfolio, and Behavioral Schemas
"""

from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field

class UserProfileSchema(BaseModel):
    user_id: str
    display_name: str
    persona_label: str
    risk_tolerance: Literal['conservative', 'moderate', 'aggressive']
    horizon_years: int
    max_single_stock_pct: float
    sector_limits: dict[str, float]
    loss_aversion: float # 0.0 to 1.0
    overtrading_score: float # 0.0 to 1.0
    updated_at: datetime | None = None

class HoldingSchema(BaseModel):
    ticker: str
    name: str = ""
    sector: str = ""
    qty: float
    avg_price: float
    current_price: float = 0.0
    current_value: float = 0.0
    pnl: float = 0.0
    pnl_pct: float = 0.0
    weight_pct: float = 0.0

class PortfolioSummarySchema(BaseModel):
    user_id: str
    persona_label: str
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_pct: float
    hhi: float
    top_sector: str
    top_sector_pct: float
    holdings: list[HoldingSchema]

class BehaviorEventSchema(BaseModel):
    id: int | None = None
    user_id: str
    ticker: str
    action: Literal['buy', 'sell']
    price: float
    qty: float
    event_ts: str
    context: str
    tag: Literal['panic_sell', 'fomo_buy', 'normal']

