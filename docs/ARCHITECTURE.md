# VibeFinance: Multi-Agent Architecture & Decision Logic

## 1. System Overview
VibeFinance (PS 04) is a multi-agent autonomous financial intelligence platform built specifically for Indian retail investors in the Nifty 50 universe (18 bellwether equities). The system converts raw market data feeds, news streams, corporate regulatory disclosures, and institutional flows into personalized, explainable, and cited investment decision support.

```mermaid
flowchart TD
    subgraph DataIngestion [Resilient Ingestion Layer]
        PR[OHLCV Price Snapshots]
        NW[News Headlines]
        FL[FII/DII Institutional Flows]
        FIL[SEBI / BSE Regulatory Filings]
        RP[ResilientProvider: Frozen Snapshot + Live Toggle]
    end

    subgraph FeatureEngineering [Deterministic Calculations]
        FE[features/indicators.py: RSI, MACD, SMAs, Volatility, Z-Scores]
    end

    subgraph ParallelAgents [Parallel Specialized Agents - LangGraph]
        A1[Momentum Agent]
        A2[Volume Anomaly Agent]
        A3[Sentiment Agent]
        A4[Filings RAG Agent - CRAG]
        A5[Institutional Flow Agent]
    end

    subgraph CoordinationLayer [Synthesis & Safety Guardrails]
        CD[Deterministic Conflict Detector]
        RA[Personalized Risk & Behavioral Profiling]
        SYN[Synthesis Agent: Composite Scoring + Citation Guard]
    end

    subgraph Presentation [Interactive Next.js Dashboard]
        DASH[Candlesticks | Signal Cards | Sourced Recommendations | Citations Drawer | SSE Latency Benchmark]
    end

    PR & NW & FL & FIL --> RP --> FE
    FE --> A1 & A2 & A3 & A4 & A5
    A1 & A2 & A3 & A4 & A5 --> CD --> RA --> SYN
    SYN --> DASH
```

---

## 2. Core Non-Negotiable Rules
1. **Deterministic Quantitative Core**: All indicators (RSI, MACD, SMAs, Volatility, Volume Z-Scores, HHI) are computed in Python (`pandas` / `numpy`), never calculated or hallucinated by LLMs.
2. **Unified Pydantic Contract**: Every agent outputs the exact same `AgentOutput` schema containing signal, confidence, reasoning, computed metrics, evidence citations, latency, and status.
3. **Citation Guard**: No actionable recommendation (`accumulate`, `hold`, `reduce`, `avoid`) is emitted without at least one cited evidence record. If zero citations exist, the synthesis layer forces `action='wait'` and output `"Insufficient sourced evidence"`.
4. **Resilient Data Fallback**: The platform defaults to a frozen demo snapshot. If a feed is unavailable or `simulate_feed_down=True`, it falls back cleanly to cache, penalizes confidence by 0.15, and tags `stale=True` with no unhandled exceptions.

---

## 3. Agent Specifications & Decision Logic

### 3.1 Momentum Agent (`backend/app/agents/momentum.py`)
- **Inputs**: 1-year OHLCV prices.
- **Formulas**:
  - RSI(14) via Wilder exponential smoothing.
  - MACD(12, 26, 9) histogram & signal line.
  - SMA20, SMA50, SMA200.
  - 20-day return & distance from 52-week high.
- **Scoring**:
  - $+1$ each: RSI $\in [50, 70]$, MACD histogram $>0$ & rising, Close $>$ SMA50 $>$ SMA200, 20d return $>0$.
  - $-1$ each: RSI $<50$, MACD histogram $<0$ & falling, Close $<$ SMA50 $<$ SMA200, 20d return $<0$.
  - Score $\in [-4, +4]$: $\ge +2 \implies \text{Bullish}$, $\le -2 \implies \text{Bearish}$, else $\text{Neutral}$.
- **Confidence**: $\min(0.90, 0.40 + 0.12 \times |\text{score}|) - 0.15 \times \mathbb{I}_{\text{stale}}$.

### 3.2 Volume Anomaly Agent (`backend/app/agents/volume.py`)
- **Inputs**: 20-day rolling volume mean and standard deviation.
- **Formula**: $Z_{\text{vol}} = \frac{V_t - \mu_{20}}{\sigma_{20}}$.
- **Signal**:
  - $Z_{\text{vol}} \ge 2.0 \implies \text{Anomalous}$ with direction bias based on 1-day price return.
  - Else $\text{Neutral}$.
- **Confidence**: Scales from $0.40$ to $0.85$ based on $\min(Z/4, 1.0)$.

### 3.3 Sentiment Agent (`backend/app/agents/sentiment.py`)
- **Inputs**: Last 14 days of headlines.
- **Scoring**: FinBERT / Gemini polarity scoring.
- **Recency Decay**: Exponential half-life of 5 days: $w_i = \exp(-0.1386 \times \Delta t_i)$.
- **Signal**: Weighted score $> +0.20 \implies \text{Bullish}$, $< -0.20 \implies \text{Bearish}$, else $\text{Neutral}$.

### 3.4 Filings RAG Agent (CRAG) (`backend/app/agents/filings_rag.py`)
- **Ingestion**: Markdown regulatory filings chunked with YAML frontmatter.
- **Embeddings**: 384-dimensional dense semantic vectors with cosine similarity.
- **CRAG Flow**:
  1. Retrieve top-8 chunks on ticker filter.
  2. Grade chunk relevance via keyword and semantic confidence.
  3. If $<2$ relevant chunks, rewrite query and widen retrieval to top-12.
  4. If zero chunks survive, return `signal='no_data'`, `status='degraded'`.
  5. Post-validation: Every claim in the agent output must link to a valid `chunk_id`.

### 3.5 Institutional Flow Agent (`backend/app/agents/flow.py`)
- **Inputs**: 90-day daily FII and DII net purchases/sales (INR Crores).
- **Metric**: 5-day cumulative institutional net flow $(FII + DII)$.
- **Signal**: $> +1500\text{ Cr} \implies \text{Bullish}$, $< -1500\text{ Cr} \implies \text{Bearish}$, else $\text{Neutral}$.

### 3.6 Conflict Detector (`backend/app/agents/conflict.py`)
- Maps signals: $\text{Bullish} = +1, \text{Bearish} = -1, \text{Neutral} = 0$.
- Flags conflict if at least one $+1$ and at least one $-1$ coexist with confidence $\ge 0.50$.
- Computes disagreement score: $\sigma_{\text{signals}}$.

### 3.7 Risk & Personalization Agent (`backend/app/agents/risk.py`)
- **Volatility Filter**:
  - Conservative: Max 60-day annualized volatility $\le 22.0\%$. Exceeding flags `risk_fit='poor'`, `max_position=0\%`.
  - Moderate: Max volatility $\le 32.0\%$.
  - Aggressive: Uncapped.
- **Concentration**: Computes Herfindahl-Hirschman Index (HHI) before and hypothetical HHI after trade.
- **Sector Headroom**: Restricts position size to remaining headroom under investor's sector cap.
- **Behavioral Nudge**: Investors with overtrading score $>0.60$ or recent panic sells receive a mandatory 48-hour cooling-off warning.

### 3.8 Synthesis Layer (`backend/app/agents/synthesis.py`)
- Weighted composite signal: Momentum (0.25), Volume (0.15), Sentiment (0.20), Filings (0.30), Flow (0.10).
- Action mapping:
  - If Conflict detected $\implies \text{Action: WAIT}$, confidence $\le 0.45$.
  - If Risk Fit is Poor $\implies \text{Action: AVOID / WAIT}$, position size $0\%$.
  - If Behavioral Cooling-off active $\implies \text{Action: WAIT}$, position size $0\%$.
  - If Composite $\ge +0.35 \implies \text{Action: ACCUMULATE}$.
  - If Composite $\le -0.35 \implies \text{Action: REDUCE / AVOID}$.
  - Else $\implies \text{Action: HOLD / WAIT}$.
- Natural-language summary ($<150$ words) synthesized by Gemini with inline citation markers `[1]`, `[2]`.

---

## 4. LangGraph Parallel Orchestration & Telemetry
The pipeline executes 5 analytical agents concurrently via `asyncio.gather`, streaming step-by-step telemetry via Server-Sent Events (SSE). The dashboard displays:
- Per-node execution latency in milliseconds.
- Parallel vs. Sequential Latency comparison chart (demonstrating $2.4\text{x}-3.0\text{x}$ acceleration).
- 18-Month historical walk-forward backtest hit rates against 30-day forward equity returns.

