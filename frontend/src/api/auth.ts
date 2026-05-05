import { get, post, put } from '@/utils/request';

export function login(data: { username: string; password: string }) {
  return post<{ access_token: string; token_type: string; user: any }>('/auth/login', data);
}

export function register(data: { username: string; password: string; real_name: string; school_id?: string }) {
  return post<any>('/auth/register', data);
}

export function getMe() {
  return get<any>('/auth/me');
}

export function changePassword(data: { old_password: string; new_password: string }) {
  return put<any>('/auth/change-password', data);
}
