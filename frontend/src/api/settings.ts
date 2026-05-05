import { get, put, post } from '@/utils/request';

export function getSettings() {
  return get<any>('/settings');
}

export function updateSettings(data: any) {
  return put<any>('/settings', data);
}

export function testMysql(data: any) {
  return post<any>('/settings/test-mysql', data);
}

export function switchDatabase(data: any) {
  return post<any>('/settings/switch-database', data);
}

export function getPasswordPolicy() {
  return get<any>('/settings/password-policy');
}

export function updatePasswordPolicy(data: any) {
  return put<any>('/settings/password-policy', data);
}

export function setMaintenanceMode(enabled: boolean) {
  return put<any>('/settings/maintenance', { enabled });
}
