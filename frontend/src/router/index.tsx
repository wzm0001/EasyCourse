import { createBrowserRouter, Navigate } from 'react-router-dom';
import MainLayout from '@/components/Layout';
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import { AuthGuard, RoleGuard } from './guards';
import { UserRole } from '@/types/auth';

import SchoolManage from '@/pages/SchoolManage';
import ApprovalManage from '@/pages/ApprovalManage';
import UserManage from '@/pages/UserManage';
import SemesterManage from '@/pages/SemesterManage';
import PeriodConfig from '@/pages/PeriodConfig';
import BasicData from '@/pages/BasicData';
import ConstraintConfig from '@/pages/ConstraintConfig';
import Schedule from '@/pages/Schedule';
import ScheduleView from '@/pages/ScheduleView';
import Export from '@/pages/Export';
import TeachingClass from '@/pages/TeachingClass';
import ScheduleWizard from '@/pages/ScheduleWizard';
import NotificationCenter from '@/pages/NotificationCenter';
import LogManage from '@/pages/LogManage';
import BackupManage from '@/pages/BackupManage';
import SystemSettings from '@/pages/SystemSettings';
import SchoolSettings from '@/pages/SchoolSettings';
import Profile from '@/pages/Profile';

const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/',
    element: (
      <AuthGuard>
        <MainLayout />
      </AuthGuard>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      {
        path: 'schools',
        element: <RoleGuard allowedRoles={[UserRole.SUPER_ADMIN]}><SchoolManage /></RoleGuard>,
      },
      {
        path: 'approvals',
        element: <RoleGuard allowedRoles={[UserRole.SUPER_ADMIN]}><ApprovalManage /></RoleGuard>,
      },
      {
        path: 'users',
        element: <RoleGuard allowedRoles={[UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN]}><UserManage /></RoleGuard>,
      },
      {
        path: 'schedule-wizard',
        element: <RoleGuard allowedRoles={[UserRole.SCHOOL_ADMIN]}><ScheduleWizard /></RoleGuard>,
      },
      {
        path: 'semesters',
        element: <RoleGuard allowedRoles={[UserRole.SCHOOL_ADMIN]}><SemesterManage /></RoleGuard>,
      },
      {
        path: 'periods',
        element: <RoleGuard allowedRoles={[UserRole.SCHOOL_ADMIN]}><PeriodConfig /></RoleGuard>,
      },
      {
        path: 'basic-data',
        element: <RoleGuard allowedRoles={[UserRole.SCHOOL_ADMIN]}><BasicData /></RoleGuard>,
      },
      {
        path: 'constraints',
        element: <RoleGuard allowedRoles={[UserRole.SCHOOL_ADMIN]}><ConstraintConfig /></RoleGuard>,
      },
      {
        path: 'schedule',
        element: <RoleGuard allowedRoles={[UserRole.SCHOOL_ADMIN]}><Schedule /></RoleGuard>,
      },
      {
        path: 'schedule-view',
        element: <RoleGuard allowedRoles={[UserRole.SCHOOL_ADMIN, UserRole.TEACHER]}><ScheduleView /></RoleGuard>,
      },
      {
        path: 'export',
        element: <RoleGuard allowedRoles={[UserRole.SCHOOL_ADMIN]}><Export /></RoleGuard>,
      },
      {
        path: 'teaching-classes',
        element: <RoleGuard allowedRoles={[UserRole.SCHOOL_ADMIN]}><TeachingClass /></RoleGuard>,
      },
      {
        path: 'notifications',
        element: <NotificationCenter />,
      },
      {
        path: 'logs',
        element: <RoleGuard allowedRoles={[UserRole.SUPER_ADMIN]}><LogManage /></RoleGuard>,
      },
      {
        path: 'backups',
        element: <RoleGuard allowedRoles={[UserRole.SUPER_ADMIN]}><BackupManage /></RoleGuard>,
      },
      {
        path: 'settings',
        element: <RoleGuard allowedRoles={[UserRole.SUPER_ADMIN]}><SystemSettings /></RoleGuard>,
      },
      {
        path: 'school-settings',
        element: <RoleGuard allowedRoles={[UserRole.SCHOOL_ADMIN]}><SchoolSettings /></RoleGuard>,
      },
      {
        path: 'profile',
        element: <Profile />,
      },
      {
        path: 'my-schedule',
        element: <RoleGuard allowedRoles={[UserRole.TEACHER]}><ScheduleView /></RoleGuard>,
      },
      {
        path: 'class-schedule',
        element: <RoleGuard allowedRoles={[UserRole.TEACHER]}><ScheduleView /></RoleGuard>,
      },
      {
        path: 'grade-schedule',
        element: <RoleGuard allowedRoles={[UserRole.TEACHER]}><ScheduleView /></RoleGuard>,
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/dashboard" replace />,
  },
]);

export default router;
