# VibeFinance: Data Assumptions & Planted Demo Scenarios

This document details the data sources, snapshot generation procedures, and planted edge cases used in VibeFinance.

## 1. Data Classification Summary

| Data Dimension | Source Type | Mode | Description |
| :--- | :--- | :--- | :--- |
| **OHLCV Pricing** | Snapshot Primary / yfinance Secondary | Frozen 2-Year Snapshot | Daily candles for 18 Nifty 50 stocks (Date, Open, High, Low, Close, Volume). |
| **News Headlines** | Snapshot Primary / RSS Secondary | Curated Snapshot | 15–25 realistic financial headlines per stock with publication dates and sources. |
| **FII / DII Flows** | Snapshot | 90-Day Net Flows | Daily institutional net purchases/sales across Indian equities in INR Crores. |
| **Corporate Filings** | Synthetic / Regulatory Markdown | 20 Disclosures (17 Tickers) | Modeled after SEBI Substantial Share Acquisition disclosures, limited audit reviews, and earnings call transcripts. |

---

## 2. Planted Edge Cases (Deterministic Demo Test Scenarios)

### Scenario A: ADANIENT (Promoter Pledge Hike + Volume Anomaly)
- **Planted Filing**: SEBI Regulation 31(1) disclosure confirming promoter pledge increase from **12.15% to 19.04% of promoter holding**, alongside an auditor review note on related-party loans.
- **Planted Pricing**: Injected volume spike on the final trading session ($Z_{\text{vol}} > 3.5$) with a $3.5\%$ downward price reaction.
- **Expected System Outcome**: Volume agent flags `anomalous` with bearish bias; Filings RAG agent retrieves the pledge excerpt with high relevance; for Conservative persona **Meena**, the Risk agent rejects allocation ($0\%$ cap) due to elevated volatility and governance risk.

### Scenario B: TATAMOTORS (Cross-Agent Signal Conflict)
- **Planted Technicals**: Bullish technical momentum across recent 60 trading days (RSI in $60-70$ range, MACD rising, price above 50 & 200 SMA).
- **Planted Filing**: Q2 FY27 Earnings Conference Call Transcript in which CFO announces a **180 bps reduction in full-year consolidated EBIT margin guidance (from 8.5% down to 6.7%)** citing European luxury EV transition costs.
- **Expected System Outcome**: Conflict Detector fires (`conflict=True`, pair `[Momentum Agent, Filings RAG Agent]`); Synthesis layer forces `action='wait'`, depresses composite confidence, and highlights both perspectives in a prominent warning banner.

### Scenario C: INFY (Positive Fundamental & Technical Alignment)
- **Planted Filing**: Q2 Results statement showing constant currency revenue growth guidance raised to $5.0\%-6.0\%$ with all-time high large deal TCV of $\$3.2$ billion.
- **Planted News**: Multiple upgrades on deal conversions.
- **Expected System Outcome**: Strong bullish alignment across Technical, News, and Fundamental agents; triggers `action='accumulate'` for aggressive personas up to maximum risk ceiling.

### Scenario D: WIPRO (Missing Corporate Disclosures - Graceful Degradation)
- **Data Configuration**: Deliberately **zero** corporate filings or markdown files exist for `WIPRO` in `data_snapshot/filings/`.
- **Expected System Outcome**: Filings RAG agent returns `signal='no_data'` with `status='degraded'` and note *"No supporting document found"*; pipeline executes without throwing exceptions; final recommendation relies strictly on verified news and price data or enforces `action='wait'`.

### Scenario E: Feed Outage Simulation (`simulate_feed_down=True`)
- **Trigger**: Toggle in the Top Bar.
- **Expected System Outcome**: Price fetcher catches simulated connection failure; immediately falls back to local cache; tags output with `stale=True` and applies a $-0.15$ penalty to technical agent confidence without crashing.

---

## 3. SEBI Disclaimer
All data, signals, and synthesized recommendations are generated strictly for academic and analytical demonstration. In accordance with SEBI (Research Analysts) Regulations, 2014, outputs do not constitute investment advice or buy/sell execution calls.

