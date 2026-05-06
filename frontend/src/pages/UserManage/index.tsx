import { Card, Button, Space, Tag, App, Popconfirm, Modal, Form, Input } from 'antd';
import { PlusOutlined, EditOutlined, KeyOutlined, StopOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { useState, useRef } from 'react';
import { getUsers, createAdmin, updateUser, resetPassword, toggleUserStatus } from '@/api/users';
import { useResponsive } from '@/hooks/useResponsive';

export default function UserManage() {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const [formOpen, setFormOpen] = useState(false);
  const [editData, setEditData] = useState<any>(null);
  const [resetOpen, setResetOpen] = useState(false);
  const [resetUserId, setResetUserId] = useState('');
  const [resetUsername, setResetUsername] = useState('');
  const actionRef = useRef<ActionType>(null);
  const [form] = Form.useForm();
  const [resetForm] = Form.useForm();

  const columns: ProColumns<any>[] = [
    { title: '用户名', dataIndex: 'username', width: 120 },
    { title: '姓名', dataIndex: 'real_name', width: 100 },
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
      title: '创建时间',
      dataIndex: 'created_at',
      width: 180,
      search: false,
      valueType: 'dateTime',
    },
    {
      title: '操作',
      valueType: 'option',
      width: 220,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="middle"
            icon={<EditOutlined />}
            onClick={() => {
              setEditData(record);
              form.setFieldsValue(record);
              setFormOpen(true);
            }}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="middle"
            icon={<KeyOutlined />}
            onClick={() => {
              setResetUserId(record.id);
              setResetUsername(record.username);
              resetForm.resetFields();
              setResetOpen(true);
            }}
          >
            重置密码
          </Button>
          <Popconfirm
            title={record.is_active ? '确定禁用该用户吗？' : '确定启用该用户吗？'}
            onConfirm={async () => {
              try {
                await toggleUserStatus(record.id, !record.is_active);
                message.success('操作成功');
                actionRef.current?.reload();
              } catch {
                message.error('操作失败');
              }
            }}
          >
            <Button
              type="link"
              size="middle"
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
    <Card title="管理员用户管理">
      <ProTable<any>
        columns={columns}
        actionRef={actionRef}
        request={async (params) => {
          const result = await getUsers({
            page: params.current || 1,
            page_size: params.pageSize || 10,
            username: params.username,
            real_name: params.real_name,
          });
          return {
            data: result.items,
            total: result.total,
            success: true,
          };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto', defaultCollapsed: true }}
        scroll={{ x: isMobile ? 600 : 900 }}
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
            新增管理员
          </Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
      />
      <Modal
        title={editData ? '编辑管理员' : '新增管理员'}
        open={formOpen}
        width={isMobile ? '90vw' : 460}
        style={{ top: 20 }}
        onCancel={() => {
          setFormOpen(false);
          setEditData(null);
        }}
        afterOpenChange={(visible) => {
          if (visible && editData) {
            form.setFieldsValue(editData);
          }
        }}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            if (editData) {
              await updateUser(editData.id, values);
              message.success('更新成功');
            } else {
              await createAdmin(values);
              message.success('创建成功');
            }
            actionRef.current?.reload();
            setFormOpen(false);
            setEditData(null);
          } catch {
            message.error('操作失败');
          }
        }}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" preserve={false} initialValues={editData || {}}>
          <Form.Item name="username" label="用户名" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input />
          </Form.Item>
          {!editData && (
            <Form.Item
              name="password"
              label="密码"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 8, message: '密码至少8位' },
                {
                  pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
                  message: '密码需包含大小写字母和数字',
                },
              ]}
            >
              <Input.Password placeholder="请输入密码" />
            </Form.Item>
          )}
          <Form.Item name="real_name" label="姓名" rules={[{ required: true, message: '请输入姓名' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="手机号">
            <Input />
          </Form.Item>
          <Form.Item name="email" label="邮箱">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
      <Modal
        title={`重置密码 - ${resetUsername}`}
        open={resetOpen}
        width={isMobile ? '90vw' : 460}
        style={{ top: 20 }}
        onCancel={() => setResetOpen(false)}
        onOk={async () => {
          try {
            const values = await resetForm.validateFields();
            await resetPassword(resetUserId, values.new_password);
            message.success('密码已重置');
            setResetOpen(false);
          } catch {
            message.error('重置失败');
          }
        }}
        destroyOnHidden
      >
        <Form form={resetForm} layout="vertical" preserve={false}>
          <Form.Item
            name="new_password"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 8, message: '密码至少8位' },
              {
                pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
                message: '密码需包含大小写字母和数字',
              },
            ]}
          >
            <Input.Password placeholder="请输入新密码" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
