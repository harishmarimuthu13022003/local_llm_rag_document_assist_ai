import React, { useState, useRef, useEffect } from 'react';
import { Send, Sliders, Sparkles, MessageSquare, Trash2, HelpCircle } from 'lucide-react';
import ChatMessage from './ChatMessage';
import TypingIndicator from './TypingIndicator';

export default function ChatWindow({
  messages = [],
  onSendMessage,
  isLoading,
  onPreviewChunk,
  onShowRetrievedChunks,
  onClearChat,
  documentsCount = 0
}) {
  const [inputQuery, setInputQuery] = useState('');
  const [topK] = useState(6);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputQuery.trim() || isLoading) return;
    onSendMessage(inputQuery.trim(), topK);
    setInputQuery('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const sampleQuestions = [
    "What are the key conclusions in the document?",
    "Summarize the main sections and findings.",
    "What methodology or guidelines are discussed?",
  ];

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-4rem)] bg-slate-950">
      {/* Messages Thread Container */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-xl mx-auto py-12 px-4">
            <div className="p-4 rounded-2xl bg-gradient-to-tr from-blue-600/20 to-indigo-600/20 border border-blue-500/30 text-blue-400 mb-6 shadow-xl shadow-blue-500/10">
              <Sparkles className="w-10 h-10" />
            </div>
            <h2 className="text-2xl font-bold text-slate-100">
              Local RAG Document Q&A Assistant
            </h2>
            <p className="text-sm text-slate-400 mt-2 leading-relaxed">
              Ask questions grounded strictly in your uploaded PDF, DOCX, or TXT documents.
              Runs completely locally via Ollama (<code className="text-blue-400 font-mono">llama3.2:3b</code>) and ChromaDB.
            </p>

            {documentsCount === 0 ? (
              <div className="mt-8 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs flex items-center space-x-2">
                <HelpCircle className="w-4 h-4 flex-shrink-0" />
                <span>Upload a document using the left sidebar to start querying context.</span>
              </div>
            ) : (
              <div className="mt-8 w-full">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                  Sample Starter Queries
                </p>
                <div className="grid grid-cols-1 gap-2">
                  {sampleQuestions.map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => { setInputQuery(q); }}
                      className="p-3 rounded-xl bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-blue-500/40 text-slate-300 text-xs text-left transition-all duration-200 flex items-center justify-between group"
                    >
                      <span>{q}</span>
                      <Send className="w-3.5 h-3.5 text-slate-500 group-hover:text-blue-400 transition-colors" />
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          messages.map((msg, index) => (
            <ChatMessage
              key={index}
              message={msg}
              onPreviewChunk={onPreviewChunk}
              onShowRetrievedChunks={onShowRetrievedChunks}
            />
          ))
        )}

        {isLoading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Section Bar */}
      <div className="p-4 border-t border-slate-800 glass-panel">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-3">
          {/* Controls Bar */}
          {messages.length > 0 && (
            <div className="flex items-center justify-end text-xs text-slate-400 px-1">
              <button
                type="button"
                onClick={onClearChat}
                className="text-slate-500 hover:text-red-400 flex items-center space-x-1 transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear Chat</span>
              </button>
            </div>
          )}

          {/* Textarea Input Container */}
          <div className="relative flex items-center">
            <textarea
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question based on your ingested documents (Press Enter to send)..."
              disabled={isLoading}
              rows={2}
              className="w-full pl-4 pr-14 py-3 bg-slate-900 border border-slate-800 focus:border-blue-500 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none resize-none transition-colors"
            />

            <button
              type="submit"
              disabled={!inputQuery.trim() || isLoading}
              className={`absolute right-3 p-2.5 rounded-lg text-white transition-all ${
                !inputQuery.trim() || isLoading
                  ? 'bg-slate-800 text-slate-600 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-500 shadow-md shadow-blue-600/20'
              }`}
              title="Send question"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
