import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import FileUpload from './components/FileUpload';
import ChunkPreviewModal from './components/ChunkPreviewModal';
import { checkHealth, listDocuments, deleteDocument, sendChatMessage, getDocumentSources } from './services/api';

export default function App() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [isRefreshingHealth, setIsRefreshingHealth] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isLoadingChat, setIsLoadingChat] = useState(false);

  // Chunk Modal State
  const [selectedChunk, setSelectedChunk] = useState(null);
  const [isChunkModalOpen, setIsChunkModalOpen] = useState(false);

  const fetchHealth = useCallback(async () => {
    setIsRefreshingHealth(true);
    try {
      const data = await checkHealth();
      setHealthStatus(data);
    } catch (err) {
      console.error("Health check error:", err);
      setHealthStatus({ status: 'unhealthy', ollama: { server_connected: false } });
    } finally {
      setIsRefreshingHealth(false);
    }
  }, []);

  const fetchDocs = useCallback(async () => {
    setIsLoadingDocs(true);
    try {
      const data = await listDocuments();
      setDocuments(data.documents || []);
    } catch (err) {
      console.error("Fetch documents error:", err);
    } finally {
      setIsLoadingDocs(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    fetchDocs();
  }, [fetchHealth, fetchDocs]);

  const handleSendMessage = async (questionText, topK) => {
    const userMsg = { role: 'user', content: questionText };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoadingChat(true);

    try {
      const response = await sendChatMessage(questionText, topK);
      const assistantMsg = {
        role: 'assistant',
        answer: response.answer,
        confidence: response.confidence,
        sources: response.sources || [],
        retrieved_chunks: response.retrieved_chunks || [],
        metrics: response.metrics || {},
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Error processing query';
      const errorMsg = {
        role: 'assistant',
        answer: `System Error: ${detail}`,
        sources: [],
        retrieved_chunks: [],
        metrics: {},
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoadingChat(false);
    }
  };

  const handleDeleteDoc = async (docName) => {
    if (!window.confirm(`Are you sure you want to delete document '${docName}'?`)) return;

    try {
      await deleteDocument(docName);
      await fetchDocs();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const handleSelectDocChunks = async (docName) => {
    try {
      const data = await getDocumentSources(docName);
      if (data.chunks && data.chunks.length > 0) {
        setSelectedChunk(data.chunks[0]);
        setIsChunkModalOpen(true);
      } else {
        alert(`No chunks found for document '${docName}'`);
      }
    } catch (err) {
      alert(`Error fetching chunks: ${err.message}`);
    }
  };

  const handlePreviewChunk = (citation) => {
    setSelectedChunk(citation);
    setIsChunkModalOpen(true);
  };

  const handleShowRetrievedChunks = (chunks) => {
    if (chunks && chunks.length > 0) {
      setSelectedChunk(chunks[0]);
      setIsChunkModalOpen(true);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header
        healthStatus={healthStatus}
        onRefreshHealth={fetchHealth}
        isRefreshing={isRefreshingHealth}
      />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          documents={documents}
          onOpenUpload={() => setIsUploadOpen(true)}
          onDeleteDocument={handleDeleteDoc}
          onClearChat={() => setMessages([])}
          isLoadingDocs={isLoadingDocs}
          onRefreshDocs={fetchDocs}
          onSelectDocChunks={handleSelectDocChunks}
        />

        <ChatWindow
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoadingChat}
          onPreviewChunk={handlePreviewChunk}
          onShowRetrievedChunks={handleShowRetrievedChunks}
          onClearChat={() => setMessages([])}
          documentsCount={documents.length}
        />
      </div>

      <FileUpload
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onIngestSuccess={fetchDocs}
      />

      <ChunkPreviewModal
        chunk={selectedChunk}
        isOpen={isChunkModalOpen}
        onClose={() => setIsChunkModalOpen(false)}
      />
    </div>
  );
}
