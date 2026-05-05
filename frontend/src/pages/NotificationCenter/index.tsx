import { useRef, useState } from 'react';
import { Card, Button, Space, message } from 'antd';
import { CheckOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { getNotifications, markAsRead, markAllAsRead } from '@/api/notifications';

export default function NotificationCenter() {
  const actionRef = useRef<ActionType>(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);

  const columns: ProColumns<any>[] = [
    {
      title: '状态',
      dataIndex: 'is_read',
      width: 80,
      valueEnum: {
        true: { text: '已读', status: 'Default' },
        false: { text: '未读', status: 'Processing' },
      },
    },
    { title: '标题', dataIndex: 'title', width: 200, ellipsis: true },
    { title: '内容', dataIndex: 'content', width: 300, ellipsis: true, search: false },
    {
      title: '类型',
      dataIndex: 'type',
      width: 100,
      valueEnum: {
        system: { text: '系统通知' },
        schedule: { text: '排课通知' },
        approval: { text: '审批通知' },
      },
    },
    { title: '时间', dataIndex: 'created_at', width: 180, valueType: 'dateTime', search: false },
    {
      title: '操作',
      valueType: 'option',
      width: 100,
      render: (_, record) => (
        <Space>
          {!record.is_read && (
            <Button
              type="link"
              size="small"
              icon={<CheckOutlined />}
              onClick={async () => {
                try {
                  await markAsRead(record.id);
                  message.success('已标记为已读');
                  actionRef.current?.reload();
                } catch {
                  message.error('操作失败');
                }
              }}
            >
              标记已读
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <Card
      title="通知中心"
      extra={
        <Button
          icon={<CheckCircleOutlined />}
          onClick={async () => {
            try {
              await markAllAsRead();
              message.success('已全部标记为已读');
              actionRef.current?.reload();
            } catch {
              message.error('操作失败');
            }
          }}
        >
          全部已读
        </Button>
      }
    >
      <ProTable<any>
        columns={columns}
        actionRef={actionRef}
        request={async (params) => {
          const result = await getNotifications({
            page: params.current || 1,
            page_size: params.pageSize || 10,
            is_read: params.is_read,
            type: params.type,
          });
          return { data: result.items, total: result.total, success: true };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto' }}
        pagination={{ defaultPageSize: 10 }}
        rowSelection={{
          selectedRowKeys,
          onChange: (keys) => setSelectedRowKeys(keys as string[]),
        }}
      />
    </Card>
  );
}
