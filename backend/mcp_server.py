"""
backend/mcp_server.py - Model Context Protocol (MCP) Server for VibeFinance
Exposes specialized tools for coding agents & LLMs:
- get_signals(ticker)
- search_filings(query, ticker)
- get_portfolio(user_id)
- analyze(ticker, user_id)
"""

import sys
import os
import json
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from typing import Any
from backend.app.graph.runner import execute_analysis_pipeline, DEFAULT_PERSONAS, DEFAULT_HOLDINGS
from backend.app.rag.retriever import retriever
from backend.app.rag.embeddings import get_text_embedding, cosine_similarity
from backend.app.features.indicators import compute_portfolio_metrics
from backend.app.data import resilient_provider

def handle_get_signals(ticker: str) -> dict[str, Any]:
    ticker = ticker.upper()
    price_res = resilient_provider.get_prices(ticker)
    news_res = resilient_provider.get_news(ticker)
    from backend.app.agents.momentum import run_momentum_agent
    from backend.app.agents.volume import run_volume_agent
    from backend.app.agents.sentiment import run_sentiment_agent

    mom = run_momentum_agent(ticker, price_res.data)
    vol = run_volume_agent(ticker, price_res.data)
    sent = run_sentiment_agent(ticker, news_res.data)

    return {
        "ticker": ticker,
        "momentum": mom.model_dump(),
        "volume": vol.model_dump(),
        "sentiment": sent.model_dump()
    }

def handle_search_filings(query: str, ticker: str = "") -> list[dict[str, Any]]:
    retriever.load_and_index()
    q_emb = get_text_embedding(query)
    candidates = retriever._chunks
    if ticker:
        candidates = [c for c in candidates if c["ticker"] == ticker.upper()]

    scored = []
    for c in candidates:
        sim = cosine_similarity(q_emb, c["embedding"])
        scored.append((sim, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for s, c in scored[:5]:
        results.append({
            "chunk_id": c["id"],
            "ticker": c["ticker"],
            "title": c["title"],
            "similarity": round(float(s), 4),
            "snippet": c["text"][:250] + "..."
        })
    return results

def handle_get_portfolio(user_id: str = "meena") -> dict[str, Any]:
    slug = user_id.lower() if user_id in DEFAULT_PERSONAS else "meena"
    holdings = DEFAULT_HOLDINGS.get(slug, [])
    prices = {}
    for h in holdings:
        t = h["ticker"]
        res = resilient_provider.get_prices(t)
        prices[t] = float(res.data['Close'].iloc[-1]) if not res.data.empty else h["avg_price"]
    
    return compute_portfolio_metrics(holdings, prices)

async def handle_analyze(ticker: str, user_id: str = "meena") -> dict[str, Any]:
    res = await execute_analysis_pipeline(ticker=ticker, user_id=user_id)
    return res.model_dump()

TOOLS = [
    {
        "name": "get_signals",
        "description": "Calculates technical momentum, volume anomaly, and news sentiment signals for a Nifty 50 equity.",
        "inputSchema": {
            "type": "object",
            "properties": {"ticker": {"type": "string", "description": "Stock ticker symbol (e.g. RELIANCE, ADANIENT)"}},
            "required": ["ticker"]
        }
    },
    {
        "name": "search_filings",
        "description": "Performs 384-dimensional semantic vector search over SEBI corporate filings and earnings call transcripts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language search query"},
                "ticker": {"type": "string", "description": "Optional ticker filter"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_portfolio",
        "description": "Retrieves investor portfolio holdings, valuation, sector exposure, and HHI concentration score.",
        "inputSchema": {
            "type": "object",
            "properties": {"user_id": {"type": "string", "description": "Persona slug: meena, arjun, rohan"}},
            "required": ["user_id"]
        }
    },
    {
        "name": "analyze",
        "description": "Executes full multi-agent financial intelligence pipeline with personalized risk profiling.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
                "user_id": {"type": "string", "description": "Investor persona slug"}
            },
            "required": ["ticker"]
        }
    }
]

async def main():
    """Stdio-based JSON-RPC MCP Server listener."""
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")

            if method == "tools/list":
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})

                if name == "get_signals":
                    res = handle_get_signals(args.get("ticker", "INFY"))
                elif name == "search_filings":
                    res = handle_search_filings(args.get("query", ""), args.get("ticker", ""))
                elif name == "get_portfolio":
                    res = handle_get_portfolio(args.get("user_id", "meena"))
                elif name == "analyze":
                    res = await handle_analyze(args.get("ticker", "INFY"), args.get("user_id", "meena"))
                else:
                    res = {"error": f"Unknown tool: {name}"}

                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
