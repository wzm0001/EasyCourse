import { get, post, put, getPage } from '@/utils/request';
import type { PageRequest } from '@/api/types';

export function getNotifications(params: PageRequest & Record<string, any>) {
  return getPage<any>('/notifications', params);
}

export function getUnreadCount() {
  return get<number>('/notifications/unread-count');
}

export function markAsRead(id: string) {
  return put<any>(`/notifications/${id}/read`);
}

export function markAllAsRead() {
  return put<any>('/notifications/read-all');
}

export function sendNotification(data: any) {
  return post<any>('/notifications', data);
}
