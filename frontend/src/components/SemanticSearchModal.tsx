'use client';

import React, { useState } from 'react';
import { Search, X, Sparkles, FileText, CheckCircle2, SlidersHorizontal } from 'lucide-react';

interface SemanticSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedTicker: string;
}

export const SemanticSearchModal: React.FC<SemanticSearchModalProps> = ({
  isOpen,
  onClose,
  selectedTicker
}) => {
  const [query, setQuery] = useState('promoter pledge and encumbrance');
  const [filterTicker, setFilterTicker] = useState<string>(selectedTicker || 'ADANIENT');
  const [results, setResults] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleSearch = async () => {
    setIsLoading(true);
    try {
      const tickerParam = filterTicker === 'ALL' ? '' : `&ticker=${filterTicker}`;
      const res = await fetch(`http://127.0.0.1:8000/api/documents/search?query=${encodeURIComponent(query)}${tickerParam}&top_k=6`);
      if (res.ok) {
        const data = await res.json();
        setResults(data);
      }
    } catch (e) {
      console.error('Semantic search failed:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const sampleQueries = [
    'promoter pledge and debt covenants',
    'EBIT margin guidance cut and cost escalation',
    'auditor qualification related party loans',
    'constant currency revenue growth deal wins',
    'US FDA Form 483 inspectional observations',
    'CASA ratio and credit deposit normalization'
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="w-full max-w-4xl bg-[#0e1626] border border-slate-800 rounded-2xl p-6 shadow-2xl flex flex-col gap-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-bold text-sm text-slate-100">
                Semantic Vector Search Engine (384-Dim Dense Embeddings)
              </h2>
              <p className="text-xs text-slate-400">
                Searches regulatory disclosures, SEBI filings & earnings call transcripts using cosine similarity.
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

        {/* Search Bar & Ticker Filter */}
        <div className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search regulatory filings semantically (e.g. margin guidance cut)..."
              className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <select
            value={filterTicker}
            onChange={(e) => setFilterTicker(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-xs text-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
          >
            <option value="ALL">All 18 Tickers</option>
            <option value="ADANIENT">ADANIENT</option>
            <option value="TATAMOTORS">TATAMOTORS</option>
            <option value="INFY">INFY</option>
            <option value="HDFCBANK">HDFCBANK</option>
            <option value="SUNPHARMA">SUNPHARMA</option>
            <option value="ITC">ITC</option>
            <option value="RELIANCE">RELIANCE</option>
            <option value="TCS">TCS</option>
          </select>

          <button
            onClick={handleSearch}
            disabled={isLoading}
            className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-lg shadow-md transition-all disabled:opacity-50 shrink-0"
          >
            {isLoading ? 'Searching...' : 'Vector Search'}
          </button>
        </div>

        {/* Sample Queries */}
        <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
          <span className="text-slate-500 font-medium">Try:</span>
          {sampleQueries.map((sq, i) => (
            <button
              key={i}
              onClick={() => {
                setQuery(sq);
                setTimeout(handleSearch, 50);
              }}
              className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 text-[10px] transition-colors"
            >
              {sq}
            </button>
          ))}
        </div>

        {/* Results Grid */}
        <div className="flex flex-col gap-2.5 mt-2 overflow-y-auto max-h-96 pr-1">
          {results.length > 0 ? (
            results.map((r, idx) => (
              <div
                key={idx}
                className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 hover:border-slate-700 transition-all text-xs flex flex-col gap-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-extrabold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded text-[10px] border border-blue-500/20">
                      {r.ticker}
                    </span>
                    <span className="font-bold text-slate-200 text-xs">{r.title}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-slate-400 font-mono">
                      Cosine Sim: <strong className="text-emerald-400 font-bold">{r.similarity_score}</strong>
                    </span>
                    <span className="text-[9px] uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-semibold">
                      {r.doc_type}
                    </span>
                  </div>
                </div>

                <p className="text-[11px] text-slate-300 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 leading-relaxed font-mono">
                  {r.snippet}
                </p>

                <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
                  <span>Disclosed: {r.doc_date}</span>
                  <span>Chunk ID: {r.chunk_id}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-12 text-slate-500 text-xs">
              Click "Vector Search" or select a sample query to retrieve semantic embeddings.
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-800 text-[11px] text-slate-400">
          <span>Vector Dimension: 384 dims (Normalized L2) • Cosine Similarity Metric</span>
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

