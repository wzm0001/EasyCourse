import { useState, useEffect } from 'react';
import { Select, Space } from 'antd';
import ScheduleTable from '@/components/ScheduleTable';
import { getClassroomSchedule } from '@/api/schedules';
import { getSemesters } from '@/api/semesters';
import { getClassrooms } from '@/api/basicData';

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

export default function ClassroomScheduleView() {
  const [semesters, setSemesters] = useState<any[]>([]);
  const [classrooms, setClassrooms] = useState<any[]>([]);
  const [selectedSemester, setSelectedSemester] = useState<string>('');
  const [selectedClassroom, setSelectedClassroom] = useState<string>('');
  const [scheduleData, setScheduleData] = useState<Record<string, Record<string, any | null>>>({});

  useEffect(() => {
    getSemesters({ page: 1, page_size: 100 }).then((res) => {
      setSemesters(res.items || []);
      const active = res.items?.find((s: any) => s.status === 'in_progress');
      if (active) setSelectedSemester(active.id);
    });
    getClassrooms({ page: 1, page_size: 200 }).then((res) => setClassrooms(res.items || []));
  }, []);

  useEffect(() => {
    if (selectedClassroom && selectedSemester) {
      getClassroomSchedule(selectedClassroom, selectedSemester)
        .then((res) => setScheduleData(res.data?.grid || {}))
        .catch(() => setScheduleData({}));
    }
  }, [selectedClassroom, selectedSemester]);

  return (
    <div>
      <Space style={{ marginBottom: 16 }} wrap>
        <span>学期：</span>
        <Select style={{ width: 220 }} value={selectedSemester} onChange={setSelectedSemester} options={semesters.map((s) => ({ label: s.name, value: s.id }))} placeholder="请选择学期" />
        <span>教室：</span>
        <Select showSearch style={{ width: 200 }} value={selectedClassroom} onChange={setSelectedClassroom} options={classrooms.map((c) => ({ label: c.name, value: c.id }))} placeholder="请选择教室" filterOption={(input, option) => (option?.label ?? '').includes(input)} />
      </Space>
      <ScheduleTable periods={defaultPeriods} days={defaultDays} data={scheduleData} viewMode="classroom" />
    </div>
  );
}
