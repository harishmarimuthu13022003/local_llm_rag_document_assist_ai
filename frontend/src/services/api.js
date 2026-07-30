import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const checkHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

export const ingestDocument = async (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/ingest', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onUploadProgress && progressEvent.total) {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onUploadProgress(percentCompleted);
      }
    },
  });
  return response.data;
};

export const sendChatMessage = async (question, topK = null) => {
  const payload = { question };
  if (topK) {
    payload.top_k = topK;
  }
  const response = await apiClient.post('/chat', payload);
  return response.data;
};

export const listDocuments = async () => {
  const response = await apiClient.get('/documents');
  return response.data;
};

export const getDocumentSources = async (docName) => {
  const response = await apiClient.get(`/sources/${encodeURIComponent(docName)}`);
  return response.data;
};

export const deleteDocument = async (docName) => {
  const response = await apiClient.delete(`/documents/${encodeURIComponent(docName)}`);
  return response.data;
};

export default apiClient;
