'use client';

import React from 'react';
import { X, FileText, Calendar, ShieldCheck, Tag, ExternalLink } from 'lucide-react';

interface CitationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  citationId: string | null;
  citationData: any;
  isLoading: boolean;
}

export const CitationDrawer: React.FC<CitationDrawerProps> = ({
  isOpen,
  onClose,
  citationId,
  citationData,
  isLoading
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm transition-opacity">
      <div className="w-full max-w-lg bg-[#0e1626] border-l border-slate-800 h-full p-6 shadow-2xl flex flex-col justify-between overflow-y-auto animate-slideLeft">
        {/* Top Header */}
        <div>
          <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400">
                <FileText className="w-4 h-4" />
              </div>
              <h2 className="font-bold text-sm text-slate-100">Verified Sourced Evidence</h2>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {isLoading ? (
            <div className="text-center py-12 text-slate-400 text-xs">
              Loading source citation metadata...
            </div>
          ) : citationData ? (
            <div className="flex flex-col gap-4 text-xs">
              {/* Badges & Metadata */}
              <div className="flex flex-wrap items-center gap-2">
                <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 font-bold border border-blue-500/20 text-[10px]">
                  {citationData.ticker}
                </span>
                <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 font-bold border border-purple-500/20 text-[10px]">
                  {citationData.doc_type}
                </span>
                <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 font-bold border border-amber-500/20 text-[10px]">
                  {citationData.source_label} DATA
                </span>
                {citationData.page && (
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">
                    Page {citationData.page}
                  </span>
                )}
              </div>

              {/* Title */}
              <div>
                <h3 className="font-bold text-sm text-slate-100 leading-snug">
                  {citationData.title}
                </h3>
                <span className="text-[11px] text-slate-400 flex items-center gap-1 mt-1">
                  <Calendar className="w-3 h-3 text-slate-500" /> Disclosed on: {citationData.doc_date}
                </span>
              </div>

              {/* Full Text Excerpt */}
              <div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                  Exact Grounded Excerpt
                </span>
                <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-3.5 text-slate-200 leading-relaxed text-[11px] font-mono whitespace-pre-wrap">
                  {citationData.snippet}
                </div>
              </div>

              {/* Attribution & Integrity Statement */}
              <div className="bg-blue-950/20 border border-blue-500/30 rounded-lg p-3 text-blue-300 text-[11px] flex items-start gap-2">
                <ShieldCheck className="w-4 h-4 text-blue-400 mt-0.5 shrink-0" />
                <div>
                  <strong className="block text-blue-200">Verified Evidence Citation</strong>
                  <p className="text-blue-300/80 mt-0.5">
                    This document passage was retrieved via semantic vector search and validated against regulatory disclosure archives.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-400 text-xs">
              Citation details could not be found.
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-slate-800 text-right">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold"
          >
            Close Drawer
          </button>
        </div>
      </div>
    </div>
  );
};

