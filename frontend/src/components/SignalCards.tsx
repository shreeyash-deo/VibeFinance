'use client';

import React from 'react';
import {
  TrendingUp,
  Activity,
  MessageSquare,
  FileText,
  DollarSign,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  CheckCircle2
} from 'lucide-react';

interface SignalCardsProps {
  signals: Record<string, any>;
  onOpenCitation: (sourceId: string) => void;
}

export const SignalCards: React.FC<SignalCardsProps> = ({ signals, onOpenCitation }) => {
  const [expandedAgent, setExpandedAgent] = React.useState<string | null>(null);

  const toggleExpand = (name: string) => {
    setExpandedAgent(expandedAgent === name ? null : name);
  };

  const agentIcons: Record<string, any> = {
    'Momentum Agent': TrendingUp,
    'Volume Anomaly Agent': Activity,
    'Sentiment Agent': MessageSquare,
    'Filings RAG Agent': FileText,
    'Institutional Flow Agent': DollarSign
  };

  const signalColors: Record<string, { bg: string; text: string; border: string }> = {
    bullish: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30' },
    bearish: { bg: 'bg-rose-500/10', text: 'text-rose-400', border: 'border-rose-500/30' },
    neutral: { bg: 'bg-slate-800/80', text: 'text-slate-300', border: 'border-slate-700/80' },
    anomalous: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30' },
    no_data: { bg: 'bg-slate-900', text: 'text-slate-500', border: 'border-slate-800' }
  };

  if (!signals || Object.keys(signals).length === 0) {
    return (
      <div className="bg-[#111827] border border-slate-800 rounded-xl p-6 text-center text-slate-400 text-xs">
        No active agent signals available. Click "Run Pipeline" to generate multi-agent intelligence.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
          Multi-Agent Signal Classifications (5 Parallel Dimensions)
        </span>
        <span className="text-[11px] text-slate-400">Structured Pydantic Contract</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {Object.entries(signals).map(([name, out]: [string, any]) => {
          const Icon = agentIcons[name] || Activity;
          const confPct = Math.round((out.confidence || 0) * 100);
          const style = signalColors[out.signal] || signalColors['neutral'];
          const isExpanded = expandedAgent === name;

          return (
            <div
              key={name}
              className="bg-[#111827] border border-slate-800 rounded-xl p-3 shadow-sm hover:border-slate-700 transition-all flex flex-col justify-between"
            >
              <div>
                {/* Header */}
                <div className="flex items-center justify-between gap-1 mb-2">
                  <div className="flex items-center gap-1.5">
                    <div className="p-1 rounded bg-slate-800 text-blue-400">
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <span className="font-semibold text-xs text-slate-200 truncate" title={name}>
                      {name.replace(' Agent', '')}
                    </span>
                  </div>
                  <span
                    className={`text-[9px] uppercase px-1.5 py-0.5 rounded font-bold border ${
                      out.status === 'ok'
                        ? 'bg-slate-800 text-emerald-400 border-slate-700'
                        : 'bg-amber-950/40 text-amber-300 border-amber-600/40'
                    }`}
                  >
                    {out.status}
                  </span>
                </div>

                {/* Signal Badge & Confidence */}
                <div className="flex items-center justify-between my-2">
                  <span
                    className={`text-xs uppercase font-extrabold px-2.5 py-0.5 rounded border ${style.bg} ${style.text} ${style.border}`}
                  >
                    {out.signal}
                  </span>
                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 block">Confidence</span>
                    <span className="text-xs font-bold text-slate-200">{confPct}%</span>
                  </div>
                </div>

                {/* Confidence Bar */}
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-2">
                  <div
                    className={`h-full rounded-full transition-all ${
                      out.signal === 'bullish'
                        ? 'bg-emerald-500'
                        : out.signal === 'bearish'
                        ? 'bg-rose-500'
                        : out.signal === 'anomalous'
                        ? 'bg-amber-500'
                        : 'bg-blue-500'
                    }`}
                    style={{ width: `${confPct}%` }}
                  />
                </div>

                {/* Grounded Reasoning Preview */}
                <p className="text-[11px] text-slate-300/90 leading-relaxed line-clamp-3">
                  {out.reasoning}
                </p>
              </div>

              {/* Expand Toggle */}
              <div className="mt-3 pt-2 border-t border-slate-800/80">
                <button
                  onClick={() => toggleExpand(name)}
                  className="w-full flex items-center justify-between text-[10px] text-slate-400 hover:text-slate-200 font-medium"
                >
                  <span>{isExpanded ? 'Hide Evidence & Metrics' : 'View Metrics & Evidence'}</span>
                  {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>

                {isExpanded && (
                  <div className="mt-2 text-[10px] flex flex-col gap-2 bg-slate-900/90 p-2 rounded border border-slate-800 animate-fadeIn">
                    <div>
                      <strong className="text-slate-400 block mb-1">Computed Metrics:</strong>
                      <div className="grid grid-cols-2 gap-1 text-[10px] font-mono text-slate-300">
                        {Object.entries(out.metrics || {}).map(([k, v]: [string, any]) => (
                          <div key={k} className="truncate">
                            <span className="text-slate-500">{k}:</span> {typeof v === 'number' ? v : String(v)}
                          </div>
                        ))}
                      </div>
                    </div>

                    {out.evidence && out.evidence.length > 0 && (
                      <div>
                        <strong className="text-slate-400 block mb-1">Citations ({out.evidence.length}):</strong>
                        <div className="flex flex-col gap-1">
                          {out.evidence.map((ev: any, idx: number) => (
                            <button
                              key={idx}
                              onClick={() => onOpenCitation(ev.source_id)}
                              className="text-left text-[10px] p-1 rounded bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 text-blue-300 hover:text-blue-200 truncate"
                            >
                              [{ev.source_type.toUpperCase()}] {ev.title}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {out.notes && out.notes.length > 0 && (
                      <div className="text-[9px] text-slate-400 italic">
                        {out.notes.join(' • ')}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

