import { useRef, useState } from 'react';
import { Button, Space, Popconfirm, Modal, Form, Input, InputNumber, Select, App } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { getCourses, createCourse, updateCourse, deleteCourse } from '@/api/basicData';
import { useResponsive } from '@/hooks/useResponsive';

export default function CourseTab() {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const actionRef = useRef<ActionType>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editData, setEditData] = useState<any>(null);
  const [form] = Form.useForm();

  const columns: ProColumns<any>[] = [
    { title: '课程名称', dataIndex: 'name', width: 180 },
    { title: '课程编码', dataIndex: 'code', width: 120 },
    {
      title: '课程类型',
      dataIndex: 'type',
      width: 100,
      valueEnum: {
        required: { text: '必修' },
        elective: { text: '选修' },
        activity: { text: '活动' },
      },
    },
    { title: '周课时', dataIndex: 'weekly_hours', width: 80, search: false },
    { title: '课时长度', dataIndex: 'duration', width: 80, search: false },
    {
      title: '操作',
      valueType: 'option',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditData(record); form.setFieldsValue(record); setFormOpen(true); }}>编辑</Button>
          <Popconfirm title="确定删除吗？" onConfirm={async () => { try { await deleteCourse(record.id); message.success('删除成功'); actionRef.current?.reload(); } catch { message.error('删除失败'); } }}>
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
          const result = await getCourses({ page: params.current || 1, page_size: params.pageSize || 10, name: params.name, type: params.type });
          return { data: result.items, total: result.total, success: true };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto' }}
        toolBarRender={() => [
          <Button key="add" type="primary" icon={<PlusOutlined />} onClick={() => { setEditData(null); form.resetFields(); setFormOpen(true); }}>新增课程</Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
      />
      <Modal
        title={editData ? '编辑课程' : '新增课程'}
        open={formOpen}
        onCancel={() => { setFormOpen(false); setEditData(null); }}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            if (editData) { await updateCourse(editData.id, values); message.success('更新成功'); }
            else { await createCourse(values); message.success('创建成功'); }
            actionRef.current?.reload(); setFormOpen(false); setEditData(null);
          } catch { message.error('操作失败'); }
        }}
        destroyOnHidden
        width={isMobile ? '90vw' : 520}
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item name="name" label="课程名称" rules={[{ required: true, message: '请输入课程名称' }]}><Input /></Form.Item>
          <Form.Item name="code" label="课程编码" rules={[{ required: true, message: '请输入课程编码' }]}><Input /></Form.Item>
          <Form.Item name="type" label="课程类型" rules={[{ required: true, message: '请选择课程类型' }]}>
            <Select options={[{ label: '必修', value: 'required' }, { label: '选修', value: 'elective' }, { label: '活动', value: 'activity' }]} />
          </Form.Item>
          <Form.Item name="weekly_hours" label="周课时"><InputNumber min={1} max={20} style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="duration" label="课时长度(分钟)"><InputNumber min={20} max={120} style={{ width: '100%' }} /></Form.Item>
        </Form>
      </Modal>
    </>
  );
}
