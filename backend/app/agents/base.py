"""
backend/app/agents/base.py - Base Agent Wrapper & Execution Harness
"""

import time
import traceback
from typing import Callable
from backend.app.schemas.agent import AgentOutput, Evidence

def safe_run(agent_name: str, ticker: str, func: Callable[..., AgentOutput], *args, **kwargs) -> AgentOutput:
    """
    Executes an agent with execution timing and safety boundary.
    Guarantees no uncaught exceptions will crash the graph; returns status='failed' on failure.
    """
    start_time = time.perf_counter()
    try:
        output = func(*args, **kwargs)
        latency = int((time.perf_counter() - start_time) * 1000)
        output.latency_ms = latency
        return output
    except Exception as e:
        latency = int((time.perf_counter() - start_time) * 1000)
        tb = traceback.format_exc()
        return AgentOutput(
            agent=agent_name,
            ticker=ticker,
            signal='no_data',
            confidence=0.0,
            reasoning=f"Agent encountered an execution exception: {str(e)}",
            metrics={},
            evidence=[],
            latency_ms=latency,
            status='failed',
            notes=[f"Execution failed: {str(e)}", tb[:200]]
        )

