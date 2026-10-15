"""
scripts/verify_e2e.py - Comprehensive End-to-End Verification Harness for VibeFinance (PS 04)
Audits every mandatory MVP requirement, API endpoint, degradation mode, and personalization path.
"""

import sys
import json
import urllib.request
import urllib.error

API_URL = "http://127.0.0.1:8000/api"
FRONTEND_URL = "http://127.0.0.1:3000"

def get(endpoint: str, headers: dict = None) -> tuple[int, dict]:
    url = f"{API_URL}{endpoint}" if endpoint.startswith("/") else endpoint
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            data = res.read().decode('utf-8')
            return res.status, json.loads(data) if data.startswith('{') or data.startswith('[') else data
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')

def post(endpoint: str, payload: dict, headers: dict = None) -> tuple[int, dict]:
    url = f"{API_URL}{endpoint}"
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            data = res.read().decode('utf-8')
            return res.status, json.loads(data)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')

def run_e2e_checks():
    print("=" * 70)
    print("VIBEFINANCE (PS 04) END-TO-END VERIFICATION AUDIT")
    print("=" * 70)

    checks_passed = 0
    total_checks = 0

    def check(title: str, condition: bool, details: str = ""):
        nonlocal checks_passed, total_checks
        total_checks += 1
        status = "PASSED" if condition else "FAILED"
        print(f"[{status}] Check {total_checks}: {title}")
        if details:
            print(f"       -> {details}")
        if condition:
            checks_passed += 1

    # 1. Frontend Web App Liveness
    try:
        with urllib.request.urlopen(FRONTEND_URL, timeout=10) as r:
            html = r.read().decode('utf-8')
            check("Next.js Frontend is Running & Healthy", r.status == 200 and "VibeFinance" in html, f"Length: {len(html)} bytes")
    except Exception as e:
        check("Next.js Frontend is Running & Healthy", False, str(e))

    # 2. Backend Health Endpoint
    code, data = get("/health")
    check("Backend API Health Check", code == 200 and data.get("status") == "healthy", f"Service: {data.get('service')}, Provider: {data.get('llm_provider')}")

    # 3. 18 Nifty 50 Stocks Feeds
    code, stocks = get("/stocks")
    check("Watchlist Universe Contains 18 Nifty 50 Stocks", code == 200 and len(stocks) == 18, f"Returned {len(stocks)} stocks with live/snapshot prices")

    # 4. Candlestick Price Action
    code, candles = get("/stocks/ADANIENT/prices")
    check("OHLCV Candlestick Feed for Charting", code == 200 and len(candles) >= 50, f"Loaded {len(candles)} daily candles for ADANIENT")

    # 5. Persona Profiles & Personalization Data
    code, meena_prof = get("/me/profile", headers={"X-User-Id": "meena"})
    check("Conservative Persona (Meena) Profile", code == 200 and meena_prof.get("risk_tolerance") == "conservative", f"Horizon: {meena_prof.get('horizon_years')}y, Max Single Stock: {meena_prof.get('max_single_stock_pct')}%")

    code, arjun_prof = get("/me/profile", headers={"X-User-Id": "arjun"})
    check("Aggressive Persona (Arjun) Profile", code == 200 and arjun_prof.get("risk_tolerance") == "aggressive", f"Horizon: {arjun_prof.get('horizon_years')}y, Max Single Stock: {arjun_prof.get('max_single_stock_pct')}%")

    code, rohan_prof = get("/me/profile", headers={"X-User-Id": "rohan"})
    check("Overtrader Persona (Rohan) Profile", code == 200 and rohan_prof.get("overtrading_score") > 0.6, f"Overtrading Score: {rohan_prof.get('overtrading_score')}")

    # 6. Portfolio & Concentration (HHI)
    code, port = get("/me/portfolio", headers={"X-User-Id": "meena"})
    check("Portfolio Valuation & HHI Concentration", code == 200 and "hhi" in port and len(port.get("holdings", [])) > 0, f"Total Value: Rs {port.get('total_value'):,.2f}, HHI: {port.get('hhi')}")

    # 7. Multi-Agent Pipeline & Personalization Differentiation (ADANIENT)
    code, meena_res = post("/analyze", {"ticker": "ADANIENT", "user_id": "meena"})
    check("ADANIENT Analysis for Meena (Conservative)", code == 200 and meena_res.get("recommendation", {}).get("position_size_pct") == 0.0, f"Action: {meena_res.get('recommendation', {}).get('action')}, Position Cap: {meena_res.get('recommendation', {}).get('position_size_pct')}%")

    code, arjun_res = post("/analyze", {"ticker": "ADANIENT", "user_id": "arjun"})
    check("ADANIENT Analysis for Arjun (Aggressive)", code == 200 and arjun_res.get("risk", {}).get("max_position_pct") > meena_res.get("risk", {}).get("max_position_pct"), f"Arjun Max Position Cap: {arjun_res.get('risk', {}).get('max_position_pct')}% vs Meena: {meena_res.get('risk', {}).get('max_position_pct')}%")

    code, rohan_res = post("/analyze", {"ticker": "ADANIENT", "user_id": "rohan"})
    has_cooling_off = any("cooling-off" in n.lower() for n in rohan_res.get("risk", {}).get("behavioral_nudges", []))
    check("Rohan Behavioral Cooling-off Nudge Triggered", code == 200 and has_cooling_off and rohan_res.get("recommendation", {}).get("action") == "wait", f"Nudges: {rohan_res.get('risk', {}).get('behavioral_nudges')}")

    # 8. Sourced RAG Grounding & Citation Validation
    citations = meena_res.get("recommendation", {}).get("citations", [])
    has_filing_cite = any(c.get("source_type") == "filing" for c in citations)
    check("Recommendation Grounded in Regulatory Filings", len(citations) >= 1 and has_filing_cite, f"Citations attached: {len(citations)}, First: {citations[0].get('title') if citations else 'None'}")

    # 9. Citation Drawer Retrieval
    first_chunk_id = next((c.get("source_id") for c in citations if c.get("source_type") == "filing"), None)
    if first_chunk_id:
        code, chunk_detail = get(f"/documents/chunks/{first_chunk_id}")
        check("Citation Drawer Document Chunk Retrieval", code == 200 and "snippet" in chunk_detail, f"Title: {chunk_detail.get('title')}, Source: {chunk_detail.get('source_label')}")
    else:
        check("Citation Drawer Document Chunk Retrieval", False, "No filing chunk id found")

    # 10. Planted Volume Anomaly (ADANIENT)
    vol_out = meena_res.get("signals", {}).get("Volume Anomaly Agent", {})
    check("Planted Volume Anomaly Detected on ADANIENT", vol_out.get("signal") == "anomalous" and vol_out.get("metrics", {}).get("volume_zscore", 0) >= 2.0, f"Signal: {vol_out.get('signal')}, Z-Score: {vol_out.get('metrics', {}).get('volume_zscore')}")

    # 11. Cross-Agent Signal Conflict Handling (TATAMOTORS)
    code, tata_res = post("/analyze", {"ticker": "TATAMOTORS", "user_id": "arjun"})
    conflict_obj = tata_res.get("conflict", {})
    check("TATAMOTORS Cross-Agent Conflict Detected", conflict_obj.get("conflict") is True and tata_res.get("recommendation", {}).get("action") == "wait", f"Disagreement Score: {conflict_obj.get('disagreement_score')}, Explanation: {conflict_obj.get('explanation')[:80]}...")

    # 12. Graceful Degradation: Feed Down Simulation
    code, feed_down_res = post("/analyze", {"ticker": "RELIANCE", "user_id": "meena", "simulate_feed_down": True})
    check("Graceful Handling of Down Price Feed", code == 200 and feed_down_res.get("recommendation", {}).get("degraded_flag") is True, f"Data Mode: {feed_down_res.get('data_mode')}, Degraded Flag: {feed_down_res.get('recommendation', {}).get('degraded_flag')}")

    # 13. Graceful Degradation: Missing Filing (WIPRO)
    code, wipro_res = post("/analyze", {"ticker": "WIPRO", "user_id": "arjun"})
    filing_sig = wipro_res.get("signals", {}).get("Filings RAG Agent", {})
    check("Graceful Handling of Missing Filing (WIPRO)", code == 200 and filing_sig.get("signal") == "no_data" and filing_sig.get("status") == "degraded", f"Filings Signal: {filing_sig.get('signal')}, Notes: {filing_sig.get('notes')}")

    # 14. Performance Logging & Session Metrics
    metrics = meena_res.get("session_metrics", {})
    has_req_metrics = "latency_total_ms" in metrics and "concentration_before" in metrics and "retrieval_relevance" in metrics
    check("Measurable Session Metrics Captured (>= 3 Metrics)", has_req_metrics, f"Total Latency: {metrics.get('latency_total_ms')}ms, HHI Before: {metrics.get('concentration_before')}, Retrieval Relevance: {metrics.get('retrieval_relevance')}")

    # 15. 18-Month Historical Walk-Forward Backtesting
    code, backtest = get("/metrics/backtest")
    check("18-Month Historical Backtesting Suite", code == 200 and len(backtest) >= 2, f"Evaluated {len(backtest)} agents across 18-month historical price data")

    # 16. Regulatory Non-Advisory Disclaimer
    disclaimer = meena_res.get("disclaimer", "")
    check("Mandatory SEBI Research Analyst Disclaimer Present", len(disclaimer) > 20 and "SEBI" in disclaimer, f"Disclaimer: {disclaimer[:70]}...")

    print("=" * 70)
    print(f"VERIFICATION SUMMARY: {checks_passed} / {total_checks} CHECKS PASSED ({(checks_passed/total_checks)*100:.1f}%)")
    print("=" * 70)

    if checks_passed == total_checks:
        print("\nALL MANDATORY MVP AND EXTENSION REQUIREMENTS FULLY SATISFIED!\n")
        sys.exit(0)
    else:
        print("\nSOME CHECKS FAILED. INVESTIGATION REQUIRED.\n")
        sys.exit(1)

if __name__ == "__main__":
    run_e2e_checks()

