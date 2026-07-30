import React from 'react';
import { Bot, Cpu, Database, HardDrive, RefreshCw } from 'lucide-react';

export default function Header({ healthStatus, onRefreshHealth, isRefreshing }) {
  const isHealthy = healthStatus?.status === 'healthy';
  const ollamaOk = healthStatus?.ollama?.server_connected;
  const modelOk = healthStatus?.ollama?.model_available;

  return (
    <header className="h-16 border-b border-slate-800 glass-panel px-6 flex items-center justify-between z-20 sticky top-0">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-xl shadow-lg shadow-blue-500/20">
          <Bot className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Local RAG Document Assistant
          </h1>
          <p className="text-xs text-slate-400 font-mono flex items-center gap-1.5">
            <span>Ollama local execution</span>
            <span className="inline-block w-1 h-1 rounded-full bg-slate-600"></span>
            <span className="text-blue-400">{healthStatus?.ollama?.model_name || 'llama3.2:3b'}</span>
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Status Indicators */}
        <div className="hidden md:flex items-center space-x-3 text-xs font-mono">
          <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-900/80 border border-slate-800">
            <Cpu className="w-3.5 h-3.5 text-blue-400" />
            <span className="text-slate-300">Ollama:</span>
            <span className={ollamaOk ? "text-emerald-400 font-semibold" : "text-amber-400 font-semibold"}>
              {ollamaOk ? (modelOk ? "Ready" : "Model Missing") : "Offline"}
            </span>
          </div>

          <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-900/80 border border-slate-800">
            <Database className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-slate-300">ChromaDB:</span>
            <span className="text-emerald-400 font-semibold">Active</span>
          </div>
        </div>

        <button
          onClick={onRefreshHealth}
          disabled={isRefreshing}
          className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-white transition-all duration-200"
          title="Refresh health status"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-blue-400' : ''}`} />
        </button>
      </div>
    </header>
  );
}
