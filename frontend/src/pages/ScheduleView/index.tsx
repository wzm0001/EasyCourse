import { Tabs } from 'antd';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/auth';
import { useAppStore } from '@/store/app';
import { UserRole } from '@/types/auth';
import ClassScheduleView from './ClassScheduleView';
import TeacherScheduleView from './TeacherScheduleView';
import ClassroomScheduleView from './ClassroomScheduleView';
import GradeScheduleView from './GradeScheduleView';
import { useState, useEffect } from 'react';
import { getMyTeachingInfo } from '@/api/basicData';

export default function ScheduleView() {
  const location = useLocation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const currentSemester = useAppStore((s) => s.currentSemester);
  const isTeacher = user?.role === UserRole.TEACHER;
  const [isHeadTeacher, setIsHeadTeacher] = useState(false);
  const [isGradeLeader, setIsGradeLeader] = useState(false);

  useEffect(() => {
    if (isTeacher && currentSemester) {
      getMyTeachingInfo(currentSemester).then((res) => {
        const headTeacherIds = res.data?.head_teacher_class_ids || [];
        const gradeLeaderIds = res.data?.grade_leader_grade_ids || [];
        setIsHeadTeacher(headTeacherIds.length > 0);
        setIsGradeLeader(gradeLeaderIds.length > 0);
      }).catch(() => {
        setIsHeadTeacher(false);
        setIsGradeLeader(false);
      });
    } else {
      setIsHeadTeacher(false);
      setIsGradeLeader(false);
    }
  }, [isTeacher, currentSemester]);

  useEffect(() => {
    if (isTeacher && !isHeadTeacher && (location.pathname === '/class-schedule' || location.pathname === '/schedule-view')) {
      navigate('/my-schedule', { replace: true });
    }
    if (isTeacher && !isGradeLeader && location.pathname === '/grade-schedule') {
      navigate('/my-schedule', { replace: true });
    }
  }, [isTeacher, isHeadTeacher, isGradeLeader, location.pathname, navigate]);

  const pathMap: Record<string, string> = {
    '/schedule-view': 'class',
    '/my-schedule': 'teacher',
    '/class-schedule': 'class',
    '/grade-schedule': 'grade',
  };

  const rawActiveKey = pathMap[location.pathname] || 'class';
  const activeKey = (isTeacher && !isHeadTeacher && rawActiveKey === 'class') ? 'teacher'
    : (isTeacher && !isGradeLeader && rawActiveKey === 'grade') ? 'teacher'
    : rawActiveKey;

  const onChange = (key: string) => {
    if (isTeacher) {
      if (key === 'teacher') navigate('/my-schedule');
      else if (key === 'class') navigate('/class-schedule');
      else if (key === 'grade') navigate('/grade-schedule');
    } else {
      const routeMap: Record<string, string> = {
        class: '/schedule-view',
        teacher: '/schedule-view',
        classroom: '/schedule-view',
        grade: '/schedule-view',
      };
      navigate(routeMap[key] || '/schedule-view');
    }
  };

  const adminTabs = [
    { key: 'class', label: '班级课表', children: <ClassScheduleView /> },
    { key: 'teacher', label: '教师课表', children: <TeacherScheduleView /> },
    { key: 'classroom', label: '教室课表', children: <ClassroomScheduleView /> },
    { key: 'grade', label: '年级汇总', children: <GradeScheduleView /> },
  ];

  const teacherTabs = [
    { key: 'teacher', label: '我的课表', children: <TeacherScheduleView /> },
    ...(isHeadTeacher ? [{ key: 'class', label: '班级课表', children: <ClassScheduleView /> }] : []),
    ...(isGradeLeader ? [{ key: 'grade', label: '年级课表', children: <GradeScheduleView /> }] : []),
  ];

  const items = isTeacher ? teacherTabs : adminTabs;

  return (
    <Tabs
      activeKey={activeKey}
      onChange={onChange}
      items={items}
    />
  );
}
