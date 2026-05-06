import { Card, Button, Space, message, Modal, Input } from 'antd';
import { CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { useState, useRef } from 'react';
import { getPendingSchools, approveSchool, rejectSchool } from '@/api/schools';

export default function ApprovalManage() {
  const actionRef = useRef<ActionType>(null);
  const [rejectModal, setRejectModal] = useState<{ open: boolean; id: string }>({ open: false, id: '' });
  const [rejectReason, setRejectReason] = useState('');

  const columns: ProColumns<any>[] = [
    { title: '学校名称', dataIndex: 'name', width: 200, ellipsis: true },
    { title: '学校编码', dataIndex: 'code', width: 120 },
    {
      title: '学校类型',
      dataIndex: 'school_type',
      width: 120,
      valueEnum: {
        primary: { text: '小学' },
        middle: { text: '初中' },
        high: { text: '高中' },
        nine_year: { text: '九年一贯制' },
        complete: { text: '完全中学' },
      },
    },
    { title: '省份', dataIndex: 'province', width: 80 },
    { title: '城市', dataIndex: 'city', width: 80 },
    { title: '联系人', dataIndex: 'contact_person', width: 100 },
    { title: '联系电话', dataIndex: 'contact_phone', width: 130 },
    { title: '申请时间', dataIndex: 'created_at', width: 180, valueType: 'dateTime', search: false },
    {
      title: '操作',
      valueType: 'option',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<CheckOutlined />}
            onClick={async () => {
              try {
                await approveSchool(record.id);
                message.success('审批通过');
                actionRef.current?.reload();
              } catch {
                message.error('操作失败');
              }
            }}
          >
            通过
          </Button>
          <Button
            danger
            size="small"
            icon={<CloseOutlined />}
            onClick={() => {
              setRejectModal({ open: true, id: record.id });
              setRejectReason('');
            }}
          >
            拒绝
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Card title="审批管理">
      <ProTable<any>
        columns={columns}
        actionRef={actionRef}
        request={async (params) => {
          const result = await getPendingSchools({
            page: params.current || 1,
            page_size: params.pageSize || 10,
            name: params.name,
          });
          return {
            data: result.items,
            total: result.total,
            success: true,
          };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto', defaultCollapsed: true }}
        scroll={{ x: 1000 }}
        pagination={{ defaultPageSize: 10 }}
      />
      <Modal
        title="拒绝原因"
        open={rejectModal.open}
        style={{ top: 20 }}
        onCancel={() => setRejectModal({ open: false, id: '' })}
        onOk={async () => {
          try {
            await rejectSchool(rejectModal.id, rejectReason);
            message.success('已拒绝');
            setRejectModal({ open: false, id: '' });
            actionRef.current?.reload();
          } catch {
            message.error('操作失败');
          }
        }}
      >
        <Input.TextArea
          rows={4}
          value={rejectReason}
          onChange={(e) => setRejectReason(e.target.value)}
          placeholder="请输入拒绝原因"
        />
      </Modal>
    </Card>
  );
}
