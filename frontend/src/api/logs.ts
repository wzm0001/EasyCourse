import { getPage, downloadFile } from '@/utils/request';
import type { PageRequest } from '@/api/types';

export function getLogs(params: PageRequest & Record<string, any>) {
  return getPage<any>('/logs', params);
}

export function exportLogs(params: Record<string, any>) {
  return downloadFile('/logs/export', 'logs.xlsx', params);
}
