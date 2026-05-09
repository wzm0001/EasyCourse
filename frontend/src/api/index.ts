import axios from 'axios';
import { getGlobalMessage } from '@/utils/globalMessage';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const remember = localStorage.getItem('remember') === 'true';
    const storage = remember ? localStorage : sessionStorage;
    const token = storage.getItem('token');
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
    const silent = error.config?.headers?.['X-Silent'] || error.config?.params?._silent;
    if (silent) {
      return Promise.reject(error);
    }
    const getErrMsg = () => {
      const data = error.response?.data;
      if (typeof data?.detail === 'string') return data.detail;
      if (typeof data?.message === 'string') return data.message;
      if (Array.isArray(data?.detail)) {
        const first = data.detail[0];
        if (first && typeof first.msg === 'string') return first.msg;
      }
      return '请求失败';
    };
    const msg = getGlobalMessage();
    switch (status) {
      case 401:
        if (error.config?.url?.includes('/auth/login')) {
          return Promise.reject(error);
        } else {
          const remember = localStorage.getItem('remember') === 'true';
          const storage = remember ? localStorage : sessionStorage;
          storage.removeItem('token');
          storage.removeItem('user');
          window.location.href = '/login';
          msg.error('登录已过期，请重新登录');
        }
        break;
      case 403:
        msg.error(getErrMsg() || '没有权限访问');
        break;
      case 404:
        break;
      case 422:
        msg.error(getErrMsg());
        break;
      case 429:
        if (error.config?.url?.includes('/conflict-check')) {
          break;
        }
        msg.error(getErrMsg() || '请求过于频繁，请稍后再试');
        break;
      case 500:
        msg.error('服务器错误，请稍后重试');
        break;
      default:
        msg.error(getErrMsg());
    }
    return Promise.reject(error);
  }
);

export default api;
