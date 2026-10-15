'use client';

import React from 'react';
import { X, Users, CheckCircle2, AlertTriangle, ShieldAlert, ArrowRight } from 'lucide-react';

interface ComparePersonasModalProps {
  isOpen: boolean;
  onClose: () => void;
  ticker: string;
  results: Record<string, any>;
  isLoading: boolean;
  onRunCompare: () => void;
}

export const ComparePersonasModal: React.FC<ComparePersonasModalProps> = ({
  isOpen,
  onClose,
  ticker,
  results,
  isLoading,
  onRunCompare
}) => {
  if (!isOpen) return null;

  const personas = [
    { id: 'meena', name: 'Meena', role: 'Conservative Retiree', desc: 'Low volatility tolerance, zero patience for pledge or audit notes.' },
    { id: 'arjun', name: 'Arjun', role: 'Aggressive Trader', desc: 'High risk appetite, tech/momentum heavy, flexible position caps.' },
    { id: 'rohan', name: 'Rohan', role: 'Emotional Overtrader', desc: 'Frequent panic-seller, triggers mandatory behavioral cooling-off nudges.' }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="w-full max-w-5xl bg-[#0e1626] border border-slate-800 rounded-2xl p-6 shadow-2xl flex flex-col gap-5 max-h-[90vh] overflow-y-auto">
        {/* Top Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
              <Users className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-bold text-base text-slate-100">
                Personalization Stress Test: {ticker} Across 3 Distinct Profiles
              </h2>
              <p className="text-xs text-slate-400">
                Demonstrates that identical market signals produce customized intelligence and risk verdicts.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 3-Persona Comparison Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {personas.map((p) => {
            const res = results[p.id];
            const rec = res?.recommendation;
            const risk = res?.risk;

            const isAvoid = rec?.action === 'avoid' || rec?.action === 'wait';

            return (
              <div
                key={p.id}
                className="bg-[#111827] border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-md"
              >
                <div>
                  {/* Persona Header */}
                  <div className="border-b border-slate-800 pb-2.5 mb-3">
                    <span className="font-extrabold text-sm text-slate-100 block">{p.name}</span>
                    <span className="text-[11px] text-indigo-400 font-semibold">{p.role}</span>
                    <p className="text-[10px] text-slate-400 mt-1 leading-snug">{p.desc}</p>
                  </div>

                  {isLoading ? (
                    <div className="text-center py-10 text-slate-400 text-xs">
                      Evaluating {p.name}...
                    </div>
                  ) : rec ? (
                    <div className="flex flex-col gap-3 text-xs">
                      {/* Action Pill */}
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400 text-[10px] uppercase font-bold">Action</span>
                        <span
                          className={`font-black uppercase text-xs px-2.5 py-0.5 rounded border ${
                            rec.action === 'accumulate'
                              ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                              : isAvoid
                              ? 'bg-rose-500/20 text-rose-400 border-rose-500/30'
                              : 'bg-blue-500/20 text-blue-400 border-blue-500/30'
                          }`}
                        >
                          {rec.action}
                        </span>
                      </div>

                      {/* Position Cap & Fit */}
                      <div className="grid grid-cols-2 gap-2 bg-slate-900/80 p-2 rounded-lg border border-slate-800 text-[11px]">
                        <div>
                          <span className="text-slate-500 text-[10px] block">Position Sizing</span>
                          <strong className="text-slate-200">{rec.position_size_pct}%</strong>
                        </div>
                        <div>
                          <span className="text-slate-500 text-[10px] block">Risk Suitability</span>
                          <strong
                            className={`uppercase ${
                              risk?.risk_fit === 'good' ? 'text-emerald-400' : 'text-amber-400'
                            }`}
                          >
                            {risk?.risk_fit}
                          </strong>
                        </div>
                      </div>

                      {/* Summary */}
                      <div>
                        <span className="text-[10px] font-bold text-slate-400 block mb-1">
                          Tailored Reasoning:
                        </span>
                        <p className="text-[11px] text-slate-300 bg-slate-900/40 p-2.5 rounded-lg border border-slate-800/80 leading-relaxed">
                          {rec.summary}
                        </p>
                      </div>

                      {/* Behavioral Nudges */}
                      {risk?.behavioral_nudges && risk.behavioral_nudges.length > 0 && (
                        <div className="bg-amber-950/20 border border-amber-500/30 rounded-lg p-2 text-amber-300 text-[10px]">
                          <strong className="block text-amber-200">Behavioral Alert:</strong>
                          {risk.behavioral_nudges[0]}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-10 text-slate-500 text-xs">
                      Click below to generate.
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800/80 text-[10px] text-slate-500 flex items-center justify-between">
                  <span>Input: Same Data Snapshot</span>
                  <span className="text-emerald-400 font-bold">Personalized</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-800">
          <span className="text-[11px] text-slate-400">
            Acceptance Check: Validates that risk tolerance, portfolio HHI, and behavioral tags alter the output.
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={onRunCompare}
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-lg shadow-md transition-all disabled:opacity-50"
            >
              {isLoading ? 'Computing All 3...' : 'Re-Run Comparison'}
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

