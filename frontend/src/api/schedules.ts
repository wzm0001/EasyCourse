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

export function removeCell(cellId: string) {
  return del<any>(`/schedules/cell/${cellId}`);
}

export function fixCell(cellId: string) {
  return put<any>(`/schedules/cell/${cellId}/fix`);
}

export function unfixCell(cellId: string) {
  return put<any>(`/schedules/cell/${cellId}/unfix`);
}

export function swapCells(data: { cell_id_1: string; cell_id_2: string }) {
  return post<any>('/schedules/swap', data);
}

export function autoSchedule(data: { semester_id: string; grade_id?: string }) {
  return post<any>('/schedules/auto', data);
}

export function clearSchedule(data: { semester_id: string; grade_id?: string }) {
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
