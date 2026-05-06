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
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
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
        if (error.config?.url?.includes('/auth/login')) {
          return Promise.reject(error);
        } else {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          window.location.href = '/login';
          message.error('登录已过期，请重新登录');
        }
        break;
      case 403:
        message.error('没有权限访问');
        break;
      case 500:
        message.error('服务器错误，请稍后重试');
        break;
      default:
        message.error(error.response?.data?.message || '请求失败');
    }
    return Promise.reject(error);
  }
);

export default api;
