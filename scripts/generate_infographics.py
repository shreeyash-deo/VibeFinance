"""
Generates visual infographic diagrams for VibeFinance PDF:
1. agent_weights_circular_diagram.png (Circular Donut Chart + Agent Indicator Cards)
2. conflict_and_risk_flow_diagram.png (Conflict Engine -> Risk Engine -> Synthesis Decision Tree)
3. tech_stack_infographic.png (4-Tier Technology Stack Architecture)
4. personas_infographic_cards.png (Visual Persona Cards with Circular Gauges)
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

def generate_agent_weights_circular():
    w, h = 1200, 520
    im = Image.new("RGB", (w, h), color="#0F172A")
    draw = ImageDraw.Draw(im)

    f_title = get_font(20, bold=True)
    f_sub = get_font(12, bold=False)
    f_card_hdr = get_font(12, bold=True)
    f_card_txt = get_font(9.5, bold=False)
    f_center_lg = get_font(22, bold=True)
    f_center_sm = get_font(10, bold=True)

    draw.text((40, 20), "SPECIALIZED AGENT WEIGHTING & MATHEMATICAL ENGINE", fill="#38BDF8", font=f_title)
    draw.text((40, 48), "Circular Composite Allocation & Deterministic Indicator Core (Python Pandas/NumPy)", fill="#94A3B8", font=f_sub)
    draw.line((40, 72, 1160, 72), fill="#1E293B", width=2)

    # Donut Center & Dimensions
    cx, cy, r_out, r_in = 220, 290, 160, 95
    bbox_out = (cx - r_out, cy - r_out, cx + r_out, cy + r_out)
    bbox_in = (cx - r_in, cy - r_in, cx + r_in, cy + r_in)

    segments = [
        ("Filings RAG", 30, "#8B5CF6", "Corrective RAG (CRAG) + 384-dim Vectors\nTop-8 Chunk Retrieval | Grounding Guardrails\nReg 30/31 Disclosures & Transcripts"),
        ("Momentum", 25, "#0EA5E9", "Wilder RSI(14) | MACD(12,26,9) | SMAs 20/50/200\nTrend Scoring [-4, +4] -> Bullish/Bearish\nDistance from 52-Week High & 20d Returns"),
        ("Sentiment", 20, "#EC4899", "Curated News Polarity with 5-Day Recency Half-Life\nw_i = exp(-0.1386 * delta_t)\nHeadline Polarity Aggregation & Stance"),
        ("Volume Anom", 15, "#F59E0B", "20-Day Rolling Volume Z-Score: Z >= 2.0\nDetects Accumulation vs Distribution\nDirection derived from concurrent 1-day return"),
        ("Inst. Flow", 10, "#10B981", "5-Day Rolling Net Institutional Capital (FII + DII)\nLiquidity Boundary: +/- Rs 1500 Cr\nMacro Liquidity Injection / Withdrawal")
    ]

    # Draw Donut Wedges
    start_angle = -90
    for name, pct, col, _ in segments:
        sweep = (pct / 100.0) * 360.0
        end_angle = start_angle + sweep
        draw.pieslice(bbox_out, start=start_angle, end=end_angle, fill=col)
        start_angle = end_angle

    # Punch Hole for Donut
    draw.ellipse(bbox_in, fill="#0F172A")
    draw.ellipse((cx - r_in - 2, cy - r_in - 2, cx + r_in + 2, cy + r_in + 2), outline="#1E293B", width=2)

    # Donut Center Text
    draw.text((cx - 45, cy - 25), "100%", fill="#FFFFFF", font=f_center_lg)
    draw.text((cx - 52, cy + 5), "COMPOSITE", fill="#38BDF8", font=f_center_sm)
    draw.text((cx - 58, cy + 20), "WEIGHTING", fill="#94A3B8", font=f_center_sm)

    # Draw Right Side Cards
    card_x = 440
    card_w = 720
    card_h = 74
    cy_start = 90

    for name, pct, col, desc in segments:
        draw_rounded_rect(draw, (card_x, cy_start, card_x + card_w, cy_start + card_h), fill="#1E293B", outline=col, radius=8)
        
        # Color Pill on Left
        draw_rounded_rect(draw, (card_x + 12, cy_start + 12, card_x + 75, cy_start + card_h - 12), fill=col, radius=6)
        draw.text((card_x + 22, cy_start + 24), f"{pct}%", fill="#FFFFFF", font=get_font(16, bold=True))

        # Title & Description
        draw.text((card_x + 90, cy_start + 10), f"{name} Agent", fill=col, font=f_card_hdr)
        draw.text((card_x + 90, cy_start + 30), desc, fill="#CBD5E1", font=f_card_txt)

        cy_start += card_h + 10

    path = os.path.join(OUTPUT_DIR, "agent_weights_circular_diagram.png")
    im.save(path, quality=95)
    print(f"Saved: {path}")

def generate_conflict_and_risk_flow():
    w, h = 1200, 560
    im = Image.new("RGB", (w, h), color="#0F172A")
    draw = ImageDraw.Draw(im)

    f_title = get_font(20, bold=True)
    f_sub = get_font(12, bold=False)
    f_box_hdr = get_font(13, bold=True)
    f_box_bold = get_font(10.5, bold=True)
    f_box_txt = get_font(9.5, bold=False)

    draw.text((40, 20), "SAFETY GUARDRAILS: CONFLICT DETECTION & RISK SIZING PIPELINE", fill="#38BDF8", font=f_title)
    draw.text((40, 48), "Cross-Agent Disagreement Variance (sigma) & Personalized Behavioral Economics Decision Tree", fill="#94A3B8", font=f_sub)
    draw.line((40, 72, 1160, 72), fill="#1E293B", width=2)

    # Box 1: Conflict Detector (Left)
    b1_x, b1_y, b1_w, b1_h = 40, 95, 340, 435
    draw_rounded_rect(draw, (b1_x, b1_y, b1_x + b1_w, b1_y + b1_h), fill="#1E293B", outline="#F59E0B", radius=10)
    draw.text((b1_x + 16, b1_y + 16), "1. CONFLICT DETECTION ENGINE", fill="#FBBF24", font=f_box_hdr)
    draw.text((b1_x + 16, b1_y + 36), "Quantifies cross-agent divergence", fill="#94A3B8", font=f_box_txt)

    c_steps = [
        ("Signal Value Mapping", "Bullish = +1.0\nNeutral = 0.0\nBearish = -1.0", "#38BDF8"),
        ("Disagreement Variance Score", "sigma_signals = StdDev([s1, s2, s3, s4, s5])\nContinuous metric of agent polarization", "#F59E0B"),
        ("Conflict Threshold Trigger", "If sigma > 0.40 and opposing signals coexist:\n• Flags amber analytical conflict alert\n• Documents opposing divergence pairs\n• Forces synthesis action to WAIT", "#EF4444")
    ]
    sy = b1_y + 65
    for title, desc, col in c_steps:
        draw_rounded_rect(draw, (b1_x + 12, sy, b1_x + b1_w - 12, sy + 105), fill="#0F172A", outline=col, radius=6)
        draw.text((b1_x + 20, sy + 10), title, fill=col, font=f_box_bold)
        draw.text((b1_x + 20, sy + 32), desc, fill="#CBD5E1", font=f_box_txt)
        sy += 120

    # Box 2: Risk & Behavioral Profiling (Center)
    b2_x, b2_y, b2_w, b2_h = 420, 95, 340, 435
    draw_rounded_rect(draw, (b2_x, b2_y, b2_x + b2_w, b2_y + b2_h), fill="#1E293B", outline="#38BDF8", radius=10)
    draw.text((b2_x + 16, b2_y + 16), "2. PERSONALIZED RISK ENGINE", fill="#38BDF8", font=f_box_hdr)
    draw.text((b2_x + 16, b2_y + 36), "Tailors allocation to investor parameters", fill="#94A3B8", font=f_box_txt)

    r_steps = [
        ("Volatility Ceiling Filter", "Conservative: Max 22% 60d volatility\nModerate: Max 32% volatility\nAggressive: Uncapped\nBreach -> 0% allocation (AVOID/WAIT)", "#38BDF8"),
        ("Herfindahl Concentration (HHI)", "HHI = Sum(w_i ^ 2)\nDelta HHI = HHI_post - HHI_pre\nCaps position if post-trade HHI > 0.30\nPrevents portfolio overconcentration", "#A855F7"),
        ("Behavioral Cooling-off Nudge", "Overtrading score > 0.60 or recent panic sells:\n• Triggers mandatory 48h cooling-off\n• Insulates against emotional drawdowns", "#EC4899")
    ]
    sy = b2_y + 65
    for title, desc, col in r_steps:
        draw_rounded_rect(draw, (b2_x + 12, sy, b2_x + b2_w - 12, sy + 105), fill="#0F172A", outline=col, radius=6)
        draw.text((b2_x + 20, sy + 10), title, fill=col, font=f_box_bold)
        draw.text((b2_x + 20, sy + 32), desc, fill="#CBD5E1", font=f_box_txt)
        sy += 120

    # Box 3: Synthesis Rules & Decision Tree (Right)
    b3_x, b3_y, b3_w, b3_h = 800, 95, 360, 435
    draw_rounded_rect(draw, (b3_x, b3_y, b3_x + b3_w, b3_y + b3_h), fill="#1E293B", outline="#10B981", radius=10)
    draw.text((b3_x + 16, b3_y + 16), "3. SYNTHESIS DECISION TREE", fill="#34D399", font=f_box_hdr)
    draw.text((b3_x + 16, b3_y + 36), "Weighted composite action mapping", fill="#94A3B8", font=f_box_txt)

    rules = [
        ("Rule A: Conflict Override", "IF Disagreement Variance sigma > 0.40:\nTHEN Force Action = 'WAIT'\nComposite Confidence capped at 45%", "#F59E0B"),
        ("Rule B: Suitability Hard Cap", "IF Volatility > Ceiling OR Sector Cap full:\nTHEN Force Max Position Cap = 0.0%\nAction = 'AVOID / WAIT' (Risk Suitability: POOR)", "#EF4444"),
        ("Rule C: Directional Consensus", "IF Composite Score >= +0.35 AND Risk Fits:\nTHEN Action = 'ACCUMULATE'\nCalculates personalized allocation (e.g. 5-15%)", "#10B981"),
        ("Rule D: Citation Guard", "Zero claims permitted without source attribution.\nRequires verified inline citations [1], [2].", "#8B5CF6")
    ]
    sy = b3_y + 65
    for title, desc, col in rules:
        draw_rounded_rect(draw, (b3_x + 12, sy, b3_x + b3_w - 12, sy + 80), fill="#0F172A", outline=col, radius=6)
        draw.text((b3_x + 20, sy + 8), title, fill=col, font=f_box_bold)
        draw.text((b3_x + 20, sy + 28), desc, fill="#CBD5E1", font=f_box_txt)
        sy += 90

    # Draw Connecting Arrows between Columns
    draw.polygon([(390, 310), (410, 320), (390, 330)], fill="#38BDF8")
    draw.polygon([(770, 310), (790, 320), (770, 330)], fill="#38BDF8")

    path = os.path.join(OUTPUT_DIR, "conflict_and_risk_flow_diagram.png")
    im.save(path, quality=95)
    print(f"Saved: {path}")

def generate_tech_stack_infographic():
    w, h = 1200, 480
    im = Image.new("RGB", (w, h), color="#0F172A")
    draw = ImageDraw.Draw(im)

    f_title = get_font(20, bold=True)
    f_sub = get_font(12, bold=False)
    f_tier_hdr = get_font(13, bold=True)
    f_item_hdr = get_font(11, bold=True)
    f_item_txt = get_font(9.5, bold=False)

    draw.text((40, 20), "VIBEFINANCE | FULL TECHNOLOGY STACK ARCHITECTURE", fill="#38BDF8", font=f_title)
    draw.text((40, 48), "Decoupled 4-Tier Architecture: Reactive Frontend, LangGraph DAG Engine, Vector RAG & Multi-Source Data", fill="#94A3B8", font=f_sub)
    draw.line((40, 72, 1160, 72), fill="#1E293B", width=2)

    tiers = [
        ("Tier 1: Frontend Client", "Next.js 14 & React 18", "#0284C7", [
            ("Framework & UI", "Next.js 14 App Router, TypeScript 5.5, Tailwind CSS dark financial palette"),
            ("Data Visualization", "Recharts 2.12 candlestick simulations, volume anomaly bars, HHI meters"),
            ("Reactive Streaming", "HTML5 EventSource consuming Server-Sent Events (SSE) telemetry"),
            ("UX Components", "Headless accessible modals, slide-out Citation Drawer, persona switcher")
        ]),
        ("Tier 2: Orchestration Engine", "FastAPI & LangGraph", "#8B5CF6", [
            ("ASGI Backend", "FastAPI asynchronous microservice running on Uvicorn with CORS support"),
            ("Multi-Agent DAG", "LangGraph state machine fan-out via asyncio.gather and state reducers"),
            ("Contract Enforcement", "Pydantic v2 strict schemas for AgentOutput, Evidence, and AnalysisResponse"),
            ("Math Core", "Pandas, NumPy, and SciPy deterministic technical indicators and HHI")
        ]),
        ("Tier 3: AI & Semantic RAG", "Gemini & Dense Vectors", "#EC4899", [
            ("LLM Synthesis", "Google Gemini 2.5 Flash / 1.5 Flash with prompt guardrails and citation guard"),
            ("Zero-Crash Fallback", "Deterministic algorithmic template fallbacks for 100% offline test passage"),
            ("384-dim Dense Vectors", "Dense semantic embeddings with unit-normalized cosine similarity"),
            ("Corrective RAG (CRAG)", "Top-k chunk retrieval with automated query rewriting and relevance gating")
        ]),
        ("Tier 4: Data & Protocol Layer", "Snapshots & MCP", "#10B981", [
            ("Price Snapshot Series", "2-year daily OHLCV CSVs across 18 Nifty 50 bellwethers (500 bars/ticker)"),
            ("Statutory Disclosures", "20 SEBI regulatory filings under Regulation 30/31 and earnings transcripts"),
            ("News & Flows", "300+ curated financial news articles and 90 continuous days of FII/DII net flows"),
            ("MCP Server", "Stdio JSON-RPC 2.0 interface exposing get_signals, search_filings, analyze")
        ])
    ]

    col_w = 265
    cx = 40
    for title, sub, col, items in tiers:
        draw_rounded_rect(draw, (cx, 95, cx + col_w, 450), fill="#1E293B", outline=col, radius=8)
        draw_rounded_rect(draw, (cx, 95, cx + col_w, 155), fill="#0F172A", outline=col, radius=8)
        draw.text((cx + 12, 105), title, fill=col, font=f_tier_hdr)
        draw.text((cx + 12, 128), sub, fill="#94A3B8", font=get_font(10, bold=True))

        iy = 170
        for ihdr, itxt in items:
            draw_rounded_rect(draw, (cx + 8, iy, cx + col_w - 8, iy + 62), fill="#0F172A", outline="#334155", radius=5)
            draw.text((cx + 14, iy + 6), ihdr, fill="#F8FAFC", font=f_item_hdr)
            draw.text((cx + 14, iy + 24), itxt, fill="#CBD5E1", font=f_item_txt)
            iy += 68

        cx += col_w + 20

    path = os.path.join(OUTPUT_DIR, "tech_stack_infographic.png")
    im.save(path, quality=95)
    print(f"Saved: {path}")

def generate_personas_infographic():
    w, h = 1200, 460
    im = Image.new("RGB", (w, h), color="#0F172A")
    draw = ImageDraw.Draw(im)

    f_title = get_font(20, bold=True)
    f_sub = get_font(12, bold=False)
    f_card_hdr = get_font(14, bold=True)
    f_bold = get_font(11, bold=True)
    f_txt = get_font(9.5, bold=False)

    draw.text((40, 20), "INVESTOR PERSONAS: DIFFERENTIATED INTELLIGENCE ON IDENTICAL INPUTS", fill="#38BDF8", font=f_title)
    draw.text((40, 48), "Proving Non-Generic Output: How Meena, Arjun, and Rohan receive distinct verdicts and risk caps for ADANIENT", fill="#94A3B8", font=f_sub)
    draw.line((40, 72, 1160, 72), fill="#1E293B", width=2)

    personas = [
        ("Meena Iyer", "Conservative Retiree (Age 62)", "#059669", [
            ("Investment Horizon", "3 Years (Capital Preservation)"),
            ("Volatility Ceiling", "Hard cap: 22.0% Annualized"),
            ("Portfolio Context", "Rs 3.61 Lakhs (Heavy FMCG & Banking)"),
            ("Verdict on ADANIENT", "ACTION: WAIT / AVOID | Position Cap: 0.0%"),
            ("Personalized Reason", "Stock volatility (36.1%) violates retiree safety cap.\nPromoter pledge hike flagged as intolerable governance risk.")
        ]),
        ("Arjun Mehta", "Aggressive Growth Trader (Age 29)", "#0284C7", [
            ("Investment Horizon", "10 Years (Compound Capital Growth)"),
            ("Volatility Ceiling", "Uncapped (Tolerates High Beta)"),
            ("Portfolio Context", "Rs 7.85 Lakhs (Tech & Infrastructure)"),
            ("Verdict on ADANIENT", "ACTION: WAIT | Position Cap: 15.0%"),
            ("Personalized Reason", "Growth volatility is acceptable for 10y horizon.\nCapital allocation paused only until institutional distribution clears.")
        ]),
        ("Rohan Verma", "Emotional Overtrader (Age 34)", "#D97706", [
            ("Investment Horizon", "Tactical / Frequent Turnover"),
            ("Overtrading Risk", "Score: 0.85 (4 Recent Panic Sells)"),
            ("Portfolio Context", "Rs 4.50 Lakhs (High Churn Rate)"),
            ("Verdict on ADANIENT", "ACTION: WAIT | Position Cap: 0.0%"),
            ("Behavioral Alert Box", "MANDATORY 48-HOUR COOLING-OFF PERIOD\nTriggered by elevated turnover score (0.85) to insulate\nagainst emotional drawdown reactions.")
        ])
    ]

    card_w = 360
    cx = 40
    for name, sub, col, rows in personas:
        draw_rounded_rect(draw, (cx, 95, cx + card_w, 435), fill="#1E293B", outline=col, radius=10)
        draw_rounded_rect(draw, (cx, 95, cx + card_w, 160), fill="#0F172A", outline=col, radius=10)
        draw.text((cx + 16, 108), name, fill="#FFFFFF", font=f_card_hdr)
        draw.text((cx + 16, 134), sub, fill=col, font=get_font(11, bold=True))

        ry = 175
        for rhdr, rtxt in rows:
            is_alert = "COOLING-OFF" in rtxt
            bg_col = "#78350F" if is_alert else "#0F172A"
            brd_col = "#F59E0B" if is_alert else "#334155"
            txt_col = "#FDE68A" if is_alert else "#CBD5E1"
            
            box_h = 55 if not is_alert else 65
            draw_rounded_rect(draw, (cx + 12, ry, cx + card_w - 12, ry + box_h), fill=bg_col, outline=brd_col, radius=6)
            draw.text((cx + 18, ry + 6), rhdr, fill=col if not is_alert else "#FBBF24", font=f_bold)
            draw.text((cx + 18, ry + 24), rtxt, fill=txt_col, font=f_txt)
            ry += box_h + 8

        cx += card_w + 20

    path = os.path.join(OUTPUT_DIR, "personas_infographic_cards.png")
    im.save(path, quality=95)
    print(f"Saved: {path}")

if __name__ == "__main__":
    generate_agent_weights_circular()
    generate_conflict_and_risk_flow()
    generate_tech_stack_infographic()
    generate_personas_infographic()

