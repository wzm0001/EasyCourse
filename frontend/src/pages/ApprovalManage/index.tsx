import { Card, Button, Space, message, Modal, Input, Descriptions, Tag } from 'antd';
import { CheckOutlined, CloseOutlined, PaperClipOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { useState, useRef } from 'react';
import { getPendingSchools, approveSchool, rejectSchool } from '@/api/schools';

export default function ApprovalManage() {
  const actionRef = useRef<ActionType>(null);
  const [rejectModal, setRejectModal] = useState<{ open: boolean; id: string }>({ open: false, id: '' });
  const [rejectReason, setRejectReason] = useState('');
  const [detailModal, setDetailModal] = useState<{ open: boolean; record: any }>({ open: false, record: {} });

  const schoolTypeMap: Record<string, string> = {
    primary: '小学',
    middle: '初中',
    high: '高中',
    nine_year: '九年一贯制',
    complete: '完全中学',
  };

  const columns: ProColumns<any>[] = [
    { title: '学校名称', dataIndex: 'name', width: 200, ellipsis: true },
    { title: '统一社会信用代码', dataIndex: 'code', width: 200 },
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
    { title: '联系人', dataIndex: 'contact_person', width: 100 },
    { title: '联系电话', dataIndex: 'contact_phone', width: 130 },
    {
      title: '附件',
      dataIndex: 'attachment',
      width: 80,
      search: false,
      render: (_, record) =>
        record.attachment ? (
          <a href={record.attachment} target="_blank" rel="noopener noreferrer">
            <PaperClipOutlined /> 查看
          </a>
        ) : '-',
    },
    { title: '申请时间', dataIndex: 'created_at', width: 180, valueType: 'dateTime', search: false },
    {
      title: '操作',
      valueType: 'option',
      width: 250,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" onClick={() => setDetailModal({ open: true, record })}>
            详情
          </Button>
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
        scroll={{ x: 1100 }}
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
      <Modal
        title="申请详情"
        open={detailModal.open}
        onCancel={() => setDetailModal({ open: false, record: {} })}
        footer={null}
        width={600}
      >
        <Descriptions column={2} bordered size="small">
          <Descriptions.Item label="学校名称">{detailModal.record.name}</Descriptions.Item>
          <Descriptions.Item label="统一社会信用代码">{detailModal.record.code}</Descriptions.Item>
          <Descriptions.Item label="学校类型">
            <Tag>{schoolTypeMap[detailModal.record.school_type] || detailModal.record.school_type}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="联系人">{detailModal.record.contact_person}</Descriptions.Item>
          <Descriptions.Item label="联系电话">{detailModal.record.contact_phone}</Descriptions.Item>
          <Descriptions.Item label="省份">{detailModal.record.province || '-'}</Descriptions.Item>
          <Descriptions.Item label="城市">{detailModal.record.city || '-'}</Descriptions.Item>
          <Descriptions.Item label="区县">{detailModal.record.district || '-'}</Descriptions.Item>
          <Descriptions.Item label="详细地址" span={2}>{detailModal.record.address || '-'}</Descriptions.Item>
          <Descriptions.Item label="附件" span={2}>
            {detailModal.record.attachment ? (
              <a href={detailModal.record.attachment} target="_blank" rel="noopener noreferrer">
                <PaperClipOutlined /> 查看附件
              </a>
            ) : '无'}
          </Descriptions.Item>
        </Descriptions>
      </Modal>
    </Card>
  );
}
