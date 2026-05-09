import { Card, Button, Space, App, Popconfirm, Modal, Form, Input, DatePicker, Tag, Tooltip } from 'antd';
import { PlusOutlined, EditOutlined, CopyOutlined, CheckCircleOutlined, InboxOutlined, RollbackOutlined, LockOutlined, DeleteOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { useState, useRef } from 'react';
import dayjs from 'dayjs';
import { useResponsive } from '@/hooks/useResponsive';
import { useAppStore } from '@/store/app';
import {
  getSemesters,
  createSemester,
  updateSemester,
  activateSemester,
  archiveSemester,
  unarchiveSemester,
  copySemester,
  deleteSemester,
} from '@/api/semesters';

const { RangePicker } = DatePicker;

export default function SemesterManage({ embedded }: { embedded?: boolean } = {}) {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const [formOpen, setFormOpen] = useState(false);
  const [editData, setEditData] = useState<any>(null);
  const [copyOpen, setCopyOpen] = useState(false);
  const [copyId, setCopyId] = useState('');
  const [copyForm] = Form.useForm();
  const [form] = Form.useForm();
  const actionRef = useRef<ActionType>(null);
  const fetchActiveSemester = useAppStore((s) => s.fetchActiveSemester);

  const columns: ProColumns<any>[] = [
    { title: '学期名称', dataIndex: 'name', width: 200, ellipsis: true },
    {
      title: '状态',
      dataIndex: 'status',
      width: 120,
      valueEnum: {
        not_started: { text: '未开始', status: 'Default' },
        in_progress: { text: '进行中', status: 'Processing' },
        finished: { text: '已结束', status: 'Warning' },
        archived: { text: '已归档', status: 'Default' },
      },
      render: (_, record) => {
        const statusMap: Record<string, { color: string; text: string; icon?: React.ReactNode }> = {
          not_started: { color: 'default', text: '未开始' },
          in_progress: { color: 'processing', text: '进行中', icon: <CheckCircleOutlined /> },
          finished: { color: 'warning', text: '已结束' },
          archived: { color: 'red', text: '已归档', icon: <LockOutlined /> },
        };
        const s = statusMap[record.status] || statusMap.not_started;
        return <Tag color={s.color} icon={s.icon}>{s.text}</Tag>;
      },
    },
    { title: '开始日期', dataIndex: 'start_date', width: 120, valueType: 'date', search: false },
    { title: '结束日期', dataIndex: 'end_date', width: 120, valueType: 'date', search: false },
    { title: '创建时间', dataIndex: 'created_at', width: 180, valueType: 'dateTime', search: false },
    {
      title: '操作',
      valueType: 'option',
      width: 320,
      render: (_, record) => {
        const isArchived = record.status === 'archived';
        return (
          <Space>
            <Tooltip title={isArchived ? '已归档学期无法编辑' : ''}>
              <Button
                type="link"
                size="small"
                icon={<EditOutlined />}
                disabled={isArchived}
                onClick={() => {
                  setEditData(record);
                  form.setFieldsValue({
                    ...record,
                    date_range: [dayjs(record.start_date), dayjs(record.end_date)],
                  });
                  setFormOpen(true);
                }}
              >
                编辑
              </Button>
            </Tooltip>
            {record.status !== 'in_progress' && !isArchived && (
              <Popconfirm
                title="确定激活该学期吗？激活后该学期将成为当前工作学期。"
                onConfirm={async () => {
                  try {
                    await activateSemester(record.id);
                    message.success('激活成功');
                    fetchActiveSemester();
                    actionRef.current?.reload();
                  } catch {
                    message.error('激活失败');
                  }
                }}
              >
                <Button type="link" size="small" icon={<CheckCircleOutlined />}>
                  激活
                </Button>
              </Popconfirm>
            )}
            {isArchived && (
              <Popconfirm
                title="确定取消归档该学期吗？取消归档后可以重新编辑和激活该学期。"
                onConfirm={async () => {
                  try {
                    await unarchiveSemester(record.id);
                    message.success('取消归档成功');
                    fetchActiveSemester();
                    actionRef.current?.reload();
                  } catch {
                    message.error('取消归档失败');
                  }
                }}
              >
                <Button type="link" size="small" icon={<RollbackOutlined />}>
                  取消归档
                </Button>
              </Popconfirm>
            )}
            {!isArchived && record.status !== 'in_progress' && (
              <Popconfirm
                title="确定归档该学期吗？归档后该学期的所有数据将无法修改。"
                onConfirm={async () => {
                  try {
                    await archiveSemester(record.id);
                    message.success('归档成功');
                    fetchActiveSemester();
                    actionRef.current?.reload();
                  } catch {
                    message.error('归档失败');
                  }
                }}
              >
                <Button type="link" size="small" icon={<InboxOutlined />} danger>
                  归档
                </Button>
              </Popconfirm>
            )}
            <Button
              type="link"
              size="small"
              icon={<CopyOutlined />}
              onClick={() => {
                setCopyId(record.id);
                copyForm.resetFields();
                setCopyOpen(true);
              }}
            >
              复制
            </Button>
            {record.status !== 'in_progress' && (
              <Popconfirm
                title="删除学期"
                description="确定删除该学期吗？删除后该学期的所有数据（年级、班级、教师、教室、教学安排、课表等）将被永久删除，无法恢复！"
                onConfirm={async () => {
                  try {
                    await deleteSemester(record.id);
                    message.success('删除成功');
                    fetchActiveSemester();
                    actionRef.current?.reload();
                  } catch {
                    message.error('删除失败');
                  }
                }}
              >
                <Button type="link" size="small" icon={<DeleteOutlined />} danger>
                  删除
                </Button>
              </Popconfirm>
            )}
          </Space>
        );
      },
    },
  ];

  const content = (
    <>
      <ProTable<any>
        columns={columns}
        actionRef={actionRef}
        request={async (params) => {
          const result = await getSemesters({
            page: params.current || 1,
            page_size: params.pageSize || 10,
            name: params.name,
            status: params.status,
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
            新增学期
          </Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
        scroll={{ x: isMobile ? 600 : 800 }}
      />
      <Modal
        title={editData ? '编辑学期' : '新增学期'}
        open={formOpen}
        width={isMobile ? '90vw' : 520}
        onCancel={() => {
          setFormOpen(false);
          setEditData(null);
        }}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            const payload = {
              ...values,
              start_date: values.date_range[0].format('YYYY-MM-DD'),
              end_date: values.date_range[1].format('YYYY-MM-DD'),
            };
            if (editData) {
              await updateSemester(editData.id, payload);
              message.success('更新成功');
            } else {
              await createSemester(payload);
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
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="学期名称" rules={[{ required: true, message: '请输入学期名称' }]}>
            <Input placeholder="如：2025-2026学年第一学期" />
          </Form.Item>
          <Form.Item name="date_range" label="学期时间" rules={[{ required: true, message: '请选择学期时间' }]}>
            <RangePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
      <Modal
        title="复制学期"
        open={copyOpen}
        width={isMobile ? '90vw' : 520}
        onCancel={() => setCopyOpen(false)}
        onOk={async () => {
          try {
            const values = await copyForm.validateFields();
            await copySemester(copyId, {
              name: values.name,
              start_date: values.date_range[0].format('YYYY-MM-DD'),
              end_date: values.date_range[1].format('YYYY-MM-DD'),
            });
            message.success('复制成功');
            setCopyOpen(false);
            actionRef.current?.reload();
          } catch {
            message.error('复制失败');
          }
        }}
        destroyOnHidden
      >
        <Form form={copyForm} layout="vertical">
          <Form.Item name="name" label="新学期名称" rules={[{ required: true, message: '请输入学期名称' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="date_range" label="新学期时间" rules={[{ required: true, message: '请选择学期时间' }]}>
            <RangePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );

  return embedded ? content : <Card title="学期管理">{content}</Card>;
}
