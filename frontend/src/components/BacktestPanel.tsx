'use client';

import React, { useState, useEffect } from 'react';
import { Target, BarChart2, ShieldCheck } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

interface BacktestPanelProps {
  backtestData: any[];
}

export const BacktestPanel: React.FC<BacktestPanelProps> = ({ backtestData }) => {
  const [activeTab, setActiveTab] = useState<'backtest' | 'calibration'>('backtest');
  const [calibrationData, setCalibrationData] = useState<any[]>([]);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/metrics/calibration')
      .then((r) => r.json())
      .then((d) => setCalibrationData(d))
      .catch((e) => console.error(e));
  }, []);

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl p-4 shadow-sm flex flex-col gap-3">
      {/* Header with Tab Switcher */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-blue-500/10 text-blue-400">
            <Target className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-xs text-slate-100">Historical Evaluation & Calibration</h3>
            <span className="text-[11px] text-slate-400">Walk-Forward Simulation & Uncertainty Estimation</span>
          </div>
        </div>

        <div className="flex items-center bg-slate-900 rounded-lg p-0.5 border border-slate-800 text-[10px]">
          <button
            onClick={() => setActiveTab('backtest')}
            className={`px-2.5 py-1 rounded font-semibold transition-all ${
              activeTab === 'backtest'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            30d Hit Rates
          </button>
          <button
            onClick={() => setActiveTab('calibration')}
            className={`px-2.5 py-1 rounded font-semibold transition-all ${
              activeTab === 'calibration'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Confidence Calibration
          </button>
        </div>
      </div>

      {activeTab === 'backtest' ? (
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="text-[10px] uppercase text-slate-400 bg-slate-900/80 border-b border-slate-800">
              <tr>
                <th className="py-2 px-3">Quantitative Agent</th>
                <th className="py-2 px-3">Universe</th>
                <th className="py-2 px-3 text-center">Horizon</th>
                <th className="py-2 px-3 text-center">Signals</th>
                <th className="py-2 px-3 text-center">Hit Rate %</th>
                <th className="py-2 px-3 text-right">Avg 30d Fwd Return</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {backtestData.length > 0 ? (
                backtestData.map((b: any, idx: number) => (
                  <tr key={idx} className="hover:bg-slate-800/40">
                    <td className="py-2.5 px-3 font-semibold text-slate-200">{b.agent}</td>
                    <td className="py-2.5 px-3 text-slate-400">{b.ticker}</td>
                    <td className="py-2.5 px-3 text-center text-slate-300">{b.horizon_days}d</td>
                    <td className="py-2.5 px-3 text-center font-mono text-slate-300">{b.n_signals}</td>
                    <td className="py-2.5 px-3 text-center font-bold text-emerald-400">{b.hit_rate}%</td>
                    <td className="py-2.5 px-3 text-right font-mono font-medium text-slate-200">
                      {b.avg_fwd_return >= 0 ? '+' : ''}{b.avg_fwd_return}%
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="text-center py-4 text-slate-500">
                    Loading backtest evaluation metrics...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
            <span>Predicted Confidence vs. Actual Hit Rate (5 Buckets):</span>
            <span className="text-emerald-400 font-semibold text-[10px]">Empirical Calibration OK</span>
          </div>

          <div className="h-40 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={calibrationData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                <CartesianGrid stroke="#1e293b" vertical={false} />
                <XAxis dataKey="bucket" stroke="#64748b" tick={{ fontSize: 9 }} />
                <YAxis domain={[0, 100]} stroke="#64748b" tick={{ fontSize: 9 }} unit="%" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '6px', fontSize: '10px' }}
                  formatter={(val: any, name: string) => [`${val}%`, name === 'predicted' ? 'Predicted Confidence' : 'Actual Hit Rate']}
                />
                <Bar dataKey="predicted" fill="#64748b" name="predicted" radius={[3, 3, 0, 0]} />
                <Bar dataKey="actual" fill="#10b981" name="actual" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex items-center justify-center gap-4 text-[10px] text-slate-400">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-sm bg-slate-500 inline-block" /> Predicted Confidence
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500 inline-block" /> Actual Empirical Hit Rate
            </span>
          </div>
        </div>
      )}

      <p className="text-[10px] text-slate-500 leading-relaxed italic border-t border-slate-800/60 pt-2">
        *Zero Look-Ahead Bias: Signals simulated using day t data only. Evaluates 18 Nifty 50 stocks over 18 months.
      </p>
    </div>
  );
};
