"""
Generates visual diagrams for VibeFinance using Pillow.
Outputs:
- docs/images/architecture_diagram.png
- docs/images/data_flow_diagram.png
- docs/images/ui_terminal_diagram.png
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Helper to get font safely
def get_font(size=14, bold=False):
    font_names = ["segoeui.ttf", "arial.ttf", "calibri.ttf"]
    if bold:
        font_names = ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"]
    for fn in font_names:
        try:
            return ImageFont.truetype(fn, size)
        except:
            pass
    return ImageFont.load_default()

def draw_rounded_rect(draw, xy, fill, outline=None, width=1, radius=8):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def generate_architecture_diagram():
    w, h = 1200, 680
    im = Image.new("RGB", (w, h), color="#0B1120")
    draw = ImageDraw.Draw(im)

    f_title = get_font(22, bold=True)
    f_subtitle = get_font(13, bold=False)
    f_header = get_font(14, bold=True)
    f_body = get_font(11, bold=False)
    f_bold = get_font(11, bold=True)
    f_small = get_font(10, bold=False)

    # Title Banner
    draw.text((40, 25), "VIBEFINANCE | MULTI-AGENT SYSTEM ARCHITECTURE", fill="#38BDF8", font=f_title)
    draw.text((40, 56), "End-to-End Autonomous Financial Intelligence DAG (LangGraph + Corrective RAG + Gemini)", fill="#94A3B8", font=f_subtitle)
    draw.line((40, 80, 1160, 80), fill="#1E293B", width=2)

    # Col 1: Ingestion
    c1_x, c1_y, c1_w, c1_h = 40, 100, 240, 540
    draw_rounded_rect(draw, (c1_x, c1_y, c1_x+c1_w, c1_y+c1_h), fill="#0F172A", outline="#334155", radius=10)
    draw.text((c1_x+15, c1_y+15), "1. DATA INGESTION", fill="#F8FAFC", font=f_header)
    draw.text((c1_x+15, c1_y+35), "Multi-Source Resilient Provider", fill="#64748B", font=f_small)

    sources = [
        ("OHLCV Price Series", "18 Nifty 50 Tickers\n2 Years (500 bars)\nCSV Snapshots", "#38BDF8"),
        ("SEBI Statutory Filings", "Regulation 30/31\nCorporate Disclosures\nEarnings Transcripts", "#A855F7"),
        ("Curated News Corpus", "300+ Indian Headlines\nRecency-Weighted\nSentiment Polarity", "#F59E0B"),
        ("Institutional Flows", "90-Day FII/DII Net\nDaily Purchases/Sales\nLiquidity Inflows", "#10B981")
    ]
    sy = c1_y + 60
    for name, desc, col in sources:
        draw_rounded_rect(draw, (c1_x+12, sy, c1_x+c1_w-12, sy+90), fill="#1E293B", outline=col, radius=6)
        draw.text((c1_x+22, sy+8), name, fill=col, font=f_bold)
        draw.text((c1_x+22, sy+28), desc, fill="#94A3B8", font=f_small)
        sy += 105

    draw_rounded_rect(draw, (c1_x+12, sy, c1_x+c1_w-12, sy+50), fill="#1E1B4B", outline="#6366F1", radius=6)
    draw.text((c1_x+22, sy+8), "ResilientProvider Fallback", fill="#818CF8", font=f_bold)
    draw.text((c1_x+22, sy+26), "Simulate Feed Down / Cache", fill="#94A3B8", font=f_small)

    # Col 2: Deterministic Core & Parallel Agents
    c2_x, c2_y, c2_w, c2_h = 310, 100, 360, 540
    draw_rounded_rect(draw, (c2_x, c2_y, c2_x+c2_w, c2_y+c2_h), fill="#0F172A", outline="#334155", radius=10)
    draw.text((c2_x+15, c2_y+15), "2. SPECIALIZED PARALLEL AGENTS", fill="#F8FAFC", font=f_header)
    draw.text((c2_x+15, c2_y+35), "LangGraph Parallel Fan-Out (asyncio.gather)", fill="#64748B", font=f_small)

    agents = [
        ("Momentum Agent (Weight: 0.25)", "Wilder RSI(14) | MACD(12,26,9) | SMAs 20/50/200\nScoring: [-4, +4] -> Bullish / Bearish", "#38BDF8"),
        ("Volume Anomaly Agent (Weight: 0.15)", "20-Day Rolling Z-Score (Z >= 2.0 -> Anomalous)\nDetects Institutional Accumulation vs. Distribution", "#F59E0B"),
        ("Sentiment Agent (Weight: 0.20)", "Exp Decay Half-Life 5d (lambda=0.1386)\nCurated Headline Polarity & Stance Scoring", "#EC4899"),
        ("Filings RAG Agent (Weight: 0.30)", "Corrective RAG (CRAG) + 384-dim Dense Vectors\nTop-k Relevance Gated | Citation Guardrails", "#A855F7"),
        ("Institutional Flow Agent (Weight: 0.10)", "5-Day Rolling Net Flow (FII + DII)\nMacro Institutional Liquidity Direction", "#10B981")
    ]
    ay = c2_y + 60
    for name, desc, col in agents:
        draw_rounded_rect(draw, (c2_x+12, ay, c2_x+c2_w-12, ay+75), fill="#1E293B", outline=col, radius=6)
        draw.text((c2_x+22, ay+8), name, fill=col, font=f_bold)
        draw.text((c2_x+22, ay+28), desc, fill="#94A3B8", font=f_small)
        ay += 90

    # Col 3: Coordination, Risk & Synthesis
    c3_x, c3_y, c3_w, c3_h = 700, 100, 460, 540
    draw_rounded_rect(draw, (c3_x, c3_y, c3_x+c3_w, c3_y+c3_h), fill="#0F172A", outline="#334155", radius=10)
    draw.text((c3_x+15, c3_y+15), "3. SYNTHESIS & PERSONALIZATION ENGINE", fill="#F8FAFC", font=f_header)
    draw.text((c3_x+15, c3_y+35), "Conflict Resolution, Suitability Caps & Citation Guard", fill="#64748B", font=f_small)

    # Box 1: Conflict Detector
    draw_rounded_rect(draw, (c3_x+15, c3_y+60, c3_x+c3_w-15, c3_y+155), fill="#1E293B", outline="#F59E0B", radius=6)
    draw.text((c3_x+25, c3_y+70), "Cross-Agent Conflict Detector (Disagreement Variance)", fill="#FBBF24", font=f_bold)
    draw.text((c3_x+25, c3_y+92), "• Computes Disagreement Variance: sigma_signals across agents\n• If sigma > 0.40 (e.g. TATAMOTORS) -> Overrides to WAIT\n• Generates Plain-English Rationale for Opposing Signals", fill="#CBD5E1", font=f_small)

    # Box 2: Risk & Personalization
    draw_rounded_rect(draw, (c3_x+15, c3_y+170, c3_x+c3_w-15, c3_y+285), fill="#1E293B", outline="#38BDF8", radius=6)
    draw.text((c3_x+25, c3_y+180), "Personalized Risk & Behavioral Profiling (3 Personas)", fill="#38BDF8", font=f_bold)
    draw.text((c3_x+25, c3_y+202), "• Meena (Conservative): 22% Vol Ceiling -> 0% Cap on High-Beta\n• Arjun (Aggressive): Accommodates Growth Volatility (15% Cap)\n• Rohan (Overtrader): Mandatory 48-Hour Cooling-Off Behavioral Alert\n• Portfolio Herfindahl-Hirschman Concentration (HHI) Sizing", fill="#CBD5E1", font=f_small)

    # Box 3: Synthesis Layer
    draw_rounded_rect(draw, (c3_x+15, c3_y+300, c3_x+c3_w-15, c3_y+415), fill="#1E293B", outline="#10B981", radius=6)
    draw.text((c3_x+25, c3_y+310), "Synthesis Layer & Strict Citation Guard", fill="#34D399", font=f_bold)
    draw.text((c3_x+25, c3_y+332), "• Weighted Composite Scoring -> ACCUMULATE / HOLD / AVOID / WAIT\n• Citation Guard: Reject ungrounded calls; requires verified citations\n• Grounded Gemini Synthesis with Inline Citing ([1], [2])\n• SEBI Non-Advisory Notice Insertion", fill="#CBD5E1", font=f_small)

    # Box 4: Presentation / Output
    draw_rounded_rect(draw, (c3_x+15, c3_y+430, c3_x+c3_w-15, c3_y+520), fill="#0284C7", outline="#38BDF8", radius=6)
    draw.text((c3_x+25, c3_y+440), "Next.js 14 Financial Intelligence Dashboard", fill="#FFFFFF", font=f_bold)
    draw.text((c3_x+25, c3_y+462), "• SSE Streaming Latency Timeline & Parallel Benchmark (2.5x)\n• Candlestick + Volume Anomaly Chart | 5 Real-Time Signal Cards\n• Sourced Recommendation Card + Slide-Out Citation Drawer", fill="#E0F2FE", font=f_small)

    path = os.path.join(OUTPUT_DIR, "architecture_diagram.png")
    im.save(path, quality=95)
    print(f"Saved: {path}")

def generate_data_flow_diagram():
    w, h = 1200, 600
    im = Image.new("RGB", (w, h), color="#0B1120")
    draw = ImageDraw.Draw(im)

    f_title = get_font(22, bold=True)
    f_subtitle = get_font(13, bold=False)
    f_header = get_font(14, bold=True)
    f_bold = get_font(11, bold=True)
    f_small = get_font(10, bold=False)

    draw.text((40, 25), "VIBEFINANCE | DATA ARCHITECTURE & FLOW MATRIX", fill="#38BDF8", font=f_title)
    draw.text((40, 56), "Ingestion, Deterministic Mathematical Transformation & Gated RAG Corpus", fill="#94A3B8", font=f_subtitle)
    draw.line((40, 80, 1160, 80), fill="#1E293B", width=2)

    cards = [
        ("OHLCV Price Series", "18 Nifty Stocks\n500 Daily Bars / Stock", [
            ("Raw Attributes", "Date, Open, High, Low, Close, Volume"),
            ("Math Transforms", "RSI(14) Wilder Smoothing\nMACD(12,26,9) & Signal Line\nSMA 20, 50, 200 Days\nRolling Volume Z-Score (20d)\n60-Day Annualized Volatility"),
            ("Output Signal", "Momentum: Bullish/Bearish [-4, +4]\nVolume: Anomalous (Z >= 2.0)")
        ], "#38BDF8"),
        ("SEBI Corporate Filings", "20 Statutory Disclosures\n17 Stocks (WIPRO = 0)", [
            ("Raw Attributes", "Title, Reg 30/31, Transcripts, Date"),
            ("Math Transforms", "Semantic Chunking (500 tokens)\n384-dim Dense Vector Embeddings\nCosine Similarity Relevance Gating\nCorrective Query Rewriting"),
            ("Output Signal", "Filings: Bullish/Bearish/No-Data\nVerified [1], [2] Chunk Citations")
        ], "#A855F7"),
        ("Curated News Headlines", "300+ Verified Articles\n15-25 Headlines / Stock", [
            ("Raw Attributes", "Headline, Publisher, Timestamp, URL"),
            ("Math Transforms", "Recency Decay: w = exp(-0.1386 * dt)\n5-Day Half-Life Weighting\nHeadline Sentiment Polarity Aggregation\nFinBERT/Gemini Stance Classification"),
            ("Output Signal", "Sentiment: Bullish (>+0.20)\nBearish (<-0.20) / Neutral")
        ], "#F59E0B"),
        ("Macro Institutional Flows", "90 Continuous Days\nDaily FII & DII Cash", [
            ("Raw Attributes", "FII Net, DII Net, Total Net (INR Cr)"),
            ("Math Transforms", "5-Day Rolling Institutional Sum\nNet Directional Liquidity Threshold\n+/- 1500 Cr Significance Boundary\nExchange Macro Liquidity Trend"),
            ("Output Signal", "Flow: Net Buying / Net Selling\nConfidence: 0.50 to 0.85")
        ], "#10B981")
    ]

    cx = 40
    cw = 265
    for title, subtitle, rows, col in cards:
        draw_rounded_rect(draw, (cx, 100, cx+cw, 560), fill="#0F172A", outline="#334155", radius=8)
        draw_rounded_rect(draw, (cx, 100, cx+cw, 160), fill="#1E293B", outline=col, radius=8)
        draw.text((cx+15, 112), title, fill=col, font=f_header)
        draw.text((cx+15, 134), subtitle, fill="#94A3B8", font=f_small)

        ry = 180
        for r_hdr, r_txt in rows:
            draw_rounded_rect(draw, (cx+10, ry, cx+cw-10, ry+105), fill="#111827", outline="#1F2937", radius=6)
            draw.text((cx+18, ry+8), r_hdr, fill="#F8FAFC", font=f_bold)
            draw.text((cx+18, ry+28), r_txt, fill="#CBD5E1", font=f_small)
            ry += 120

        cx += cw + 25

    path = os.path.join(OUTPUT_DIR, "data_flow_diagram.png")
    im.save(path, quality=95)
    print(f"Saved: {path}")

def generate_ui_terminal_diagram():
    w, h = 1200, 750
    im = Image.new("RGB", (w, h), color="#0B1120")
    draw = ImageDraw.Draw(im)

    f_title = get_font(20, bold=True)
    f_subtitle = get_font(12, bold=False)
    f_header = get_font(13, bold=True)
    f_bold = get_font(11, bold=True)
    f_small = get_font(9.5, bold=False)
    f_badge = get_font(10, bold=True)

    # Window Header
    draw_rounded_rect(draw, (20, 20, 1180, 730), fill="#020617", outline="#1E293B", radius=12)
    draw_rounded_rect(draw, (20, 20, 1180, 80), fill="#0F172A", outline="#334155", radius=12)

    # Mac dots
    draw.ellipse((40, 45, 52, 57), fill="#EF4444")
    draw.ellipse((60, 45, 72, 57), fill="#F59E0B")
    draw.ellipse((80, 45, 92, 57), fill="#10B981")

    draw.text((115, 38), "⚡ VibeFinance", fill="#38BDF8", font=f_title)
    draw.text((275, 42), "|  Persona: Meena Patel (Conservative) ▼  |  Stock: ADANIENT (Rs 4016.55) ▼  |  Data: Snapshot [Cached]", fill="#94A3B8", font=f_subtitle)

    # Top Bar Action Buttons
    draw_rounded_rect(draw, (850, 36, 950, 64), fill="#1E293B", outline="#38BDF8", radius=5)
    draw.text((862, 43), "Compare Personas", fill="#38BDF8", font=f_small)

    draw_rounded_rect(draw, (960, 36, 1055, 64), fill="#1E293B", outline="#A855F7", radius=5)
    draw.text((972, 43), "Vector Search", fill="#C084FC", font=f_small)

    draw_rounded_rect(draw, (1065, 36, 1160, 64), fill="#7F1D1D", outline="#EF4444", radius=5)
    draw.text((1075, 43), "Simulate Feed Down", fill="#FCA5A5", font=f_small)

    # Left Panel: Profile & Portfolio
    draw_rounded_rect(draw, (35, 95, 275, 560), fill="#0F172A", outline="#1E293B", radius=8)
    draw.text((50, 110), "INVESTOR PROFILE & PORTFOLIO", fill="#F8FAFC", font=f_header)
    draw.text((50, 135), "Persona: Meena Patel (Retiree, 62)\nHorizon: 3 Years | Tolerance: Conservative\nMax Volatility Ceiling: 22.0%", fill="#94A3B8", font=f_small)

    draw.line((50, 185, 260, 185), fill="#1E293B", width=1)
    draw.text((50, 195), "PORTFOLIO VALUATION", fill="#38BDF8", font=f_bold)
    draw.text((50, 215), "Total Value: Rs 3,61,034.00\nCash Balance: Rs 42,500.00\nActive Positions: 6 Equities", fill="#CBD5E1", font=f_small)

    draw.line((50, 270, 260, 270), fill="#1E293B", width=1)
    draw.text((50, 280), "SECTOR EXPOSURE LIMITS", fill="#F59E0B", font=f_bold)
    draw.text((50, 300), "Banking:  24.5% / 25% max (0.5% left)\nIT Sector: 18.0% / 20% max (2.0% left)\nEnergy:    12.4% / 15% max (2.6% left)", fill="#CBD5E1", font=f_small)

    draw.line((50, 360, 260, 360), fill="#1E293B", width=1)
    draw.text((50, 370), "HERFINDAHL CONCENTRATION (HHI)", fill="#EC4899", font=f_bold)
    draw.text((50, 390), "Current HHI Score: 0.4048 (High)\nPost-Trade Simulated HHI: 0.4048\nStatus: Breaches diversification limit\nRecommendation: Diversify holdings", fill="#CBD5E1", font=f_small)

    # Center Panel: Candlestick + 5 Signal Cards
    draw_rounded_rect(draw, (290, 95, 830, 320), fill="#0F172A", outline="#1E293B", radius=8)
    draw.text((305, 110), "ADANIENT | DAILY CANDLESTICK & VOLUME ANOMALY CHART", fill="#F8FAFC", font=f_header)
    draw.text((305, 130), "Current: Rs 4016.55 (-3.50%) | SMA20: Rs 4200.64 | SMA50: Rs 4075.87 | SMA200: Rs 3759.70", fill="#64748B", font=f_small)

    # Simulated chart graphics
    draw.line((320, 250, 800, 250), fill="#1E293B", width=1)
    draw.line((320, 210, 500, 190), fill="#38BDF8", width=2) # SMA20
    draw.line((500, 190, 800, 230), fill="#38BDF8", width=2)
    draw.line((320, 230, 800, 210), fill="#F59E0B", width=2) # SMA50

    # Volume anomaly bar
    draw_rounded_rect(draw, (710, 250, 735, 305), fill="#EF4444", radius=2)
    draw_rounded_rect(draw, (700, 215, 745, 235), fill="#7F1D1D", outline="#EF4444", radius=4)
    draw.text((706, 220), "Z: 5.76!", fill="#FCA5A5", font=f_badge)

    # 5 Parallel Signal Cards
    sig_w = 102
    signals = [
        ("Momentum", "BEARISH", "Conf: 76%", "RSI: 42.2\nMACD: -24.0", "#EF4444", "#7F1D1D"),
        ("Volume Anom", "ANOMALOUS", "Conf: 85%", "4.3x 20d Vol\nZ = 5.76", "#EF4444", "#7F1D1D"),
        ("Sentiment", "BEARISH", "Conf: 80%", "Score: -0.237\n5 Headlines", "#EF4444", "#7F1D1D"),
        ("Filings RAG", "BEARISH", "Conf: 85%", "Reg 31(1)\nPledge: 19%", "#A855F7", "#581C87"),
        ("Inst Flow", "NET BUYING", "Conf: 65%", "5d Flow:\n+Rs 1840 Cr", "#10B981", "#064E3B")
    ]
    sx = 290
    for name, sig, conf, metrics, txt_col, bg_col in signals:
        draw_rounded_rect(draw, (sx, 430, sx+sig_w, 560), fill="#0F172A", outline="#1E293B", radius=6)
        draw.text((sx+8, 438), name, fill="#F8FAFC", font=f_bold)
        draw_rounded_rect(draw, (sx+8, 458, sx+sig_w-8, 478), fill=bg_col, radius=4)
        draw.text((sx+12, 462), sig, fill=txt_col, font=f_badge)
        draw.text((sx+8, 485), conf, fill="#94A3B8", font=f_small)
        draw.text((sx+8, 505), metrics, fill="#CBD5E1", font=f_small)
        sx += sig_w + 8

    # Right Panel: Recommendation Card
    draw_rounded_rect(draw, (845, 95, 1165, 560), fill="#0F172A", outline="#1E293B", radius=8)
    draw.text((860, 110), "SOURCED RECOMMENDATION", fill="#F8FAFC", font=f_header)

    # Action badge
    draw_rounded_rect(draw, (860, 135, 990, 170), fill="#7F1D1D", outline="#EF4444", radius=6)
    draw.text((875, 143), "WAIT / AVOID", fill="#FCA5A5", font=f_title)

    draw.text((860, 185), "Suitability Sizing Cap: 0.0% (Risk Ceiling)", fill="#EF4444", font=f_bold)
    draw.text((860, 205), "Composite Confidence: 45.0% | Horizon: 3y", fill="#94A3B8", font=f_small)

    # Summary Text with Inline Citations
    draw.text((860, 230), "Synthesis Reasoning:", fill="#38BDF8", font=f_bold)
    summary_text = (
        "ADANIENT exhibits severe governance\n"
        "and volatility risks. Regulatory filings\n"
        "confirm promoter pledge increased from\n"
        "12% to 19% [1], accompanied by an\n"
        "anomalous 4.29x volume distribution surge\n"
        "[2]. Stock 60-day volatility (36.1%) violates\n"
        "Meena's 22.0% retiree safety limit."
    )
    draw.text((860, 252), summary_text, fill="#E2E8F0", font=f_small)

    # Verified Citations
    draw.text((860, 360), "Verified Grounding Evidence:", fill="#A855F7", font=f_bold)
    draw_rounded_rect(draw, (860, 380, 1150, 425), fill="#1E1B4B", outline="#6366F1", radius=5)
    draw.text((868, 386), "[1] SEBI Reg 31(1) Pledge Filing (SYNTHETIC)", fill="#C7D2FE", font=f_bold)
    draw.text((868, 404), "Promoter pledge increased from 12% to 19.2%...", fill="#A5B4FC", font=f_small)

    draw_rounded_rect(draw, (860, 435, 1150, 480), fill="#1E293B", outline="#334155", radius=5)
    draw.text((868, 441), "[2] Daily Volume Anomaly Z-Score (NSE)", fill="#93C5FD", font=f_bold)
    draw.text((868, 459), "Turnover spike Z=5.76 with -3.5% price decline...", fill="#BFDBFE", font=f_small)

    # SEBI Disclaimer
    draw_rounded_rect(draw, (860, 495, 1150, 545), fill="#1C1917", outline="#78350F", radius=5)
    draw.text((868, 502), "SEBI Non-Advisory Notice:", fill="#FBBF24", font=f_badge)
    draw.text((868, 518), "Educational decision-support model only. Not certified advice.", fill="#FDE68A", font=f_small)

    # Bottom Panel: SSE Latency & Backtesting
    draw_rounded_rect(draw, (35, 575, 1165, 715), fill="#0F172A", outline="#1E293B", radius=8)
    draw.text((50, 588), "REAL-TIME TELEMETRY & 18-MONTH WALK-FORWARD BACKTESTING SUITE", fill="#F8FAFC", font=f_header)

    # Telemetry Left
    draw.text((50, 615), "Live Execution Latency Graph (SSE):", fill="#38BDF8", font=f_bold)
    draw.text((50, 635), "Parallel DAG Execution: 25 ms | Estimated Sequential Execution: 65 ms\nSpeedup Acceleration Factor: 2.5x Faster | Retrieval Relevance: 1.00", fill="#CBD5E1", font=f_small)

    # Backtest Right
    draw.text((650, 615), "Historical Signal Win Rates (30-Day Forward Returns):", fill="#10B981", font=f_bold)
    draw.text((650, 635), "Momentum: 49.6% (940 signals) | Volume Anomaly: 54.3% (70 signals)\nBuy & Hold Nifty Benchmark: 44.2% | Strategy Alpha: +10.1% Win Rate", fill="#CBD5E1", font=f_small)

    path = os.path.join(OUTPUT_DIR, "ui_terminal_diagram.png")
    im.save(path, quality=95)
    print(f"Saved: {path}")

if __name__ == "__main__":
    generate_architecture_diagram()
    generate_data_flow_diagram()
    generate_ui_terminal_diagram()

