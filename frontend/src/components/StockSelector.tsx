'use client';

import React from 'react';
import { Search } from 'lucide-react';

interface StockSelectorProps {
  stocks: any[];
  selectedTicker: string;
  onSelectTicker: (ticker: string) => void;
}

export const StockSelector: React.FC<StockSelectorProps> = ({
  stocks,
  selectedTicker,
  onSelectTicker
}) => {
  const [filter, setFilter] = React.useState('');

  const filtered = stocks.filter(
    (s) =>
      s.ticker.toLowerCase().includes(filter.toLowerCase()) ||
      s.name.toLowerCase().includes(filter.toLowerCase()) ||
      s.sector.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between gap-3">
        <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
          Nifty 50 Focus Watchlist ({stocks.length})
        </span>
        <div className="relative w-44">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-2 text-slate-400" />
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Search stock..."
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-3 py-1 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-1.5 scrollbar-thin">
        {filtered.map((s) => {
          const isSelected = selectedTicker === s.ticker;
          const isUp = s.change_24h >= 0;
          return (
            <button
              key={s.ticker}
              onClick={() => onSelectTicker(s.ticker)}
              className={`px-3 py-1.5 rounded-lg border text-left shrink-0 transition-all ${
                isSelected
                  ? 'bg-blue-600/20 border-blue-500 text-white shadow-sm'
                  : 'bg-slate-900/80 border-slate-800/80 text-slate-300 hover:bg-slate-800/80 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-xs">{s.ticker}</span>
                <span className="text-[10px] text-slate-400">({s.sector})</span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] mt-0.5">
                <span className="font-semibold text-slate-200">Rs {s.latest_price}</span>
                <span className={`text-[10px] font-medium ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {isUp ? '+' : ''}{s.change_pct}%
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

