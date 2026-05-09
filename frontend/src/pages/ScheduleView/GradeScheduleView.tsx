import { useState, useEffect } from 'react';
import { Select, Space, Card } from 'antd';
import { getGradeSchedule } from '@/api/schedules';
import { getSemesters } from '@/api/semesters';
import { getGrades, getMyTeachingInfo } from '@/api/basicData';
import ScheduleTable from '@/components/ScheduleTable';
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

export default function GradeScheduleView() {
  const user = useAuthStore((s) => s.user);
  const isTeacher = user?.role === UserRole.TEACHER;

  const [semesters, setSemesters] = useState<any[]>([]);
  const [grades, setGrades] = useState<any[]>([]);
  const [selectedSemester, setSelectedSemester] = useState<string>('');
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  const [classGrids, setClassGrids] = useState<any[]>([]);
  const [teacherGradeIds, setTeacherGradeIds] = useState<string[] | null>(null);
  const [gradeLeaderGradeIds, setGradeLeaderGradeIds] = useState<string[] | null>(null);

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
        setTeacherGradeIds(res.data?.grade_ids || []);
        setGradeLeaderGradeIds(res.data?.grade_leader_grade_ids || []);
      });
    } else {
      setTeacherGradeIds(null);
      setGradeLeaderGradeIds(null);
    }
  }, [isTeacher, selectedSemester]);

  useEffect(() => {
    if (selectedSemester) {
      getGrades({ page: 1, page_size: 100, semester_id: selectedSemester }).then((res) => {
        let gradeList = res.items || [];
        if (isTeacher) {
          const allowedIds = new Set([
            ...(teacherGradeIds || []),
            ...(gradeLeaderGradeIds || []),
          ]);
          if (allowedIds.size > 0) {
            gradeList = gradeList.filter((g: any) => allowedIds.has(g.id));
          }
        }
        setGrades(gradeList);
        setSelectedGrade('');
        setClassGrids([]);
      });
    } else {
      setGrades([]);
      setSelectedGrade('');
      setClassGrids([]);
    }
  }, [selectedSemester, isTeacher, teacherGradeIds, gradeLeaderGradeIds]);

  useEffect(() => {
    if (selectedGrade && selectedSemester) {
      getGradeSchedule(selectedGrade, selectedSemester)
        .then((res) => {
          const grids = res.data || [];
          setClassGrids(grids);
        })
        .catch(() => setClassGrids([]));
    }
  }, [selectedGrade, selectedSemester]);

  return (
    <div>
      <Space style={{ marginBottom: 16 }} wrap>
        <span>学期：</span>
        <Select style={{ width: 220 }} value={selectedSemester} onChange={setSelectedSemester} options={semesters.map((s) => ({ label: s.name, value: s.id }))} placeholder="请选择学期" />
        <span>年级：</span>
        <Select style={{ width: 150 }} value={selectedGrade} onChange={setSelectedGrade} options={grades.map((g) => ({ label: g.name, value: g.id }))} placeholder="请选择年级" />
      </Space>
      {classGrids.map((grid) => (
        <Card
          key={grid.class_id}
          title={grid.class_name || grid.class_id}
          size="small"
          style={{ marginBottom: 16 }}
        >
          <ScheduleTable
            periods={defaultPeriods}
            days={defaultDays}
            data={transformCellsToGrid(grid.cells || [])}
            viewMode="class"
          />
        </Card>
      ))}
    </div>
  );
}
