import { downloadFile } from '@/utils/request';

export function exportClassExcel(classId: string, semesterId: string) {
  return downloadFile(`/exports/class/${classId}/excel`, `class_schedule.xlsx`, { semester_id: semesterId });
}

export function exportClassPdf(classId: string, semesterId: string) {
  return downloadFile(`/exports/class/${classId}/pdf`, `class_schedule.pdf`, { semester_id: semesterId });
}

export function exportTeacherExcel(teacherId: string, semesterId: string) {
  return downloadFile(`/exports/teacher/${teacherId}/excel`, `teacher_schedule.xlsx`, { semester_id: semesterId });
}

export function exportTeacherPdf(teacherId: string, semesterId: string) {
  return downloadFile(`/exports/teacher/${teacherId}/pdf`, `teacher_schedule.pdf`, { semester_id: semesterId });
}

export function batchExportTeachers(gradeId: string, semesterId: string) {
  return downloadFile(`/exports/teachers/batch`, `teachers_schedules.zip`, { grade_id: gradeId, semester_id: semesterId });
}

export function batchExportClasses(gradeId: string, semesterId: string) {
  return downloadFile(`/exports/classes/batch`, `classes_schedules.zip`, { grade_id: gradeId, semester_id: semesterId });
}

export function customExport(data: any) {
  return downloadFile(`/exports/custom`, `custom_export.xlsx`, data);
}
