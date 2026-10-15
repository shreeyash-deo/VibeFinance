"""
backend/app/api/routes_portfolio.py - Portfolio Holdings, Watchlist, and Behavior Tracking
"""

from fastapi import APIRouter, Depends
from backend.app.deps import get_current_user_id
from backend.app.schemas.profile import PortfolioSummarySchema, HoldingSchema, BehaviorEventSchema
from backend.app.graph.runner import DEFAULT_PERSONAS, DEFAULT_HOLDINGS, DEFAULT_BEHAVIOR
from backend.app.features.indicators import compute_portfolio_metrics
from backend.app.data import resilient_provider

router = APIRouter(tags=["Portfolio"])

@router.get("/me/portfolio", response_model=PortfolioSummarySchema)
async def get_my_portfolio(current_user_id: str = Depends(get_current_user_id)):
    slug = current_user_id.lower()
    if slug not in DEFAULT_PERSONAS:
        slug = "meena"

    holdings_raw = DEFAULT_HOLDINGS.get(slug, [])
    # Get current prices for valuation
    current_prices = {}
    for h in holdings_raw:
        t = h["ticker"]
        res = resilient_provider.get_prices(t, period='1y')
        if not res.data.empty:
            current_prices[t] = float(res.data['Close'].iloc[-1])
        else:
            current_prices[t] = float(h["avg_price"])

    metrics = compute_portfolio_metrics(holdings_raw, current_prices)

    holdings_list = []
    for h in holdings_raw:
        t = h["ticker"]
        qty = float(h["qty"])
        avg_price = float(h["avg_price"])
        curr_price = current_prices.get(t, avg_price)
        val = qty * curr_price
        cost = qty * avg_price
        pnl = val - cost
        pnl_pct = (pnl / cost * 100) if cost > 0 else 0.0
        tot_val = metrics["total_value"]
        weight = (val / tot_val * 100) if tot_val > 0 else 0.0

        holdings_list.append(HoldingSchema(
            ticker=t,
            name=t,
            sector=h.get("sector", "Other"),
            qty=qty,
            avg_price=avg_price,
            current_price=round(curr_price, 2),
            current_value=round(val, 2),
            pnl=round(pnl, 2),
            pnl_pct=round(pnl_pct, 2),
            weight_pct=round(weight, 2)
        ))

    top_sec = "None"
    top_sec_pct = 0.0
    for sec, pct in metrics["sector_exposure"].items():
        if pct > top_sec_pct:
            top_sec = sec
            top_sec_pct = pct

    return PortfolioSummarySchema(
        user_id=slug,
        persona_label=DEFAULT_PERSONAS[slug]["persona_label"],
        total_value=metrics["total_value"],
        total_cost=metrics["total_cost"],
        total_pnl=metrics["total_pnl"],
        total_pnl_pct=metrics["total_pnl_pct"],
        hhi=metrics["hhi"],
        top_sector=top_sec,
        top_sector_pct=top_sec_pct,
        holdings=holdings_list
    )

@router.get("/me/behavior", response_model=list[BehaviorEventSchema])
async def get_behavior_events(current_user_id: str = Depends(get_current_user_id)):
    slug = current_user_id.lower()
    events = DEFAULT_BEHAVIOR.get(slug, [])
    res = []
    for i, e in enumerate(events):
        res.append(BehaviorEventSchema(
            id=i + 1,
            user_id=slug,
            ticker=e["ticker"],
            action=e["action"],
            price=e["price"],
            qty=e["qty"],
            event_ts="2026-09-24T11:30:00Z",
            context=e["context"],
            tag=e["tag"]
        ))
    return res

