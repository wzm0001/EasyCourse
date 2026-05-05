import axios from 'axios';
import { message } from 'antd';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const status = error.response?.status;
    switch (status) {
      case 401:
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        message.error('Login expired, please login again');
        break;
      case 403:
        message.error('No permission to access');
        break;
      case 500:
        message.error('Server error, please try again later');
        break;
      default:
        message.error(error.response?.data?.message || 'Request failed');
    }
    return Promise.reject(error);
  }
);

export default api;
