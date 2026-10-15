"""
backend/app/api/routes_metrics.py - Market Stocks, Candlestick Feeds, Citations & Backtest Data
"""

from fastapi import APIRouter, HTTPException
from backend.app.schemas.api import StockItemSchema, PriceCandleSchema, BacktestResultSchema, DocumentChunkDetailSchema
from backend.app.data import resilient_provider
from backend.app.rag.retriever import retriever
from backend.app.eval.backtest import run_historical_backtest

router = APIRouter(tags=["Metrics & Market Data"])

STOCK_CATALOG = [
    {"ticker": "RELIANCE", "name": "Reliance Industries Ltd", "sector": "Energy", "yf_symbol": "RELIANCE.NS"},
    {"ticker": "TCS", "name": "Tata Consultancy Services Ltd", "sector": "Information Technology", "yf_symbol": "TCS.NS"},
    {"ticker": "INFY", "name": "Infosys Ltd", "sector": "Information Technology", "yf_symbol": "INFY.NS"},
    {"ticker": "HDFCBANK", "name": "HDFC Bank Ltd", "sector": "Banking", "yf_symbol": "HDFCBANK.NS"},
    {"ticker": "ICICIBANK", "name": "ICICI Bank Ltd", "sector": "Banking", "yf_symbol": "ICICIBANK.NS"},
    {"ticker": "SBIN", "name": "State Bank of India", "sector": "Banking", "yf_symbol": "SBIN.NS"},
    {"ticker": "ITC", "name": "ITC Ltd", "sector": "FMCG", "yf_symbol": "ITC.NS"},
    {"ticker": "HINDUNILVR", "name": "Hindustan Unilever Ltd", "sector": "FMCG", "yf_symbol": "HINDUNILVR.NS"},
    {"ticker": "LT", "name": "Larsen & Toubro Ltd", "sector": "Construction", "yf_symbol": "LT.NS"},
    {"ticker": "BHARTIARTL", "name": "Bharti Airtel Ltd", "sector": "Telecommunications", "yf_symbol": "BHARTIARTL.NS"},
    {"ticker": "KOTAKBANK", "name": "Kotak Mahindra Bank Ltd", "sector": "Banking", "yf_symbol": "KOTAKBANK.NS"},
    {"ticker": "AXISBANK", "name": "Axis Bank Ltd", "sector": "Banking", "yf_symbol": "AXISBANK.NS"},
    {"ticker": "MARUTI", "name": "Maruti Suzuki India Ltd", "sector": "Automobile", "yf_symbol": "MARUTI.NS"},
    {"ticker": "SUNPHARMA", "name": "Sun Pharmaceutical Industries Ltd", "sector": "Healthcare", "yf_symbol": "SUNPHARMA.NS"},
    {"ticker": "TATAMOTORS", "name": "Tata Motors Ltd", "sector": "Automobile", "yf_symbol": "TATAMOTORS.NS"},
    {"ticker": "ADANIENT", "name": "Adani Enterprises Ltd", "sector": "Metals & Mining", "yf_symbol": "ADANIENT.NS"},
    {"ticker": "ASIANPAINT", "name": "Asian Paints Ltd", "sector": "Consumer Durables", "yf_symbol": "ASIANPAINT.NS"},
    {"ticker": "WIPRO", "name": "Wipro Ltd", "sector": "Information Technology", "yf_symbol": "WIPRO.NS"}
]

@router.get("/stocks", response_model=list[StockItemSchema])
async def get_stocks():
    """Returns the 18 Nifty 50 stocks with current prices and 24h change."""
    results = []
    for s in STOCK_CATALOG:
        t = s["ticker"]
        res = resilient_provider.get_prices(t, period='1y')
        df = res.data
        if not df.empty and len(df) >= 2:
            latest = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2])
            chg = round(latest - prev, 2)
            chg_pct = round((chg / prev) * 100, 2)
            vol = int(df['Volume'].iloc[-1])
        else:
            latest = 1000.0
            chg = 0.0
            chg_pct = 0.0
            vol = 100000

        results.append(StockItemSchema(
            ticker=t,
            name=s["name"],
            sector=s["sector"],
            yf_symbol=s["yf_symbol"],
            latest_price=latest,
            change_24h=chg,
            change_pct=chg_pct,
            volume_24h=vol
        ))
    return results

@router.get("/stocks/{ticker}/prices", response_model=list[PriceCandleSchema])
async def get_stock_prices(ticker: str, period: str = "1y"):
    """Returns historical OHLCV candles for charting."""
    res = resilient_provider.get_prices(ticker, period=period)
    df = res.data
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No price data available for {ticker}")

    candles = []
    # Return last 100 candles for clean lightweight-chart display
    chart_slice = df.iloc[-100:] if len(df) > 100 else df
    for _, row in chart_slice.iterrows():
        d_str = row['Date'].strftime("%Y-%m-%d") if hasattr(row['Date'], 'strftime') else str(row['Date'])[:10]
        candles.append(PriceCandleSchema(
            date=d_str,
            open=float(row['Open']),
            high=float(row['High']),
            low=float(row['Low']),
            close=float(row['Close']),
            volume=int(row['Volume'])
        ))
    return candles

@router.get("/documents/chunks/{chunk_id}", response_model=DocumentChunkDetailSchema)
async def get_chunk_detail(chunk_id: str):
    """Returns exact text and metadata for citation drawer."""
    ch = retriever.get_chunk_by_id(chunk_id)
    if not ch:
        # Check if synthesized filing
        raise HTTPException(status_code=404, detail=f"Document chunk '{chunk_id}' not found.")

    return DocumentChunkDetailSchema(
        chunk_id=ch["id"],
        ticker=ch["ticker"],
        title=ch["title"],
        doc_type=ch.get("doc_type", "FILING"),
        doc_date=ch.get("doc_date", "2026-10-01"),
        source_label=ch.get("source_label", "SYNTHETIC"),
        page=ch.get("page"),
        snippet=ch["text"],
        url=ch.get("url")
    )

@router.get("/metrics/backtest", response_model=list[BacktestResultSchema])
async def get_backtest_metrics():
    """Returns walk-forward historical hit-rate and forward return metrics."""
    return run_historical_backtest(30)

@router.get("/metrics/calibration")
async def get_confidence_calibration():
    """Returns confidence calibration buckets: predicted confidence vs actual hit rate."""
    from backend.app.eval.backtest import run_confidence_calibration
    return run_confidence_calibration()

@router.get("/documents/search")
async def search_documents(query: str, ticker: str | None = None, top_k: int = 5):
    """
    Performs 384-dimensional dense semantic vector search across regulatory filings corpus.
    """
    retriever.load_and_index()
    from backend.app.rag.embeddings import get_text_embedding, cosine_similarity
    
    query_emb = get_text_embedding(query)
    candidates = retriever._chunks
    if ticker:
        candidates = [c for c in candidates if c["ticker"] == ticker.upper()]

    scored = []
    for ch in candidates:
        sim = cosine_similarity(query_emb, ch["embedding"])
        scored.append((sim, ch))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for s, ch in scored[:top_k]:
        results.append({
            "chunk_id": ch["id"],
            "ticker": ch["ticker"],
            "title": ch["title"],
            "doc_type": ch.get("doc_type", "FILING"),
            "doc_date": ch.get("doc_date", "2026-10-01"),
            "similarity_score": round(float(s), 4),
            "snippet": ch["text"][:300] + ("..." if len(ch["text"]) > 300 else ""),
            "page": ch.get("page", 1)
        })
    return results

@router.get("/data/sources/{ticker}")
async def get_data_sources_summary(ticker: str):
    """
    Returns multi-source data ingestion telemetry for a given ticker:
    Prices candles, news headlines with sentiment, FII/DII flow status, and filings.
    """
    ticker = ticker.upper()
    price_res = resilient_provider.get_prices(ticker, period='1y')
    news_res = resilient_provider.get_news(ticker, days=14)
    flows_res = resilient_provider.get_flows(days=30)
    
    retriever.load_and_index()
    filing_chunks = [c for c in retriever._chunks if c["ticker"] == ticker]

    df_p = price_res.data
    candles_count = len(df_p) if not df_p.empty else 0
    latest_close = float(df_p['Close'].iloc[-1]) if candles_count > 0 else 0.0

    return {
        "ticker": ticker,
        "prices": {
            "source": price_res.source,
            "candles_count": candles_count,
            "latest_close": latest_close,
            "as_of": price_res.as_of.isoformat(),
            "stale": price_res.stale
        },
        "news": {
            "source": news_res.source,
            "count": len(news_res.data),
            "headlines": news_res.data[:6]
        },
        "flows": {
            "source": flows_res.source,
            "days_recorded": len(flows_res.data),
            "stale": flows_res.stale
        },
        "filings": {
            "corpus_count": len(filing_chunks),
            "documents": [{"chunk_id": c["id"], "title": c["title"], "type": c.get("doc_type")} for c in filing_chunks[:4]]
        }
    }


