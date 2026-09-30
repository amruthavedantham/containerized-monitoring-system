import React, { useState } from 'react';
import { Activity, Clock, AlertTriangle, Zap, TrendingUp, Sparkles, Filter } from 'lucide-react';

export default function LiveMetricsGraph({ history = [], currentMetrics = {}, isDemoRunning = false }) {
  const [hoveredPoint, setHoveredPoint] = useState(null);
  const [activeSeries, setActiveSeries] = useState({
    traffic: true,
    latency: true,
    errors: true
  });

  // Keep last 30 data points for optimal chart rendering
  const data = history.slice(-30);

  const toggleSeries = (key) => {
    setActiveSeries(prev => ({ ...prev, [key]: !prev[key] }));
  };

  // SVG dimensions
  const svgWidth = 700;
  const svgHeight = 220;
  const padding = { top: 20, right: 25, bottom: 30, left: 45 };
  const chartWidth = svgWidth - padding.left - padding.right;
  const chartHeight = svgHeight - padding.top - padding.bottom;

  // Compute maximum values for scaling (with sensible minimums)
  const maxTraffic = Math.max(...data.map(d => d.traffic || 0), currentMetrics.request_rate_per_sec || 0, 40);
  const maxLatency = Math.max(...data.map(d => d.latency || 0), currentMetrics.p90_latency_seconds || 0, 1.0);
  const maxErrors = Math.max(...data.map(d => d.errors || 0), currentMetrics.error_rate_per_sec || 0, 10);

  // Normalization helper (0 to 1)
  const normalize = (val, max) => Math.min(Math.max((val || 0) / (max || 1), 0), 1);

  // Generate SVG coordinates for a series
  const getCoordinates = (accessor, maxVal) => {
    if (data.length === 0) return [];
    const step = chartWidth / Math.max(data.length - 1, 1);
    return data.map((d, i) => {
      const x = padding.left + i * step;
      const normalized = normalize(accessor(d), maxVal);
      const y = padding.top + chartHeight - (normalized * chartHeight);
      return { x, y, val: accessor(d), data: d };
    });
  };

  const trafficCoords = getCoordinates(d => d.traffic, maxTraffic);
  const latencyCoords = getCoordinates(d => d.latency, maxLatency);
  const errorCoords = getCoordinates(d => d.errors, maxErrors);

  // Build SVG smooth path command
  const buildPath = (coords) => {
    if (coords.length === 0) return '';
    if (coords.length === 1) return `M ${coords[0].x} ${coords[0].y}`;
    return coords.reduce((acc, curr, idx, arr) => {
      if (idx === 0) return `M ${curr.x} ${curr.y}`;
      const prev = arr[idx - 1];
      const cpX1 = prev.x + (curr.x - prev.x) / 2;
      const cpY1 = prev.y;
      const cpX2 = prev.x + (curr.x - prev.x) / 2;
      const cpY2 = curr.y;
      return `${acc} C ${cpX1} ${cpY1}, ${cpX2} ${cpY2}, ${curr.x} ${curr.y}`;
    }, '');
  };

  // Build SVG area under curve
  const buildAreaPath = (coords) => {
    if (coords.length === 0) return '';
    const linePath = buildPath(coords);
    const lastX = coords[coords.length - 1].x;
    const firstX = coords[0].x;
    const bottomY = padding.top + chartHeight;
    return `${linePath} L ${lastX} ${bottomY} L ${firstX} ${bottomY} Z`;
  };

  const currentTraffic = currentMetrics.request_rate_per_sec ?? (data.length > 0 ? data[data.length - 1].traffic : 0);
  const currentLatency = currentMetrics.p90_latency_seconds ?? (data.length > 0 ? data[data.length - 1].latency : 0);
  const currentErrors = currentMetrics.error_percentage ?? (data.length > 0 ? data[data.length - 1].errors : 0);

  return (
    <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 md:p-7 space-y-6 shadow-xl relative overflow-hidden">
      {/* Glow highlight */}
      <div className="absolute top-0 right-1/4 w-96 h-48 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header with Title & Legend Toggles */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-400" />
              Live Input & System Metrics Graph
            </h3>
            {isDemoRunning ? (
              <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                </span>
                Demo Active
              </span>
            ) : (
              <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                Live Feed
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time visualization of evaluated traffic, latency, and error distribution.
          </p>
        </div>

        {/* Series Filter Toggles */}
        <div className="flex items-center gap-2 bg-slate-950/80 p-1 rounded-xl border border-slate-800 self-start sm:self-auto">
          <button
            onClick={() => toggleSeries('traffic')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeSeries.traffic
                ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40'
                : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-indigo-400" />
            Traffic
          </button>

          <button
            onClick={() => toggleSeries('latency')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeSeries.latency
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            Latency
          </button>

          <button
            onClick={() => toggleSeries('errors')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeSeries.errors
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-rose-400" />
            Errors
          </button>
        </div>
      </div>

      {/* SVG Time-Series Chart */}
      <div className="relative bg-slate-950/70 border border-slate-800/80 rounded-xl p-3 sm:p-4 overflow-hidden">
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="w-full h-48 sm:h-60 overflow-visible"
          onMouseLeave={() => setHoveredPoint(null)}
        >
          <defs>
            {/* Traffic Gradient */}
            <linearGradient id="trafficGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#818cf8" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#818cf8" stopOpacity="0.0" />
            </linearGradient>
            {/* Latency Gradient */}
            <linearGradient id="latencyGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#fbbf24" stopOpacity="0.30" />
              <stop offset="100%" stopColor="#fbbf24" stopOpacity="0.0" />
            </linearGradient>
            {/* Errors Gradient */}
            <linearGradient id="errorGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f43f5e" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#f43f5e" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Background horizontal grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
            const y = padding.top + chartHeight * pct;
            return (
              <g key={i}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={padding.left + chartWidth}
                  y2={y}
                  stroke="#1e293b"
                  strokeDasharray="4 4"
                  strokeWidth="1"
                />
                <text
                  x={padding.left - 8}
                  y={y + 4}
                  fill="#64748b"
                  fontSize="10"
                  fontFamily="monospace"
                  textAnchor="end"
                >
                  {Math.round((1 - pct) * 100)}%
                </text>
              </g>
            );
          })}

          {/* Traffic Series */}
          {activeSeries.traffic && trafficCoords.length > 0 && (
            <>
              <path d={buildAreaPath(trafficCoords)} fill="url(#trafficGrad)" />
              <path
                d={buildPath(trafficCoords)}
                fill="none"
                stroke="#818cf8"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </>
          )}

          {/* Latency Series */}
          {activeSeries.latency && latencyCoords.length > 0 && (
            <>
              <path d={buildAreaPath(latencyCoords)} fill="url(#latencyGrad)" />
              <path
                d={buildPath(latencyCoords)}
                fill="none"
                stroke="#fbbf24"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </>
          )}

          {/* Errors Series */}
          {activeSeries.errors && errorCoords.length > 0 && (
            <>
              <path d={buildAreaPath(errorCoords)} fill="url(#errorGrad)" />
              <path
                d={buildPath(errorCoords)}
                fill="none"
                stroke="#f43f5e"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </>
          )}

          {/* Interactive Hover Vertical Line & Target Points */}
          {hoveredPoint && (
            <g>
              <line
                x1={hoveredPoint.x}
                y1={padding.top}
                x2={hoveredPoint.x}
                y2={padding.top + chartHeight}
                stroke="#94a3b8"
                strokeWidth="1.5"
                strokeDasharray="2 2"
              />
            </g>
          )}

          {/* Invisible interactive hover rects along X axis */}
          {data.map((d, i) => {
            const step = chartWidth / Math.max(data.length - 1, 1);
            const x = padding.left + i * step;
            return (
              <rect
                key={i}
                x={x - step / 2}
                y={padding.top}
                width={step}
                height={chartHeight}
                fill="transparent"
                className="cursor-crosshair"
                onMouseEnter={() => setHoveredPoint({ x, data: d })}
              />
            );
          })}
        </svg>

        {/* Floating Tooltip */}
        {hoveredPoint && (
          <div
            className="absolute z-20 pointer-events-none p-2.5 rounded-xl bg-slate-900/95 border border-slate-700 shadow-2xl text-xs space-y-1 backdrop-blur-md"
            style={{
              left: `${Math.min(Math.max((hoveredPoint.x / svgWidth) * 100, 10), 80)}%`,
              top: '12px'
            }}
          >
            <div className="text-[10px] font-mono text-slate-400 border-b border-slate-800 pb-1">
              Time: {hoveredPoint.data.time || 'Live'}
            </div>
            {activeSeries.traffic && (
              <div className="flex items-center justify-between gap-4 text-indigo-300 font-mono">
                <span>Traffic:</span>
                <span className="font-bold">{hoveredPoint.data.traffic} req/s</span>
              </div>
            )}
            {activeSeries.latency && (
              <div className="flex items-center justify-between gap-4 text-amber-300 font-mono">
                <span>Latency:</span>
                <span className="font-bold">{hoveredPoint.data.latency}s</span>
              </div>
            )}
            {activeSeries.errors && (
              <div className="flex items-center justify-between gap-4 text-rose-300 font-mono">
                <span>Errors:</span>
                <span className="font-bold">{hoveredPoint.data.errors} {hoveredPoint.data.error_rate_per_sec !== undefined ? 'err/s' : '%'}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Live Metric Badges Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-1">
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Traffic Rate</div>
              <div className="text-lg font-bold font-mono text-white">{currentTraffic} <span className="text-xs text-slate-400 font-normal">req/s</span></div>
            </div>
          </div>
          <span className="text-[11px] font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
            Scale: {maxTraffic}
          </span>
        </div>

        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Clock className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">P90 Latency</div>
              <div className="text-lg font-bold font-mono text-white">{currentLatency} <span className="text-xs text-slate-400 font-normal">s</span></div>
            </div>
          </div>
          <span className="text-[11px] font-mono text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
            Scale: {maxLatency}s
          </span>
        </div>

        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <AlertTriangle className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Error Rate</div>
              <div className="text-lg font-bold font-mono text-white">{currentErrors} <span className="text-xs text-slate-400 font-normal">{typeof currentErrors === 'number' && currentErrors > 0 && currentErrors <= 100 ? '%' : 'err/s'}</span></div>
            </div>
          </div>
          <span className="text-[11px] font-mono text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
            Scale: {maxErrors}
          </span>
        </div>
      </div>
    </div>
  );
}
