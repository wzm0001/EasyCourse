import api from '@/api';
import type { APIResponse, PageRequest, PageResponse } from '@/api/types';
import axios from 'axios';

export async function get<T>(url: string, params?: Record<string, any>): Promise<APIResponse<T>> {
  const response = await api.get<APIResponse<T>>(url, { params });
  return response.data;
}

export async function post<T>(url: string, data?: any): Promise<APIResponse<T>> {
  const response = await api.post<APIResponse<T>>(url, data);
  return response.data;
}

export async function put<T>(url: string, data?: any): Promise<APIResponse<T>> {
  const response = await api.put<APIResponse<T>>(url, data);
  return response.data;
}

export async function del<T>(url: string): Promise<APIResponse<T>> {
  const response = await api.delete<APIResponse<T>>(url);
  return response.data;
}

export async function getPage<T>(
  url: string,
  params: PageRequest & Record<string, any>
): Promise<PageResponse<T>> {
  const response = await api.get<APIResponse<PageResponse<T>>>(url, { params });
  return response.data.data;
}

export function createCancelToken() {
  const source = axios.CancelToken.source();
  return source;
}

export async function downloadFile(url: string, filename: string, params?: Record<string, any>): Promise<void> {
  const response = await api.get(url, {
    params,
    responseType: 'blob',
  });
  const blob = new Blob([response.data]);
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}
