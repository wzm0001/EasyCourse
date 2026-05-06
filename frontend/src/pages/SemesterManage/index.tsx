import { Card, Button, Space, App, Popconfirm, Modal, Form, Input, DatePicker } from 'antd';
import { PlusOutlined, EditOutlined, CopyOutlined, CheckCircleOutlined, InboxOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { useState, useRef } from 'react';
import dayjs from 'dayjs';
import { useResponsive } from '@/hooks/useResponsive';
import {
  getSemesters,
  createSemester,
  updateSemester,
  activateSemester,
  archiveSemester,
  copySemester,
} from '@/api/semesters';

const { RangePicker } = DatePicker;

export default function SemesterManage() {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const [formOpen, setFormOpen] = useState(false);
  const [editData, setEditData] = useState<any>(null);
  const [copyOpen, setCopyOpen] = useState(false);
  const [copyId, setCopyId] = useState('');
  const [copyForm] = Form.useForm();
  const [form] = Form.useForm();
  const actionRef = useRef<ActionType>(null);

  const columns: ProColumns<any>[] = [
    { title: '学期名称', dataIndex: 'name', width: 200, ellipsis: true },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      valueEnum: {
        not_started: { text: '未开始', status: 'Default' },
        in_progress: { text: '进行中', status: 'Processing' },
        finished: { text: '已结束', status: 'Warning' },
        archived: { text: '已归档', status: 'Default' },
      },
    },
    { title: '开始日期', dataIndex: 'start_date', width: 120, valueType: 'date', search: false },
    { title: '结束日期', dataIndex: 'end_date', width: 120, valueType: 'date', search: false },
    { title: '创建时间', dataIndex: 'created_at', width: 180, valueType: 'dateTime', search: false },
    {
      title: '操作',
      valueType: 'option',
      width: 280,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
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
          {record.status !== 'in_progress' && (
            <Popconfirm
              title="确定激活该学期吗？"
              onConfirm={async () => {
                try {
                  await activateSemester(record.id);
                  message.success('激活成功');
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
          {record.status === 'finished' && (
            <Popconfirm
              title="确定归档该学期吗？"
              onConfirm={async () => {
                try {
                  await archiveSemester(record.id);
                  message.success('归档成功');
                  actionRef.current?.reload();
                } catch {
                  message.error('归档失败');
                }
              }}
            >
              <Button type="link" size="small" icon={<InboxOutlined />}>
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
        </Space>
      ),
    },
  ];

  return (
    <Card title="学期管理">
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
        <Form form={form} layout="vertical" preserve={false}>
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
        <Form form={copyForm} layout="vertical" preserve={false}>
          <Form.Item name="name" label="新学期名称" rules={[{ required: true, message: '请输入学期名称' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="date_range" label="新学期时间" rules={[{ required: true, message: '请选择学期时间' }]}>
            <RangePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
