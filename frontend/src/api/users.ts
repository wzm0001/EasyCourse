import { post, put, getPage } from '@/utils/request';
import type { PageRequest } from '@/api/types';

export function getUsers(params: PageRequest & Record<string, any>) {
  return getPage<any>('/users', params);
}

export function createAdmin(data: any) {
  return post<any>('/users/admin', data);
}

export function createTeacher(data: any) {
  return post<any>('/users/teacher', data);
}

export function updateUser(id: string, data: any) {
  return put<any>(`/users/${id}`, data);
}

export function resetPassword(id: string, newPassword: string) {
  return put<any>(`/users/${id}/password`, { new_password: newPassword });
}

export function toggleUserStatus(id: string, isActive: boolean) {
  return put<any>(`/users/${id}/status`, { is_active: isActive });
}
