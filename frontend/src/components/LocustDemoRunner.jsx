import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Clock, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Flame, 
  RotateCcw, 
  StopCircle, 
  Zap, 
  Radio, 
  Layers,
  ArrowRight,
  TrendingUp
} from 'lucide-react';

export default function LocustDemoRunner({ onMetricsUpdate }) {
  const [activeDemo, setActiveDemo] = useState(null); // { demo_id, scenario, status, ... }
  const [isStarting, setIsStarting] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [completedDemo, setCompletedDemo] = useState(null);

  const pollIntervalRef = useRef(null);

  // Check if there is already an active demo on mount
  useEffect(() => {
    const checkActiveDemo = async () => {
      try {
        const res = await fetch('/api/demos/active');
        if (res.ok) {
          const data = await res.json();
          if (data.active && data.demo) {
            setActiveDemo(data.demo);
            startPolling(data.demo.demo_id);
          }
        }
      } catch {
        // Backend offline or unreachable
      }
    };
    checkActiveDemo();

    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, []);

  const startPolling = (demoId) => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);

    pollIntervalRef.current = setInterval(async () => {
      try {
        const res = await fetch(`/api/demos/${demoId}/status`);
        if (!res.ok) {
          if (res.status === 404) {
            clearInterval(pollIntervalRef.current);
            setActiveDemo(null);
          }
          return;
        }

        const data = await res.json();
        setActiveDemo(data);

        // Notify parent graph of real-time metrics
        if (data.current_metrics && onMetricsUpdate) {
          onMetricsUpdate({
            traffic: data.current_metrics.request_rate_per_sec || 0,
            latency: data.current_metrics.p90_latency_seconds || 0,
            errors: data.current_metrics.error_percentage || 0,
            raw: data.current_metrics
          });
        }

        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(pollIntervalRef.current);
          setCompletedDemo(data);
          setActiveDemo(null);
        }
      } catch (err) {
        console.error('Error polling demo status:', err);
      }
    }, 1000);
  };

  const handleStartDemo = async (scenario) => {
    setErrorMessage(null);
    setCompletedDemo(null);
    setIsStarting(true);

    try {
      const res = await fetch('/api/demos/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || `Failed to start demo (${res.status})`);
      }

      const initialDemoState = {
        demo_id: data.demo_id,
        scenario: data.scenario,
        status: 'running',
        elapsed_seconds: 0,
        remaining_seconds: data.duration || 60,
        total_seconds: data.duration || 60,
        progress_percent: 0,
        current_metrics: {
          request_rate_per_sec: 10,
          latency_seconds: 0.1,
          p90_latency_seconds: 0.2,
          error_percentage: 0,
          requests_in_progress: 5
        }
      };

      setActiveDemo(initialDemoState);
      startPolling(data.demo_id);
    } catch (err) {
      setErrorMessage(err.message || 'Unable to start demo. Please ensure the backend is running.');
    } finally {
      setIsStarting(false);
    }
  };

  const handleStopDemo = async () => {
    try {
      await fetch('/api/demos/stop', { method: 'POST' });
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
      if (activeDemo) {
        setCompletedDemo({ ...activeDemo, status: 'completed', cancelled: true });
      }
      setActiveDemo(null);
    } catch (err) {
      console.error('Error stopping demo:', err);
    }
  };

  const isRunning = activeDemo && activeDemo.status === 'running';

  return (
    <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 md:p-7 space-y-6 shadow-xl relative overflow-hidden">
      {/* Background glow decoration */}
      <div className="absolute top-0 left-1/3 w-80 h-36 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Radio className="w-5 h-5 text-indigo-400" />
            Interactive Locust Demo Scenarios
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Trigger simulated 60-second realistic traffic surges to test alerting, latency elevation, and error spikes.
          </p>
        </div>

        {isRunning && (
          <button
            onClick={handleStopDemo}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-500/20 border border-rose-500/40 text-rose-300 hover:bg-rose-500/30 text-xs font-semibold transition-all self-start sm:self-auto"
          >
            <StopCircle className="w-4 h-4" /> Stop Active Demo
          </button>
        )}
      </div>

      {/* Error Alert Message */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start gap-3 text-xs text-rose-300">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="font-bold">Execution Error: </span>
            {errorMessage}
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            className="text-rose-400 hover:text-rose-200 font-mono text-sm"
          >
            ×
          </button>
        </div>
      )}

      {/* Action Buttons (Disabled while running) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Run Latency Demo Button */}
        <button
          onClick={() => handleStartDemo('demo_latency')}
          disabled={isRunning || isStarting}
          className={`p-5 rounded-xl border text-left transition-all relative overflow-hidden group ${
            isRunning || isStarting
              ? 'bg-slate-950/40 border-slate-800 opacity-60 cursor-not-allowed'
              : 'bg-gradient-to-br from-slate-900/90 to-amber-950/20 border-amber-500/30 hover:border-amber-500 hover:shadow-lg hover:shadow-amber-500/10 cursor-pointer'
          }`}
        >
          <div className="flex items-start justify-between gap-3 mb-2">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <span className="font-bold text-sm text-white group-hover:text-amber-300 transition-colors">
                  Run Latency Demo
                </span>
                <span className="block text-[11px] font-mono text-amber-400/80">
                  scenario: demo_latency
                </span>
              </div>
            </div>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-950 border border-slate-800 font-mono text-slate-400">
              60s
            </span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed mt-2">
            Starts with normal baseline traffic, increases <code className="text-amber-300 font-mono">/slow</code> responses during the middle 20s spike, then recovers smoothly.
          </p>
          <div className="mt-3 flex items-center gap-2 text-[11px] text-amber-300/80 font-medium">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>High Latency Rise • 0% Errors</span>
          </div>
        </button>

        {/* Run Latency + Errors Demo Button */}
        <button
          onClick={() => handleStartDemo('demo_errors')}
          disabled={isRunning || isStarting}
          className={`p-5 rounded-xl border text-left transition-all relative overflow-hidden group ${
            isRunning || isStarting
              ? 'bg-slate-950/40 border-slate-800 opacity-60 cursor-not-allowed'
              : 'bg-gradient-to-br from-slate-900/90 to-rose-950/20 border-rose-500/30 hover:border-rose-500 hover:shadow-lg hover:shadow-rose-500/10 cursor-pointer'
          }`}
        >
          <div className="flex items-start justify-between gap-3 mb-2">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400">
                <Flame className="w-5 h-5" />
              </div>
              <div>
                <span className="font-bold text-sm text-white group-hover:text-rose-300 transition-colors">
                  Run Latency + Errors Demo
                </span>
                <span className="block text-[11px] font-mono text-rose-400/80">
                  scenario: demo_errors
                </span>
              </div>
            </div>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-950 border border-slate-800 font-mono text-slate-400">
              60s
            </span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed mt-2">
            Follows the same load pattern, but injects deliberate <code className="text-rose-300 font-mono">/error</code> 500 HTTP responses during the surge alongside latency.
          </p>
          <div className="mt-3 flex items-center gap-2 text-[11px] text-rose-300/80 font-medium">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>High Latency Rise • High Error Storm</span>
          </div>
        </button>
      </div>

      {/* Active Running Demo Live Card */}
      {isRunning && (
        <div className="rounded-xl border border-indigo-500/40 bg-indigo-950/20 p-5 md:p-6 space-y-4 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
              </span>
              <div>
                <div className="text-xs font-mono uppercase tracking-wider text-indigo-400">
                  Active Locust Run
                </div>
                <div className="text-base font-bold text-white flex items-center gap-2">
                  <span>Scenario: <span className="font-mono text-indigo-300">{activeDemo.scenario}</span></span>
                </div>
              </div>
            </div>

            {/* Countdown Badge */}
            <div className="flex items-center gap-2 self-start sm:self-auto px-3.5 py-1.5 rounded-xl bg-slate-950 border border-indigo-500/30">
              <Clock className="w-4 h-4 text-indigo-400" />
              <span className="text-xs font-mono text-slate-300">
                Remaining: <span className="text-indigo-300 font-bold text-sm">{activeDemo.remaining_seconds}s</span> / 60s
              </span>
            </div>
          </div>

          {/* Linear Progress Bar */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-[11px] font-mono text-slate-400">
              <span>Progress: {activeDemo.progress_percent}%</span>
              <span>
                {activeDemo.elapsed_seconds < 20 ? 'Phase 1: Baseline Normal (0-20s)' :
                 activeDemo.elapsed_seconds < 40 ? 'Phase 2: Active Spike Surge (20-40s)' :
                 'Phase 3: System Recovery (40-60s)'}
              </span>
            </div>
            <div className="w-full h-3 bg-slate-950 rounded-full overflow-hidden border border-slate-800 p-0.5">
              <div
                className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-amber-500 to-rose-500 transition-all duration-1000"
                style={{ width: `${Math.min(Math.max(activeDemo.progress_percent, 3), 100)}%` }}
              />
            </div>
          </div>

          {/* Live KPI Meters Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <span className="text-[11px] text-slate-400 uppercase font-semibold flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-indigo-400" /> Request Rate
              </span>
              <div className="text-lg font-bold font-mono text-white mt-1">
                {activeDemo.current_metrics?.request_rate_per_sec ?? 0} <span className="text-xs text-slate-400 font-normal">req/s</span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <span className="text-[11px] text-slate-400 uppercase font-semibold flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-amber-400" /> P90 Latency
              </span>
              <div className="text-lg font-bold font-mono text-amber-300 mt-1">
                {activeDemo.current_metrics?.p90_latency_seconds ?? 0} <span className="text-xs text-slate-400 font-normal">s</span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <span className="text-[11px] text-slate-400 uppercase font-semibold flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-rose-400" /> Error Rate
              </span>
              <div className="text-lg font-bold font-mono text-rose-400 mt-1">
                {activeDemo.current_metrics?.error_percentage ?? 0} <span className="text-xs text-slate-400 font-normal">%</span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <span className="text-[11px] text-slate-400 uppercase font-semibold flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-blue-400" /> Concurrent Reqs
              </span>
              <div className="text-lg font-bold font-mono text-blue-300 mt-1">
                {activeDemo.current_metrics?.requests_in_progress ?? 0}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Completion State Banner */}
      {completedDemo && !isRunning && (
        <div className={`rounded-xl p-5 border flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
          completedDemo.status === 'completed'
            ? 'bg-emerald-950/20 border-emerald-500/40 text-emerald-300'
            : 'bg-rose-950/20 border-rose-500/40 text-rose-300'
        }`}>
          <div className="flex items-start sm:items-center gap-3">
            {completedDemo.status === 'completed' ? (
              <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0 mt-0.5 sm:mt-0" />
            ) : (
              <XCircle className="w-6 h-6 text-rose-400 shrink-0 mt-0.5 sm:mt-0" />
            )}
            <div>
              <div className="font-bold text-sm text-white">
                {completedDemo.status === 'completed' 
                  ? `Demo '${completedDemo.scenario}' Completed Successfully!` 
                  : `Demo '${completedDemo.scenario}' Finished with Errors`}
              </div>
              <p className="text-xs text-slate-300 mt-0.5">
                {completedDemo.cancelled 
                  ? 'The demo run was stopped by user request.'
                  : '60-second demonstration completed. The system has returned to normal baseline traffic.'}
              </p>
            </div>
          </div>

          <button
            onClick={() => setCompletedDemo(null)}
            className="px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 hover:border-slate-500 text-xs font-semibold text-slate-200 transition-all self-start sm:self-auto flex items-center gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Dismiss
          </button>
        </div>
      )}
    </div>
  );
}
