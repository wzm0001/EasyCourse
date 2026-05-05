import { useState, useEffect } from 'react';
import { Select, Space, Table, Tag } from 'antd';
import { getGradeSchedule } from '@/api/schedules';
import { getSemesters } from '@/api/semesters';
import { getGrades } from '@/api/basicData';

export default function GradeScheduleView() {
  const [semesters, setSemesters] = useState<any[]>([]);
  const [grades, setGrades] = useState<any[]>([]);
  const [selectedSemester, setSelectedSemester] = useState<string>('');
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  const [scheduleData, setScheduleData] = useState<any[]>([]);

  useEffect(() => {
    getSemesters({ page: 1, page_size: 100 }).then((res) => {
      setSemesters(res.items || []);
      const active = res.items?.find((s: any) => s.status === 'in_progress');
      if (active) setSelectedSemester(active.id);
    });
    getGrades({ page: 1, page_size: 100 }).then((res) => setGrades(res.items || []));
  }, []);

  useEffect(() => {
    if (selectedGrade && selectedSemester) {
      getGradeSchedule(selectedGrade, selectedSemester)
        .then((res) => setScheduleData(res.data?.classes || []))
        .catch(() => setScheduleData([]));
    }
  }, [selectedGrade, selectedSemester]);

  const columns = [
    { title: '班级', dataIndex: 'class_name', key: 'class_name', fixed: 'left' as const, width: 120 },
    { title: '周一', dataIndex: 'day_1', key: 'day_1', width: 200, render: (val: any[]) => val?.map((c, i) => <Tag key={i} style={{ marginBottom: 2 }}>{c.course_name}</Tag>) },
    { title: '周二', dataIndex: 'day_2', key: 'day_2', width: 200, render: (val: any[]) => val?.map((c, i) => <Tag key={i} style={{ marginBottom: 2 }}>{c.course_name}</Tag>) },
    { title: '周三', dataIndex: 'day_3', key: 'day_3', width: 200, render: (val: any[]) => val?.map((c, i) => <Tag key={i} style={{ marginBottom: 2 }}>{c.course_name}</Tag>) },
    { title: '周四', dataIndex: 'day_4', key: 'day_4', width: 200, render: (val: any[]) => val?.map((c, i) => <Tag key={i} style={{ marginBottom: 2 }}>{c.course_name}</Tag>) },
    { title: '周五', dataIndex: 'day_5', key: 'day_5', width: 200, render: (val: any[]) => val?.map((c, i) => <Tag key={i} style={{ marginBottom: 2 }}>{c.course_name}</Tag>) },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }} wrap>
        <span>学期：</span>
        <Select style={{ width: 220 }} value={selectedSemester} onChange={setSelectedSemester} options={semesters.map((s) => ({ label: s.name, value: s.id }))} placeholder="请选择学期" />
        <span>年级：</span>
        <Select style={{ width: 150 }} value={selectedGrade} onChange={setSelectedGrade} options={grades.map((g) => ({ label: g.name, value: g.id }))} placeholder="请选择年级" />
      </Space>
      <Table
        columns={columns}
        dataSource={scheduleData}
        rowKey="class_id"
        pagination={false}
        bordered
        size="small"
        scroll={{ x: 1200 }}
      />
    </div>
  );
}
