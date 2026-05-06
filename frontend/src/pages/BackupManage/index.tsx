import { useRef, useState } from 'react';
import { Card, Button, Space, App, Popconfirm, Modal, Form, Input } from 'antd';
import { PlusOutlined, DownloadOutlined, UndoOutlined, DeleteOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { getBackups, createBackup, restoreBackup, deleteBackup, downloadBackup } from '@/api/backups';
import { useResponsive } from '@/hooks/useResponsive';

export default function BackupManage() {
  const actionRef = useRef<ActionType>(null);
  const [remarkOpen, setRemarkOpen] = useState(false);
  const [form] = Form.useForm();
  const { message } = App.useApp();
  const { isMobile } = useResponsive();

  const columns: ProColumns<any>[] = [
    { title: '备份名称', dataIndex: 'name', width: 200 },
    { title: '大小', dataIndex: 'size', width: 100, search: false },
    { title: '备注', dataIndex: 'remark', width: 200, ellipsis: true, search: false },
    { title: '创建时间', dataIndex: 'created_at', width: 180, valueType: 'dateTime', search: false },
    {
      title: '操作',
      valueType: 'option',
      width: 250,
      render: (_, record) => (
        <Space>
          <Popconfirm
            title="确定还原到该备份吗？当前数据将被覆盖。"
            onConfirm={async () => {
              try {
                await restoreBackup(record.id);
                message.success('还原成功');
              } catch {
                message.error('还原失败');
              }
            }}
          >
            <Button type="link" size="small" icon={<UndoOutlined />}>还原</Button>
          </Popconfirm>
          <Button
            type="link"
            size="small"
            icon={<DownloadOutlined />}
            onClick={async () => {
              try {
                await downloadBackup(record.id);
                message.success('下载成功');
              } catch {
                message.error('下载失败');
              }
            }}
          >
            下载
          </Button>
          <Popconfirm
            title="确定删除该备份吗？"
            onConfirm={async () => {
              try {
                await deleteBackup(record.id);
                message.success('删除成功');
                actionRef.current?.reload();
              } catch {
                message.error('删除失败');
              }
            }}
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Card title="备份还原">
      <ProTable<any>
        columns={columns}
        actionRef={actionRef}
        request={async (params) => {
          const result = await getBackups({
            page: params.current || 1,
            page_size: params.pageSize || 10,
            name: params.name,
          });
          return { data: result.items, total: result.total, success: true };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto', defaultCollapsed: true }}
        scroll={{ x: isMobile ? 600 : 800 }}
        toolBarRender={() => [
          <Button
            key="add"
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => { form.resetFields(); setRemarkOpen(true); }}
          >
            创建备份
          </Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
      />
      <Modal
        title="创建备份"
        open={remarkOpen}
        style={{ top: 20 }}
        onCancel={() => setRemarkOpen(false)}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            await createBackup(values);
            message.success('备份创建成功');
            setRemarkOpen(false);
            actionRef.current?.reload();
          } catch {
            message.error('备份创建失败');
          }
        }}
        destroyOnHidden
        width={isMobile ? '90vw' : 520}
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item name="remark" label="备注">
            <Input.TextArea rows={3} placeholder="请输入备份备注" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
