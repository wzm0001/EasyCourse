import { post, put, getPage } from '@/utils/request';
import type { PageRequest } from '@/api/types';

export function getUsers(params: PageRequest & Record<string, any>) {
  return getPage<any>('/users', params);
}

export function createTeacher(data: any) {
  return post<any>('/users/teacher', data);
}

export function updateUser(id: string, data: any) {
  return put<any>(`/users/${id}`, data);
}

export function resetPassword(id: string) {
  return put<any>(`/users/${id}/reset-password`);
}

export function toggleUserStatus(id: string) {
  return put<any>(`/users/${id}/toggle-status`);
}
