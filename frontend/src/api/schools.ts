import { get, post, put, del, getPage } from '@/utils/request';
import type { PageRequest } from '@/api/types';

export function getSchools(params: PageRequest & Record<string, any>) {
  return getPage<any>('/schools', params);
}

export function getSchool(id: string) {
  return get<any>(`/schools/${id}`);
}

export function createSchool(data: any) {
  return post<any>('/schools', data);
}

export function updateSchool(id: string, data: any) {
  return put<any>(`/schools/${id}`, data);
}

export function getPendingSchools(params: PageRequest & Record<string, any>) {
  return getPage<any>('/schools/pending', params);
}

export function approveSchool(id: string) {
  return post<any>(`/schools/${id}/approve`);
}

export function rejectSchool(id: string, reason?: string) {
  return post<any>(`/schools/${id}/reject`, { reason });
}

export function deleteSchool(id: string) {
  return del<any>(`/schools/${id}`);
}

export function resetSchoolPassword(id: string) {
  return post<any>(`/schools/${id}/reset-password`);
}

export function batchResetSchoolPassword(schoolIds: string[]) {
  return post<any>('/schools/batch-reset-password', { school_ids: schoolIds });
}
