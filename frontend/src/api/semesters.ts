import { get, post, put, del, getPage } from '@/utils/request';
import type { PageRequest } from '@/api/types';

export function getSemesters(params: PageRequest & Record<string, any>) {
  return getPage<any>('/semesters', params);
}

export function getActiveSemester() {
  return get<any>('/semesters/active');
}

export function createSemester(data: any) {
  return post<any>('/semesters', data);
}

export function updateSemester(id: string, data: any) {
  return put<any>(`/semesters/${id}`, data);
}

export function activateSemester(id: string) {
  return post<any>(`/semesters/${id}/activate`);
}

export function archiveSemester(id: string) {
  return post<any>(`/semesters/${id}/archive`);
}

export function unarchiveSemester(id: string) {
  return post<any>(`/semesters/${id}/unarchive`);
}

export function copySemester(id: string, data: any) {
  return post<any>(`/semesters/${id}/copy`, data);
}

export function deleteSemester(id: string) {
  return del<any>(`/semesters/${id}`);
}
