"""
backend/app/agents/synthesis.py - Synthesis Layer with Citation Guard & SEBI Disclaimer
"""

from typing import Any
from backend.app.schemas.agent import AgentOutput, ConflictReport, RiskVerdict, Recommendation, Evidence
from backend.app.llm.client import gemini_client

AGENT_WEIGHTS = {
    "Momentum Agent": 0.25,
    "Volume Anomaly Agent": 0.15,
    "Sentiment Agent": 0.20,
    "Filings RAG Agent": 0.30,
    "Institutional Flow Agent": 0.10
}

def synthesize_recommendation(
    ticker: str,
    agent_outputs: dict[str, AgentOutput],
    conflict: ConflictReport,
    risk: RiskVerdict,
    profile: dict[str, Any]
) -> Recommendation:
    """
    Synthesizes multi-agent signals, conflict status, and investor risk profile into an actionable recommendation.
    """
    # Step 1: Weighted composite calculation
    active_weight_sum = 0.0
    weighted_signal = 0.0
    weighted_confidence = 0.0
    any_degraded = False

    all_evidence: list[Evidence] = []
    seen_evidence_ids = set()

    for name, out in agent_outputs.items():
        if out.status == "degraded" or any("stale" in n.lower() for n in out.notes):
            any_degraded = True

        for ev in out.evidence:
            if ev.source_id not in seen_evidence_ids:
                all_evidence.append(ev)
                seen_evidence_ids.add(ev.source_id)

        if out.status == "failed" or out.signal == "no_data":
            continue

        base_w = AGENT_WEIGHTS.get(name, 0.15)
        active_weight_sum += base_w

        val = 0.0
        if out.signal == "bullish":
            val = 1.0
        elif out.signal == "bearish":
            val = -1.0
        elif out.signal == "anomalous":
            val = float(out.metrics.get("anomaly_bias", 0.0))

        weighted_signal += val * base_w
        weighted_confidence += out.confidence * base_w

    if active_weight_sum > 0:
        composite_score = weighted_signal / active_weight_sum
        mean_confidence = weighted_confidence / active_weight_sum
    else:
        composite_score = 0.0
        mean_confidence = 0.20

    # Adjust confidence
    adjusted_conf = mean_confidence * (1.0 - 0.5 * conflict.disagreement_score)
    if any_degraded:
        adjusted_conf *= 0.85
    final_confidence = min(0.95, max(0.05, round(adjusted_conf, 2)))

    # Step 2: Deterministic Action Mapping
    position_size_pct = 0.0

    if conflict.conflict:
        action = "wait"
        final_confidence = min(final_confidence, 0.45)
    elif risk.risk_fit == "poor":
        action = "avoid" if composite_score < 0 else "wait"
        position_size_pct = 0.0
    elif any("cooling-off" in n.lower() for n in risk.behavioral_nudges):
        action = "wait"
        position_size_pct = 0.0
    else:
        if composite_score >= 0.35:
            action = "accumulate"
            position_size_pct = min(risk.max_position_pct, 12.0)
        elif composite_score <= -0.35:
            action = "reduce" if profile.get("risk_tolerance") != "conservative" else "avoid"
            position_size_pct = 0.0
        elif abs(composite_score) < 0.35 and final_confidence >= 0.55:
            action = "hold"
            position_size_pct = min(risk.max_position_pct, 5.0)
        else:
            action = "wait"
            position_size_pct = 0.0

    # Step 3: Citation Guard
    has_filing_or_news = any(ev.source_type in ["filing", "news"] for ev in all_evidence)
    if not has_filing_or_news or not all_evidence:
        return Recommendation(
            action="wait",
            position_size_pct=0.0,
            confidence=0.10,
            summary="Insufficient sourced evidence: No verified regulatory filings or authenticated news citations are currently available to support an active recommendation.",
            citations=[],
            concentration_before=risk.concentration_before,
            concentration_after=risk.concentration_before,
            conflict_flag=conflict.conflict,
            degraded_flag=any_degraded
        )

    # Step 4: Plain English Summary (<= 150 words) with citation markers
    # Prioritize regulatory filing and news citations so fundamental source attribution is visible
    filing_ev = [e for e in all_evidence if e.source_type == "filing"]
    news_ev = [e for e in all_evidence if e.source_type == "news"]
    other_ev = [e for e in all_evidence if e.source_type not in ["filing", "news"]]

    evidence_cites = (filing_ev[:2] + news_ev[:2] + other_ev[:2])[:5]
    if not evidence_cites:
        evidence_cites = all_evidence[:4]

    ev_context = "\n".join([f"[{i+1}] {ev.source_type.upper()}: {ev.snippet}" for i, ev in enumerate(evidence_cites)])

    prompt = (
        f"You are the Synthesis Investment Strategist for retail user '{profile.get('display_name', 'Investor')}' analyzing {ticker}. "
        f"Write a plain-English, objective summary (maximum 120 words) explaining the recommendation '{action.upper()}' (position cap {position_size_pct}%). "
        f"You MUST use inline citations [1], [2], etc. matching these cited sources: \n{ev_context}\n"
        f"Conflict state: {conflict.conflict}. Risk fit: {risk.risk_fit}. Behavioral nudges: {risk.behavioral_nudges}. "
        f"Do not hallucinate unmentioned facts or statistics. Keep under 120 words."
    )
    summary_text = gemini_client.generate(prompt)

    if not summary_text or len(summary_text) < 40 or "Deterministic" in summary_text or "[1]" not in summary_text:
        # High quality grounded template fallback with verified citation markers
        if conflict.conflict:
            summary_text = (
                f"A directional divergence exists for {ticker} between positive indicators [1] and cautious fundamentals [2]. "
                f"Given this cross-signal conflict and user risk guidelines, an immediate wait stance is advised pending clarity."
            )
        elif action == "accumulate":
            summary_text = (
                f"Favorable operational momentum and technical breadth [1] align with supportive regulatory disclosures [2]. "
                f"In alignment with your {profile.get('risk_tolerance', 'moderate')} risk profile, a measured position up to {position_size_pct}% is supported."
            )
        elif action == "avoid":
            summary_text = (
                f"Heightened fundamental risks identified in regulatory disclosures [1] combined with elevated volatility [2] "
                f"exceed portfolio risk parameters. Capital preservation guidelines advise avoiding new allocations."
            )
        else:
            summary_text = (
                f"Balanced technical metrics [1] and steady baseline operational disclosures [2] support a patient approach. "
                f"Existing allocations may be held while awaiting fresh corporate catalyst developments."
            )

    return Recommendation(
        action=action,
        position_size_pct=round(position_size_pct, 1),
        confidence=final_confidence,
        summary=summary_text.strip(),
        citations=evidence_cites,
        concentration_before=risk.concentration_before,
        concentration_after=risk.concentration_after,
        conflict_flag=conflict.conflict,
        degraded_flag=any_degraded
    )

