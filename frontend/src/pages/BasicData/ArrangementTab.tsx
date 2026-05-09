import { useState, useEffect, useCallback } from 'react';
import { Card, Select, Space, App, Table, Tag, Empty, InputNumber, Row, Col, Statistic, Progress, Tooltip } from 'antd';
import { CheckCircleOutlined, HomeOutlined, TeamOutlined, ThunderboltOutlined, SunOutlined, MoonOutlined } from '@ant-design/icons';
import { useResponsive } from '@/hooks/useResponsive';
import { useAppStore } from '@/store/app';
import { getGrades, getTeachers, getTeachingArrangementSummary, createTeachingArrangement, updateTeachingArrangement, deleteTeachingArrangement } from '@/api/basicData';

const periodTypeConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  morning_reading: { label: '早读', color: 'orange', icon: <SunOutlined /> },
  regular: { label: '正课', color: 'blue', icon: <ThunderboltOutlined /> },
  evening_study: { label: '晚自习', color: 'purple', icon: <MoonOutlined /> },
};

const periodOrder = ['morning_reading', 'regular', 'evening_study'];

export default function ArrangementTab() {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const currentSemester = useAppStore((s) => s.currentSemester);

  const [grades, setGrades] = useState<any[]>([]);
  const [teachers, setTeachers] = useState<any[]>([]);
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  const [summaryData, setSummaryData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [savingKeys, setSavingKeys] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (currentSemester) {
      getGrades({ page: 1, page_size: 100, semester_id: currentSemester }).then((res) => setGrades(res.items || []));
      getTeachers({ page: 1, page_size: 200, semester_id: currentSemester }).then((res) => setTeachers(res.items || []));
    }
  }, [currentSemester]);

  const loadSummary = useCallback(async () => {
    if (!currentSemester) return;
    setLoading(true);
    try {
      getTeachers({ page: 1, page_size: 200, semester_id: currentSemester }).then((res) => setTeachers(res.items || []));
      const res = await getTeachingArrangementSummary({
        semester_id: currentSemester,
        grade_id: selectedGrade || undefined,
      });
      setSummaryData(Array.isArray(res) ? res : res.data || []);
    } catch {
      setSummaryData([]);
    } finally {
      setLoading(false);
    }
  }, [currentSemester, selectedGrade]);

  useEffect(() => {
    loadSummary();
  }, [loadSummary]);

  const handleTeacherChange = async (cls: any, course: any, teacherId: string) => {
    const key = `${cls.class_id}_${course.course_id}`;
    const existing = cls.teacher_assignments?.find((a: any) => a.course_id === course.course_id);
    setSavingKeys((prev) => new Set(prev).add(key));
    try {
      if (existing) {
        if (teacherId) await updateTeachingArrangement(existing.id, { teacher_id: teacherId });
        else await deleteTeachingArrangement(existing.id);
      } else if (teacherId) {
        await createTeachingArrangement({
          teacher_id: teacherId, course_id: course.course_id,
          class_id: cls.class_id, weekly_hours: course.weekly_hours, continuous_hours: 1,
        }, currentSemester || undefined);
      }
      loadSummary();
    } catch {
      message.error('操作失败');
    } finally {
      setSavingKeys((prev) => { const n = new Set(prev); n.delete(key); return n; });
    }
  };

  const handleHoursChange = async (cls: any, course: any, weeklyHours: number | null) => {
    if (!weeklyHours) return;
    const existing = cls.teacher_assignments?.find((a: any) => a.course_id === course.course_id);
    if (!existing) return;
    const key = `${cls.class_id}_${course.course_id}`;
    setSavingKeys((prev) => new Set(prev).add(key));
    try {
      await updateTeachingArrangement(existing.id, { weekly_hours: weeklyHours });
      loadSummary();
    } catch {
      message.error('更新课时失败');
    } finally {
      setSavingKeys((prev) => { const n = new Set(prev); n.delete(key); return n; });
    }
  };

  const getAssigned = (cls: any, courseId: string) =>
    cls.teacher_assignments?.find((a: any) => a.course_id === courseId) || null;

  let totalCourses = 0, totalAssigned = 0;
  for (const item of summaryData) {
    totalCourses += item.total_courses || 0;
    totalAssigned += item.assigned_count || 0;
  }

  const teacherOptions = [
    { label: '— 选择教师 —', value: '' },
    ...teachers.map((t) => ({
      label: `${t.name}${t.teaching_group ? ` (${t.teaching_group})` : ''}${t.specialization ? ` · ${t.specialization}` : ''}`,
      value: t.id,
    })),
  ];

  if (!currentSemester) {
    return <Empty description="请先在「学期设置」中选择或创建一个学期" image={Empty.PRESENTED_IMAGE_SIMPLE} />;
  }

  if (summaryData.length === 0 && !loading) {
    return <Empty description="暂无班级数据，请先在「班级设置」中创建班级" image={Empty.PRESENTED_IMAGE_SIMPLE} />;
  }

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={isMobile ? 12 : 6}>
          <Card size="small"><Statistic title="班级数" value={summaryData.length} prefix={<TeamOutlined />} /></Card>
        </Col>
        <Col span={isMobile ? 12 : 6}>
          <Card size="small"><Statistic title="课程项" value={totalCourses} /></Card>
        </Col>
        <Col span={isMobile ? 12 : 6}>
          <Card size="small"><Statistic title="已分配" value={totalAssigned} suffix={`/ ${totalCourses}`} /></Card>
        </Col>
        <Col span={isMobile ? 12 : 6}>
          <Card size="small">
            <Progress type="circle" size={36} percent={totalCourses > 0 ? Math.round((totalAssigned / totalCourses) * 100) : 0}
              status={totalAssigned >= totalCourses && totalCourses > 0 ? 'success' : 'active'} />
            <span style={{ marginLeft: 8, color: '#999', fontSize: 12 }}>完成率</span>
          </Card>
        </Col>
      </Row>

      <Space style={{ marginBottom: 16 }}>
        <span>年级：</span>
        <Select style={{ width: 150 }} value={selectedGrade} onChange={setSelectedGrade}
          options={[{ label: '全部', value: '' }, ...grades.map((g) => ({ label: g.name, value: g.id }))]}
          allowClear onClear={() => setSelectedGrade('')} />
      </Space>

      {summaryData.map((cls) => {
        const courses = cls.courses || [];
        const grouped: Record<string, any[]> = {};
        for (const c of courses) {
          const pt = c.period_type || 'regular';
          if (!grouped[pt]) grouped[pt] = [];
          grouped[pt].push(c);
        }
        return (
          <Card key={cls.class_id} size="small" style={{ marginBottom: 12, background: '#fafafa' }}
            title={
              <Space size="middle">
                <span style={{ fontSize: 14, fontWeight: 600 }}>{cls.class_name}</span>
                {cls.classroom_name && <Tag icon={<HomeOutlined />} color="cyan">{cls.classroom_name}</Tag>}
                <Tag color={cls.assigned_count >= cls.total_courses ? 'success' : 'warning'}>
                  {cls.assigned_count}/{cls.total_courses}
                </Tag>
              </Space>
            }
          >
            {periodOrder.map((pt) => {
              const items = grouped[pt];
              if (!items || items.length === 0) return null;
              const config = periodTypeConfig[pt] || periodTypeConfig.regular;
              return (
                <div key={pt} style={{ marginBottom: 10 }}>
                  <div style={{ marginBottom: 4 }}>
                    <Tag icon={config.icon} color={config.color}>{config.label}</Tag>
                  </div>
                  <Table dataSource={items} rowKey="course_id" pagination={false} size="small" showHeader={false}
                    columns={[
                      { title: '课程', dataIndex: 'course_name', width: isMobile ? 70 : 100, render: (n: string) => <strong>{n}</strong> },
                      {
                        title: '周课时', width: 70,
                        render: (_, course) => (
                          <InputNumber size="small" min={1} max={20}
                            value={getAssigned(cls, course.course_id)?.weekly_hours ?? course.weekly_hours}
                            onChange={(v) => handleHoursChange(cls, course, v)} style={{ width: 52 }}
                            disabled={!getAssigned(cls, course.course_id)} />
                        ),
                      },
                      {
                        title: '教师', width: isMobile ? 130 : 200,
                        render: (_, course) => {
                          const assigned = getAssigned(cls, course.course_id);
                          return (
                            <Select size="small" style={{ width: '100%' }}
                              value={assigned?.teacher_id || ''}
                              onChange={(v) => handleTeacherChange(cls, course, v)}
                              options={teacherOptions} placeholder="选择教师"
                              loading={savingKeys.has(`${cls.class_id}_${course.course_id}`)}
                              showSearch optionFilterProp="label" />
                          );
                        },
                      },
                      {
                        title: '', width: 40,
                        render: (_, course) => getAssigned(cls, course.course_id)
                          ? <Tooltip title={getAssigned(cls, course.course_id).teacher_name}><CheckCircleOutlined style={{ color: '#52c41a', fontSize: 16 }} /></Tooltip>
                          : <span style={{ color: '#ccc' }}>—</span>,
                      },
                    ]} />
                </div>
              );
            })}
          </Card>
        );
      })}
    </div>
  );
}
