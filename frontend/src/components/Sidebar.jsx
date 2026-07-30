import React from 'react';
import { FileText, Plus, Trash2, Layers, FileCode, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';

export default function Sidebar({
  documents = [],
  onOpenUpload,
  onDeleteDocument,
  onClearChat,
  isLoadingDocs,
  onRefreshDocs,
  onSelectDocChunks
}) {
  const totalChunks = documents.reduce((acc, doc) => acc + (doc.chunk_count || 0), 0);

  return (
    <aside className="w-80 border-r border-slate-800 bg-slate-950 flex flex-col h-[calc(100vh-4rem)]">
      {/* Upload Trigger Button */}
      <div className="p-4 border-b border-slate-800">
        <button
          onClick={onOpenUpload}
          className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl font-medium shadow-lg shadow-blue-600/25 flex items-center justify-center space-x-2 transition-all duration-200"
        >
          <Plus className="w-5 h-5" />
          <span>Upload Document</span>
        </button>
      </div>

      {/* Ingested Documents Header */}
      <div className="px-4 py-3 border-b border-slate-800/60 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Layers className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Indexed Corpus ({documents.length})
          </span>
        </div>
        <button
          onClick={onRefreshDocs}
          className="text-slate-400 hover:text-slate-200 text-xs p-1"
          title="Reload documents"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoadingDocs ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Document List Container */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {isLoadingDocs && documents.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 text-slate-500 text-sm">
            <RefreshCw className="w-5 h-5 animate-spin mb-2 text-blue-500" />
            Loading documents...
          </div>
        ) : documents.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center text-slate-500 p-4">
            <FileCode className="w-10 h-10 mb-3 text-slate-600 stroke-[1.5]" />
            <p className="text-sm font-medium text-slate-400">No documents ingested</p>
            <p className="text-xs text-slate-500 mt-1">Upload PDF, DOCX, or TXT files to enable local RAG context query.</p>
          </div>
        ) : (
          documents.map((doc) => (
            <div
              key={doc.document_name}
              className="group relative p-3 rounded-xl bg-slate-900/60 hover:bg-slate-900 border border-slate-800/80 hover:border-slate-700 transition-all duration-200"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-2.5 overflow-hidden">
                  <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 mt-0.5">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div className="truncate">
                    <h3 className="text-sm font-medium text-slate-200 truncate group-hover:text-blue-400 transition-colors">
                      {doc.document_name}
                    </h3>
                    <p className="text-xs text-slate-400 font-mono mt-0.5 flex items-center space-x-2">
                      <span>{doc.chunk_count} chunks</span>
                      <span>•</span>
                      <span>{doc.max_page} {doc.max_page === 1 ? 'page' : 'pages'}</span>
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => onSelectDocChunks(doc.document_name)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-blue-400 hover:bg-slate-800"
                    title="View Chunks"
                  >
                    <Layers className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => onDeleteDocument(doc.document_name)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-slate-800"
                    title="Delete document"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer Info & Clear Chat */}
      <div className="p-4 border-t border-slate-800 space-y-3 bg-slate-950">
        <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
          <span>Total Vector Chunks:</span>
          <span className="font-semibold text-blue-400">{totalChunks}</span>
        </div>

        <button
          onClick={onClearChat}
          className="w-full py-2 px-3 rounded-lg border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-900 text-xs font-medium flex items-center justify-center space-x-2 transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5 text-slate-400" />
          <span>Clear Chat History</span>
        </button>
      </div>
    </aside>
  );
}
