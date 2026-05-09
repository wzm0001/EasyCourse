import { get, post, del, put } from '@/utils/request';

export function getClassSchedule(classId: string, semesterId: string) {
  return get<any>(`/schedules/class/${classId}`, { semester_id: semesterId });
}

export function getTeacherSchedule(teacherId: string, semesterId: string) {
  return get<any>(`/schedules/teacher/${teacherId}`, { semester_id: semesterId });
}

export function getClassroomSchedule(classroomId: string, semesterId: string) {
  return get<any>(`/schedules/classroom/${classroomId}`, { semester_id: semesterId });
}

export function getGradeSchedule(gradeId: string, semesterId: string) {
  return get<any>(`/schedules/grade/${gradeId}`, { semester_id: semesterId });
}

export function getSchoolSchedule(semesterId: string) {
  return get<any>('/schedules/school', { semester_id: semesterId });
}

export function placeCell(data: any) {
  return post<any>('/schedules/place', data);
}

export function dragDropCell(data: any) {
  return post<any>('/schedules/drag-drop', data);
}

export function moveCell(data: { cell_id: string; target_day_of_week: number; target_period_type: string; target_period_index: number }) {
  return post<any>('/schedules/move', data);
}

export function checkConflicts(data: any) {
  return post<any>('/schedules/conflict-check', data);
}

export function removeCell(cellId: string) {
  return del<any>(`/schedules/cells/${cellId}`);
}

export function lockCell(cellId: string) {
  return post<any>(`/schedules/cells/${cellId}/lock`);
}

export function unlockCell(cellId: string) {
  return post<any>(`/schedules/cells/${cellId}/unlock`);
}

export function swapCells(data: { cell_id_1: string; cell_id_2: string }) {
  return post<any>('/schedules/swap', data);
}

export function autoSchedule(data: { semester_id: string; grade_id?: string; keep_locked?: boolean }) {
  return post<any>('/schedules/auto', data);
}

export function clearSchedule(data: { semester_id: string; grade_id?: string; keep_locked?: boolean }) {
  return post<any>('/schedules/clear', data);
}

export function getLockStatus(semesterId: string) {
  return get<any>('/schedules/lock', { semester_id: semesterId });
}

export function acquireLock(semesterId: string) {
  return post<any>('/schedules/lock/acquire', { semester_id: semesterId });
}

export function releaseLock(semesterId: string) {
  return post<any>('/schedules/lock/release', { semester_id: semesterId });
}
