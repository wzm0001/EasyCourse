import { post, put, del, getPage } from '@/utils/request';
import type { PageRequest } from '@/api/types';

export function getTeachingClasses(params: PageRequest & Record<string, any>) {
  return getPage<any>('/teaching-classes', params);
}

export function createTeachingClass(data: any) {
  return post<any>('/teaching-classes', data);
}

export function updateTeachingClass(id: string, data: any) {
  return put<any>(`/teaching-classes/${id}`, data);
}

export function deleteTeachingClass(id: string) {
  return del<any>(`/teaching-classes/${id}`);
}
