import { useState, useEffect, useRef } from 'react';
import { 
  Activity, 
  Settings, 
  AlertCircle, 
  Clock, 
  BarChart2, 
  Play, 
  CheckCircle2, 
  XCircle, 
  Copy, 
  TerminalSquare,
  Server,
  ShieldAlert,
  Cpu,
  Zap,
  Gauge,
  TrendingUp,
  AlertTriangle,
  RefreshCw,
  Sliders,
  Layers,
  Sparkles,
  Radio,
  RotateCcw
} from 'lucide-react';
import LiveMetricsGraph from './components/LiveMetricsGraph';
import LocustDemoRunner from './components/LocustDemoRunner';

const ENDPOINTS = [
  { path: '/health', name: 'Health Check', icon: Activity, description: 'Verifies if the API is running correctly.', color: 'text-emerald-400' },
  { path: '/process', name: 'Process Data', icon: Settings, description: 'Simulates a short data processing task.', color: 'text-blue-400' },
  { path: '/slow', name: 'Slow Response', icon: Clock, description: 'Simulates a delayed response (2s).', color: 'text-amber-400' },
  { path: '/error', name: 'Intentional Error', icon: AlertCircle, description: 'Triggers a deliberate 500 server error.', color: 'text-rose-400' },
  { path: '/metrics', name: 'Prometheus Metrics', icon: BarChart2, description: 'Fetches raw Prometheus monitoring metrics.', color: 'text-indigo-400' }
];

const PRESET_SCENARIOS = [
  {
    name: 'Normal Baseline',
    color: 'emerald',
    icon: CheckCircle2,
    features: { request_rate_per_sec: 8.5, error_rate_per_sec: 0.0, p90_latency_seconds: 0.21, requests_in_progress: 3 }
  },
  {
    name: 'Ramp Up Load',
    color: 'blue',
    icon: TrendingUp,
    features: { request_rate_per_sec: 30.2, error_rate_per_sec: 0.0, p90_latency_seconds: 0.08, requests_in_progress: 18 }
  },
  {
    name: 'Traffic Spike',
    color: 'amber',
    icon: Zap,
    features: { request_rate_per_sec: 74.2, error_rate_per_sec: 7.3, p90_latency_seconds: 0.038, requests_in_progress: 51 }
  },
  {
    name: 'Heavy Error Storm',
    color: 'rose',
    icon: AlertTriangle,
    features: { request_rate_per_sec: 105.3, error_rate_per_sec: 21.0, p90_latency_seconds: 0.024, requests_in_progress: 88 }
  }
];

function generateInitialHistory() {
  const points = [];
  const now = Date.now();
  for (let i = 15; i >= 0; i--) {
    const t = new Date(now - i * 3000);
    points.push({
      time: t.toTimeString().split(' ')[0],
      traffic: 8.5,
      latency: 0.21,
      errors: 0.0
    });
  }
  return points;
}

function App() {
  const [activeTab, setActiveTab] = useState('ml_dashboard');
  const [backendStatus, setBackendStatus] = useState('checking');
  const [mlServiceStatus, setMlServiceStatus] = useState('checking');

  // API Control Panel state
  const [activeEndpoint, setActiveEndpoint] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [statusCode, setStatusCode] = useState(null);
  const [copied, setCopied] = useState(false);

  // ML Prediction & Custom Inputs state
  const [simParams, setSimParams] = useState({
    request_rate_per_sec: 8.5,
    error_rate_per_sec: 0.0,
    p90_latency_seconds: 0.21,
    requests_in_progress: 3.0
  });

  const [prediction, setPrediction] = useState(null);
  const [mlLoading, setMlLoading] = useState(false);
  const [isCustomMode, setIsCustomMode] = useState(false);

  // Live Metrics Graph history state
  const [metricsHistory, setMetricsHistory] = useState(generateInitialHistory);
  const isCustomModeRef = useRef(isCustomMode);
  isCustomModeRef.current = isCustomMode;

  // Background health & status polling
  useEffect(() => {
    let isMounted = true;

    const runHealthCheck = async () => {
      try {
        const res = await fetch('/health');
        if (isMounted) setBackendStatus(res.ok ? 'online' : 'offline');
      } catch {
        if (isMounted) setBackendStatus('offline');
      }

      try {
        const mlRes = await fetch('/predict');
        if (isMounted) {
          if (mlRes.ok) {
            setMlServiceStatus('active');
            const data = await mlRes.json();
            // Only update prediction from polling if user is not evaluating custom inputs
            if (!isCustomModeRef.current) {
              setPrediction(data);
            }
          } else {
            setMlServiceStatus('error');
          }
        }
      } catch {
        if (isMounted) setMlServiceStatus('offline');
      }
    };

    runHealthCheck();
    const interval = setInterval(runHealthCheck, 8000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Poll real-time metrics for graph updates when not in active Locust demo
  useEffect(() => {
    const pollRealtimeMetrics = async () => {
      if (backendStatus === 'offline') return;
      try {
        const res = await fetch('/api/metrics/realtime');
        if (res.ok) {
          const data = await res.json();
          const nowStr = new Date().toTimeString().split(' ')[0];
          setMetricsHistory(prev => [
            ...prev.slice(-29),
            {
              time: nowStr,
              traffic: data.request_rate_per_sec ?? 0,
              latency: data.p90_latency_seconds ?? 0,
              errors: data.error_percentage ?? 0
            }
          ]);
        }
      } catch {
        // Backend not serving realtime endpoint or offline
      }
    };

    const metricInterval = setInterval(pollRealtimeMetrics, 3000);
    return () => clearInterval(metricInterval);
  }, [backendStatus]);

  // Handler for metrics streaming from active Locust demo runner
  const handleDemoMetricsUpdate = (newMetrics) => {
    const nowStr = new Date().toTimeString().split(' ')[0];
    setMetricsHistory(prev => [
      ...prev.slice(-29),
      {
        time: nowStr,
        traffic: newMetrics.traffic,
        latency: newMetrics.latency,
        errors: newMetrics.errors
      }
    ]);

    // Also update simParams and trigger ML prediction update to reflect the surge live
    const updatedFeatures = {
      request_rate_per_sec: newMetrics.traffic,
      error_rate_per_sec: newMetrics.raw?.error_rate_per_sec ?? (newMetrics.traffic * (newMetrics.errors / 100)),
      p90_latency_seconds: newMetrics.latency,
      requests_in_progress: newMetrics.raw?.requests_in_progress ?? 10
    };
    setSimParams(updatedFeatures);
    handleRunPrediction(updatedFeatures, false);
  };

  // Run ML prediction evaluation
  const handleRunPrediction = async (featuresToUse = simParams, markCustom = true) => {
    setMlLoading(true);
    if (markCustom) setIsCustomMode(true);

    try {
      const res = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(featuresToUse)
      });
      if (res.ok) {
        const data = await res.json();
        setPrediction(data);
      } else {
        // Fallback GET query params
        const params = new URLSearchParams(featuresToUse).toString();
        const getRes = await fetch(`/predict?${params}`);
        if (getRes.ok) {
          const data = await getRes.json();
          setPrediction(data);
        }
      }

      // Append evaluated custom values to live metrics graph
      const nowStr = new Date().toTimeString().split(' ')[0];
      setMetricsHistory(prev => [
        ...prev.slice(-29),
        {
          time: nowStr,
          traffic: featuresToUse.request_rate_per_sec || 0,
          latency: featuresToUse.p90_latency_seconds || 0,
          errors: featuresToUse.error_rate_per_sec || 0
        }
      ]);
    } catch (err) {
      console.error('Prediction failed:', err);
    } finally {
      setMlLoading(false);
    }
  };

  const applyPreset = (preset) => {
    setSimParams(preset.features);
    handleRunPrediction(preset.features, true);
  };

  const handleResetToBaseline = () => {
    setIsCustomMode(false);
    const baseline = {
      request_rate_per_sec: 8.5,
      error_rate_per_sec: 0.0,
      p90_latency_seconds: 0.21,
      requests_in_progress: 3.0
    };
    setSimParams(baseline);
    handleRunPrediction(baseline, false);
  };

  const handleEndpointClick = async (endpoint) => {
    setActiveEndpoint(endpoint);
    setLoading(true);
    setError(null);
    setResponse(null);
    setStatusCode(null);
    setCopied(false);

    try {
      const res = await fetch(endpoint.path);
      setStatusCode(res.status);
      
      const contentType = res.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const data = await res.json();
        setResponse(JSON.stringify(data, null, 2));
      } else {
        const text = await res.text();
        setResponse(text);
      }
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (response) {
      navigator.clipboard.writeText(response);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const isApiOffline = backendStatus === 'offline';

  const getStatusTheme = (status) => {
    if (isApiOffline) {
      return { 
        bg: 'bg-rose-950/40', 
        border: 'border-rose-500/80 shadow-2xl shadow-rose-950/70', 
        text: 'text-rose-400', 
        badgeBg: 'bg-rose-600', 
        pingBg: 'bg-rose-500' 
      };
    }
    if (status === 'High Risk') {
      return { 
        bg: 'bg-rose-500/10', 
        border: 'border-rose-500/40 shadow-xl shadow-rose-500/5', 
        text: 'text-rose-400', 
        badgeBg: 'bg-rose-500', 
        pingBg: 'bg-rose-400' 
      };
    }
    if (status === 'Medium Risk') {
      return { 
        bg: 'bg-amber-500/10', 
        border: 'border-amber-500/40 shadow-xl shadow-amber-500/5', 
        text: 'text-amber-400', 
        badgeBg: 'bg-amber-500', 
        pingBg: 'bg-amber-400' 
      };
    }
    return { 
      bg: 'bg-emerald-500/10', 
      border: 'border-emerald-500/30 shadow-xl shadow-emerald-500/5', 
      text: 'text-emerald-400', 
      badgeBg: 'bg-emerald-500', 
      pingBg: 'bg-emerald-400' 
    };
  };

  const currentTheme = getStatusTheme(prediction?.risk_level);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 p-4 md:p-8 font-sans selection:bg-indigo-500/30">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Top Header */}
        <header className="bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-2xl rounded-2xl p-6 md:p-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-600/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 pointer-events-none"></div>
          
          <div className="relative z-10 space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                <ShieldAlert className="w-7 h-7" />
              </div>
              <div>
                <h1 className="text-3xl font-extrabold bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
                  Container Monitoring & ML Anomaly System
                </h1>
                <p className="text-slate-400 text-sm max-w-2xl leading-relaxed">
                  Real-time Isolation Forest anomaly detection, Prometheus metric integration & predictive alerting dashboard.
                </p>
              </div>
            </div>
          </div>

          <div className="relative z-10 flex flex-wrap items-center gap-3">
            {/* Status Pills */}
            <div className={`flex items-center gap-2 px-3.5 py-1.5 rounded-full border text-xs font-medium ${
              backendStatus === 'online' 
                ? 'bg-slate-950/80 border-slate-800 text-slate-200' 
                : 'bg-rose-950/60 border-rose-500/50 text-rose-300'
            }`}>
              <span className="text-slate-400">API:</span>
              <span className="flex items-center gap-1.5 capitalize font-semibold">
                <span className={`w-2 h-2 rounded-full ${backendStatus === 'online' ? 'bg-emerald-500' : 'bg-rose-500 animate-ping'}`} />
                {backendStatus === 'online' ? 'Online' : 'Down (Offline)'}
              </span>
            </div>

            <div className="flex items-center gap-2 bg-slate-950/80 px-3.5 py-1.5 rounded-full border border-slate-800 text-xs font-medium">
              <span className="text-slate-400">ML Engine:</span>
              <span className="flex items-center gap-1.5 capitalize text-indigo-400 font-semibold">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
                </span>
                {mlServiceStatus}
              </span>
            </div>

            {/* Tab Navigation */}
            <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800">
              <button
                onClick={() => setActiveTab('ml_dashboard')}
                className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all duration-200 flex items-center gap-2 cursor-pointer ${
                  activeTab === 'ml_dashboard' 
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' 
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Cpu className="w-3.5 h-3.5" /> ML Intelligence
              </button>

              <button
                onClick={() => setActiveTab('api_panel')}
                className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all duration-200 flex items-center gap-2 cursor-pointer ${
                  activeTab === 'api_panel' 
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' 
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <TerminalSquare className="w-3.5 h-3.5" /> API Tester
              </button>
            </div>
          </div>
        </header>

        {activeTab === 'ml_dashboard' ? (
          <div className="space-y-8">
            
            {/* Top Row: Hero Risk Status & Gauge Card */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              
              {/* Prediction Hero Banner */}
              <div className={`lg:col-span-7 rounded-2xl p-6 md:p-8 border ${currentTheme.bg} ${currentTheme.border} backdrop-blur-xl relative overflow-hidden flex flex-col justify-between transition-all duration-500`}>
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-slate-400 mb-2">
                      <Sparkles className={`w-4 h-4 ${isApiOffline ? 'text-rose-400' : 'text-indigo-400'}`} /> 
                      {isApiOffline ? 'API Connectivity Failure' : 'Isolation Forest Model Output'}
                    </div>
                    <div className="flex items-center gap-3">
                      <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                        Status: <span className={currentTheme.text}>
                          {isApiOffline ? 'App is Down' : (prediction?.risk_level || 'Evaluating...')}
                        </span>
                      </h2>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-950/80 border border-white/10 shrink-0">
                    <span className="relative flex h-3 w-3">
                      <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${currentTheme.pingBg} opacity-75`}></span>
                      <span className={`relative inline-flex rounded-full h-3 w-3 ${currentTheme.badgeBg}`}></span>
                    </span>
                    <span className="text-xs font-bold font-mono text-slate-200">
                      {isApiOffline ? 'OFFLINE' : `Code ${prediction?.risk_code ?? 0}`}
                    </span>
                  </div>
                </div>

                {/* Risk Explanation or Offline Alert */}
                <div className="my-6 space-y-3">
                  <p className="text-slate-300 text-sm leading-relaxed">
                    {isApiOffline && 'CRITICAL: The backend Flask API is offline or unreachable. Request processing is down and metrics cannot be refreshed.'}
                    {!isApiOffline && prediction?.risk_level === 'High Risk' && 'Severe metric anomaly detected! Multiple parameters deviate significantly from baseline normal thresholds.'}
                    {!isApiOffline && prediction?.risk_level === 'Medium Risk' && 'Elevated metric variation observed. Traffic load, latency, or errors are drifting from baseline norms.'}
                    {!isApiOffline && prediction?.risk_level === 'Normal' && 'System metrics operate smoothly within expected Isolation Forest baseline parameters.'}
                  </p>

                  {isApiOffline ? (
                    <div className="flex flex-wrap gap-2 pt-2">
                      <span className="px-2.5 py-1 rounded-md bg-rose-950/80 border border-rose-500/50 text-rose-300 text-xs font-mono flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5 text-rose-400" /> Backend Service Down
                      </span>
                      <span className="px-2.5 py-1 rounded-md bg-rose-950/80 border border-rose-500/50 text-rose-300 text-xs font-mono">
                        Port 5000 Unreachable
                      </span>
                    </div>
                  ) : (
                    prediction?.affected_metrics && prediction.affected_metrics.length > 0 && (
                      <div className="flex flex-wrap gap-2 pt-2">
                        <span className="text-xs font-semibold text-slate-400 self-center">Triggers:</span>
                        {prediction.affected_metrics.map((metric, idx) => (
                          <span key={idx} className="px-2.5 py-1 rounded-md bg-slate-950/80 border border-rose-500/30 text-rose-300 text-xs font-mono">
                            {metric}
                          </span>
                        ))}
                      </div>
                    )
                  )}
                </div>

                {/* Footer Metrics */}
                <div className="pt-4 border-t border-white/10 flex items-center justify-between text-xs text-slate-400">
                  <span>Timestamp: <span className="font-mono text-slate-200">{prediction?.timestamp_utc || 'N/A'}</span></span>
                  <span>Raw Score: <span className="font-mono text-slate-200">{isApiOffline ? 'N/A' : (prediction?.raw_score ?? '0.00')}</span></span>
                </div>
              </div>

              {/* Anomaly Gauge Card */}
              <div className="lg:col-span-5 bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 md:p-8 flex flex-col justify-between">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                    <Gauge className="w-4 h-4 text-indigo-400" /> Anomaly Score Meter
                  </h3>
                  <span className={`text-2xl font-mono font-extrabold ${isApiOffline ? 'text-rose-400' : 'text-white'}`}>
                    {isApiOffline ? '1.00 (Down)' : (prediction ? prediction.anomaly_score.toFixed(2) : '0.00')}
                  </span>
                </div>

                {/* Continuous Progress Bar / Meter */}
                <div className="space-y-4 my-auto">
                  <div className="relative w-full h-5 bg-slate-950 rounded-full overflow-hidden border border-slate-800 p-0.5">
                    <div 
                      className={`h-full rounded-full transition-all duration-500 ${
                        isApiOffline ? 'bg-gradient-to-r from-rose-600 to-rose-500' :
                        (prediction?.anomaly_score || 0) >= 0.75 ? 'bg-gradient-to-r from-amber-500 to-rose-500' :
                        (prediction?.anomaly_score || 0) >= 0.50 ? 'bg-gradient-to-r from-emerald-500 to-amber-500' :
                        'bg-gradient-to-r from-indigo-500 to-emerald-500'
                      }`}
                      style={{ 
                        width: isApiOffline ? '100%' : `${Math.min(Math.max((prediction?.anomaly_score || 0) * 100, 4), 100)}%` 
                      }}
                    />
                  </div>

                  <div className="flex justify-between text-[11px] font-mono text-slate-400">
                    <span className="text-emerald-400">0.0 (Normal)</span>
                    <span className="text-amber-400">0.50 (Medium)</span>
                    <span className="text-rose-400">0.75+ (High Risk)</span>
                  </div>
                </div>

                <div className="mt-6 p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-400 flex items-center gap-3">
                  <ShieldAlert className="w-5 h-5 text-indigo-400 shrink-0" />
                  <span>Prometheus metric exposed: <code className="text-indigo-300 font-mono">ml_anomaly_score</code></span>
                </div>
              </div>

            </div>

            {/* Live Metrics Graph (Traffic, Latency, Errors) */}
            <LiveMetricsGraph
              history={metricsHistory}
              currentMetrics={simParams}
              isDemoRunning={false}
            />

            {/* Interactive Locust Demo Runner Section */}
            <LocustDemoRunner onMetricsUpdate={handleDemoMetricsUpdate} />

            {/* Feature Health Matrix (4 Metric Cards) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { label: 'Request Rate', value: `${simParams.request_rate_per_sec} req/s`, name: 'request_rate_per_sec', target: '< 30 req/s', icon: Zap, color: 'indigo' },
                { label: 'HTTP Error Rate', value: `${simParams.error_rate_per_sec} err/s`, name: 'error_rate_per_sec', target: '0.00 err/s', icon: AlertTriangle, color: 'rose' },
                { label: 'P90 Latency', value: `${simParams.p90_latency_seconds}s`, name: 'p90_latency_seconds', target: '< 0.50s', icon: Clock, color: 'amber' },
                { label: 'In-Progress Reqs', value: `${simParams.requests_in_progress}`, name: 'requests_in_progress', target: '< 15', icon: Layers, color: 'blue' }
              ].map((item, idx) => (
                <div key={idx} className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 hover:border-slate-700 transition-all">
                  <div className="flex justify-between items-start mb-3">
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{item.label}</span>
                    <div className="p-2 rounded-lg bg-slate-950 border border-slate-800 text-indigo-400">
                      <item.icon className="w-4 h-4" />
                    </div>
                  </div>
                  <div className="text-2xl font-bold font-mono text-white mb-2">{item.value}</div>
                  <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/50">
                    <span>Baseline Normal:</span>
                    <span className="font-mono text-slate-300">{item.target}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Interactive Scenario Simulator & Presets */}
            <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 md:p-8 space-y-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Sliders className="w-5 h-5 text-indigo-400" /> Interactive Anomaly Simulator & Preset Scenarios
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Select a load testing scenario or adjust metric parameters to test Isolation Forest predictions live.
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  {isCustomMode && (
                    <button
                      onClick={handleResetToBaseline}
                      className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs flex items-center gap-1.5 transition-all cursor-pointer"
                    >
                      <RotateCcw className="w-3.5 h-3.5" /> Reset Live
                    </button>
                  )}

                  <button
                    onClick={() => handleRunPrediction(simParams, true)}
                    disabled={mlLoading}
                    className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition-all cursor-pointer"
                  >
                    <RefreshCw className={`w-4 h-4 ${mlLoading ? 'animate-spin' : ''}`} />
                    Evaluate Custom Inputs
                  </button>
                </div>
              </div>

              {/* Preset Buttons */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {PRESET_SCENARIOS.map((preset, idx) => (
                  <button
                    key={idx}
                    onClick={() => applyPreset(preset)}
                    className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-900/80 transition-all text-left group cursor-pointer"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <preset.icon className={`w-4 h-4 text-${preset.color}-400`} />
                      <span className="font-bold text-sm text-slate-200 group-hover:text-indigo-300 transition-colors">
                        {preset.name}
                      </span>
                    </div>
                    <div className="text-[11px] font-mono text-slate-400 space-y-0.5">
                      <div>Reqs: {preset.features.request_rate_per_sec}/s</div>
                      <div>Errors: {preset.features.error_rate_per_sec}/s</div>
                    </div>
                  </button>
                ))}
              </div>

              {/* Interactive Sliders */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4 border-t border-slate-800">
                
                {/* Request Rate Slider */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-300">Request Rate (per sec)</span>
                    <span className="font-mono text-indigo-400">{simParams.request_rate_per_sec}</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="120" 
                    step="0.5"
                    value={simParams.request_rate_per_sec}
                    onChange={(e) => setSimParams({...simParams, request_rate_per_sec: parseFloat(e.target.value)})}
                    className="w-full accent-indigo-500 bg-slate-950 rounded-lg cursor-pointer"
                  />
                </div>

                {/* Error Rate Slider */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-300">HTTP Error Rate (per sec)</span>
                    <span className="font-mono text-rose-400">{simParams.error_rate_per_sec}</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="25" 
                    step="0.1"
                    value={simParams.error_rate_per_sec}
                    onChange={(e) => setSimParams({...simParams, error_rate_per_sec: parseFloat(e.target.value)})}
                    className="w-full accent-rose-500 bg-slate-950 rounded-lg cursor-pointer"
                  />
                </div>

                {/* P90 Latency Slider */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-300">P90 Latency (seconds)</span>
                    <span className="font-mono text-amber-400">{simParams.p90_latency_seconds}s</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="2.0" 
                    step="0.01"
                    value={simParams.p90_latency_seconds}
                    onChange={(e) => setSimParams({...simParams, p90_latency_seconds: parseFloat(e.target.value)})}
                    className="w-full accent-amber-500 bg-slate-950 rounded-lg cursor-pointer"
                  />
                </div>

                {/* In Progress Slider */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-300">Requests In Progress</span>
                    <span className="font-mono text-blue-400">{simParams.requests_in_progress}</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="100" 
                    step="1"
                    value={simParams.requests_in_progress}
                    onChange={(e) => setSimParams({...simParams, requests_in_progress: parseInt(e.target.value, 10)})}
                    className="w-full accent-blue-500 bg-slate-950 rounded-lg cursor-pointer"
                  />
                </div>

              </div>
            </div>

            {/* Predictive Alerts Panel */}
            <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 md:p-8 space-y-4">
              <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-amber-400" /> Alertmanager Predictive Rules Configuration
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2">
                  <div className="flex justify-between items-center text-slate-200 font-bold">
                    <span>PredictiveHighAnomalyRisk</span>
                    <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30">critical</span>
                  </div>
                  <p className="text-slate-400 font-sans text-xs">
                    Triggers when <code className="text-rose-300">ml_anomaly_risk_level &gt;= 2</code> or <code className="text-rose-300">ml_anomaly_score &gt;= 0.75</code> for 15s.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2">
                  <div className="flex justify-between items-center text-slate-200 font-bold">
                    <span>PredictiveMediumAnomalyRisk</span>
                    <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">warning</span>
                  </div>
                  <p className="text-slate-400 font-sans text-xs">
                    Triggers when <code className="text-amber-300">ml_anomaly_risk_level == 1</code> or anomaly score &gt; 0.50 for 30s.
                  </p>
                </div>
              </div>
            </div>

          </div>
        ) : (
          /* API Control Panel Tab */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-4 space-y-4">
              <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                <Server className="w-4 h-4" /> Available Endpoints
              </h2>
              
              <div className="flex flex-col gap-3">
                {ENDPOINTS.map((endpoint) => (
                  <button
                    key={endpoint.path}
                    onClick={() => handleEndpointClick(endpoint)}
                    className={`text-left p-4 rounded-xl transition-all duration-300 border relative overflow-hidden group cursor-pointer
                      ${activeEndpoint?.path === endpoint.path 
                        ? 'bg-slate-800/80 border-indigo-500/50 shadow-lg shadow-indigo-500/10' 
                        : 'bg-slate-900/40 border-slate-800/50 hover:bg-slate-800/60 hover:border-slate-700/50'
                      }`}
                  >
                    <div className="relative z-10 flex items-start gap-4">
                      <div className={`p-2 rounded-lg bg-slate-950 border border-slate-800 ${endpoint.color}`}>
                        <endpoint.icon className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-slate-200">{endpoint.name}</span>
                          <span className="text-xs px-2 py-0.5 rounded bg-slate-950 border border-slate-800 font-mono text-slate-400">
                            {endpoint.path}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">
                          {endpoint.description}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div className="lg:col-span-8">
              <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-2xl h-full flex flex-col overflow-hidden">
                <div className="bg-slate-950/80 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Play className="w-4 h-4 text-slate-400" />
                    <span className="font-mono text-sm font-medium text-slate-300">
                      {activeEndpoint ? `GET ${activeEndpoint.path}` : 'Select an endpoint to test'}
                    </span>
                  </div>
                  
                  {statusCode && (
                    <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold
                      ${statusCode >= 200 && statusCode < 300 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 
                        'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
                      {statusCode >= 200 && statusCode < 300 ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                      {statusCode} Response
                    </div>
                  )}
                </div>

                <div className="flex-1 p-6 relative group min-h-[400px] overflow-auto">
                  {!activeEndpoint && !loading && !response && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500">
                      <TerminalSquare className="w-12 h-12 mb-4 opacity-20" />
                      <p>Awaiting request...</p>
                    </div>
                  )}

                  {loading && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-950/60 backdrop-blur-sm z-10">
                      <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mb-4"></div>
                      <p className="text-sm text-slate-400 animate-pulse">Fetching response...</p>
                    </div>
                  )}

                  {error && (
                    <div className="mb-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                      <div>
                        <h4 className="text-sm font-semibold text-rose-400 mb-1">Request Failed</h4>
                        <p className="text-xs text-rose-300/80 font-mono">{error}</p>
                      </div>
                    </div>
                  )}

                  {response && (
                    <div className="relative h-full">
                      <button 
                        onClick={copyToClipboard}
                        className="absolute top-2 right-2 p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition-colors z-10 cursor-pointer"
                        title="Copy to clipboard"
                      >
                        {copied ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                      </button>
                      <pre className="font-mono text-sm text-slate-300 leading-relaxed overflow-x-auto pb-4">
                        <code>{response}</code>
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default App;
