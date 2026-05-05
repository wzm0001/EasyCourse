import { get, post } from '@/utils/request';

export function getGradePeriods(gradeId: string) {
  return get<any>(`/periods/grades/${gradeId}`);
}

export function setupGradePeriods(gradeId: string, data: any) {
  return post<any>(`/periods/grades/${gradeId}`, data);
}

export function getDayPeriods(gradeId: string) {
  return get<any>(`/periods/grades/${gradeId}/days`);
}

export function setupDayPeriods(gradeId: string, data: any) {
  return post<any>(`/periods/grades/${gradeId}/days`, data);
}

export function getAvailablePeriods(gradeId: string) {
  return get<any>(`/periods/grades/${gradeId}/available`);
}

export function getTemplates() {
  return get<any[]>('/periods/templates');
}

export function createTemplate(data: any) {
  return post<any>('/periods/templates', data);
}

export function applyTemplate(templateId: string, gradeId: string) {
  return post<any>(`/periods/templates/${templateId}/apply`, { grade_id: gradeId });
}
