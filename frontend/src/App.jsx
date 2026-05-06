import React, { useState, useEffect } from 'react';
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
  Server
} from 'lucide-react';

const ENDPOINTS = [
  { path: '/health', name: 'Health Check', icon: Activity, description: 'Verifies if the API is running correctly.', color: 'text-emerald-400' },
  { path: '/process', name: 'Process Data', icon: Settings, description: 'Simulates a short data processing task.', color: 'text-blue-400' },
  { path: '/slow', name: 'Slow Response', icon: Clock, description: 'Simulates a delayed response (2s).', color: 'text-amber-400' },
  { path: '/error', name: 'Intentional Error', icon: AlertCircle, description: 'Triggers a deliberate 500 server error.', color: 'text-rose-400' },
  { path: '/metrics', name: 'Prometheus Metrics', icon: BarChart2, description: 'Fetches raw Prometheus monitoring metrics.', color: 'text-indigo-400' }
];

function App() {
  const [activeEndpoint, setActiveEndpoint] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [statusCode, setStatusCode] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // Check backend status on load
    fetch('/health')
      .then(res => {
        if (res.ok) setBackendStatus('online');
        else setBackendStatus('error');
      })
      .catch(() => setBackendStatus('offline'));
  }, []);

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

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 p-4 md:p-8 font-sans selection:bg-indigo-500/30">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header Section */}
        <header className="bg-white/10 backdrop-blur-lg border border-white/10 shadow-xl rounded-2xl p-6 md:p-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>
          
          <div className="relative z-10 space-y-2">
            <div className="flex items-center gap-3">
              <TerminalSquare className="w-8 h-8 text-indigo-400" />
              <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                API Control Panel
              </h1>
            </div>
            <p className="text-slate-400 max-w-xl leading-relaxed">
              Welcome to the unified developer dashboard. Navigate, test, and monitor all backend endpoints from a single interface. Built with React and Tailwind CSS.
            </p>
          </div>

          <div className="relative z-10 flex items-center gap-3 bg-slate-900/50 px-4 py-2 rounded-full border border-slate-800">
            <div className="flex items-center gap-2">
              <div className="relative flex h-3 w-3">
                {backendStatus === 'online' && (
                  <>
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                  </>
                )}
                {backendStatus === 'offline' && <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>}
                {backendStatus === 'error' && <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500"></span>}
                {backendStatus === 'checking' && <span className="relative inline-flex rounded-full h-3 w-3 bg-slate-500 animate-pulse"></span>}
              </div>
              <span className="text-sm font-medium text-slate-300">
                Backend System: <span className="capitalize">{backendStatus}</span>
              </span>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Navigation Sidebar */}
          <div className="lg:col-span-4 space-y-4">
            <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Server className="w-4 h-4" /> Available Endpoints
            </h2>
            
            <div className="flex flex-col gap-3">
              {ENDPOINTS.map((endpoint) => (
                <button
                  key={endpoint.path}
                  onClick={() => handleEndpointClick(endpoint)}
                  className={`text-left p-4 rounded-xl transition-all duration-300 border relative overflow-hidden group
                    ${activeEndpoint?.path === endpoint.path 
                      ? 'bg-slate-800/80 border-indigo-500/50 shadow-lg shadow-indigo-500/10' 
                      : 'bg-slate-900/40 border-slate-800/50 hover:bg-slate-800/60 hover:border-slate-700/50'
                    }`}
                >
                  <div className={`absolute inset-0 bg-gradient-to-r from-${endpoint.color.split('-')[1]}-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity`} />
                  
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

          {/* Response Viewer Panel */}
          <div className="lg:col-span-8">
            <div className="bg-white/10 backdrop-blur-lg border border-white/10 shadow-xl rounded-2xl h-full flex flex-col overflow-hidden bg-[#0a0f1c]/80">
              
              {/* Panel Header */}
              <div className="bg-slate-900/80 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
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

              {/* Panel Body */}
              <div className="flex-1 p-6 relative group min-h-[400px] overflow-auto">
                {!activeEndpoint && !loading && !response && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500">
                    <TerminalSquare className="w-12 h-12 mb-4 opacity-20" />
                    <p>Awaiting request...</p>
                  </div>
                )}

                {loading && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#0a0f1c]/50 backdrop-blur-sm z-10">
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
                      className="absolute top-2 right-2 p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100 z-10"
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
      </div>
    </div>
  );
}

export default App;
