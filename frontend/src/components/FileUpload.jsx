import React, { useState } from 'react';
import { Upload, X, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { ingestDocument } from '../services/api';

export default function FileUpload({ isOpen, onClose, onIngestSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  if (!isOpen) return null;

  const handleFileSelect = (file) => {
    setErrorMsg(null);
    setSuccessMsg(null);
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx', 'txt'].includes(ext)) {
      setErrorMsg(`Unsupported file type '.${ext}'. Please select PDF, DOCX, or TXT.`);
      setSelectedFile(null);
      return;
    }
    setSelectedFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleUploadSubmit = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadProgress(0);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      const res = await ingestDocument(selectedFile, (progress) => {
        setUploadProgress(progress);
      });

      setSuccessMsg(`Successfully ingested '${res.document_name}' (${res.total_chunks} vector chunks generated across ${res.total_pages} pages).`);
      setSelectedFile(null);
      onIngestSuccess();

      setTimeout(() => {
        setSuccessMsg(null);
        onClose();
      }, 2000);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Ingestion failed';
      setErrorMsg(`Ingestion Error: ${detail}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-lg glass-panel rounded-2xl p-6 border border-slate-800 shadow-2xl relative">
        <button
          onClick={onClose}
          disabled={isUploading}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <h2 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
          <Upload className="w-5 h-5 text-blue-400" />
          <span>Upload Document</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Select a PDF, DOCX, or TXT document to parse, chunk, embed, and store in local ChromaDB.
        </p>

        {/* Drag and Drop Zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          className={`mt-5 p-8 border-2 border-dashed rounded-xl flex flex-col items-center justify-center transition-all ${
            isDragOver
              ? 'border-blue-500 bg-blue-500/10'
              : selectedFile
              ? 'border-emerald-500/50 bg-emerald-500/5'
              : 'border-slate-800 bg-slate-900/40 hover:border-slate-700'
          }`}
        >
          {selectedFile ? (
            <div className="flex flex-col items-center text-center">
              <FileText className="w-10 h-10 text-emerald-400 mb-2" />
              <p className="text-sm font-semibold text-slate-200">{selectedFile.name}</p>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                {(selectedFile.size / 1024).toFixed(1)} KB
              </p>
              <button
                onClick={() => setSelectedFile(null)}
                disabled={isUploading}
                className="mt-3 text-xs text-red-400 hover:text-red-300 underline"
              >
                Change file
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center text-center">
              <Upload className="w-10 h-10 text-slate-500 mb-3" />
              <p className="text-sm font-medium text-slate-300">
                Drag and drop your document file here, or{' '}
                <label className="text-blue-400 hover:underline cursor-pointer">
                  browse
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt"
                    className="hidden"
                    onChange={(e) => handleFileSelect(e.target.files[0])}
                  />
                </label>
              </p>
              <p className="text-xs text-slate-500 mt-2">Supports PDF, DOCX, and TXT files</p>
            </div>
          )}
        </div>

        {/* Progress Bar */}
        {isUploading && (
          <div className="mt-4 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
              <span className="flex items-center gap-2">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-400" />
                Processing Ingestion Pipeline...
              </span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
              <div
                className="bg-gradient-to-r from-blue-500 to-indigo-500 h-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Feedback Messages */}
        {errorMsg && (
          <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="mt-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-start space-x-2">
            <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Actions */}
        <div className="mt-6 flex justify-end space-x-3">
          <button
            onClick={onClose}
            disabled={isUploading}
            className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 bg-slate-900 rounded-lg border border-slate-800"
          >
            Cancel
          </button>
          <button
            onClick={handleUploadSubmit}
            disabled={!selectedFile || isUploading}
            className={`px-5 py-2 text-xs font-medium text-white rounded-lg transition-all flex items-center space-x-2 ${
              !selectedFile || isUploading
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-500 shadow-lg shadow-blue-600/20'
            }`}
          >
            {isUploading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Ingesting...</span>
              </>
            ) : (
              <span>Start Ingestion</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
