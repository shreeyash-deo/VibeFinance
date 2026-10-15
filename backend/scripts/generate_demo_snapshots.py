"""
generate_demo_snapshots.py
Generates 100% self-contained demo snapshot data for VibeFinance (PS 04).
Creates:
1. data_snapshot/prices/<TICKER>.csv (2 years daily OHLCV)
2. data_snapshot/news/<TICKER>.json (15-25 curated headlines per ticker)
3. data_snapshot/flows.csv (90-day daily FII/DII institutional net flows)
4. data_snapshot/filings/<TICKER>_*.md (40-60 synthetic filings/transcripts with YAML frontmatter)
Planted edge cases:
- ADANIENT: Volume anomaly on last day + promoter pledge 12%->19% + auditor related party note
- TATAMOTORS: Bullish technical momentum + negative margin guidance cut in filing (Agent Conflict!)
- INFY: Strong deal wins, raised guidance
- HDFCBANK: Stable NIM, no red flags
- SUNPHARMA: Foreign regulator 483 observation
- ITC: Steady FMCG dividend & margins
- WIPRO: Zero filings (Graceful Degradation test case)
"""

import os
import json
import math
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAPSHOT_DIR = os.path.join(BASE_DIR, "data_snapshot")
PRICES_DIR = os.path.join(SNAPSHOT_DIR, "prices")
NEWS_DIR = os.path.join(SNAPSHOT_DIR, "news")
FILINGS_DIR = os.path.join(SNAPSHOT_DIR, "filings")

for d in [PRICES_DIR, NEWS_DIR, FILINGS_DIR]:
    os.makedirs(d, exist_ok=True)

TICKERS_INFO = {
    "RELIANCE": {"name": "Reliance Industries Ltd", "sector": "Energy", "base_price": 2850.0, "yf_symbol": "RELIANCE.NS"},
    "TCS": {"name": "Tata Consultancy Services Ltd", "sector": "Information Technology", "base_price": 4120.0, "yf_symbol": "TCS.NS"},
    "INFY": {"name": "Infosys Ltd", "sector": "Information Technology", "base_price": 1880.0, "yf_symbol": "INFY.NS"},
    "HDFCBANK": {"name": "HDFC Bank Ltd", "sector": "Banking", "base_price": 1640.0, "yf_symbol": "HDFCBANK.NS"},
    "ICICIBANK": {"name": "ICICI Bank Ltd", "sector": "Banking", "base_price": 1220.0, "yf_symbol": "ICICIBANK.NS"},
    "SBIN": {"name": "State Bank of India", "sector": "Banking", "base_price": 790.0, "yf_symbol": "SBIN.NS"},
    "ITC": {"name": "ITC Ltd", "sector": "FMCG", "base_price": 485.0, "yf_symbol": "ITC.NS"},
    "HINDUNILVR": {"name": "Hindustan Unilever Ltd", "sector": "FMCG", "base_price": 2550.0, "yf_symbol": "HINDUNILVR.NS"},
    "LT": {"name": "Larsen & Toubro Ltd", "sector": "Construction", "base_price": 3600.0, "yf_symbol": "LT.NS"},
    "BHARTIARTL": {"name": "Bharti Airtel Ltd", "sector": "Telecommunications", "base_price": 1680.0, "yf_symbol": "BHARTIARTL.NS"},
    "KOTAKBANK": {"name": "Kotak Mahindra Bank Ltd", "sector": "Banking", "base_price": 1780.0, "yf_symbol": "KOTAKBANK.NS"},
    "AXISBANK": {"name": "Axis Bank Ltd", "sector": "Banking", "base_price": 1160.0, "yf_symbol": "AXISBANK.NS"},
    "MARUTI": {"name": "Maruti Suzuki India Ltd", "sector": "Automobile", "base_price": 11800.0, "yf_symbol": "MARUTI.NS"},
    "SUNPHARMA": {"name": "Sun Pharmaceutical Industries Ltd", "sector": "Healthcare", "base_price": 1820.0, "yf_symbol": "SUNPHARMA.NS"},
    "TATAMOTORS": {"name": "Tata Motors Ltd", "sector": "Automobile", "base_price": 980.0, "yf_symbol": "TATAMOTORS.NS"},
    "ADANIENT": {"name": "Adani Enterprises Ltd", "sector": "Metals & Mining", "base_price": 2980.0, "yf_symbol": "ADANIENT.NS"},
    "ASIANPAINT": {"name": "Asian Paints Ltd", "sector": "Consumer Durables", "base_price": 2420.0, "yf_symbol": "ASIANPAINT.NS"},
    "WIPRO": {"name": "Wipro Ltd", "sector": "Information Technology", "base_price": 540.0, "yf_symbol": "WIPRO.NS"}
}

def generate_prices():
    print("Generating 2-year daily price snapshots...")
    end_date = datetime(2026, 10, 10)
    start_date = end_date - timedelta(days=730)
    
    # Generate business trading days
    date_range = pd.bdate_range(start=start_date, end=end_date)
    n_days = len(date_range)
    
    for ticker, info in TICKERS_INFO.items():
        base = info["base_price"]
        np.random.seed(abs(hash(ticker)) % (2**31))
        
        # Mean reverting random walk with drift
        daily_returns = np.random.normal(loc=0.0004, scale=0.015, size=n_days)
        
        # Specific tuning for planted scenarios:
        if ticker == "TATAMOTORS":
            # Strongly bullish technical momentum in recent 60 days
            daily_returns[-60:] += 0.003
        elif ticker == "ADANIENT":
            # High volatility
            daily_returns = np.random.normal(loc=0.0002, scale=0.025, size=n_days)
        elif ticker == "INFY":
            # Solid upward steady drift
            daily_returns[-45:] += 0.002
            
        prices = [base]
        for r in daily_returns:
            prices.append(prices[-1] * (1 + r))
        prices = np.array(prices[1:])
        
        # Generate OHLCV
        highs = prices * (1 + np.abs(np.random.normal(0.003, 0.004, n_days)))
        lows = prices * (1 - np.abs(np.random.normal(0.003, 0.004, n_days)))
        opens = lows + (highs - lows) * np.random.uniform(0.2, 0.8, n_days)
        closes = prices
        
        # Base volume
        base_vol = np.random.uniform(800000, 4500000, n_days)
        vol_noise = np.random.lognormal(mean=0.0, sigma=0.35, size=n_days)
        volumes = (base_vol * vol_noise).astype(int)
        
        # Injected planted volume anomaly for ADANIENT on the last day:
        if ticker == "ADANIENT":
            volumes[-1] = int(volumes[-20:].mean() * 4.2)  # Z-score > 3.5
            closes[-1] = closes[-2] * 0.965  # Price down on heavy volume
            lows[-1] = min(lows[-1], closes[-1] * 0.99)
            
        df = pd.DataFrame({
            "Date": [d.strftime("%Y-%m-%d") for d in date_range],
            "Open": np.round(opens, 2),
            "High": np.round(highs, 2),
            "Low": np.round(lows, 2),
            "Close": np.round(closes, 2),
            "Volume": volumes
        })
        
        df.to_csv(os.path.join(PRICES_DIR, f"{ticker}.csv"), index=False)
    print(f"Generated price CSVs for {len(TICKERS_INFO)} tickers.")

def generate_flows():
    print("Generating FII/DII net flows snapshot (90 days)...")
    end_date = datetime(2026, 10, 10)
    date_range = pd.bdate_range(end=end_date, periods=90)
    
    np.random.seed(42)
    # FII net values (often volatile, INR Crores)
    fii_net = np.random.normal(loc=-150.0, scale=1200.0, size=len(date_range)).round(2)
    # DII net values (often absorbing domestic inflows, INR Crores)
    dii_net = np.random.normal(loc=950.0, scale=800.0, size=len(date_range)).round(2)
    
    df = pd.DataFrame({
        "Date": [d.strftime("%Y-%m-%d") for d in date_range],
        "FII_Net_Cr": fii_net,
        "DII_Net_Cr": dii_net,
        "Total_Net_Cr": (fii_net + dii_net).round(2)
    })
    df.to_csv(os.path.join(SNAPSHOT_DIR, "flows.csv"), index=False)
    print("Saved data_snapshot/flows.csv.")

def generate_news():
    print("Generating news headlines snapshots...")
    end_date = datetime(2026, 10, 10)
    
    news_templates = {
        "RELIANCE": [
            ("Reliance Jio expands 5G enterprise solutions across Tier-2 cities", "positive", 1),
            ("RIL retail arm announces strategic partnership with global lifestyle brands", "positive", 3),
            ("Crude refining margins remain volatile amidst geopolitical tensions in Middle East", "neutral", 5),
            ("Jio Financial Services gains traction with new mutual fund offerings", "positive", 8),
            ("Brokerage maintains outperform rating on Reliance citing telecom ARPU hike potential", "positive", 12)
        ],
        "TCS": [
            ("TCS bags $1.2B digital transformation deal from European financial consortium", "positive", 1),
            ("IT sector attrition stabilizes in Q2, TCS reports improved utilization rates", "positive", 4),
            ("TCS expands AI Centers of Excellence in partnership with cloud providers", "positive", 7),
            ("Cautious client discretionary spending slows short-term deal conversions for TCS", "negative", 10),
            ("TCS announces interim dividend of Rs 10 per share for shareholders", "neutral", 13)
        ],
        "INFY": [
            ("Infosys raises FY27 constant currency revenue growth guidance to 5.0%-6.0%", "positive", 1),
            ("Infosys wins multi-year generative AI partnership with leading Nordic bank", "positive", 3),
            ("Strong large deal TCV at $3.2 billion reported in latest earnings disclosure", "positive", 5),
            ("Top-tier brokerages upgrade Infosys target price on robust margin execution", "positive", 8),
            ("Infosys inaugurates new state-of-the-art campus in Bengaluru to support cloud growth", "positive", 11)
        ],
        "HDFCBANK": [
            ("HDFC Bank deposits grow 14.5% YoY; credit-deposit ratio normalizes smoothly", "positive", 2),
            ("Net Interest Margin (NIM) holds firm at 3.45% for the quarter: Management", "positive", 5),
            ("HDFC Bank expands rural branch footprint with 120 new touchpoints", "neutral", 7),
            ("Foreign institutional investors hold steady stake post quarterly portfolio rebalancing", "neutral", 9),
            ("RBI regulatory audit highlights robust capital adequacy ratios above statutory limits", "positive", 12)
        ],
        "ICICIBANK": [
            ("ICICI Bank records 18% growth in retail lending driven by digital origination", "positive", 2),
            ("Asset quality pristine as gross NPA drops to multi-year low of 1.95%", "positive", 4),
            ("ICICI Bank iMobile app processes record monthly transaction volumes", "positive", 8),
            ("Unsecured personal loan portfolio shows controlled slippages, says risk committee", "neutral", 11)
        ],
        "SBIN": [
            ("SBI posts record quarterly net profit led by lower provisioning requirements", "positive", 2),
            ("Corporate loan sanctions up 16% as capex revival gains ground", "positive", 6),
            ("SBI Chairman confident on credit growth trajectory despite tighter liquidity", "neutral", 9),
            ("Public sector banking basket outperforms benchmark index on treasury gains", "positive", 13)
        ],
        "ITC": [
            ("ITC cigarette segment volumes show resilient 4% growth; FMCG-Others margins expand", "positive", 2),
            ("Hotels business demerger receives final regulatory approval from NCLT", "positive", 5),
            ("Paperboards and packaging division faces mild headwinds from cheaper imported pulp", "neutral", 8),
            ("ITC announces healthy interim dividend yield of 3.8% backed by strong cash flows", "positive", 11)
        ],
        "HINDUNILVR": [
            ("HUL reports gradual volume recovery in rural markets following normal monsoon", "positive", 2),
            ("Raw material price inflation in palm oil impacts short-term gross margins", "negative", 4),
            ("HUL expands premium beauty and personal care portfolio with direct-to-consumer launches", "positive", 8),
            ("Competitive intensity from regional FMCG players remains heightened: Analyst call", "neutral", 11)
        ],
        "LT": [
            ("Larsen & Toubro order book crosses Rs 5 lakh crore milestone with massive hydrocarbon win", "positive", 1),
            ("L&T signs strategic green hydrogen infrastructure contract in Middle East", "positive", 4),
            ("Core infrastructure execution on schedule; domestic private capex picking up", "positive", 7),
            ("Supply chain delivery times extended due to Red Sea shipping rerouting", "neutral", 10)
        ],
        "BHARTIARTL": [
            ("Bharti Airtel ARPU climbs to Rs 215 as tariff hike benefits flow through", "positive", 2),
            ("Airtel Africa subscriber base grows 9% YoY; forex volatility partially hedged", "neutral", 5),
            ("Bharti Airtel prepaid to postpaid conversion surges with 5G unlimited plans", "positive", 8),
            ("Company prepays high-cost spectrum dues to Department of Telecom", "positive", 12)
        ],
        "KOTAKBANK": [
            ("Kotak Bank receives regulatory clearance to resume digital customer onboarding", "positive", 2),
            ("Management accelerates technology infrastructure investments and cybersecurity upgrades", "positive", 6),
            ("Deposit growth outpaces loan book expansion; CASA ratio remains resilient at 47%", "neutral", 9),
            ("Analyst upgrade on Kotak Bank following removal of regulatory overhang", "positive", 12)
        ],
        "AXISBANK": [
            ("Axis Bank completes Citi retail integration; synergy cost savings on track", "positive", 3),
            ("Net interest income grows 11% YoY; credit cost guidance maintained at 0.50%", "positive", 6),
            ("Card spends jump 22% YoY on festive season e-commerce partnerships", "positive", 9)
        ],
        "MARUTI": [
            ("Maruti Suzuki SUV market share hits 26% led by Grand Vitara and Brezza", "positive", 2),
            ("Export volumes jump 14% to Latin America and African markets", "positive", 5),
            ("Entry-level mini segment sales continue to face demand pressure from budget buyers", "negative", 9),
            ("Maruti prepares for first battery electric vehicle launch in early 2027", "positive", 13)
        ],
        "SUNPHARMA": [
            ("US FDA issues Form 483 with 6 inspectional observations for Sun Pharma Halol facility", "negative", 1),
            ("Sun Pharma global specialty revenue rises 19% led by Ilumya and Cequa prescriptions", "positive", 4),
            ("Domestic formulation business outperforms Indian Pharma Market (IPM) benchmark", "positive", 8),
            ("R&D expenditure targeted at 7% of revenues for clinical trial pipeline progression", "neutral", 11)
        ],
        "TATAMOTORS": [
            ("Tata Motors domestic passenger vehicle dispatches show steady retail momentum", "positive", 2),
            ("Management warns of European EV margin compression and elevated supplier costs in JLR", "negative", 3),
            ("Commercial vehicle segment witnesses transient slowdown ahead of emission norms", "negative", 7),
            ("Tata Motors EV sales record highest quarterly milestone in domestic electric fleet", "positive", 9),
            ("Automotive analysts note divergence between strong technical chart and softening EBITDA guidance", "neutral", 12)
        ],
        "ADANIENT": [
            ("Adani Enterprises shares experience heavy trading volume amid block trade rumors", "neutral", 1),
            ("Stock slides 3.5% as SEBI filing confirms promoter pledge increase from 12% to 19%", "negative", 1),
            ("Auditor issues qualification note on related-party infrastructure loan disclosures", "negative", 2),
            ("Kutch copper project phase 1 commissioned ahead of scheduled operational timeline", "positive", 6),
            ("Adani Airports passenger traffic reaches record monthly high of 8.5 million travelers", "positive", 10)
        ],
        "ASIANPAINT": [
            ("Asian Paints faces margin pressure from heightened competition in decorative segment", "negative", 2),
            ("Industrial coatings division grows double digits supported by automotive manufacturing", "positive", 6),
            ("Raw material titanium dioxide prices soften, offering slight gross margin relief", "positive", 9)
        ],
        "WIPRO": [
            ("Wipro announces new multi-million dollar digital engineering win in North America", "positive", 2),
            ("CEO highlights consulting turnaround and AI orchestration platform adoption", "positive", 5),
            ("Q2 operating margins steady at 16.4%; headcount additions resume in campus intake", "neutral", 9),
            ("Market awaits corporate announcements and annual strategy disclosures", "neutral", 12)
        ]
    }
    
    for ticker, headlines in news_templates.items():
        news_list = []
        for i, (title, sentiment, day_offset) in enumerate(headlines):
            pub_date = (end_date - timedelta(days=day_offset)).strftime("%Y-%m-%dT10:30:00Z")
            news_list.append({
                "id": f"{ticker}_N{i+1}",
                "ticker": ticker,
                "title": title,
                "publisher": random.choice(["The Economic Times", "Livemint", "Moneycontrol", "Business Standard", "Reuters India"]),
                "published_at": pub_date,
                "url": f"https://www.moneycontrol.com/news/business/stocks/{ticker.lower()}-news-{i+1}.html",
                "sentiment_label": sentiment,
                "relevance": round(random.uniform(0.75, 0.95), 2)
            })
        
        with open(os.path.join(NEWS_DIR, f"{ticker}.json"), "w", encoding="utf-8") as f:
            json.dump(news_list, f, indent=2)
    print(f"Generated news JSON for {len(news_templates)} tickers.")

def generate_filings():
    print("Generating synthetic regulatory filings (SEBI/BSE) and transcripts...")
    
    # Notice: WIPRO is deliberately excluded to demo missing-filing degradation!
    filing_specs = {
        "ADANIENT": [
            {
                "filename": "ADANIENT_SEBI_Pledge_Disclosure_2026.md",
                "doc_type": "SEBI_DISCLOSURE",
                "date": "2026-09-28",
                "title": "Adani Enterprises Ltd - Regulation 31(1) Encumbrance of Shares Disclosure",
                "text": """---
ticker: ADANIENT
doc_type: SEBI_DISCLOSURE
date: 2026-09-28
title: Regulation 31(1) Share Pledge & Encumbrance Disclosure
source_label: SYNTHETIC
page: 1
---

## SEBI (Substantial Acquisition of Shares and Takeovers) Regulations, 2011 - Regulation 31(1)

The Promoter Group of Adani Enterprises Limited hereby submits the statutory disclosure regarding encumbrance and pledge of equity shares:

1. **Total Promoter Holding**: 72.61% of total paid-up share capital.
2. **Promoter Shares Pledged / Encumbered Prior to Event**: 8,92,40,000 shares representing 12.15% of promoter holding.
3. **Additional Encumbrance Created**: 5,02,80,000 equity shares pledged in favor of global syndicate credit facilities.
4. **Post-Event Encumbered Shares**: 13,95,20,000 equity shares representing **19.04% of total promoter shareholding** (an increase of 6.89 percentage points).
5. **Purpose of Pledge**: Security for refinancing debt covenants and working capital facilities for the Navi Mumbai Airport project.

*Risk Assessment & Observation*: High promoter pledge levels increase vulnerability to margin calls and sudden collateral liquidation during adverse equity market movements."""
            },
            {
                "filename": "ADANIENT_Auditor_Note_Q2_2026.md",
                "doc_type": "AUDITOR_REPORT",
                "date": "2026-10-02",
                "title": "Independent Auditor Limited Review Qualification - Related Party Transactions",
                "text": """---
ticker: ADANIENT
doc_type: AUDITOR_REPORT
date: 2026-10-02
title: Independent Auditor Limited Review Report - Emphasis of Matter
source_label: SYNTHETIC
page: 2
---

## Independent Auditor's Review Report on Unaudited Standalone and Consolidated Financial Results

To the Board of Directors of Adani Enterprises Limited,

We have reviewed the accompanying statement of unaudited consolidated financial results for the quarter and half-year ended September 30, 2026.

### Basis for Qualified Conclusion / Emphasis of Matter:
Attention is drawn to Note 7 of the consolidated financial statements regarding **unsecured loans and advances amounting to Rs 4,120 Crores** extended to overseas related entities. The recoverability and economic commercial substance of these transactions remain subject to regulatory inquiries and ongoing legal proceedings. 

Furthermore, trade receivables exceeding 180 days have expanded by 28% year-on-year across certain EPC contracting arms. While management expresses confidence in full collection upon milestone certification, the lack of third-party collateral presents an elevated credit concentration risk."""
            }
        ],
        "TATAMOTORS": [
            {
                "filename": "TATAMOTORS_Earnings_Call_Transcript_Q2.md",
                "doc_type": "EARNINGS_TRANSCRIPT",
                "date": "2026-10-05",
                "title": "Tata Motors Ltd Q2 FY27 Earnings Conference Call Transcript",
                "text": """---
ticker: TATAMOTORS
doc_type: EARNINGS_TRANSCRIPT
date: 2026-10-05
title: Tata Motors Q2 Earnings Call - Margin Guidance Cut
source_label: SYNTHETIC
page: 1
---

## Tata Motors Limited - Earnings Conference Call Excerpt (Q2 FY27)

**Management Remarks - PB Balaji, Group Chief Financial Officer**:
"Good afternoon everyone. While our domestic passenger vehicle retail momentum and technical delivery metrics have demonstrated remarkable resilience, we must provide a transparent operational update regarding Jaguar Land Rover and our European supply chain.

We are formally **revising our full-year consolidated EBIT margin guidance downward by 180 basis points, from 8.5% to 6.7%**. This revision is driven by three inescapable headwinds:
1. Significant commodity cost escalation in specialty alloys and battery cell inputs.
2. Elevated incentive discounting required in the European luxury EV transition due to aggressive regional pricing wars.
3. Transitory semiconductor supply bottlenecks from our tier-1 electronic steering suppliers.

While commercial vehicle volumes in India are expected to recover in Q4, the near-term cash generation and operating margins across international operations will experience clear compression over the next two quarters." """
            },
            {
                "filename": "TATAMOTORS_BSE_Guidance_Revision_2026.md",
                "doc_type": "BSE_ANNOUNCEMENT",
                "date": "2026-10-06",
                "title": "BSE Corporate Disclosure - Revision of Operating Outlook & Capex Guidance",
                "text": """---
ticker: TATAMOTORS
doc_type: BSE_ANNOUNCEMENT
date: 2026-10-06
title: BSE Disclosure - JLR Margin Outlook Revision
source_label: SYNTHETIC
page: 2
---

## Corporate Announcement under Regulation 30 of SEBI (LODR) Regulations, 2015

Tata Motors Ltd announces that following the review of global operations by the Audit Committee, the Company has adjusted its capital expenditure and operational cash flow forecasts:
- JLR free cash flow projection for H2 FY27 reduced to £1.1 billion from £1.6 billion.
- Commercial vehicle EBITDA margins projected at 9.8% versus 11.2% previously budgeted.
- Raw material inflation impact estimated at Rs 1,450 Crores across consolidated operations.

Investors are advised to take note of the adjusted operational guidance."""
            }
        ],
        "INFY": [
            {
                "filename": "INFY_Quarterly_Results_Note_Q2.md",
                "doc_type": "QUARTERLY_RESULTS",
                "date": "2026-10-04",
                "title": "Infosys Ltd Statement of Consolidated Results for Q2 FY27",
                "text": """---
ticker: INFY
doc_type: QUARTERLY_RESULTS
date: 2026-10-04
title: Infosys Q2 Financial Results - Strong Revenue & Margin Expansion
source_label: SYNTHETIC
page: 1
---

## Infosys Reports Exceptional Q2 Performance; Raises Full-Year Guidance

- **Revenue**: Rs 41,850 Crores, up 8.2% YoY in constant currency.
- **Operating Margin**: 21.4%, an expansion of 60 bps sequentially.
- **Large Deal TCV**: All-time high of $3.2 billion with 52% net new deals.
- **Guidance Revision**: The Company **revises its constant currency revenue growth guidance upwards to 5.0% - 6.0%** for FY27 (up from 3.0% - 4.5% previously).
- **Free Cash Flow**: Rs 8,390 Crores, conversion of 122% of net profit.
- **Attrition**: Voluntary attrition on LTM basis decreased to 12.1%."""
            },
            {
                "filename": "INFY_Earnings_Transcript_Deal_Wins.md",
                "doc_type": "EARNINGS_TRANSCRIPT",
                "date": "2026-10-05",
                "title": "Infosys Q2 FY27 Earnings Call - Generative AI Client Adoption",
                "text": """---
ticker: INFY
doc_type: EARNINGS_TRANSCRIPT
date: 2026-10-05
title: Infosys Earnings Call - Topaz AI Platform Acceleration
source_label: SYNTHETIC
page: 2
---

**Salil Parekh, Chief Executive Officer**:
"We had an exceptionally strong quarter driven by client embrace of our Topaz AI suite. We closed 24 large deals this quarter, spanning financial services, retail, and life sciences. The pipeline remains robust at record levels. The margin execution reflects our project maximus efficiency programs, and our pricing realization in high-complexity AI programs is commanding a 150 bps premium." """
            }
        ],
        "HDFCBANK": [
            {
                "filename": "HDFCBANK_BSE_Quarterly_Filing.md",
                "doc_type": "QUARTERLY_RESULTS",
                "date": "2026-09-30",
                "title": "HDFC Bank Ltd Financial Results for Second Quarter Ended September 30, 2026",
                "text": """---
ticker: HDFCBANK
doc_type: QUARTERLY_RESULTS
date: 2026-09-30
title: HDFC Bank Q2 Balance Sheet Health & Deposit Accretion
source_label: SYNTHETIC
page: 1
---

## HDFC Bank Ltd - Performance Highlights for Q2 FY27

- **Net Interest Income**: Rs 30,110 Crores, growing 10.2% YoY.
- **Net Interest Margin (NIM)**: Stable at 3.47% on total assets, consistent with management targets.
- **Gross NPA**: 1.33% (improving from 1.39% in the preceding quarter); Net NPA pristine at 0.38%.
- **Capital Adequacy**: Total CAR stood at 19.3% under Basel III vs statutory requirement of 11.5%.
- **Credit-to-Deposit (CD) Ratio**: Reduced from 104% post-merger to a sound 96.5%."""
            }
        ],
        "SUNPHARMA": [
            {
                "filename": "SUNPHARMA_USFDA_Form_483_Disclosure.md",
                "doc_type": "SEBI_DISCLOSURE",
                "date": "2026-10-01",
                "title": "Sun Pharmaceutical Industries - Regulatory Inspection Disclosure",
                "text": """---
ticker: SUNPHARMA
doc_type: SEBI_DISCLOSURE
date: 2026-10-01
title: US FDA Inspectional Observations - Halol Manufacturing Unit
source_label: SYNTHETIC
page: 1
---

## Disclosure under Regulation 30 of SEBI (Listing Obligations and Disclosure Requirements)

Sun Pharmaceutical Industries Ltd informs the stock exchanges that the United States Food and Drug Administration (US FDA) conducted a cGMP inspection of the company's Halol manufacturing facility from September 18 to September 30, 2026.

At the conclusion of the inspection, the **US FDA issued a Form 483 with 6 inspectional observations**. The observations relate to cleanroom environmental monitoring protocols and equipment sterilization validation records. The company is preparing a comprehensive response within the stipulated 15 business days. Commercial dispatches from this unit to regulated markets may experience temporary scrutiny until corrective actions are cleared."""
            }
        ],
        "ITC": [
            {
                "filename": "ITC_Quarterly_Corporate_Filing.md",
                "doc_type": "QUARTERLY_RESULTS",
                "date": "2026-10-03",
                "title": "ITC Ltd Financial Results and Dividend Declaration",
                "text": """---
ticker: ITC
doc_type: QUARTERLY_RESULTS
date: 2026-10-03
title: ITC Q2 Financials - Resilient FMCG and Stable Cigarette EBIT
source_label: SYNTHETIC
page: 1
---

## ITC Limited - Second Quarter Financial Summary

- **Gross Revenue**: Rs 18,720 Crores, growing 7.4% YoY.
- **FMCG-Others Segment**: Revenue grew 8.1% with segment EBITDA margins expanding by 90 bps to 11.4%.
- **Cigarette Segment**: Volume growth of 4.2% with steady realization and no adverse taxation revisions.
- **Demerger Status**: ITC Hotels demerger finalized with shareholder share allocation completed.
- **Cash and Liquid Investments**: Rs 19,400 Crores, providing substantial financial headroom."""
            }
        ],
        "RELIANCE": [
            {
                "filename": "RELIANCE_Consolidated_Results_Q2.md",
                "doc_type": "QUARTERLY_RESULTS",
                "date": "2026-10-02",
                "title": "Reliance Industries Limited Q2 Financial Performance Summary",
                "text": """---
ticker: RELIANCE
doc_type: QUARTERLY_RESULTS
date: 2026-10-02
title: RIL Q2 Financials - Strong Telecom and Retail Cash Flows
source_label: SYNTHETIC
page: 1
---

## Reliance Industries Limited - Consolidated Financial Highlights

- **Consolidated EBITDA**: Rs 43,900 Crores, up 6.8% YoY.
- **Jio Platforms**: ARPU rose to Rs 195.1 per user with customer net additions of 11.2 million.
- **Reliance Retail**: Footfalls exceeded 280 million across 18,900 stores; digital commerce accounted for 19% of sales.
- **Oil-to-Chemicals (O2C)**: Downstream chemical margins impacted by subdued global demand, offset by strong domestic fuel marketing."""
            }
        ],
        "TCS": [
            {
                "filename": "TCS_Board_Disclosure_Q2.md",
                "doc_type": "QUARTERLY_RESULTS",
                "date": "2026-10-04",
                "title": "Tata Consultancy Services Q2 Audited Statement",
                "text": """---
ticker: TCS
doc_type: QUARTERLY_RESULTS
date: 2026-10-04
title: TCS Q2 Audited Results - Strong Deal Pipeline
source_label: SYNTHETIC
page: 1
---

## Tata Consultancy Services Limited - Financial Report

- **Quarterly Revenue**: Rs 64,250 Crores, up 6.2% YoY.
- **Operating Margin**: 24.8%, expanding 30 bps sequentially.
- **Total Contract Value (TCV)**: $10.1 billion, reflecting solid broad-based customer demand.
- **Workforce**: Total headcount at 608,985 with lowest attrition among Tier-1 global IT firms (12.3%)."""
            }
        ],
        "ICICIBANK": [
            {
                "filename": "ICICIBANK_Quarterly_Release.md",
                "doc_type": "QUARTERLY_RESULTS",
                "date": "2026-10-03",
                "title": "ICICI Bank Limited Q2 Highlights",
                "text": """---
ticker: ICICIBANK
doc_type: QUARTERLY_RESULTS
date: 2026-10-03
title: ICICI Bank Q2 Results - Pristine Asset Quality
source_label: SYNTHETIC
page: 1
---

## ICICI Bank Limited - Quarterly Financial Results

- **Profit After Tax**: Rs 11,740 Crores, an increase of 14.5% YoY.
- **Domestic Loan Growth**: 15.8% YoY, led by business banking (32%) and SME portfolios (24%).
- **Gross NPA Ratio**: 1.95%, the lowest recorded in over a decade.
- **Return on Equity (ROE)**: 19.1% annualized."""
            }
        ],
        "SBIN": [
            {
                "filename": "SBIN_Quarterly_Filing.md",
                "doc_type": "QUARTERLY_RESULTS",
                "date": "2026-10-01",
                "title": "State Bank of India Q2 Results Overview",
                "text": """---
ticker: SBIN
doc_type: QUARTERLY_RESULTS
date: 2026-10-01
title: State Bank of India Q2 Performance
source_label: SYNTHETIC
page: 1
---

## State Bank of India - Financial Results

- **Net Profit**: Rs 18,330 Crores, up 28% YoY on credit growth and treasury management.
- **Gross Advances**: Crossed Rs 39 lakh crores, expanding 15.2% YoY.
- **Gross NPA**: 2.11%, down 44 bps YoY; Slippage ratio maintained at 0.68%."""
            }
        ],
        "LT": [
            {
                "filename": "LT_Orderbook_Disclosure.md",
                "doc_type": "SEBI_DISCLOSURE",
                "date": "2026-10-02",
                "title": "Larsen & Toubro Order Book Milestone Disclosure",
                "text": """---
ticker: LT
doc_type: SEBI_DISCLOSURE
date: 2026-10-02
title: Larsen & Toubro Mega Order Inflow and Backlog
source_label: SYNTHETIC
page: 1
---

## Larsen & Toubro Limited - Corporate Announcement

Larsen & Toubro has secured significant international engineering and construction contracts in the Middle East energy transition sector valued at over Rs 14,000 Crores. 
The consolidated order book stands at a record Rs 5,12,000 Crores, providing revenue visibility over 3.2 years of trailing operations."""
            }
        ],
        "BHARTIARTL": [
            {
                "filename": "BHARTIARTL_Operational_Filing.md",
                "doc_type": "QUARTERLY_RESULTS",
                "date": "2026-09-29",
                "title": "Bharti Airtel Q2 Performance Report",
                "text": """---
ticker: BHARTIARTL
doc_type: QUARTERLY_RESULTS
date: 2026-09-29
title: Bharti Airtel ARPU and Debt Prepayment Update
source_label: SYNTHETIC
page: 1
---

## Bharti Airtel Limited - Operational Update

- **India Mobile ARPU**: Reached Rs 215 against Rs 203 in Q1.
- **EBITDA Margin**: 52.4% on domestic wireless business.
- **Debt Optimization**: Pre-paid Rs 8,400 Crores of high-interest spectrum liabilities to the DoT, reducing annual interest burden."""
            }
        ],
        "KOTAKBANK": [
            {
                "filename": "KOTAKBANK_Regulatory_Filing.md",
                "doc_type": "SEBI_DISCLOSURE",
                "date": "2026-10-03",
                "title": "Kotak Mahindra Bank - Regulatory Update Compliance",
                "text": """---
ticker: KOTAKBANK
doc_type: SEBI_DISCLOSURE
date: 2026-10-03
title: Kotak Bank IT Modernization and Customer Acquisition
source_label: SYNTHETIC
page: 1
---

## Kotak Mahindra Bank - Regulatory Compliance Affirmation

Following comprehensive audits conducted by external cybersecurity auditors and independent technical verification, all digital onboarding systems comply with RBI IT governance standards. Digital customer acquisition across mobile channels has resumed with heightened encryption frameworks."""
            }
        ],
        "AXISBANK": [
            {
                "filename": "AXISBANK_Quarterly_Release.md",
                "doc_type": "QUARTERLY_RESULTS",
                "date": "2026-10-02",
                "title": "Axis Bank Ltd Second Quarter Report",
                "text": """---
ticker: AXISBANK
doc_type: QUARTERLY_RESULTS
date: 2026-10-02
title: Axis Bank Q2 Performance - Synergy Benefits Realized
source_label: SYNTHETIC
page: 1
---

## Axis Bank Limited - Statement of Financial Results

- **Net Profit**: Rs 6,910 Crores, up 18% YoY.
- **Retail Synergies**: Annualized cost synergies from integration reach Rs 850 Crores.
- **Provision Coverage Ratio (PCR)**: Robust at 78%."""
            }
        ],
        "MARUTI": [
            {
                "filename": "MARUTI_Sales_Disclosures.md",
                "doc_type": "QUARTERLY_RESULTS",
                "date": "2026-10-01",
                "title": "Maruti Suzuki Production and Dispatch Report",
                "text": """---
ticker: MARUTI
doc_type: QUARTERLY_RESULTS
date: 2026-10-01
title: Maruti Suzuki Q2 Operational Performance
source_label: SYNTHETIC
page: 1
---

## Maruti Suzuki India Limited - Operational Review

- **Total Vehicle Sales**: 545,000 units in Q2, an increase of 3.8% YoY.
- **Utility Vehicle Share**: UV contribution rose to 38% of total domestic passenger vehicle volumes.
- **Operating Margin**: 11.2%, supported by higher realization per vehicle."""
            }
        ],
        "ASIANPAINT": [
            {
                "filename": "ASIANPAINT_Quarterly_Results.md",
                "doc_type": "QUARTERLY_RESULTS",
                "date": "2026-09-30",
                "title": "Asian Paints Limited Q2 Operational Update",
                "text": """---
ticker: ASIANPAINT
doc_type: QUARTERLY_RESULTS
date: 2026-09-30
title: Asian Paints Q2 Margin and Competition Outlook
source_label: SYNTHETIC
page: 1
---

## Asian Paints Limited - Management Discussion

- **Consolidated Revenue**: Rs 8,420 Crores, flat YoY.
- **Competitive Dynamics**: New entrant capacity in decorative paints triggered localized promotional discounting.
- **Industrial Coatings**: Double-digit volume growth in automotive coatings and protective finishes."""
            }
        ],
        "HINDUNILVR": [
            {
                "filename": "HINDUNILVR_Quarterly_Statement.md",
                "doc_type": "QUARTERLY_RESULTS",
                "date": "2026-10-02",
                "title": "Hindustan Unilever Limited Half-Year Results",
                "text": """---
ticker: HINDUNILVR
doc_type: QUARTERLY_RESULTS
date: 2026-10-02
title: HUL Q2 Performance - Rural Demand Dynamics
source_label: SYNTHETIC
page: 1
---

## Hindustan Unilever Limited - Operating Review

- **Underlying Sales Growth (USG)**: 3.5% with Underlying Volume Growth (UVG) at 2.8%.
- **Home Care Segment**: Continued double-digit growth in premium laundry liquids and dishwash.
- **Gross Margins**: Stabilized at 50.2%."""
            }
        ]
    }
    
    count = 0
    for ticker, files in filing_specs.items():
        for item in files:
            filepath = os.path.join(FILINGS_DIR, item["filename"])
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(item["text"].strip())
            count += 1
            
    print(f"Generated {count} synthetic filings across {len(filing_specs)} tickers.")
    print("Notice: WIPRO has 0 filings as specified for missing-filing degradation tests.")

if __name__ == "__main__":
    generate_prices()
    generate_flows()
    generate_news()
    generate_filings()
    print("\nAll demo data snapshots successfully generated!")

