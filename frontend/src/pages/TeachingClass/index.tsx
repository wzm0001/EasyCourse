import { useState, useEffect, useCallback } from 'react';
import { Card, Select, Space, App, Table, Button, Tag, Empty, InputNumber, Row, Col, Statistic, Progress, Tooltip, Popconfirm } from 'antd';
import { UserOutlined, DeleteOutlined, CheckCircleOutlined, HomeOutlined, TeamOutlined, ThunderboltOutlined, SunOutlined, MoonOutlined } from '@ant-design/icons';
import { useResponsive } from '@/hooks/useResponsive';
import { useAppStore } from '@/store/app';
import ScheduleStepper from '@/components/ScheduleStepper';
import { getGrades, getTeachers, getTeachingArrangementSummary, createTeachingArrangement, updateTeachingArrangement, deleteTeachingArrangement } from '@/api/basicData';
import { getSemesters } from '@/api/semesters';

const periodTypeConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  morning_reading: { label: '早读', color: 'orange', icon: <SunOutlined /> },
  regular: { label: '正课', color: 'blue', icon: <ThunderboltOutlined /> },
  evening_study: { label: '晚自习', color: 'purple', icon: <MoonOutlined /> },
};

export default function TeachingArrangement() {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const currentSemester = useAppStore((s) => s.currentSemester);

  const [semesters, setSemesters] = useState<any[]>([]);
  const [grades, setGrades] = useState<any[]>([]);
  const [teachers, setTeachers] = useState<any[]>([]);
  const [selectedSemester, setSelectedSemester] = useState<string>('');
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  const [summaryData, setSummaryData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [savingKeys, setSavingKeys] = useState<Set<string>>(new Set());

  useEffect(() => {
    getSemesters({ page: 1, page_size: 100 }).then((res) => {
      setSemesters(res.items || []);
      if (currentSemester) setSelectedSemester(currentSemester);
      else {
        const active = res.items?.find((s: any) => s.status === 'in_progress');
        if (active) setSelectedSemester(active.id);
      }
    });
  }, [currentSemester]);

  useEffect(() => {
    if (selectedSemester) {
      getGrades({ page: 1, page_size: 100, semester_id: selectedSemester }).then((res) => setGrades(res.items || []));
      getTeachers({ page: 1, page_size: 200, semester_id: selectedSemester }).then((res) => setTeachers(res.items || []));
    }
  }, [selectedSemester]);

  const loadSummary = useCallback(async () => {
    if (!selectedSemester) return;
    setLoading(true);
    try {
      getTeachers({ page: 1, page_size: 200, semester_id: selectedSemester }).then((res) => setTeachers(res.items || []));
      const res = await getTeachingArrangementSummary({
        semester_id: selectedSemester,
        grade_id: selectedGrade || undefined,
      });
      setSummaryData(Array.isArray(res) ? res : res.data || []);
    } catch {
      setSummaryData([]);
      message.error('加载教学安排失败');
    } finally {
      setLoading(false);
    }
  }, [selectedSemester, selectedGrade, message]);

  useEffect(() => {
    loadSummary();
  }, [loadSummary]);

  const handleTeacherChange = async (cls: any, course: any, teacherId: string) => {
    const key = `${cls.class_id}_${course.course_id}`;
    const existing = cls.teacher_assignments?.find((a: any) => a.course_id === course.course_id);

    setSavingKeys((prev) => new Set(prev).add(key));
    try {
      if (existing) {
        if (teacherId) {
          await updateTeachingArrangement(existing.id, { teacher_id: teacherId });
        } else {
          await deleteTeachingArrangement(existing.id);
        }
      } else if (teacherId) {
        await createTeachingArrangement({
          teacher_id: teacherId,
          course_id: course.course_id,
          class_id: cls.class_id,
          weekly_hours: course.weekly_hours,
          continuous_hours: 1,
        }, selectedSemester);
      }
      loadSummary();
    } catch {
      message.error('操作失败');
    } finally {
      setSavingKeys((prev) => {
        const next = new Set(prev);
        next.delete(key);
        return next;
      });
    }
  };

  const handleHoursChange = async (cls: any, course: any, weeklyHours: number | null) => {
    if (!weeklyHours) return;
    const key = `${cls.class_id}_${course.course_id}`;
    const existing = cls.teacher_assignments?.find((a: any) => a.course_id === course.course_id);
    if (!existing) return;

    setSavingKeys((prev) => new Set(prev).add(key));
    try {
      await updateTeachingArrangement(existing.id, { weekly_hours: weeklyHours });
      loadSummary();
    } catch {
      message.error('更新课时失败');
    } finally {
      setSavingKeys((prev) => {
        const next = new Set(prev);
        next.delete(key);
        return next;
      });
    }
  };

  const getAssigned = (cls: any, courseId: string) => {
    return cls.teacher_assignments?.find((a: any) => a.course_id === courseId) || null;
  };

  const getSummaryStats = () => {
    let totalCourses = 0;
    let totalAssigned = 0;
    for (const item of summaryData) {
      totalCourses += item.total_courses || 0;
      totalAssigned += item.assigned_count || 0;
    }
    return { totalCourses, totalAssigned };
  };

  const stats = getSummaryStats();

  const teacherOptions = [
    { label: '— 请选择教师 —', value: '' },
    ...teachers.map((t) => ({
      label: `${t.name}${t.teaching_group ? ` (${t.teaching_group})` : ''}${t.specialization ? ` · ${t.specialization}` : ''}`,
      value: t.id,
    })),
  ];

  const renderClassCard = (cls: any) => {
    const courses = cls.courses || [];
    const grouped: Record<string, any[]> = {};
    for (const c of courses) {
      const pt = c.period_type || 'regular';
      if (!grouped[pt]) grouped[pt] = [];
      grouped[pt].push(c);
    }
    const periodOrder = ['morning_reading', 'regular', 'evening_study'];

    return (
      <Card
        size="small"
        style={{ marginBottom: 12, background: '#fafafa' }}
        title={
          <Space size="middle">
            <span style={{ fontSize: 16, fontWeight: 600 }}>{cls.class_name}</span>
            {cls.classroom_name && (
              <Tag icon={<HomeOutlined />} color="cyan">{cls.classroom_name}</Tag>
            )}
            <Tag color={cls.assigned_count >= cls.total_courses ? 'success' : 'warning'}>
              {cls.assigned_count}/{cls.total_courses} 已分配
            </Tag>
          </Space>
        }
      >
        {periodOrder.map((pt) => {
          const items = grouped[pt];
          if (!items || items.length === 0) return null;
          const config = periodTypeConfig[pt] || periodTypeConfig.regular;
          return (
            <div key={pt} style={{ marginBottom: 12 }}>
              <div style={{ marginBottom: 6 }}>
                <Tag icon={config.icon} color={config.color}>{config.label}</Tag>
                <span style={{ color: '#999', fontSize: 12 }}>{items.length}门课程</span>
              </div>
              <Table
                dataSource={items}
                rowKey="course_id"
                pagination={false}
                size="small"
                showHeader={false}
                columns={[
                  {
                    title: '课程',
                    dataIndex: 'course_name',
                    width: isMobile ? 80 : 120,
                    render: (name: string) => <strong>{name}</strong>,
                  },
                  {
                    title: '周课时',
                    width: isMobile ? 60 : 80,
                    render: (_, course) => (
                      <InputNumber
                        size="small"
                        min={1}
                        max={20}
                        value={getAssigned(cls, course.course_id)?.weekly_hours ?? course.weekly_hours}
                        onChange={(v) => handleHoursChange(cls, course, v)}
                        style={{ width: 55 }}
                        disabled={!getAssigned(cls, course.course_id)}
                      />
                    ),
                  },
                  {
                    title: '授课教师',
                    width: isMobile ? 140 : 220,
                    render: (_, course) => {
                      const assigned = getAssigned(cls, course.course_id);
                      const key = `${cls.class_id}_${course.course_id}`;
                      return (
                        <Select
                          size="small"
                          style={{ width: '100%' }}
                          value={assigned?.teacher_id || ''}
                          onChange={(v) => handleTeacherChange(cls, course, v)}
                          options={teacherOptions}
                          placeholder="选择教师"
                          loading={savingKeys.has(key)}
                          showSearch
                          optionFilterProp="label"
                        />
                      );
                    },
                  },
                  {
                    title: '状态',
                    width: 60,
                    render: (_, course) => {
                      const assigned = getAssigned(cls, course.course_id);
                      return assigned
                        ? <Tooltip title={assigned.teacher_name}><CheckCircleOutlined style={{ color: '#52c41a', fontSize: 16 }} /></Tooltip>
                        : <span style={{ color: '#ccc', fontSize: 16 }}>—</span>;
                    },
                  },
                ]}
              />
            </div>
          );
        })}
        {courses.length === 0 && (
          <Empty description="该年级尚未设置课程，请先在「基础数据 → 年级设置」中添加课程" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        )}
      </Card>
    );
  };

  return (
    <Card title="教学安排" extra={<ScheduleStepper />}>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={isMobile ? 24 : 6}>
          <Card size="small">
            <Statistic title="本学期班级" value={summaryData.length} prefix={<TeamOutlined />} />
          </Card>
        </Col>
        <Col span={isMobile ? 24 : 6}>
          <Card size="small">
            <Statistic title="课程项总数" value={stats.totalCourses} />
          </Card>
        </Col>
        <Col span={isMobile ? 24 : 6}>
          <Card size="small">
            <Statistic title="已分配教师" value={stats.totalAssigned} suffix={`/ ${stats.totalCourses}`} />
          </Card>
        </Col>
        <Col span={isMobile ? 24 : 6}>
          <Card size="small">
            <Progress
              type="circle"
              size={40}
              percent={stats.totalCourses > 0 ? Math.round((stats.totalAssigned / stats.totalCourses) * 100) : 0}
              status={stats.totalAssigned >= stats.totalCourses && stats.totalCourses > 0 ? 'success' : 'active'}
            />
            <span style={{ marginLeft: 8, color: '#999', fontSize: 12 }}>完成率</span>
          </Card>
        </Col>
      </Row>

      <Space style={{ marginBottom: 16 }} wrap>
        <span>学期：</span>
        <Select
          style={{ width: 220 }}
          value={selectedSemester}
          onChange={(v) => { setSelectedSemester(v); setSelectedGrade(''); }}
          options={semesters.map((s) => ({ label: s.name, value: s.id }))}
          placeholder="请选择学期"
        />
        <span>年级：</span>
        <Select
          style={{ width: 150 }}
          value={selectedGrade}
          onChange={setSelectedGrade}
          options={[{ label: '全部年级', value: '' }, ...grades.map((g) => ({ label: g.name, value: g.id }))]}
          placeholder="请选择年级"
          allowClear
          onClear={() => setSelectedGrade('')}
        />
      </Space>

      {!selectedSemester ? (
        <Empty description="请先选择学期" />
      ) : summaryData.length === 0 && !loading ? (
        <Empty description="暂无班级数据，请先在「基础数据 → 班级设置」中创建班级" image={Empty.PRESENTED_IMAGE_SIMPLE}>
          <span style={{ color: '#999', fontSize: 12 }}>
            操作顺序：学期设置 → 年级与时间段 → 基础数据（年级/教室/班级/教师）→ 本页教学安排
          </span>
        </Empty>
      ) : (
        <div>
          {summaryData.map((cls) => (
            <div key={cls.class_id}>{renderClassCard(cls)}</div>
          ))}
        </div>
      )}
    </Card>
  );
}
