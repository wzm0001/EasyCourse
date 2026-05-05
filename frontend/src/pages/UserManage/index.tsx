import { Card, Button, Space, Tag, message, Popconfirm, Modal, Form, Input, Select } from 'antd';
import { PlusOutlined, EditOutlined, KeyOutlined, StopOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { useState, useRef } from 'react';
import { getUsers, createTeacher, updateUser, resetPassword, toggleUserStatus } from '@/api/users';

export default function UserManage() {
  const [formOpen, setFormOpen] = useState(false);
  const [editData, setEditData] = useState<any>(null);
  const actionRef = useRef<ActionType>(null);
  const [form] = Form.useForm();

  const columns: ProColumns<any>[] = [
    { title: '用户名', dataIndex: 'username', width: 120 },
    { title: '姓名', dataIndex: 'real_name', width: 100 },
    {
      title: '角色',
      dataIndex: 'role',
      width: 120,
      valueEnum: {
        super_admin: { text: '超级管理员', status: 'Error' },
        school_admin: { text: '学校管理员', status: 'Processing' },
        teacher: { text: '教师', status: 'Success' },
      },
    },
    { title: '学校', dataIndex: 'school_name', width: 150, search: false },
    { title: '手机号', dataIndex: 'phone', width: 130, search: false },
    { title: '邮箱', dataIndex: 'email', width: 180, search: false, ellipsis: true },
    {
      title: '状态',
      dataIndex: 'is_active',
      width: 80,
      search: false,
      render: (_, record) => (
        <Tag color={record.is_active ? 'success' : 'default'}>{record.is_active ? '启用' : '禁用'}</Tag>
      ),
    },
    {
      title: '操作',
      valueType: 'option',
      width: 220,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => {
              setEditData(record);
              form.setFieldsValue(record);
              setFormOpen(true);
            }}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定重置该用户密码吗？"
            onConfirm={async () => {
              try {
                await resetPassword(record.id);
                message.success('密码已重置');
              } catch {
                message.error('重置失败');
              }
            }}
          >
            <Button type="link" size="small" icon={<KeyOutlined />}>
              重置密码
            </Button>
          </Popconfirm>
          <Popconfirm
            title={record.is_active ? '确定禁用该用户吗？' : '确定启用该用户吗？'}
            onConfirm={async () => {
              try {
                await toggleUserStatus(record.id);
                message.success('操作成功');
                actionRef.current?.reload();
              } catch {
                message.error('操作失败');
              }
            }}
          >
            <Button
              type="link"
              size="small"
              danger={record.is_active}
              icon={<StopOutlined />}
            >
              {record.is_active ? '禁用' : '启用'}
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Card title="用户管理">
      <ProTable<any>
        columns={columns}
        actionRef={actionRef}
        request={async (params) => {
          const result = await getUsers({
            page: params.current || 1,
            page_size: params.pageSize || 10,
            username: params.username,
            real_name: params.real_name,
            role: params.role,
          });
          return {
            data: result.items,
            total: result.total,
            success: true,
          };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto' }}
        toolBarRender={() => [
          <Button
            key="add"
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setEditData(null);
              form.resetFields();
              setFormOpen(true);
            }}
          >
            新增教师
          </Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
      />
      <Modal
        title={editData ? '编辑用户' : '新增教师'}
        open={formOpen}
        onCancel={() => {
          setFormOpen(false);
          setEditData(null);
        }}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            if (editData) {
              await updateUser(editData.id, values);
              message.success('更新成功');
            } else {
              await createTeacher(values);
              message.success('创建成功');
            }
            actionRef.current?.reload();
            setFormOpen(false);
            setEditData(null);
          } catch {
            message.error('操作失败');
          }
        }}
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item name="username" label="用户名" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input disabled={!!editData} />
          </Form.Item>
          {!editData && (
            <Form.Item name="password" label="密码" rules={[{ required: true, message: '请输入密码' }]}>
              <Input.Password />
            </Form.Item>
          )}
          <Form.Item name="real_name" label="姓名" rules={[{ required: true, message: '请输入姓名' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="role" label="角色" rules={[{ required: true, message: '请选择角色' }]}>
            <Select
              options={[
                { label: '教师', value: 'teacher' },
                { label: '学校管理员', value: 'school_admin' },
              ]}
            />
          </Form.Item>
          <Form.Item name="phone" label="手机号">
            <Input />
          </Form.Item>
          <Form.Item name="email" label="邮箱">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
