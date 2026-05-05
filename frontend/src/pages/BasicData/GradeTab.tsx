import { useRef, useState } from 'react';
import { Button, Space, message, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { getGrades, createGrade, updateGrade, deleteGrade } from '@/api/basicData';
import { Modal, Form, Input, InputNumber } from 'antd';

export default function GradeTab() {
  const actionRef = useRef<ActionType>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editData, setEditData] = useState<any>(null);
  const [form] = Form.useForm();

  const columns: ProColumns<any>[] = [
    { title: '年级名称', dataIndex: 'name', width: 200 },
    { title: '年级编码', dataIndex: 'code', width: 120 },
    { title: '年级序号', dataIndex: 'order', width: 80, search: false },
    { title: '学生人数', dataIndex: 'student_count', width: 100, search: false },
    {
      title: '操作',
      valueType: 'option',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditData(record); form.setFieldsValue(record); setFormOpen(true); }}>
            编辑
          </Button>
          <Popconfirm title="确定删除吗？" onConfirm={async () => { try { await deleteGrade(record.id); message.success('删除成功'); actionRef.current?.reload(); } catch { message.error('删除失败'); } }}>
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
          const result = await getGrades({ page: params.current || 1, page_size: params.pageSize || 10, name: params.name });
          return { data: result.items, total: result.total, success: true };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto' }}
        toolBarRender={() => [
          <Button key="add" type="primary" icon={<PlusOutlined />} onClick={() => { setEditData(null); form.resetFields(); setFormOpen(true); }}>新增年级</Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
      />
      <Modal
        title={editData ? '编辑年级' : '新增年级'}
        open={formOpen}
        onCancel={() => { setFormOpen(false); setEditData(null); }}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            if (editData) { await updateGrade(editData.id, values); message.success('更新成功'); }
            else { await createGrade(values); message.success('创建成功'); }
            actionRef.current?.reload(); setFormOpen(false); setEditData(null);
          } catch { message.error('操作失败'); }
        }}
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item name="name" label="年级名称" rules={[{ required: true, message: '请输入年级名称' }]}><Input /></Form.Item>
          <Form.Item name="code" label="年级编码" rules={[{ required: true, message: '请输入年级编码' }]}><Input /></Form.Item>
          <Form.Item name="order" label="年级序号" rules={[{ required: true, message: '请输入年级序号' }]}><InputNumber min={1} style={{ width: '100%' }} /></Form.Item>
        </Form>
      </Modal>
    </>
  );
}
