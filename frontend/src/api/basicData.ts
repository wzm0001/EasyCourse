import { get, post, put, del, getPage, downloadFile } from '@/utils/request';
import type { PageRequest } from '@/api/types';

const PREFIX = '/basic-data';

export function getGrades(params: PageRequest & Record<string, any>) {
  return getPage<any>(`${PREFIX}/grades`, params);
}

export function createGrade(data: any, semesterId?: string) {
  const params = semesterId ? { semester_id: semesterId } : undefined;
  return post<any>(`${PREFIX}/grades${params ? `?semester_id=${semesterId}` : ''}`, data);
}

export function updateGrade(id: string, data: any) {
  return put<any>(`${PREFIX}/grades/${id}`, data);
}

export function deleteGrade(id: string) {
  return del<any>(`${PREFIX}/grades/${id}`);
}

export function getClasses(params: PageRequest & Record<string, any>) {
  return getPage<any>(`${PREFIX}/classes`, params);
}

export function createClass(data: any, semesterId?: string) {
  return post<any>(`${PREFIX}/classes${semesterId ? `?semester_id=${semesterId}` : ''}`, data);
}

export function updateClass(id: string, data: any) {
  return put<any>(`${PREFIX}/classes/${id}`, data);
}

export function deleteClass(id: string) {
  return del<any>(`${PREFIX}/classes/${id}`);
}

export function getCourses(params: PageRequest & Record<string, any>) {
  return getPage<any>(`${PREFIX}/courses`, params);
}

export function createCourse(data: any) {
  return post<any>(`${PREFIX}/courses`, data);
}

export function updateCourse(id: string, data: any) {
  return put<any>(`${PREFIX}/courses/${id}`, data);
}

export function deleteCourse(id: string) {
  return del<any>(`${PREFIX}/courses/${id}`);
}

export function getGradeCourses(params: PageRequest & Record<string, any>) {
  return getPage<any>(`${PREFIX}/grade-courses`, params);
}

export function createGradeCourse(data: any, semesterId?: string) {
  const params = semesterId ? { semester_id: semesterId } : undefined;
  return post<any>(`${PREFIX}/grade-courses${params ? `?semester_id=${semesterId}` : ''}`, data);
}

export function updateGradeCourse(id: string, data: any) {
  return put<any>(`${PREFIX}/grade-courses/${id}`, data);
}

export function deleteGradeCourse(id: string) {
  return del<any>(`${PREFIX}/grade-courses/${id}`);
}

export function batchAddGradeCourses(data: any, semesterId?: string) {
  const params = semesterId ? { semester_id: semesterId } : undefined;
  return post<any>(`${PREFIX}/grade-courses/batch${params ? `?semester_id=${semesterId}` : ''}`, data);
}

export function getTeachers(params: PageRequest & Record<string, any>) {
  return getPage<any>(`${PREFIX}/teachers`, params);
}

export function createTeacher(data: any, semesterId?: string) {
  return post<any>(`${PREFIX}/teachers${semesterId ? `?semester_id=${semesterId}` : ''}`, data);
}

export function updateTeacher(id: string, data: any) {
  return put<any>(`${PREFIX}/teachers/${id}`, data);
}

export function deleteTeacher(id: string) {
  return del<any>(`${PREFIX}/teachers/${id}`);
}

export function getTeacherCourses(teacherId: string) {
  return get<any[]>(`${PREFIX}/teachers/${teacherId}/courses`);
}

export function setTeacherCourses(teacherId: string, data: any) {
  return post<any>(`${PREFIX}/teachers/${teacherId}/courses`, data);
}

export function getClassrooms(params: PageRequest & Record<string, any>) {
  return getPage<any>(`${PREFIX}/classrooms`, params);
}

export function createClassroom(data: any, semesterId?: string) {
  return post<any>(`${PREFIX}/classrooms${semesterId ? `?semester_id=${semesterId}` : ''}`, data);
}

export function updateClassroom(id: string, data: any) {
  return put<any>(`${PREFIX}/classrooms/${id}`, data);
}

export function deleteClassroom(id: string) {
  return del<any>(`${PREFIX}/classrooms/${id}`);
}

export function getClassroomCourses(classroomId: string) {
  return get<any>(`${PREFIX}/classrooms/${classroomId}/courses`);
}

export function setClassroomCourses(classroomId: string, data: any) {
  return put<any>(`${PREFIX}/classrooms/${classroomId}/courses`, data);
}

export function getTeachingArrangements(params: PageRequest & Record<string, any>) {
  return getPage<any>(`${PREFIX}/teaching-arrangements`, params);
}

export function getTeachingArrangementSummary(params?: { grade_id?: string; semester_id?: string }) {
  return get<any[]>(`${PREFIX}/teaching-arrangements/summary`, params);
}

export function createTeachingArrangement(data: any, semesterId?: string) {
  return post<any>(`${PREFIX}/teaching-arrangements${semesterId ? `?semester_id=${semesterId}` : ''}`, data);
}

export function updateTeachingArrangement(id: string, data: any) {
  return put<any>(`${PREFIX}/teaching-arrangements/${id}`, data);
}

export function deleteTeachingArrangement(id: string) {
  return del<any>(`${PREFIX}/teaching-arrangements/${id}`);
}

export function batchCreateTeachingArrangements(data: any) {
  return post<any>(`${PREFIX}/teaching-arrangements/batch`, data);
}

export function quickSetup(data: any) {
  return post<any>(`${PREFIX}/quick-setup`, data);
}

export function downloadTemplate(type: string) {
  return downloadFile(`${PREFIX}/excel/template/${type}`, `${type}_template.xlsx`);
}

export function importData(type: string, file: File) {
  const formData = new FormData();
  formData.append('file', file);
  return post<any>(`${PREFIX}/excel/import/${type}`, formData);
}

export function exportData(type: string, params?: Record<string, any>) {
  return downloadFile(`${PREFIX}/excel/export/${type}`, `${type}_export.xlsx`, params);
}

export function getMyTeachingInfo(semesterId?: string) {
  const params = semesterId ? { semester_id: semesterId } : undefined;
  return get<any>(`${PREFIX}/my-teaching-info`, params);
}
