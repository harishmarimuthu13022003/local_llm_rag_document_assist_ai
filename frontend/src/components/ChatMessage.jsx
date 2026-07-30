import React from 'react';
import { User, Bot, Clock, AlertTriangle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function ChatMessage({ message, onPreviewChunk, onShowRetrievedChunks }) {
  const isUser = message.role === 'user';
  const isFallback = message.answer === "I don't know based on the provided documents.";

  return (
    <div className={`flex items-start space-x-3.5 ${isUser ? 'flex-row-reverse space-x-reverse' : ''} mb-6`}>
      {/* Avatar Icon */}
      <div
        className={`p-2 rounded-xl flex-shrink-0 shadow-md ${
          isUser
            ? 'bg-gradient-to-tr from-slate-700 to-slate-800 text-slate-200 border border-slate-700'
            : 'bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-blue-500/20'
        }`}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>

      {/* Content Container */}
      <div className={`flex-1 max-w-3xl ${isUser ? 'text-right' : ''}`}>
        {/* Role Header */}
        <div className={`flex items-center space-x-2 text-xs text-slate-400 font-mono mb-1 ${isUser ? 'justify-end' : ''}`}>
          <span className="font-semibold text-slate-300">{isUser ? 'You' : 'Document Assistant'}</span>
          {!isUser && message.metrics?.llm_latency_ms > 0 && (
            <span className="flex items-center space-x-1 text-slate-500">
              <span>•</span>
              <Clock className="w-3 h-3 text-slate-500 inline" />
              <span>{message.metrics.llm_latency_ms}ms</span>
            </span>
          )}
        </div>

        {/* Bubble */}
        <div
          className={`p-4 rounded-2xl text-sm leading-relaxed text-left border shadow-lg ${
            isUser
              ? 'bg-blue-600 text-white border-blue-500 rounded-tr-none'
              : isFallback
              ? 'bg-amber-950/30 border-amber-500/30 text-amber-200 rounded-tl-none'
              : 'glass-panel border-slate-800 text-slate-200 rounded-tl-none'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div>
              {isFallback && (
                <div className="flex items-center space-x-2 text-amber-400 font-medium text-xs mb-2">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                  <span>Strict Fallback Policy Triggered</span>
                </div>
              )}

              <div className="markdown-content">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.answer}
                </ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

