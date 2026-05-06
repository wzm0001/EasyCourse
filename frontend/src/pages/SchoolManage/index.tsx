import { Card, Button, Space, Tag, App, Popconfirm, Modal, Form, Input, Radio } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CheckOutlined, KeyOutlined, ReloadOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { useState, useRef } from 'react';
import { getSchools, deleteSchool, approveSchool, resetSchoolPassword, batchResetSchoolPassword } from '@/api/schools';
import SchoolForm from './SchoolForm';

const DEFAULT_PASSWORD = 'Admin@123';

const statusColorMap: Record<string, string> = {
  pending: 'orange',
  active: 'green',
  rejected: 'red',
  disabled: 'default',
};

const statusTextMap: Record<string, string> = {
  pending: '待审批',
  active: '已审批',
  rejected: '已拒绝',
  disabled: '已禁用',
};

export default function SchoolManage() {
  const [formOpen, setFormOpen] = useState(false);
  const [editData, setEditData] = useState<any>(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const actionRef = useRef<ActionType>(null);
  const { message } = App.useApp();

  const [resetModalOpen, setResetModalOpen] = useState(false);
  const [resetTarget, setResetTarget] = useState<{ type: 'single' | 'batch'; id?: string; count?: number }>({ type: 'single' });
  const [resetForm] = Form.useForm();

  const openResetModal = (type: 'single' | 'batch', id?: string, count?: number) => {
    setResetTarget({ type, id, count });
    resetForm.resetFields();
    resetForm.setFieldsValue({ passwordType: 'default' });
    setResetModalOpen(true);
  };

  const handleResetConfirm = async () => {
    try {
      const values = await resetForm.validateFields();
      const customPwd = values.passwordType === 'custom' ? values.customPassword : undefined;
      if (resetTarget.type === 'single' && resetTarget.id) {
        const res = await resetSchoolPassword(resetTarget.id, customPwd);
        message.success((res as any)?.message || '密码重置成功');
      } else if (resetTarget.type === 'batch') {
        const res = await batchResetSchoolPassword(selectedRowKeys as string[], customPwd);
        message.success((res as any)?.message || '批量重置成功');
        setSelectedRowKeys([]);
        actionRef.current?.reload();
      }
      setResetModalOpen(false);
    } catch (e: any) {
      if (e?.response?.data?.detail) {
        message.error(e.response.data.detail);
      }
    }
  };

  const columns: ProColumns<any>[] = [
    { title: '学校名称', dataIndex: 'name', width: 200, ellipsis: true },
    { title: '学校编码', dataIndex: 'code', width: 120 },
    {
      title: '学校类型',
      dataIndex: 'school_type',
      width: 120,
      search: false,
      valueEnum: {
        primary: { text: '小学' },
        middle: { text: '初中' },
        high: { text: '高中' },
        nine_year: { text: '九年一贯制' },
        complete: { text: '完全中学' },
      },
    },
    { title: '省份', dataIndex: 'province', width: 80, search: false },
    { title: '城市', dataIndex: 'city', width: 80, search: false },
    { title: '区县', dataIndex: 'district', width: 80, search: false },
    { title: '详细地址', dataIndex: 'address', width: 150, search: false, ellipsis: true },
    { title: '联系人', dataIndex: 'contact_person', width: 100, search: false },
    { title: '联系电话', dataIndex: 'contact_phone', width: 130, search: false },
    { title: '管理员账号', dataIndex: 'admin_username', width: 120, search: false },
    {
      title: '管理员状态',
      dataIndex: 'admin_is_active',
      width: 100,
      search: false,
      render: (_, record) => (
        <Tag color={record.admin_is_active ? 'success' : 'default'}>
          {record.admin_is_active ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '学校状态',
      dataIndex: 'status',
      width: 100,
      valueEnum: {
        pending: { text: '待审批', status: 'Warning' },
        active: { text: '已审批', status: 'Success' },
        rejected: { text: '已拒绝', status: 'Error' },
        disabled: { text: '已禁用', status: 'Default' },
      },
      render: (_, record) => (
        <Tag color={statusColorMap[record.status]}>{statusTextMap[record.status]}</Tag>
      ),
    },
    { title: '用户数', dataIndex: 'user_count', width: 80, search: false },
    {
      title: '操作',
      valueType: 'option',
      width: 260,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => {
              setEditData(record);
              setFormOpen(true);
            }}
          >
            编辑
          </Button>
          {record.status === 'pending' && (
            <Popconfirm
              title="确定审批通过该学校吗？"
              onConfirm={async () => {
                try {
                  await approveSchool(record.id);
                  message.success('审批成功');
                  actionRef.current?.reload();
                } catch {
                  message.error('审批失败');
                }
              }}
            >
              <Button type="link" size="small" icon={<CheckOutlined />}>
                审批
              </Button>
            </Popconfirm>
          )}
          <Button
            type="link"
            size="small"
            icon={<KeyOutlined />}
            onClick={() => openResetModal('single', record.id)}
          >
            重置密码
          </Button>
          <Popconfirm
            title="确定删除该学校吗？"
            onConfirm={async () => {
              try {
                await deleteSchool(record.id);
                message.success('删除成功');
                actionRef.current?.reload();
              } catch {
                message.error('删除失败');
              }
            }}
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const handleBatchResetPassword = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择需要重置密码的学校');
      return;
    }
    openResetModal('batch', undefined, selectedRowKeys.length);
  };

  return (
    <Card title="学校管理">
      <ProTable<any>
        columns={columns}
        actionRef={actionRef}
        rowSelection={{
          selectedRowKeys,
          onChange: setSelectedRowKeys,
        }}
        request={async (params) => {
          const result = await getSchools({
            page: params.current || 1,
            page_size: params.pageSize || 10,
            name: params.name,
            code: params.code,
            status: params.status,
          });
          return {
            data: result.items,
            total: result.total,
            success: true,
          };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto', defaultCollapsed: true }}
        scroll={{ x: 1400 }}
        toolBarRender={() => [
          <Button
            key="add"
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setEditData(null);
              setFormOpen(true);
            }}
          >
            新增学校
          </Button>,
          <Button
            key="batch-reset"
            danger
            icon={<ReloadOutlined />}
            disabled={selectedRowKeys.length === 0}
            onClick={handleBatchResetPassword}
          >
            批量重置密码 {selectedRowKeys.length > 0 ? `(${selectedRowKeys.length})` : ''}
          </Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
      />
      <SchoolForm
        open={formOpen}
        editData={editData}
        onClose={() => {
          setFormOpen(false);
          setEditData(null);
        }}
        onSuccess={() => actionRef.current?.reload()}
      />
      <Modal
        title={resetTarget.type === 'single' ? '重置管理员密码' : `批量重置密码（${resetTarget.count} 个学校）`}
        open={resetModalOpen}
        onCancel={() => setResetModalOpen(false)}
        onOk={handleResetConfirm}
        okText="确定重置"
        okButtonProps={{ danger: true }}
        destroyOnClose
        width={460}
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
                <>
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
                  <Form.Item
                    name="confirmPassword"
                    label="确认密码"
                    dependencies={['customPassword']}
                    rules={[
                      { required: true, message: '请确认新密码' },
                      ({ getFieldValue }) => ({
                        validator(_, value) {
                          if (!value || getFieldValue('customPassword') === value) {
                            return Promise.resolve();
                          }
                          return Promise.reject(new Error('两次输入的密码不一致'));
                        },
                      }),
                    ]}
                  >
                    <Input.Password placeholder="请再次输入新密码" />
                  </Form.Item>
                </>
              ) : null
            }
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
