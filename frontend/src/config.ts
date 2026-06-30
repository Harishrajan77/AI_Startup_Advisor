// API Configuration helper
const API_HOST = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';

export const PROJECT_NAME = (import.meta as any).env.VITE_APP_NAME || 'AI Startup Advisor';
export const PROJECT_SUBTITLE = (import.meta as any).env.VITE_APP_SUBTITLE || 'validation engine';

export const API_URL = API_HOST;
export const ENDPOINTS = {
  validate: `${API_HOST}/api/validate`,
  status: (id: string) => `${API_HOST}/api/validate/${id}`,
  history: `${API_HOST}/api/history`,
};
