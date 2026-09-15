import axios from 'axios';

const API_BASE_URL = `${(import.meta.env.VITE_API_URL || 'http://localhost:8001').replace(/\/$/, '')}/api`;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('resumeai_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor to handle errors gracefully without breaking user session
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.warn("API Error caught:", error.response?.status, error.message);
    return Promise.reject(error);
  }
);

export default api;
