import React from 'react';
import { FileText, Eye, Sparkles } from 'lucide-react';

export default function SourceCitation({ citation, onPreviewChunk }) {
  const { document_name, page_number, score, snippet, chunk_id } = citation;

  return (
    <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-blue-500/40 transition-all duration-200 group">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2 truncate">
          <div className="p-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400">
            <FileText className="w-3.5 h-3.5" />
          </div>
          <div className="truncate">
            <h4 className="text-xs font-semibold text-slate-200 truncate group-hover:text-blue-400 transition-colors">
              {document_name}
            </h4>
            <div className="flex items-center space-x-2 text-[11px] text-slate-400 font-mono mt-0.5">
              <span>Page {page_number}</span>
              <span>•</span>
              <span className="text-emerald-400 flex items-center gap-0.5">
                <Sparkles className="w-3 h-3 inline" />
                {Math.round(score * 100)}% match
              </span>
            </div>
          </div>
        </div>

        <button
          onClick={() => onPreviewChunk(citation)}
          className="p-1.5 rounded-lg bg-slate-800 hover:bg-blue-600/20 text-slate-400 hover:text-blue-400 border border-slate-700 transition-all text-xs flex items-center space-x-1"
          title="Preview Chunk"
        >
          <Eye className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Preview</span>
        </button>
      </div>

      {snippet && (
        <p className="mt-2 text-xs text-slate-400 line-clamp-2 italic bg-slate-950/60 p-2 rounded-lg border border-slate-800/60">
          "{snippet}"
        </p>
      )}
    </div>
  );
}
