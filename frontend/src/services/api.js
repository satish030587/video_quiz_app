import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add a timestamp to prevent caching
    const timestamp = new Date().getTime();
    if (config.url.includes('?')) {
      config.url = `${config.url}&_t=${timestamp}`;
    } else {
      config.url = `${config.url}?_t=${timestamp}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(
            'http://localhost:8000/api/auth/token/refresh/',
            { refresh: refreshToken }
          );
          
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          
          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, but don't redirect yet
        
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        // Don't force redirect - let the component handle authentication errors
        // This prevents unwanted page refreshes
        return Promise.reject({
          ...error,
          tokenRefreshFailed: true
        });
      }
    }

    return Promise.reject(error);
  }
);

export default api;
