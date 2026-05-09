import { post, put, del, getPage } from '@/utils/request';
import type { PageRequest } from '@/api/types';

export function getConstraints(params: PageRequest & Record<string, any>) {
  return getPage<any>('/constraints', params);
}

export function createConstraint(data: any, semesterId?: string) {
  const params = semesterId ? `?semester_id=${semesterId}` : '';
  return post<any>(`/constraints${params}`, data);
}

export function updateConstraint(id: string, data: any) {
  return put<any>(`/constraints/${id}`, data);
}

export function deleteConstraint(id: string) {
  return del<any>(`/constraints/${id}`);
}

export function toggleConstraint(id: string) {
  return put<any>(`/constraints/${id}/toggle`);
}
