import { useState, useEffect } from 'react';
import { Select, Space } from 'antd';
import ScheduleTable from '@/components/ScheduleTable';
import { getClassSchedule } from '@/api/schedules';
import { getSemesters } from '@/api/semesters';
import { getGrades, getClasses, getMyTeachingInfo } from '@/api/basicData';
import { useAuthStore } from '@/store/auth';
import { UserRole } from '@/types/auth';

const defaultDays = [
  { key: '1', label: '周一' }, { key: '2', label: '周二' }, { key: '3', label: '周三' },
  { key: '4', label: '周四' }, { key: '5', label: '周五' }, { key: '6', label: '周六' }, { key: '7', label: '周日' },
];

function buildPeriods(grade: any) {
  const periods = [];
  const mr = grade?.morning_reading_count ?? 1;
  const rc = grade?.regular_class_count ?? 8;
  const es = grade?.evening_study_count ?? 0;
  for (let i = 1; i <= mr; i++) {
    periods.push({ key: `morning_reading_${i}`, label: `早读${i}` });
  }
  for (let i = 1; i <= rc; i++) {
    periods.push({ key: `regular_${i}`, label: `第${i}节` });
  }
  for (let i = 1; i <= es; i++) {
    periods.push({ key: `evening_study_${i}`, label: `晚自习${i}` });
  }
  return periods;
}

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

export default function ClassScheduleView() {
  const user = useAuthStore((s) => s.user);
  const isTeacher = user?.role === UserRole.TEACHER;

  const [semesters, setSemesters] = useState<any[]>([]);
  const [grades, setGrades] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [selectedSemester, setSelectedSemester] = useState<string>('');
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  const [selectedClass, setSelectedClass] = useState<string>('');
  const [scheduleData, setScheduleData] = useState<Record<string, Record<string, any | null>>>({});
  const [periods, setPeriods] = useState(buildPeriods(null));
  const [headTeacherClassIds, setHeadTeacherClassIds] = useState<string[] | null>(null);

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
        setHeadTeacherClassIds(res.data?.head_teacher_class_ids || []);
      });
    } else {
      setHeadTeacherClassIds(null);
    }
  }, [isTeacher, selectedSemester]);

  useEffect(() => {
    if (selectedSemester) {
      getGrades({ page: 1, page_size: 100, semester_id: selectedSemester }).then((res) => {
        setGrades(res.items || []);
        setSelectedGrade('');
        setSelectedClass('');
        setClasses([]);
        setScheduleData({});
      });
    } else {
      setGrades([]);
      setSelectedGrade('');
      setSelectedClass('');
      setClasses([]);
      setScheduleData({});
    }
  }, [selectedSemester]);

  useEffect(() => {
    if (selectedGrade && selectedSemester) {
      getClasses({ page: 1, page_size: 200, grade_id: selectedGrade, semester_id: selectedSemester }).then((res) => {
        let classList = res.items || [];
        if (isTeacher && headTeacherClassIds) {
          classList = classList.filter((c: any) => headTeacherClassIds.includes(c.id));
        }
        setClasses(classList);
        if (classList.length > 0) setSelectedClass(classList[0].id);
        else setSelectedClass('');
      });
      const grade = grades.find((g) => g.id === selectedGrade);
      setPeriods(buildPeriods(grade));
    } else {
      setClasses([]);
      setSelectedClass('');
      setPeriods(buildPeriods(null));
    }
  }, [selectedGrade, grades, selectedSemester, isTeacher, headTeacherClassIds]);

  useEffect(() => {
    if (selectedClass && selectedSemester) {
      getClassSchedule(selectedClass, selectedSemester)
        .then((res) => {
          const cells = res.data?.cells || [];
          setScheduleData(transformCellsToGrid(cells));
        })
        .catch(() => setScheduleData({}));
    }
  }, [selectedClass, selectedSemester]);

  return (
    <div>
      <Space style={{ marginBottom: 16 }} wrap>
        <span>学期：</span>
        <Select style={{ width: 220 }} value={selectedSemester} onChange={setSelectedSemester} options={semesters.map((s) => ({ label: s.name, value: s.id }))} placeholder="请选择学期" />
        <span>年级：</span>
        <Select style={{ width: 150 }} value={selectedGrade} onChange={setSelectedGrade} options={grades.map((g) => ({ label: g.name, value: g.id }))} placeholder="请选择年级" />
        <span>班级：</span>
        <Select style={{ width: 180 }} value={selectedClass} onChange={setSelectedClass} options={classes.map((c) => ({ label: c.name, value: c.id }))} placeholder="请选择班级" />
      </Space>
      <ScheduleTable periods={periods} days={defaultDays} data={scheduleData} viewMode="class" />
    </div>
  );
}
