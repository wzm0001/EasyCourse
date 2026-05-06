import { useRef } from 'react';
import { Card, Button, message } from 'antd';
import { ExportOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { getLogs, exportLogs } from '@/api/logs';

export default function LogManage() {
  const actionRef = useRef<ActionType>(null);

  const columns: ProColumns<any>[] = [
    { title: '时间', dataIndex: 'created_at', width: 180, valueType: 'dateTime' },
    { title: '操作人', dataIndex: 'username', width: 120 },
    {
      title: '操作类型',
      dataIndex: 'action',
      width: 120,
      valueEnum: {
        login: { text: '登录' },
        create: { text: '创建' },
        update: { text: '更新' },
        delete: { text: '删除' },
        export: { text: '导出' },
        import: { text: '导入' },
        schedule: { text: '排课' },
      },
    },
    { title: '模块', dataIndex: 'module', width: 120, search: false },
    { title: '描述', dataIndex: 'description', width: 300, ellipsis: true, search: false },
    { title: 'IP地址', dataIndex: 'ip_address', width: 130, search: false },
  ];

  return (
    <Card
      title="日志管理"
      extra={
        <Button
          icon={<ExportOutlined />}
          onClick={async () => {
            try {
              await exportLogs({});
              message.success('导出成功');
            } catch {
              message.error('导出失败');
            }
          }}
        >
          导出日志
        </Button>
      }
    >
      <ProTable<any>
        columns={columns}
        actionRef={actionRef}
        request={async (params) => {
          const result = await getLogs({
            page: params.current || 1,
            page_size: params.pageSize || 10,
            username: params.username,
            action: params.action,
          });
          return { data: result.items, total: result.total, success: true };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto', defaultCollapsed: true }}
        scroll={{ x: 900 }}
        pagination={{ defaultPageSize: 10 }}
      />
    </Card>
  );
}
