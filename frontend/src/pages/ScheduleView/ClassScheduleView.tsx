import { useState, useEffect } from 'react';
import { Select, Space } from 'antd';
import ScheduleTable from '@/components/ScheduleTable';
import { getClassSchedule } from '@/api/schedules';
import { getSemesters } from '@/api/semesters';
import { getGrades, getClasses } from '@/api/basicData';

const defaultDays = [
  { key: '1', label: '周一' }, { key: '2', label: '周二' }, { key: '3', label: '周三' },
  { key: '4', label: '周四' }, { key: '5', label: '周五' }, { key: '6', label: '周六' }, { key: '7', label: '周日' },
];

const defaultPeriods = [
  { key: 'morning_1', label: '早读1' }, { key: 'morning_2', label: '早读2' },
  { key: 'class_1', label: '第1节' }, { key: 'class_2', label: '第2节' }, { key: 'class_3', label: '第3节' },
  { key: 'class_4', label: '第4节' }, { key: 'class_5', label: '第5节' }, { key: 'class_6', label: '第6节' },
  { key: 'class_7', label: '第7节' }, { key: 'class_8', label: '第8节' },
  { key: 'evening_1', label: '晚自习1' }, { key: 'evening_2', label: '晚自习2' },
];

export default function ClassScheduleView() {
  const [semesters, setSemesters] = useState<any[]>([]);
  const [grades, setGrades] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [selectedSemester, setSelectedSemester] = useState<string>('');
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  const [selectedClass, setSelectedClass] = useState<string>('');
  const [scheduleData, setScheduleData] = useState<Record<string, Record<string, any | null>>>({});

  useEffect(() => {
    getSemesters({ page: 1, page_size: 100 }).then((res) => {
      setSemesters(res.items || []);
      const active = res.items?.find((s: any) => s.status === 'in_progress');
      if (active) setSelectedSemester(active.id);
    });
    getGrades({ page: 1, page_size: 100 }).then((res) => setGrades(res.items || []));
  }, []);

  useEffect(() => {
    if (selectedGrade) {
      getClasses({ page: 1, page_size: 200, grade_id: selectedGrade }).then((res) => {
        setClasses(res.items || []);
        if (res.items?.length > 0) setSelectedClass(res.items[0].id);
      });
    }
  }, [selectedGrade]);

  useEffect(() => {
    if (selectedClass && selectedSemester) {
      getClassSchedule(selectedClass, selectedSemester)
        .then((res) => setScheduleData(res.data?.grid || {}))
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
      <ScheduleTable periods={defaultPeriods} days={defaultDays} data={scheduleData} viewMode="class" />
    </div>
  );
}
