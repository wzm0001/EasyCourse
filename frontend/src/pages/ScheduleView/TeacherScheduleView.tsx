import { useState, useEffect } from 'react';
import { Select, Space } from 'antd';
import ScheduleTable from '@/components/ScheduleTable';
import { getTeacherSchedule } from '@/api/schedules';
import { getSemesters } from '@/api/semesters';
import { getTeachers, getMyTeachingInfo } from '@/api/basicData';
import { useAuthStore } from '@/store/auth';
import { UserRole } from '@/types/auth';

const defaultDays = [
  { key: '1', label: '周一' }, { key: '2', label: '周二' }, { key: '3', label: '周三' },
  { key: '4', label: '周四' }, { key: '5', label: '周五' }, { key: '6', label: '周六' }, { key: '7', label: '周日' },
];

const defaultPeriods = [
  { key: 'morning_reading_1', label: '早读1' },
  { key: 'regular_1', label: '第1节' }, { key: 'regular_2', label: '第2节' }, { key: 'regular_3', label: '第3节' },
  { key: 'regular_4', label: '第4节' }, { key: 'regular_5', label: '第5节' }, { key: 'regular_6', label: '第6节' },
  { key: 'regular_7', label: '第7节' }, { key: 'regular_8', label: '第8节' },
  { key: 'evening_study_1', label: '晚自习1' }, { key: 'evening_study_2', label: '晚自习2' },
];

function transformCellsToGrid(cells: any[]) {
  const grid: Record<string, Record<string, any | null>> = {};
  for (const cell of cells) {
    const pKey = `${cell.period_type}_${cell.period_index}`;
    const dKey = String(cell.day_of_week);
    if (!grid[pKey]) grid[pKey] = {};
    grid[pKey][dKey] = cell;
  }
  return grid;
}

export default function TeacherScheduleView() {
  const user = useAuthStore((s) => s.user);
  const isTeacher = user?.role === UserRole.TEACHER;

  const [semesters, setSemesters] = useState<any[]>([]);
  const [teachers, setTeachers] = useState<any[]>([]);
  const [selectedSemester, setSelectedSemester] = useState<string>('');
  const [selectedTeacher, setSelectedTeacher] = useState<string>('');
  const [scheduleData, setScheduleData] = useState<Record<string, Record<string, any | null>>>({});
  const [myTeacherId, setMyTeacherId] = useState<string | null>(null);

  useEffect(() => {
    getSemesters({ page: 1, page_size: 100 }).then((res) => {
      setSemesters(res.items || []);
      const active = res.items?.find((s: any) => s.status === 'in_progress');
      if (active) setSelectedSemester(active.id);
    });
  }, []);

  useEffect(() => {
    if (isTeacher && selectedSemester) {
      getMyTeachingInfo(selectedSemester).then((res) => {
        const tid = res.data?.teacher_id || null;
        setMyTeacherId(tid);
        if (tid) setSelectedTeacher(tid);
      });
    } else if (selectedSemester) {
      getTeachers({ page: 1, page_size: 200, semester_id: selectedSemester }).then((res) => {
        setTeachers(res.items || []);
        setSelectedTeacher('');
        setScheduleData({});
      });
    }
  }, [isTeacher, selectedSemester]);

  useEffect(() => {
    if (selectedTeacher && selectedSemester) {
      getTeacherSchedule(selectedTeacher, selectedSemester)
        .then((res) => {
          const cells = res.data?.cells || [];
          setScheduleData(transformCellsToGrid(cells));
        })
        .catch(() => setScheduleData({}));
    } else {
      setScheduleData({});
    }
  }, [selectedTeacher, selectedSemester]);

  return (
    <div>
      <Space style={{ marginBottom: 16 }} wrap>
        <span>学期：</span>
        <Select style={{ width: 220 }} value={selectedSemester} onChange={setSelectedSemester} options={semesters.map((s) => ({ label: s.name, value: s.id }))} placeholder="请选择学期" />
        {!isTeacher && (
          <>
            <span>教师：</span>
            <Select showSearch style={{ width: 200 }} value={selectedTeacher} onChange={setSelectedTeacher} options={teachers.map((t) => ({ label: t.name, value: t.id }))} placeholder="请选择教师" filterOption={(input, option) => (option?.label ?? '').includes(input)} />
          </>
        )}
      </Space>
      <ScheduleTable periods={defaultPeriods} days={defaultDays} data={scheduleData} viewMode="teacher" />
    </div>
  );
}
