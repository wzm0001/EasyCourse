import { useRef, useState, useEffect } from 'react';
import { Button, Popconfirm, Modal, Form, Select, InputNumber, App } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { getTeachingArrangements, createTeachingArrangement, deleteTeachingArrangement, getGrades, getClasses, getCourses, getTeachers } from '@/api/basicData';
import { useResponsive } from '@/hooks/useResponsive';

export default function ArrangementTab() {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const actionRef = useRef<ActionType>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [grades, setGrades] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [courses, setCourses] = useState<any[]>([]);
  const [teachers, setTeachers] = useState<any[]>([]);
  const [form] = Form.useForm();

  useEffect(() => {
    getGrades({ page: 1, page_size: 100 }).then((res) => setGrades(res.items || []));
    getClasses({ page: 1, page_size: 200 }).then((res) => setClasses(res.items || []));
    getCourses({ page: 1, page_size: 200 }).then((res) => setCourses(res.items || []));
    getTeachers({ page: 1, page_size: 200 }).then((res) => setTeachers(res.items || []));
  }, []);

  const columns: ProColumns<any>[] = [
    { title: '年级', dataIndex: 'grade_name', width: 100 },
    { title: '班级', dataIndex: 'class_name', width: 120 },
    { title: '课程', dataIndex: 'course_name', width: 120 },
    { title: '教师', dataIndex: 'teacher_name', width: 100 },
    { title: '周课时', dataIndex: 'weekly_hours', width: 80 },
    { title: '连排节数', dataIndex: 'continuous_hours', width: 90, search: false },
    {
      title: '操作',
      valueType: 'option',
      width: 100,
      render: (_, record) => (
        <Popconfirm title="确定删除吗？" onConfirm={async () => { try { await deleteTeachingArrangement(record.id); message.success('删除成功'); actionRef.current?.reload(); } catch { message.error('删除失败'); } }}>
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button>
        </Popconfirm>
      ),
    },
  ];

  return (
    <>
      <ProTable<any>
        columns={columns}
        actionRef={actionRef}
        request={async (params) => {
          const result = await getTeachingArrangements({ page: params.current || 1, page_size: params.pageSize || 10, grade_id: params.grade_id, class_id: params.class_id });
          return { data: result.items, total: result.total, success: true };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto' }}
        toolBarRender={() => [
          <Button key="add" type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); setFormOpen(true); }}>新增教学安排</Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
      />
      <Modal
        title="新增教学安排"
        open={formOpen}
        onCancel={() => setFormOpen(false)}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            await createTeachingArrangement(values);
            message.success('创建成功');
            actionRef.current?.reload();
            setFormOpen(false);
          } catch { message.error('操作失败'); }
        }}
        destroyOnHidden
        width={isMobile ? '90vw' : 520}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="grade_id" label="年级" rules={[{ required: true, message: '请选择年级' }]}>
            <Select options={grades.map((g) => ({ label: g.name, value: g.id }))} placeholder="请选择年级" />
          </Form.Item>
          <Form.Item name="class_id" label="班级" rules={[{ required: true, message: '请选择班级' }]}>
            <Select options={classes.map((c) => ({ label: c.name, value: c.id }))} placeholder="请选择班级" />
          </Form.Item>
          <Form.Item name="course_id" label="课程" rules={[{ required: true, message: '请选择课程' }]}>
            <Select options={courses.map((c) => ({ label: c.name, value: c.id }))} placeholder="请选择课程" />
          </Form.Item>
          <Form.Item name="teacher_id" label="教师" rules={[{ required: true, message: '请选择教师' }]}>
            <Select options={teachers.map((t) => ({ label: t.real_name, value: t.id }))} placeholder="请选择教师" />
          </Form.Item>
          <Form.Item name="weekly_hours" label="周课时" rules={[{ required: true, message: '请输入周课时' }]}>
            <InputNumber min={1} max={20} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="continuous_hours" label="连排节数">
            <InputNumber min={1} max={4} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
