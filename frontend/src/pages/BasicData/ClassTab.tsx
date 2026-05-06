import { useRef, useState, useEffect } from 'react';
import { Button, Space, Popconfirm, Modal, Form, Input, InputNumber, Select, App } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { getClasses, createClass, updateClass, deleteClass, getGrades, getClassrooms } from '@/api/basicData';
import { useResponsive } from '@/hooks/useResponsive';
import { useAppStore } from '@/store/app';

export default function ClassTab() {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const actionRef = useRef<ActionType>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editData, setEditData] = useState<any>(null);
  const [grades, setGrades] = useState<any[]>([]);
  const [classrooms, setClassrooms] = useState<any[]>([]);
  const [form] = Form.useForm();
  const currentSemester = useAppStore((s) => s.currentSemester);

  useEffect(() => {
    getGrades({ page: 1, page_size: 100, semester_id: currentSemester || undefined }).then((res) => setGrades(res.items || []));
    getClassrooms({ page: 1, page_size: 200, semester_id: currentSemester || undefined }).then((res) => setClassrooms(res.items || []));
  }, [currentSemester]);

  const columns: ProColumns<any>[] = [
    { title: '班级名称', dataIndex: 'name', width: 180 },
    { title: '班级编码', dataIndex: 'code', width: 120 },
    { title: '所属年级', dataIndex: 'grade_name', width: 120 },
    { title: '绑定教室', dataIndex: 'classroom_name', width: 120, search: false, render: (_, record) => record.classroom_name || '-' },
    { title: '班主任', dataIndex: 'head_teacher_name', width: 100, search: false },
    { title: '学生人数', dataIndex: 'student_count', width: 100, search: false },
    {
      title: '操作',
      valueType: 'option',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditData(record); form.setFieldsValue(record); setFormOpen(true); }}>编辑</Button>
          <Popconfirm title="确定删除吗？" onConfirm={async () => { try { await deleteClass(record.id); message.success('删除成功'); actionRef.current?.reload(); } catch { message.error('删除失败'); } }}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <>
      <ProTable<any>
        columns={columns}
        actionRef={actionRef}
        request={async (params) => {
          const result = await getClasses({ page: params.current || 1, page_size: params.pageSize || 10, name: params.name, grade_id: params.grade_id, semester_id: currentSemester || undefined });
          return { data: result.items, total: result.total, success: true };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto' }}
        toolBarRender={() => [
          <Button key="add" type="primary" icon={<PlusOutlined />} onClick={() => { setEditData(null); form.resetFields(); setFormOpen(true); }}>新增班级</Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
      />
      <Modal
        title={editData ? '编辑班级' : '新增班级'}
        open={formOpen}
        onCancel={() => { setFormOpen(false); setEditData(null); }}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            if (editData) { await updateClass(editData.id, values); message.success('更新成功'); }
            else { await createClass({ ...values, semester_id: currentSemester }); message.success('创建成功'); }
            actionRef.current?.reload(); setFormOpen(false); setEditData(null);
          } catch { message.error('操作失败'); }
        }}
        destroyOnHidden
        width={isMobile ? '90vw' : 520}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="班级名称" rules={[{ required: true, message: '请输入班级名称' }]}><Input /></Form.Item>
          <Form.Item name="code" label="班级编码" rules={[{ required: true, message: '请输入班级编码' }]}><Input /></Form.Item>
          <Form.Item name="grade_id" label="所属年级" rules={[{ required: true, message: '请选择年级' }]}>
            <Select options={grades.map((g) => ({ label: g.name, value: g.id }))} placeholder="请选择年级" />
          </Form.Item>
          <Form.Item name="classroom_id" label="绑定教室">
            <Select
              options={classrooms.map((c) => ({ label: `${c.name}${c.capacity ? ` (容量:${c.capacity})` : ''}`, value: c.id }))}
              placeholder="请选择教室"
              allowClear
            />
          </Form.Item>
          <Form.Item name="student_count" label="学生人数"><InputNumber min={0} style={{ width: '100%' }} /></Form.Item>
        </Form>
      </Modal>
    </>
  );
}
