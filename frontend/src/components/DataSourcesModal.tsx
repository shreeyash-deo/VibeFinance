'use client';

import React, { useState, useEffect } from 'react';
import { X, Database, TrendingUp, Newspaper, DollarSign, FileText } from 'lucide-react';

interface DataSourcesModalProps {
  isOpen: boolean;
  onClose: () => void;
  ticker: string;
}

export const DataSourcesModal: React.FC<DataSourcesModalProps> = ({
  isOpen,
  onClose,
  ticker
}) => {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen && ticker) {
      setIsLoading(true);
      fetch(`http://127.0.0.1:8000/api/data/sources/${ticker}`)
        .then((res) => res.json())
        .then((d) => setData(d))
        .catch((e) => console.error(e))
        .finally(() => setIsLoading(false));
    }
  }, [isOpen, ticker]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="w-full max-w-4xl bg-[#0e1626] border border-slate-800 rounded-2xl p-6 shadow-2xl flex flex-col gap-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-bold text-sm text-slate-100">
                Multi-Source Ingestion Telemetry: {ticker}
              </h2>
              <p className="text-xs text-slate-400">
                4 Simultaneous Ingestion Feeds: OHLCV Prices, News Sentiment, FII/DII Net Flows, and Statutory Filings.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {isLoading ? (
          <div className="text-center py-16 text-slate-400 text-xs">
            Querying multi-source ingestion feeds...
          </div>
        ) : data ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            {/* 1. OHLCV Prices Feed */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-slate-200 flex items-center gap-1.5">
                    <TrendingUp className="w-4 h-4 text-blue-400" /> OHLCV Price Action Feed
                  </span>
                  <span className="text-[10px] uppercase font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    {data.prices?.source}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px] bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 mb-2">
                  <div>
                    <span className="text-slate-500">Candles Ingested:</span>
                    <strong className="text-slate-200 block">{data.prices?.candles_count} Days</strong>
                  </div>
                  <div>
                    <span className="text-slate-500">Latest Closing Price:</span>
                    <strong className="text-slate-200 block">Rs {data.prices?.latest_close}</strong>
                  </div>
                  <div>
                    <span className="text-slate-500">Feed Freshness:</span>
                    <strong className="text-emerald-400 block">{data.prices?.stale ? 'Stale' : 'Verified OK'}</strong>
                  </div>
                  <div>
                    <span className="text-slate-500">As Of Date:</span>
                    <strong className="text-slate-200 block">{data.prices?.as_of?.slice(0, 10)}</strong>
                  </div>
                </div>
              </div>
              <span className="text-[10px] text-slate-500">2-Year historical OHLCV data loaded without gaps.</span>
            </div>

            {/* 2. News Headlines Feed */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-slate-200 flex items-center gap-1.5">
                    <Newspaper className="w-4 h-4 text-purple-400" /> News Headlines Sentiment Feed
                  </span>
                  <span className="text-[10px] font-bold text-slate-400">
                    {data.news?.count} Headlines
                  </span>
                </div>
                <div className="flex flex-col gap-1.5 max-h-36 overflow-y-auto pr-1">
                  {(data.news?.headlines || []).map((h: any, idx: number) => (
                    <div key={idx} className="p-1.5 rounded bg-slate-950/60 border border-slate-800/80 text-[10px] flex items-center justify-between">
                      <span className="text-slate-200 truncate pr-2">{h.title}</span>
                      <span className={`text-[9px] uppercase px-1.5 py-0.2 rounded font-bold shrink-0 ${h.sentiment_label === 'positive' ? 'text-emerald-400 bg-emerald-500/10' : (h.sentiment_label === 'negative' ? 'text-rose-400 bg-rose-500/10' : 'text-slate-400 bg-slate-800')}`}>
                        {h.sentiment_label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
              <span className="text-[10px] text-slate-500 mt-2">14-day exponential recency weighting applied.</span>
            </div>

            {/* 3. FII / DII Institutional Flows */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-slate-200 flex items-center gap-1.5">
                    <DollarSign className="w-4 h-4 text-amber-400" /> Institutional FII/DII Net Flows
                  </span>
                  <span className="text-[10px] uppercase font-bold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
                    NSE Clearing
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px] bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
                  <div>
                    <span className="text-slate-500">Days Logged:</span>
                    <strong className="text-slate-200 block">{data.flows?.days_recorded} Trading Days</strong>
                  </div>
                  <div>
                    <span className="text-slate-500">Status:</span>
                    <strong className="text-emerald-400 block">{data.flows?.stale ? 'Stale' : 'Active'}</strong>
                  </div>
                </div>
              </div>
              <span className="text-[10px] text-slate-500 mt-2">Sourced daily institutional provisional turnover.</span>
            </div>

            {/* 4. Regulatory Filings Corpus */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-slate-200 flex items-center gap-1.5">
                    <FileText className="w-4 h-4 text-indigo-400" /> Regulatory Filings Corpus
                  </span>
                  <span className="text-[10px] font-bold text-slate-400">
                    {data.filings?.corpus_count} Chunks Ingested
                  </span>
                </div>
                <div className="flex flex-col gap-1.5 max-h-36 overflow-y-auto pr-1">
                  {(data.filings?.documents || []).length > 0 ? (
                    data.filings.documents.map((d: any, idx: number) => (
                      <div key={idx} className="p-1.5 rounded bg-slate-950/60 border border-slate-800/80 text-[10px]">
                        <strong className="text-slate-200 block truncate">{d.title}</strong>
                        <span className="text-[9px] text-slate-500 uppercase">{d.type}</span>
                      </div>
                    ))
                  ) : (
                    <div className="text-slate-500 text-[11px] py-4 text-center">
                      Zero corporate filings stored (graceful degradation demo case).
                    </div>
                  )}
                </div>
              </div>
              <span className="text-[10px] text-slate-500 mt-2">Vectorized into 384-dim dense embeddings.</span>
            </div>
          </div>
        ) : null}

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-800 text-[11px] text-slate-400">
          <span>Demonstrates ingestion of multi-dimensional unstructured and structured streams.</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

