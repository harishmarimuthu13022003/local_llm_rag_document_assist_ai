import React from 'react';
import { Bot } from 'lucide-react';

export default function TypingIndicator() {
  return (
    <div className="flex items-start space-x-3 p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 max-w-xl animate-pulse">
      <div className="p-2 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/20">
        <Bot className="w-5 h-5" />
      </div>
      <div className="flex-1 pt-1">
        <p className="text-xs text-blue-400 font-mono mb-2">Ollama llama3.2:3b is generating grounded response...</p>
        <div className="flex items-center space-x-1.5 h-4">
          <div className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-dot-1"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-dot-2"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-blue-400 animate-dot-3"></div>
        </div>
      </div>
    </div>
  );
}
