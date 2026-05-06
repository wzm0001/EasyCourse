import { Card, Button, Space, Tag, App, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CheckOutlined, KeyOutlined, ReloadOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { useState, useRef } from 'react';
import { getSchools, deleteSchool, approveSchool, resetSchoolPassword, batchResetSchoolPassword } from '@/api/schools';
import SchoolForm from './SchoolForm';

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
  const { message, modal } = App.useApp();

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
          <Popconfirm
            title="确定重置该学校管理员密码吗？"
            description="密码将重置为默认密码 Admin@123"
            onConfirm={async () => {
              try {
                const res = await resetSchoolPassword(record.id);
                message.success((res as any)?.message || '密码重置成功');
              } catch (e: any) {
                const detail = e?.response?.data?.detail || '密码重置失败';
                message.error(detail);
              }
            }}
          >
            <Button type="link" size="small" icon={<KeyOutlined />}>
              重置密码
            </Button>
          </Popconfirm>
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
    modal.confirm({
      title: '批量重置密码',
      content: `确定将选中的 ${selectedRowKeys.length} 个学校的管理员密码重置为默认密码 Admin@123 吗？`,
      okText: '确定重置',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          const res = await batchResetSchoolPassword(selectedRowKeys as string[]);
          message.success((res as any)?.message || '批量重置成功');
          setSelectedRowKeys([]);
          actionRef.current?.reload();
        } catch (e: any) {
          const detail = e?.response?.data?.detail || '批量重置失败';
          message.error(detail);
        }
      },
    });
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
        tableAlertOptionRender={() => (
          <Space size="middle">
            <Button
              type="primary"
              danger
              icon={<ReloadOutlined />}
              disabled={selectedRowKeys.length === 0}
              onClick={handleBatchResetPassword}
            >
              批量重置密码 {selectedRowKeys.length > 0 ? `(${selectedRowKeys.length})` : ''}
            </Button>
          </Space>
        )}
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
    </Card>
  );
}
