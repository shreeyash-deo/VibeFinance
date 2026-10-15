'use client';

import React from 'react';
import { UserCheck, PieChart, ShieldAlert, ArrowUpRight, ArrowDownRight, Layers, Gauge } from 'lucide-react';

interface LeftPanelProps {
  profile: any;
  portfolio: any;
  behaviorEvents: any[];
}

export const LeftPanel: React.FC<LeftPanelProps> = ({
  profile,
  portfolio,
  behaviorEvents
}) => {
  if (!profile) return null;

  const riskBadgeColors: Record<string, string> = {
    conservative: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    moderate: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    aggressive: 'bg-rose-500/20 text-rose-400 border-rose-500/30'
  };

  const isOvertrader = profile.overtrading_score > 0.6;
  const hhiVal = portfolio?.hhi || 0.0;
  const hhiStatus = hhiVal > 0.25 ? 'High (Concentrated)' : hhiVal > 0.15 ? 'Moderate Diversity' : 'Well Diversified';

  return (
    <div className="flex flex-col gap-4 text-xs h-full">
      {/* 1. Active Investor Profile Card */}
      <div className="bg-[#111827] border border-slate-800 rounded-xl p-4 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400">
              <UserCheck className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-slate-100 text-sm">{profile.display_name}</h3>
              <p className="text-[11px] text-slate-400">{profile.persona_label}</p>
            </div>
          </div>
          <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${riskBadgeColors[profile.risk_tolerance] || 'bg-slate-800 text-slate-300'}`}>
            {profile.risk_tolerance}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2 text-[11px] bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80 mb-3">
          <div>
            <span className="text-slate-400 block text-[10px]">Horizon</span>
            <span className="font-semibold text-slate-200">{profile.horizon_years} Years</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">Single Stock Cap</span>
            <span className="font-semibold text-slate-200">{profile.max_single_stock_pct}%</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">Loss Aversion</span>
            <span className="font-semibold text-slate-200">{profile.loss_aversion * 100}%</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">Overtrading Risk</span>
            <span className={`font-semibold ${isOvertrader ? 'text-amber-400' : 'text-slate-200'}`}>
              {profile.overtrading_score * 100}%
            </span>
          </div>
        </div>

        {/* Sector Allocation Ceilings with Progress Headroom Bars */}
        <div>
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-2 flex items-center justify-between">
            <span>Sector Limits & Exposure</span>
            <span className="text-[9px] text-slate-500">Policy Caps</span>
          </span>
          <div className="flex flex-col gap-2">
            {Object.entries(profile.sector_limits || {}).map(([sec, cap]) => {
              const currentExp = (portfolio?.holdings || [])
                .filter((h: any) => h.sector === sec)
                .reduce((acc: number, h: any) => acc + (h.weight_pct || 0), 0);
              const limitNum = Number(cap);
              const pctUsed = Math.min(100, Math.round((currentExp / limitNum) * 100));
              const isOver = currentExp >= limitNum;

              return (
                <div key={sec} className="bg-slate-900/70 p-2 rounded-lg border border-slate-800/80">
                  <div className="flex items-center justify-between text-[11px] mb-1">
                    <span className="text-slate-300 font-medium">{sec}</span>
                    <span className="font-mono text-[10px]">
                      <strong className={isOver ? 'text-rose-400' : 'text-slate-200'}>{currentExp.toFixed(1)}%</strong>
                      <span className="text-slate-500"> / {limitNum}% cap</span>
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        isOver ? 'bg-rose-500' : pctUsed > 75 ? 'bg-amber-500' : 'bg-blue-500'
                      }`}
                      style={{ width: `${pctUsed}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* 2. Behavioral Flags & Nudges */}
      {isOvertrader && (
        <div className="bg-amber-950/20 border border-amber-500/30 rounded-xl p-3 text-amber-300 flex items-start gap-2.5">
          <ShieldAlert className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />
          <div>
            <strong className="block text-[11px] text-amber-200">Behavioral Risk Alert Active</strong>
            <p className="text-[11px] text-amber-300/80 mt-0.5 leading-relaxed">
              4 impulsive panic sells recorded in last 60 days. System mandates cooling-off evaluations on new trades.
            </p>
          </div>
        </div>
      )}

      {/* 3. Portfolio Concentration & HHI */}
      {portfolio && (
        <div className="bg-[#111827] border border-slate-800 rounded-xl p-4 shadow-sm flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-300 flex items-center gap-1.5">
              <PieChart className="w-3.5 h-3.5 text-indigo-400" /> Portfolio Concentration
            </span>
            <span className="text-[11px] text-slate-400">
              Total: <strong className="text-white">Rs {portfolio.total_value?.toLocaleString()}</strong>
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
              <span className="text-slate-400 block text-[10px]">HHI Score</span>
              <span className="text-sm font-bold text-slate-100">{hhiVal}</span>
              <span className="text-[9px] text-indigo-400 block mt-0.5 font-medium">
                {hhiStatus}
              </span>
            </div>
            <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
              <span className="text-slate-400 block text-[10px]">Unrealized P&L</span>
              <span className={`text-sm font-bold flex items-center ${portfolio.total_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {portfolio.total_pnl >= 0 ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
                Rs {Math.abs(portfolio.total_pnl || 0).toLocaleString()} ({portfolio.total_pnl_pct}%)
              </span>
            </div>
          </div>

          {/* Holdings Table */}
          <div>
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
              Current Holdings
            </span>
            <div className="overflow-x-auto max-h-44 overflow-y-auto">
              <table className="w-full text-[10px] text-left">
                <thead className="text-slate-400 bg-slate-900/80 sticky top-0">
                  <tr>
                    <th className="py-1 px-1.5">Ticker</th>
                    <th className="py-1 px-1.5">Qty</th>
                    <th className="py-1 px-1.5">Avg</th>
                    <th className="py-1 px-1.5">Weight</th>
                    <th className="py-1 px-1.5 text-right">P&L</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {(portfolio.holdings || []).map((h: any) => (
                    <tr key={h.ticker} className="hover:bg-slate-800/40">
                      <td className="py-1.5 px-1.5 font-semibold text-slate-200">{h.ticker}</td>
                      <td className="py-1.5 px-1.5 text-slate-300">{h.qty}</td>
                      <td className="py-1.5 px-1.5 text-slate-300">Rs {h.avg_price}</td>
                      <td className="py-1.5 px-1.5 text-slate-400">{h.weight_pct}%</td>
                      <td className={`py-1.5 px-1.5 text-right font-medium ${h.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {h.pnl >= 0 ? '+' : ''}{h.pnl_pct}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
