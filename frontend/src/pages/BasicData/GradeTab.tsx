import { useRef, useState, useEffect } from 'react';
import { Button, Space, Popconfirm, Modal, Form, Input, InputNumber, App, Card, Table, Empty, Row, Col, Tabs, Select } from 'antd';
import { MinusCircleOutlined, EditOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { getGrades, createGrade, updateGrade, deleteGrade, getGradeCourses, updateGradeCourse, deleteGradeCourse, batchAddGradeCourses, getTeachers } from '@/api/basicData';
import { useResponsive } from '@/hooks/useResponsive';
import { useAppStore } from '@/store/app';

interface GradeCourseItem {
  id: string;
  grade_id: string;
  course_id: string;
  course_name: string;
  course_code: string;
  weekly_hours: number;
  period_type: string;
}

const periodTypeLabels: Record<string, string> = {
  morning_reading: '早读',
  regular: '正课',
  evening_study: '晚自习',
};

export default function GradeTab() {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const actionRef = useRef<ActionType>(null);
  const [gradeFormOpen, setGradeFormOpen] = useState(false);
  const [editGradeData, setEditGradeData] = useState<any>(null);
  const [gradeForm] = Form.useForm();
  const currentSemester = useAppStore((s) => s.currentSemester);
  const [teachers, setTeachers] = useState<any[]>([]);

  useEffect(() => {
    if (currentSemester) {
      getTeachers({ page: 1, page_size: 200, semester_id: currentSemester }).then((res) => {
        setTeachers(res.items || []);
      });
    }
  }, [currentSemester]);

  useEffect(() => {
    actionRef.current?.reload();
    setSelectedGrade(null);
    setGradeCourses([]);
  }, [currentSemester]);

  const [selectedGrade, setSelectedGrade] = useState<any>(null);
  const [gradeCourses, setGradeCourses] = useState<GradeCourseItem[]>([]);
  const [editCourseOpen, setEditCourseOpen] = useState(false);
  const [editCourseData, setEditCourseData] = useState<GradeCourseItem | null>(null);
  const [courseForm] = Form.useForm();

  const [batchOpen, setBatchOpen] = useState(false);
  const [batchPeriodType, setBatchPeriodType] = useState<string>('regular');
  const [batchForm] = Form.useForm();

  const loadGradeCourses = async (gradeId: string) => {
    try {
      const res = await getGradeCourses({ grade_id: gradeId, page: 1, page_size: 200 });
      setGradeCourses(res.items || []);
    } catch {
      message.error('加载年级课程失败');
    }
  };

  const handleGradeSelect = (record: any) => {
    if (selectedGrade?.id === record.id) {
      setSelectedGrade(null);
      setGradeCourses([]);
    } else {
      setSelectedGrade(record);
      loadGradeCourses(record.id);
    }
  };

  const handleEditCourse = (record: GradeCourseItem) => {
    setEditCourseData(record);
    courseForm.setFieldsValue({ weekly_hours: record.weekly_hours, period_type: record.period_type });
    setEditCourseOpen(true);
  };

  const handleEditCourseSubmit = async () => {
    try {
      const values = await courseForm.validateFields();
      await updateGradeCourse(editCourseData!.id, { weekly_hours: values.weekly_hours, period_type: values.period_type });
      message.success('更新成功');
      setEditCourseOpen(false);
      loadGradeCourses(selectedGrade.id);
      actionRef.current?.reload();
    } catch {
      message.error('操作失败');
    }
  };

  const handleDeleteCourse = async (id: string) => {
    try {
      await deleteGradeCourse(id);
      message.success('删除成功');
      loadGradeCourses(selectedGrade.id);
      actionRef.current?.reload();
    } catch {
      message.error('删除失败');
    }
  };

  const handleBatchAdd = (periodType: string) => {
    if (!selectedGrade) {
      message.warning('请先选择年级');
      return;
    }
    setBatchPeriodType(periodType);
    batchForm.resetFields();
    batchForm.setFieldsValue({
      courses: [{ name: '', weekly_hours: 1 }],
    });
    setBatchOpen(true);
  };

  const handleBatchSubmit = async () => {
    try {
      const values = await batchForm.validateFields();
      const validCourses = values.courses.filter((c: any) => c && c.name && c.name.trim());
      if (validCourses.length === 0) {
        message.warning('请至少添加一门课程');
        return;
      }
      await batchAddGradeCourses(
        { grade_id: selectedGrade.id, period_type: batchPeriodType, courses: validCourses },
        currentSemester || undefined
      );
      message.success('批量添加成功');
      setBatchOpen(false);
      loadGradeCourses(selectedGrade.id);
      actionRef.current?.reload();
    } catch {
      message.error('操作失败');
    }
  };

  const getPeriodCourses = (type: string) => {
    return gradeCourses.filter((c) => c.period_type === type);
  };

  const gradeColumns: ProColumns<any>[] = [
    { title: '年级名称', dataIndex: 'name', width: 150 },
    { title: '年级长', dataIndex: 'grade_leader_name', width: 100, search: false, render: (_: any, record: any) => record.grade_leader_name || '-' },
    { title: '课程数', dataIndex: 'course_count', width: 80, search: false },
    { title: '早读节数', dataIndex: 'morning_reading_count', width: 90, search: false },
    { title: '正课节数', dataIndex: 'regular_class_count', width: 90, search: false },
    { title: '晚自习节数', dataIndex: 'evening_study_count', width: 100, search: false },
    {
      title: '操作',
      valueType: 'option',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button
            type={selectedGrade?.id === record.id ? 'primary' : 'link'}
            size="small"
            onClick={() => handleGradeSelect(record)}
          >
            {selectedGrade?.id === record.id ? '收起课程' : '管理课程'}
          </Button>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditGradeData(record); gradeForm.setFieldsValue(record); setGradeFormOpen(true); }}>
            编辑
          </Button>
          <Popconfirm title="确定删除吗？" onConfirm={async () => { try { await deleteGrade(record.id); message.success('删除成功'); if (selectedGrade?.id === record.id) { setSelectedGrade(null); setGradeCourses([]); } actionRef.current?.reload(); } catch { message.error('删除失败'); } }}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const courseColumns = [
    { title: '课程编码', dataIndex: 'course_code', width: 120 },
    { title: '课程名称', dataIndex: 'course_name', width: 180 },
    { title: '周课时', dataIndex: 'weekly_hours', width: 100 },
    {
      title: '操作',
      width: 150,
      render: (_: any, record: GradeCourseItem) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEditCourse(record)}>编辑</Button>
          <Popconfirm title="确定删除该课程吗？" onConfirm={() => handleDeleteCourse(record.id)}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const renderPeriodTabContent = (periodType: string) => {
    const courses = getPeriodCourses(periodType);
    return (
      <Card
        extra={
          <Button type="primary" size="small" icon={<PlusOutlined />} onClick={() => handleBatchAdd(periodType)}>
            添加{periodTypeLabels[periodType]}课程
          </Button>
        }
        size="small"
      >
        <Table
          columns={courseColumns}
          dataSource={courses}
          rowKey="id"
          pagination={false}
          size="small"
          locale={{ emptyText: <Empty description={`暂无${periodTypeLabels[periodType]}课程`} /> }}
        />
      </Card>
    );
  };

  return (
    <>
      <ProTable<any>
        columns={gradeColumns}
        actionRef={actionRef}
        request={async (params) => {
          const result = await getGrades({ page: params.current || 1, page_size: params.pageSize || 10, name: params.name, semester_id: currentSemester || undefined });
          return { data: result.items, total: result.total, success: true };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto' }}
        toolBarRender={() => [
          <Button key="add" type="primary" icon={<PlusOutlined />} onClick={() => { setEditGradeData(null); gradeForm.resetFields(); setGradeFormOpen(true); }}>新增年级</Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
      />

      {selectedGrade && (
        <Card
          title={`${selectedGrade.name} - 课程设置（早读${selectedGrade.morning_reading_count}节 · 正课${selectedGrade.regular_class_count}节 · 晚自习${selectedGrade.evening_study_count}节）`}
          style={{ marginTop: 16 }}
        >
          <Tabs
            items={[
              {
                key: 'regular',
                label: `正课`,
                children: renderPeriodTabContent('regular'),
              },
              {
                key: 'morning_reading',
                label: `早读`,
                children: renderPeriodTabContent('morning_reading'),
              },
              {
                key: 'evening_study',
                label: `晚自习`,
                children: renderPeriodTabContent('evening_study'),
              },
            ]}
          />
        </Card>
      )}

      <Modal
        title={editGradeData ? '编辑年级' : '新增年级'}
        open={gradeFormOpen}
        onCancel={() => { setGradeFormOpen(false); setEditGradeData(null); }}
        onOk={async () => {
          try {
            const values = await gradeForm.validateFields();
            if (editGradeData) { await updateGrade(editGradeData.id, values); message.success('更新成功'); }
            else { await createGrade(values, currentSemester || undefined); message.success('创建成功'); }
            actionRef.current?.reload(); setGradeFormOpen(false); setEditGradeData(null);
          } catch { message.error('操作失败'); }
        }}
        destroyOnHidden
        width={isMobile ? '90vw' : 520}
      >
        <Form form={gradeForm} layout="vertical" initialValues={{ morning_reading_count: 1, regular_class_count: 8, evening_study_count: 0, sort_order: 0 }}>
          <Form.Item name="name" label="年级名称" rules={[{ required: true, message: '请输入年级名称' }]}><Input /></Form.Item>
          <Form.Item name="grade_leader_id" label="年级长">
            <Select
              allowClear
              showSearch
              placeholder="请选择年级长"
              filterOption={(input, option) => (option?.label ?? '').includes(input)}
              options={teachers.map((t) => ({ label: t.name, value: t.id }))}
            />
          </Form.Item>
          <Form.Item name="morning_reading_count" label="早读节数" rules={[{ required: true }]}><InputNumber min={0} max={3} style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="regular_class_count" label="正课节数" rules={[{ required: true }]}><InputNumber min={1} max={12} style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="evening_study_count" label="晚自习节数" rules={[{ required: true }]}><InputNumber min={0} max={4} style={{ width: '100%' }} /></Form.Item>
        </Form>
      </Modal>

      <Modal
        title={editCourseData ? `编辑课程 - ${editCourseData.course_name}` : '编辑课程'}
        open={editCourseOpen}
        onCancel={() => { setEditCourseOpen(false); setEditCourseData(null); }}
        onOk={handleEditCourseSubmit}
        destroyOnHidden
        width={isMobile ? '90vw' : 400}
      >
        <Form form={courseForm} layout="vertical">
          <Form.Item label="课程名称">
            <Input value={editCourseData?.course_name} disabled />
          </Form.Item>
          <Form.Item name="weekly_hours" label="周课时" rules={[{ required: true, message: '请输入周课时' }]}>
            <InputNumber min={1} max={20} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="period_type" label="所属时段" rules={[{ required: true }]}>
            <Input value={courseForm.getFieldValue('period_type') ? periodTypeLabels[courseForm.getFieldValue('period_type')] : ''} disabled />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`批量添加${periodTypeLabels[batchPeriodType]}课程 - ${selectedGrade?.name || ''}`}
        open={batchOpen}
        onCancel={() => setBatchOpen(false)}
        onOk={handleBatchSubmit}
        destroyOnHidden
        width={isMobile ? '95vw' : 700}
      >
        <Form form={batchForm} layout="vertical">
          <Form.List name="courses">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => (
                  <Row key={key} gutter={16} align="middle" style={{ marginBottom: 8 }}>
                    <Col flex="auto">
                      <Form.Item
                        {...restField}
                        name={[name, 'name']}
                        rules={[{ required: true, message: '请输入课程名称' }]}
                        style={{ marginBottom: 0 }}
                      >
                        <Input placeholder="课程名称，如：语文、数学" />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item
                        {...restField}
                        name={[name, 'weekly_hours']}
                        initialValue={1}
                        rules={[{ required: true, message: '请输入周课时' }]}
                        style={{ marginBottom: 0 }}
                      >
                        <InputNumber min={1} max={20} placeholder="周课时" style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={2}>
                      {fields.length > 1 && (
                        <MinusCircleOutlined
                          style={{ color: '#ff4d4f', fontSize: 18 }}
                          onClick={() => remove(name)}
                        />
                      )}
                    </Col>
                  </Row>
                ))}
                <Form.Item>
                  <Button type="dashed" onClick={() => add({ name: '', weekly_hours: 1 })} block icon={<PlusOutlined />}>
                    添加课程
                  </Button>
                </Form.Item>
              </>
            )}
          </Form.List>
        </Form>
      </Modal>
    </>
  );
}
