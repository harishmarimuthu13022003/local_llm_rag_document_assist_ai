import React from 'react';
import { X, FileText, Copy, Check, Layers } from 'lucide-react';

export default function ChunkPreviewModal({ chunk, isOpen, onClose }) {
  const [copied, setCopied] = React.useState(false);

  if (!isOpen || !chunk) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(chunk.text || chunk.snippet || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-2xl glass-panel rounded-2xl p-6 border border-slate-800 shadow-2xl relative max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-xl">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100">
                Vector Chunk Preview
              </h3>
              <p className="text-xs text-slate-400 font-mono flex items-center gap-2 mt-0.5">
                <span>Doc: {chunk.document_name}</span>
                <span>•</span>
                <span>Page {chunk.page_number}</span>
                {chunk.score && (
                  <>
                    <span>•</span>
                    <span className="text-emerald-400">Score: {chunk.score}</span>
                  </>
                )}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleCopy}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors text-xs flex items-center space-x-1"
              title="Copy text"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Chunk Details */}
        <div className="flex-1 overflow-y-auto my-4 space-y-4 pr-1">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 font-sans text-sm text-slate-300 leading-relaxed whitespace-pre-wrap selection:bg-blue-600 selection:text-white">
            {chunk.text || chunk.snippet}
          </div>

          {chunk.chunk_id && (
            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs font-mono text-slate-400 flex items-center justify-between">
              <span>Chunk Identifier:</span>
              <span className="text-blue-400 truncate max-w-xs">{chunk.chunk_id}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-white bg-blue-600 hover:bg-blue-500 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
