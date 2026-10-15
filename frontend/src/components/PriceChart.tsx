'use client';

import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';

interface PriceChartProps {
  candles: any[];
  ticker: string;
  latestPrice: number;
}

export const PriceChart: React.FC<PriceChartProps> = ({
  candles,
  ticker,
  latestPrice
}) => {
  if (!candles || candles.length === 0) {
    return (
      <div className="bg-[#111827] border border-slate-800 rounded-xl p-6 text-center text-slate-400 text-xs h-64 flex items-center justify-center">
        Loading price action series...
      </div>
    );
  }

  const data = candles.slice(-50).map((c) => ({
    date: c.date.slice(5),
    close: c.close,
    open: c.open,
    high: c.high,
    low: c.low,
    volume: c.volume,
    color: c.close >= c.open ? '#10b981' : '#ef4444'
  }));

  const minPrice = Math.min(...data.map((d) => d.low)) * 0.98;
  const maxPrice = Math.max(...data.map((d) => d.high)) * 1.02;

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl p-4 shadow-sm flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-bold text-sm text-slate-100">{ticker} Technical Price Action</span>
          <span className="text-xs text-slate-400">Daily OHLCV Snapshot</span>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span className="text-slate-400">Last Close: <strong className="text-white text-sm">Rs {latestPrice}</strong></span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            50-Day View
          </span>
        </div>
      </div>

      <div className="h-60 w-full mt-2">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 10 }} tickLine={false} />
            <YAxis
              yAxisId="price"
              domain={[Math.round(minPrice), Math.round(maxPrice)]}
              stroke="#64748b"
              tick={{ fontSize: 10 }}
              tickLine={false}
              orientation="right"
            />
            <YAxis
              yAxisId="volume"
              orientation="left"
              domain={[0, 'dataMax * 3']}
              hide={true}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '8px',
                fontSize: '11px'
              }}
              formatter={(val: any, name: string) => [
                name === 'close' ? `Rs ${val}` : val.toLocaleString(),
                name === 'close' ? 'Close Price' : 'Volume'
              ]}
            />
            <Bar yAxisId="volume" dataKey="volume" fill="#475569" opacity={0.35} radius={[2, 2, 0, 0]} />
            <Area
              yAxisId="price"
              type="monotone"
              dataKey="close"
              stroke="#3b82f6"
              strokeWidth={2}
              fill="url(#priceGradient)"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

