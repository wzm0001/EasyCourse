import { Card, Button, Space, Tag, App, Popconfirm, Modal, Form, Input, Radio } from 'antd';
import { PlusOutlined, EditOutlined, KeyOutlined, StopOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { useState, useRef } from 'react';
import { getUsers, createAdmin, createTeacher, updateUser, resetPassword, toggleUserStatus } from '@/api/users';
import { useResponsive } from '@/hooks/useResponsive';
import { useAuthStore } from '@/store/auth';

const DEFAULT_PASSWORD = 'Admin@123';

export default function UserManage() {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const user = useAuthStore((s) => s.user);
  const isSuperAdmin = user?.role === 'super_admin';
  const schoolName = user?.school_name || '';

  const [formOpen, setFormOpen] = useState(false);
  const [editData, setEditData] = useState<any>(null);
  const [resetOpen, setResetOpen] = useState(false);
  const [resetUserId, setResetUserId] = useState('');
  const [resetUsername, setResetUsername] = useState('');
  const actionRef = useRef<ActionType>(null);
  const [form] = Form.useForm();
  const [resetForm] = Form.useForm();

  const columns: ProColumns<any>[] = isSuperAdmin
    ? [
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
                  resetForm.setFieldsValue({ passwordType: 'default' });
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
      ]
    : [
        { title: '教师姓名', dataIndex: 'username', width: 120 },
        { title: '学校名称', dataIndex: 'school_name', width: 150, search: false },
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
                size="middle"
                icon={<EditOutlined />}
                onClick={() => {
                  setEditData(record);
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
                  resetForm.setFieldsValue({ passwordType: 'default' });
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
    <Card title={isSuperAdmin ? '管理员用户管理' : '教师管理'}>
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
          const items = (result.items || []).map((item: any) => ({
            ...item,
            school_name: item.school_name || schoolName,
          }));
          return {
            data: items,
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
            {isSuperAdmin ? '新增管理员' : '添加教师'}
          </Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
      />
      <Modal
        title={isSuperAdmin ? (editData ? '编辑管理员' : '新增管理员') : (editData ? '编辑教师' : '添加教师')}
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
            } else if (isSuperAdmin) {
              await createAdmin(values);
              message.success('创建成功');
            } else {
              await createTeacher({
                username: values.username,
                real_name: values.username,
                phone: values.phone,
                email: values.email || '',
                password: DEFAULT_PASSWORD,
              });
              message.success(`教师添加成功，默认密码为 ${DEFAULT_PASSWORD}`);
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
          {isSuperAdmin ? (
            <>
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
            </>
          ) : (
            <>
              <Form.Item name="username" label="教师姓名" rules={[{ required: true, message: '请输入教师姓名' }]} extra="教师姓名将作为登录用户名">
                <Input placeholder="请输入教师姓名" />
              </Form.Item>
              <Form.Item label="学校名称">
                <Input value={schoolName} disabled />
              </Form.Item>
              <Form.Item name="phone" label="手机号" rules={[{ required: true, message: '请输入手机号' }, { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' }]}>
                <Input placeholder="请输入手机号" />
              </Form.Item>
              <Form.Item name="email" label="邮箱">
                <Input placeholder="请输入邮箱（可选）" />
              </Form.Item>
              {!editData && (
                <div style={{ color: '#999', fontSize: 12, marginTop: -8, marginBottom: 16 }}>
                  添加后默认密码为 {DEFAULT_PASSWORD}
                </div>
              )}
            </>
          )}
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
            const customPwd = values.passwordType === 'custom' ? values.customPassword : undefined;
            await resetPassword(resetUserId, customPwd || DEFAULT_PASSWORD);
            message.success('密码已重置');
            setResetOpen(false);
          } catch (e: any) {
            const detail = e?.response?.data?.detail;
            if (typeof detail === 'string') {
              message.error(detail);
            } else if (Array.isArray(detail) && detail[0]?.msg) {
              message.error(detail[0].msg);
            }
          }
        }}
        okText="确定重置"
        okButtonProps={{ danger: true }}
        destroyOnHidden
      >
        <Form form={resetForm} layout="vertical" preserve={false} style={{ marginTop: 16 }}>
          <Form.Item name="passwordType" label="密码设置">
            <Radio.Group>
              <Radio value="default">使用默认密码（{DEFAULT_PASSWORD}）</Radio>
              <Radio value="custom">自定义密码</Radio>
            </Radio.Group>
          </Form.Item>
          <Form.Item
            noStyle
            shouldUpdate={(prev, cur) => prev.passwordType !== cur.passwordType}
          >
            {({ getFieldValue }) =>
              getFieldValue('passwordType') === 'custom' ? (
                <Form.Item
                  name="customPassword"
                  label="新密码"
                  rules={[
                    { required: true, message: '请输入新密码' },
                    { min: 8, message: '密码至少8位' },
                    { pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/, message: '密码需包含大小写字母和数字' },
                  ]}
                >
                  <Input.Password placeholder="请输入新密码" />
                </Form.Item>
              ) : null
            }
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
