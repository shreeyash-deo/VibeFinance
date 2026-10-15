"""
backend/app/agents/risk.py - Personalized Investor Risk & Behavioral Profiling Agent
"""

from typing import Any
from backend.app.schemas.agent import RiskVerdict, AgentOutput
from backend.app.features.indicators import compute_portfolio_metrics

def evaluate_investor_risk(
    ticker: str,
    sector: str,
    profile: dict[str, Any],
    holdings: list[dict[str, Any]],
    current_prices: dict[str, float],
    volatility_60d: float,
    behavior_events: list[dict[str, Any]],
    filings_agent_output: AgentOutput | None = None
) -> RiskVerdict:
    """
    Evaluates individual investor risk capacity, concentration thresholds (HHI), and behavioral heuristics.
    """
    risk_tol = profile.get("risk_tolerance", "moderate").lower()
    max_single_stock = float(profile.get("max_single_stock_pct", 10.0))
    sector_limits = profile.get("sector_limits", {})
    loss_aversion = float(profile.get("loss_aversion", 0.5))
    overtrading_score = float(profile.get("overtrading_score", 0.1))

    # Base concentration before
    port_metrics_before = compute_portfolio_metrics(holdings, current_prices)
    hhi_before = port_metrics_before["hhi"]
    curr_sector_exposure = port_metrics_before["sector_exposure"].get(sector, 0.0)

    blocked_reasons = []
    behavioral_nudges = []
    risk_fit = "good"
    max_position = max_single_stock

    # Check 1: Volatility vs Risk Tolerance
    # Conservative <= 22%, Moderate <= 32%, Aggressive no cap
    if risk_tol == "conservative" and volatility_60d > 22.0:
        blocked_reasons.append(
            f"Annualized 60-day volatility ({volatility_60d:.1f}%) exceeds Conservative risk ceiling (22.0%)."
        )
        risk_fit = "poor"
        max_position = 0.0
    elif risk_tol == "moderate" and volatility_60d > 32.0:
        blocked_reasons.append(
            f"Annualized volatility ({volatility_60d:.1f}%) exceeds Moderate risk threshold (32.0%)."
        )
        risk_fit = "stretch"
        max_position = min(max_position, 5.0)

    # Check 2: Regulatory / Filing negative flags for Conservative profiles
    if risk_tol == "conservative" and filings_agent_output and filings_agent_output.signal == "bearish":
        blocked_reasons.append(
            "Regulatory / corporate filings contain negative disclosures (e.g. pledge/audit note), incompatible with conservative capital preservation."
        )
        risk_fit = "poor"
        max_position = 0.0

    # Check 3: Sector Headroom
    sector_limit = float(sector_limits.get(sector, 35.0))
    headroom = max(0.0, sector_limit - curr_sector_exposure)
    if headroom < max_position:
        if headroom <= 0:
            blocked_reasons.append(
                f"Sector allocation to {sector} ({curr_sector_exposure:.1f}%) is at or above your mandated policy limit ({sector_limit:.1f}%)."
            )
            max_position = 0.0
            if risk_fit == "good":
                risk_fit = "stretch"
        else:
            blocked_reasons.append(
                f"Position capped at {headroom:.1f}% due to remaining headroom in {sector} sector limit ({sector_limit:.1f}%)."
            )
            max_position = round(headroom, 1)

    # Check 4: Behavioral Flags (Panic Selling / Overtrading History)
    has_recent_panic_sell = False
    for ev in behavior_events:
        tag = ev.get("tag", "")
        if tag == "panic_sell":
            has_recent_panic_sell = True
            break

    if overtrading_score > 0.60 or has_recent_panic_sell:
        behavioral_nudges.append(
            "Behavioral Alert: Elevated trading frequency and past impulsive exits detected. A mandatory 48-hour cooling-off period is recommended before initiating new capital allocation."
        )

    if loss_aversion > 0.70 and risk_fit != "poor":
        behavioral_nudges.append(
            "Loss Aversion Notice: Strict stop-loss trailing rules recommended to insulate against emotional drawdown reactions."
        )

    # Hypothetical HHI after allocation
    hhi_after = hhi_before
    if max_position > 0:
        hypo_weight = max_position / 100.0
        hhi_after = round(hhi_before + (hypo_weight ** 2), 4)

    return RiskVerdict(
        max_position_pct=round(max_position, 1),
        blocked_reasons=blocked_reasons,
        behavioral_nudges=behavioral_nudges,
        concentration_before=round(hhi_before, 4),
        concentration_after=round(hhi_after, 4),
        risk_fit=risk_fit
    )

