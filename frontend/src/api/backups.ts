import { post, del, getPage, downloadFile } from '@/utils/request';
import type { PageRequest } from '@/api/types';

export function getBackups(params: PageRequest & Record<string, any>) {
  return getPage<any>('/backups', params);
}

export function createBackup(data?: any) {
  return post<any>('/backups', data);
}

export function restoreBackup(id: string) {
  return post<any>(`/backups/${id}/restore`);
}

export function deleteBackup(id: string) {
  return del<any>(`/backups/${id}`);
}

export function downloadBackup(id: string) {
  return downloadFile(`/backups/${id}/download`, `backup_${id}.sql`);
}
