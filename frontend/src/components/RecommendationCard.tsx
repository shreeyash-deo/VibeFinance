'use client';

import React from 'react';
import {
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  FileCheck2,
  ExternalLink,
  Info
} from 'lucide-react';

interface RecommendationCardProps {
  recommendation: any;
  conflict: any;
  risk: any;
  ticker: string;
  onOpenCitation: (sourceId: string) => void;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  conflict,
  risk,
  ticker,
  onOpenCitation
}) => {
  if (!recommendation) {
    return (
      <div className="bg-[#111827] border border-slate-800 rounded-xl p-6 text-center text-slate-400 text-xs h-full flex flex-col items-center justify-center">
        <Sparkles className="w-8 h-8 text-slate-600 mb-2" />
        <span className="font-semibold text-slate-300">Awaiting Pipeline Execution</span>
        <p className="text-slate-500 mt-1 max-w-xs">
          Select a stock and click "Run Pipeline" to generate explainable, personalized financial intelligence.
        </p>
      </div>
    );
  }

  const actionColors: Record<string, { bg: string; text: string; border: string }> = {
    accumulate: { bg: 'bg-emerald-500/20', text: 'text-emerald-400', border: 'border-emerald-500/40' },
    hold: { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/40' },
    avoid: { bg: 'bg-rose-500/20', text: 'text-rose-400', border: 'border-rose-500/40' },
    wait: { bg: 'bg-amber-500/20', text: 'text-amber-400', border: 'border-amber-500/40' },
    reduce: { bg: 'bg-purple-500/20', text: 'text-purple-400', border: 'border-purple-500/40' }
  };

  const actionStyle = actionColors[recommendation.action] || actionColors['wait'];

  // Parse summary text and replace [1], [2] markers with clickable buttons
  const renderSummaryWithCitations = (summary: string, citations: any[]) => {
    if (!summary) return null;
    const parts = summary.split(/(\[\d+\])/g);
    return parts.map((part, i) => {
      const match = part.match(/\[(\d+)\]/);
      if (match) {
        const citeIndex = parseInt(match[1], 10) - 1;
        const citedItem = citations[citeIndex];
        return (
          <button
            key={i}
            onClick={() => citedItem && onOpenCitation(citedItem.source_id)}
            className="inline-flex items-center px-1 py-0.2 mx-0.5 text-[11px] font-bold text-blue-400 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 rounded transition-colors"
            title={citedItem ? `${citedItem.title}: ${citedItem.snippet}` : 'View Citation'}
          >
            {part}
          </button>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl p-4 shadow-sm flex flex-col gap-3 h-full">
      {/* 1. Header & Action Badge */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-slate-100 text-sm">{ticker} Synthesis Recommendation</h3>
            <span className="text-[11px] text-slate-400">Grounded Multi-Agent Intelligence</span>
          </div>
        </div>
        <span
          className={`text-sm uppercase font-black px-3 py-1 rounded-lg border shadow-sm ${actionStyle.bg} ${actionStyle.text} ${actionStyle.border}`}
        >
          {recommendation.action}
        </span>
      </div>

      {/* 2. Conflict Alert Banner (If Applicable) */}
      {conflict && conflict.conflict && (
        <div className="bg-amber-950/30 border border-amber-500/40 rounded-xl p-3 text-amber-300 text-xs flex flex-col gap-2">
          <div className="flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <strong className="text-xs text-amber-200">Analytical Signal Conflict Detected</strong>
                <span className="font-mono text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded border border-amber-500/30 font-bold">
                  Disagreement: {conflict.disagreement_score}
                </span>
              </div>
              <p className="text-[11px] text-amber-300/90 mt-1 leading-relaxed">
                {conflict.explanation}
              </p>
            </div>
          </div>

          {conflict.pairs && conflict.pairs.length > 0 && (
            <div className="bg-slate-950/60 p-2 rounded-lg border border-amber-500/20 text-[10px] flex items-center justify-between text-slate-300">
              <span className="text-emerald-400 font-bold">[{conflict.pairs[0][0]}: Bullish]</span>
              <span className="text-amber-400 font-extrabold text-xs">⚡ DIVERGENCE ⚡</span>
              <span className="text-rose-400 font-bold">[{conflict.pairs[0][1]}: Bearish]</span>
            </div>
          )}
        </div>
      )}

      {/* 3. Position Sizing & Confidence Matrix */}
      <div className="grid grid-cols-3 gap-2 text-xs bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
        <div>
          <span className="text-slate-400 text-[10px] block">Position Sizing</span>
          <span className="font-bold text-slate-100 text-sm">
            {recommendation.position_size_pct}%
          </span>
        </div>
        <div>
          <span className="text-slate-400 text-[10px] block">Composite Confidence</span>
          <span className="font-bold text-slate-100 text-sm">
            {Math.round(recommendation.confidence * 100)}%
          </span>
        </div>
        <div>
          <span className="text-slate-400 text-[10px] block">Risk Suitability</span>
          <span
            className={`font-bold text-xs uppercase ${
              risk?.risk_fit === 'good'
                ? 'text-emerald-400'
                : risk?.risk_fit === 'stretch'
                ? 'text-amber-400'
                : 'text-rose-400'
            }`}
          >
            {risk?.risk_fit || 'EVALUATED'}
          </span>
        </div>
      </div>

      {/* 4. Plain-English Synthesized Summary with Citations */}
      <div className="flex-1 flex flex-col justify-between">
        <div>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            Synthesized Reasoning Chain
          </span>
          <p className="text-xs text-slate-200 leading-relaxed bg-slate-900/40 p-3 rounded-lg border border-slate-800/80">
            {renderSummaryWithCitations(recommendation.summary, recommendation.citations || [])}
          </p>
        </div>

        {/* Citations List */}
        {recommendation.citations && recommendation.citations.length > 0 && (
          <div className="mt-3">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
              Verified Source Citations ({recommendation.citations.length})
            </span>
            <div className="flex flex-col gap-1.5">
              {recommendation.citations.map((ev: any, idx: number) => (
                <button
                  key={idx}
                  onClick={() => onOpenCitation(ev.source_id)}
                  className="flex items-center justify-between text-left p-2 rounded-lg bg-slate-900/90 hover:bg-slate-800/90 border border-slate-800 hover:border-slate-700 text-xs transition-all group"
                >
                  <div className="flex items-center gap-2 truncate">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                      [{idx + 1}]
                    </span>
                    <span className="text-slate-300 font-medium text-[11px] truncate group-hover:text-blue-300">
                      {ev.title}
                    </span>
                  </div>
                  <ExternalLink className="w-3 h-3 text-slate-500 group-hover:text-slate-300 shrink-0 ml-1" />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 5. SEBI Disclaimer */}
        <div className="mt-3 p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80 text-[10px] text-slate-400 leading-relaxed flex items-start gap-2">
          <Info className="w-3.5 h-3.5 text-slate-500 mt-0.5 shrink-0" />
          <span>{recommendation.disclaimer}</span>
        </div>
      </div>
    </div>
  );
};

