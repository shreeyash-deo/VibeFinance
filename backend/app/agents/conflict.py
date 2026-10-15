"""
backend/app/agents/conflict.py - Deterministic Multi-Agent Conflict Detector
"""

import numpy as np
from backend.app.schemas.agent import AgentOutput, ConflictReport

def detect_conflicts(agent_outputs: dict[str, AgentOutput]) -> ConflictReport:
    """
    Evaluates cross-agent signal divergence.
    Detects when at least one confident bullish signal (>=0.5) and one confident bearish signal (>=0.5) coexist.
    """
    bullish_agents = []
    bearish_agents = []
    values = []

    for name, out in agent_outputs.items():
        if out.status == "failed" or out.signal == "no_data":
            continue

        sig_val = 0
        if out.signal == "bullish":
            sig_val = 1
        elif out.signal == "bearish":
            sig_val = -1
        elif out.signal == "anomalous":
            bias = out.metrics.get("anomaly_bias", 0.0)
            sig_val = 1 if bias > 0 else (-1 if bias < 0 else 0)

        values.append(sig_val * out.confidence)

        if sig_val == 1 and out.confidence >= 0.50:
            bullish_agents.append((name, out))
        elif sig_val == -1 and out.confidence >= 0.50:
            bearish_agents.append((name, out))

    conflict = len(bullish_agents) > 0 and len(bearish_agents) > 0
    disagreement_score = round(float(np.std(values)), 3) if len(values) > 1 else 0.0

    pairs = []
    for b_name, _ in bullish_agents:
        for br_name, _ in bearish_agents:
            pairs.append((b_name, br_name))

    if conflict:
        b_names = ", ".join([b[0] for b in bullish_agents])
        br_names = ", ".join([br[0] for br in bearish_agents])
        explanation = (
            f"Cross-Agent Conflict Detected: Strong bullish signal from [{b_names}] directly diverges from "
            f"bearish indications from [{br_names}]. Synthetic guidance suggests waiting for clearer directional consensus."
        )
    else:
        explanation = "Analytical consensus maintained across active agent signals without acute directional opposition."

    return ConflictReport(
        conflict=conflict,
        pairs=pairs,
        disagreement_score=disagreement_score,
        explanation=explanation
    )

