import { useRef, useState, useEffect } from 'react';
import { Card, Button, Space, App, Popconfirm, Modal, Form, Select, Input } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { getTeachingClasses, createTeachingClass, updateTeachingClass, deleteTeachingClass } from '@/api/teachingClasses';
import { getGrades, getCourses, getClasses } from '@/api/basicData';
import { useResponsive } from '@/hooks/useResponsive';

export default function TeachingClass({ embedded }: { embedded?: boolean } = {}) {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const actionRef = useRef<ActionType>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editData, setEditData] = useState<any>(null);
  const [grades, setGrades] = useState<any[]>([]);
  const [courses, setCourses] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [form] = Form.useForm();

  useEffect(() => {
    getGrades({ page: 1, page_size: 100 }).then((res) => setGrades(res.items || []));
    getCourses({ page: 1, page_size: 200 }).then((res) => setCourses(res.items || []));
    getClasses({ page: 1, page_size: 200 }).then((res) => setClasses(res.items || []));
  }, []);

  const columns: ProColumns<any>[] = [
    { title: '教学班名称', dataIndex: 'name', width: 200 },
    { title: '年级', dataIndex: 'grade_name', width: 100 },
    { title: '课程', dataIndex: 'course_name', width: 120 },
    { title: '教师', dataIndex: 'teacher_name', width: 100 },
    { title: '班级数', dataIndex: 'class_count', width: 80, search: false },
    { title: '学生数', dataIndex: 'student_count', width: 80, search: false },
    {
      title: '类型',
      dataIndex: 'type',
      width: 100,
      valueEnum: {
        fixed: { text: '固定班' },
        walking: { text: '走班' },
      },
    },
    {
      title: '操作',
      valueType: 'option',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditData(record); form.setFieldsValue(record); setFormOpen(true); }}>编辑</Button>
          <Popconfirm title="确定删除吗？" onConfirm={async () => { try { await deleteTeachingClass(record.id); message.success('删除成功'); actionRef.current?.reload(); } catch { message.error('删除失败'); } }}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const content = (
    <>
      <ProTable<any>
        columns={columns}
        actionRef={actionRef}
        request={async (params) => {
          const result = await getTeachingClasses({ page: params.current || 1, page_size: params.pageSize || 10, name: params.name, type: params.type });
          return { data: result.items, total: result.total, success: true };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto' }}
        toolBarRender={() => [
          <Button key="add" type="primary" icon={<PlusOutlined />} onClick={() => { setEditData(null); form.resetFields(); setFormOpen(true); }}>新增教学班</Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
        scroll={{ x: isMobile ? 600 : 800 }}
      />
      <Modal
        title={editData ? '编辑教学班' : '新增教学班'}
        open={formOpen}
        width={isMobile ? '90vw' : 520}
        onCancel={() => { setFormOpen(false); setEditData(null); }}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            if (editData) { await updateTeachingClass(editData.id, values); message.success('更新成功'); }
            else { await createTeachingClass(values); message.success('创建成功'); }
            actionRef.current?.reload(); setFormOpen(false); setEditData(null);
          } catch { message.error('操作失败'); }
        }}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item name="name" label="教学班名称" rules={[{ required: true, message: '请输入名称' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="grade_id" label="年级" rules={[{ required: true, message: '请选择年级' }]}>
            <Select options={grades.map((g) => ({ label: g.name, value: g.id }))} placeholder="请选择年级" />
          </Form.Item>
          <Form.Item name="course_id" label="课程" rules={[{ required: true, message: '请选择课程' }]}>
            <Select options={courses.map((c) => ({ label: c.name, value: c.id }))} placeholder="请选择课程" />
          </Form.Item>
          <Form.Item name="type" label="类型" rules={[{ required: true, message: '请选择类型' }]}>
            <Select options={[{ label: '固定班', value: 'fixed' }, { label: '走班', value: 'walking' }]} />
          </Form.Item>
          <Form.Item name="class_ids" label="包含班级" rules={[{ required: true, message: '请选择班级' }]}>
            <Select mode="multiple" options={classes.map((c) => ({ label: c.name, value: c.id }))} placeholder="请选择班级" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );

  return embedded ? content : <Card title="教学班管理">{content}</Card>;
}
