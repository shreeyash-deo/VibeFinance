'use client';

import React from 'react';
import { ShieldAlert, Play, Users, RefreshCw, AlertTriangle, Database, WifiOff, Sparkles, FolderArchive } from 'lucide-react';

interface TopBarProps {
  activePersona: string;
  onSelectPersona: (persona: string) => void;
  dataMode: 'cached' | 'live';
  onToggleDataMode: () => void;
  simulateFeedDown: boolean;
  onToggleFeedDown: () => void;
  simulateMissingFiling: boolean;
  onToggleMissingFiling: () => void;
  onRunAnalysis: () => void;
  onOpenCompareModal: () => void;
  onOpenSearchModal: () => void;
  onOpenDataSourcesModal: () => void;
  isLoading: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({
  activePersona,
  onSelectPersona,
  dataMode,
  onToggleDataMode,
  simulateFeedDown,
  onToggleFeedDown,
  simulateMissingFiling,
  onToggleMissingFiling,
  onRunAnalysis,
  onOpenCompareModal,
  onOpenSearchModal,
  onOpenDataSourcesModal,
  isLoading
}) => {
  const personas = [
    { id: 'meena', name: 'Meena', role: 'Conservative (Retiree)' },
    { id: 'arjun', name: 'Arjun', role: 'Aggressive (Trader)' },
    { id: 'rohan', name: 'Rohan', role: 'Overtrader (Impulsive)' }
  ];

  return (
    <header className="border-b border-slate-800 bg-[#0d1322] px-6 py-3 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-40">
      {/* Brand & SEBI Compliance */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center font-black text-white text-lg shadow-lg shadow-blue-500/20">
            V
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-white tracking-tight">VibeFinance</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 font-semibold border border-blue-500/30">
                MULTI-AGENT v1.0
              </span>
            </div>
            <span className="text-[11px] text-slate-400 flex items-center gap-1">
              <ShieldAlert className="w-3 h-3 text-amber-400 inline" /> SEBI Non-Advisory Decision Support
            </span>
          </div>
        </div>
      </div>

      {/* Center Controls: Persona Switcher */}
      <div className="flex items-center bg-slate-900/90 rounded-lg p-1 border border-slate-800">
        <span className="text-xs text-slate-400 px-2 font-medium">Persona:</span>
        {personas.map((p) => {
          const isActive = activePersona === p.id;
          return (
            <button
              key={p.id}
              onClick={() => onSelectPersona(p.id)}
              className={`px-3 py-1 text-xs rounded font-medium transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              {p.name}
              <span className="text-[10px] text-slate-400 ml-1">({p.id})</span>
            </button>
          );
        })}
      </div>

      {/* Extension Modals & Degradation Simulator Toggles */}
      <div className="flex flex-wrap items-center gap-2">
        {/* Semantic Vector Search Trigger */}
        <button
          onClick={onOpenSearchModal}
          className="flex items-center gap-1.5 px-2.5 py-1 text-xs rounded bg-slate-900 border border-slate-800 text-blue-300 hover:border-blue-500/50 hover:bg-blue-500/10 transition-all"
          title="Search regulatory filings using 384-dim semantic vector embeddings"
        >
          <Sparkles className="w-3.5 h-3.5 text-blue-400" />
          <span>Vector Search</span>
        </button>

        {/* Multi-Source Feeds Explorer Trigger */}
        <button
          onClick={onOpenDataSourcesModal}
          className="flex items-center gap-1.5 px-2.5 py-1 text-xs rounded bg-slate-900 border border-slate-800 text-emerald-300 hover:border-emerald-500/50 hover:bg-emerald-500/10 transition-all"
          title="Inspect 4 simultaneous multi-source data ingestion feeds"
        >
          <FolderArchive className="w-3.5 h-3.5 text-emerald-400" />
          <span>Data Feeds</span>
        </button>

        {/* Degradation Simulator Toggles */}
        <button
          onClick={onToggleFeedDown}
          className={`flex items-center gap-1.5 px-2.5 py-1 text-xs rounded border transition-all ${
            simulateFeedDown
              ? 'bg-red-500/20 border-red-500/50 text-red-300 animate-pulse'
              : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
          }`}
          title="Simulate data feed crash to test resilient cache fallback"
        >
          <WifiOff className="w-3.5 h-3.5" />
          <span>Feed Down</span>
        </button>

        <button
          onClick={onToggleMissingFiling}
          className={`flex items-center gap-1.5 px-2.5 py-1 text-xs rounded border transition-all ${
            simulateMissingFiling
              ? 'bg-amber-500/20 border-amber-500/50 text-amber-300'
              : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
          }`}
          title="Simulate missing filings to test graceful degradation"
        >
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>Missing Filing</span>
        </button>

        {/* Compare Personas Trigger */}
        <button
          onClick={onOpenCompareModal}
          className="flex items-center gap-1 px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded border border-slate-700 transition-colors"
        >
          <Users className="w-3.5 h-3.5 text-indigo-400" />
          <span>Compare Personas</span>
        </button>

        {/* Run Analysis Button */}
        <button
          onClick={onRunAnalysis}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-4 py-1.5 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white text-xs font-bold rounded shadow-md shadow-blue-600/30 transition-all disabled:opacity-50"
        >
          {isLoading ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Synthesizing...</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Run Pipeline</span>
            </>
          )}
        </button>
      </div>
    </header>
  );
};
