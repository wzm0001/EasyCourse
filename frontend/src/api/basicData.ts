import { get, post, put, del, getPage, downloadFile } from '@/utils/request';
import type { PageRequest } from '@/api/types';

export function getGrades(params: PageRequest & Record<string, any>) {
  return getPage<any>('/grades', params);
}

export function createGrade(data: any) {
  return post<any>('/grades', data);
}

export function updateGrade(id: string, data: any) {
  return put<any>(`/grades/${id}`, data);
}

export function deleteGrade(id: string) {
  return del<any>(`/grades/${id}`);
}

export function getClasses(params: PageRequest & Record<string, any>) {
  return getPage<any>('/classes', params);
}

export function createClass(data: any) {
  return post<any>('/classes', data);
}

export function updateClass(id: string, data: any) {
  return put<any>(`/classes/${id}`, data);
}

export function deleteClass(id: string) {
  return del<any>(`/classes/${id}`);
}

export function getCourses(params: PageRequest & Record<string, any>) {
  return getPage<any>('/courses', params);
}

export function createCourse(data: any) {
  return post<any>('/courses', data);
}

export function updateCourse(id: string, data: any) {
  return put<any>(`/courses/${id}`, data);
}

export function deleteCourse(id: string) {
  return del<any>(`/courses/${id}`);
}

export function getGradeCourses(gradeId: string) {
  return get<any[]>(`/grades/${gradeId}/courses`);
}

export function setGradeCourses(gradeId: string, data: any) {
  return post<any>(`/grades/${gradeId}/courses`, data);
}

export function getTeachers(params: PageRequest & Record<string, any>) {
  return getPage<any>('/teachers', params);
}

export function createTeacher(data: any) {
  return post<any>('/teachers', data);
}

export function updateTeacher(id: string, data: any) {
  return put<any>(`/teachers/${id}`, data);
}

export function deleteTeacher(id: string) {
  return del<any>(`/teachers/${id}`);
}

export function getTeacherCourses(teacherId: string) {
  return get<any[]>(`/teachers/${teacherId}/courses`);
}

export function setTeacherCourses(teacherId: string, data: any) {
  return post<any>(`/teachers/${teacherId}/courses`, data);
}

export function getClassrooms(params: PageRequest & Record<string, any>) {
  return getPage<any>('/classrooms', params);
}

export function createClassroom(data: any) {
  return post<any>('/classrooms', data);
}

export function updateClassroom(id: string, data: any) {
  return put<any>(`/classrooms/${id}`, data);
}

export function deleteClassroom(id: string) {
  return del<any>(`/classrooms/${id}`);
}

export function getClassroomCourses(classroomId: string) {
  return get<any[]>(`/classrooms/${classroomId}/courses`);
}

export function setClassroomCourses(classroomId: string, data: any) {
  return post<any>(`/classrooms/${classroomId}/courses`, data);
}

export function getTeachingArrangements(params: PageRequest & Record<string, any>) {
  return getPage<any>('/teaching-arrangements', params);
}

export function createTeachingArrangement(data: any) {
  return post<any>('/teaching-arrangements', data);
}

export function updateTeachingArrangement(id: string, data: any) {
  return put<any>(`/teaching-arrangements/${id}`, data);
}

export function deleteTeachingArrangement(id: string) {
  return del<any>(`/teaching-arrangements/${id}`);
}

export function downloadTemplate(type: string) {
  return downloadFile(`/basic-data/template/${type}`, `${type}_template.xlsx`);
}

export function importData(type: string, file: File) {
  const formData = new FormData();
  formData.append('file', file);
  return post<any>(`/basic-data/import/${type}`, formData);
}

export function exportData(type: string, params?: Record<string, any>) {
  return downloadFile(`/basic-data/export/${type}`, `${type}_export.xlsx`, params);
}
