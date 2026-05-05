import { useRef, useState } from 'react';
import { Card, Button, Space, message, Popconfirm, Switch } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { getConstraints, createConstraint, updateConstraint, deleteConstraint, toggleConstraint } from '@/api/constraints';
import ConstraintForm from './ConstraintForm';

const typeLabels: Record<string, string> = {
  teacher_unavailable: '教师不可排课时段',
  class_unavailable: '班级不可排课时段',
  classroom_unavailable: '教室不可排课时段',
  course_continuous: '课程连排约束',
  course_scattered: '课程分散约束',
  teacher_max_daily: '教师每天最大课时',
  course_preferred_period: '课程优先时段',
  grade_exclusive: '年级互斥约束',
};

export default function ConstraintConfig() {
  const actionRef = useRef<ActionType>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editData, setEditData] = useState<any>(null);

  const columns: ProColumns<any>[] = [
    { title: '约束名称', dataIndex: 'name', width: 200, ellipsis: true },
    {
      title: '约束类型',
      dataIndex: 'type',
      width: 160,
      valueEnum: Object.fromEntries(Object.entries(typeLabels).map(([k, v]) => [k, { text: v }])),
    },
    { title: '优先级', dataIndex: 'priority', width: 80, search: false },
    {
      title: '状态',
      dataIndex: 'enabled',
      width: 80,
      search: false,
      render: (_, record) => (
        <Switch
          checked={record.enabled}
          size="small"
          onChange={async () => {
            try {
              await toggleConstraint(record.id);
              message.success('操作成功');
              actionRef.current?.reload();
            } catch {
              message.error('操作失败');
            }
          }}
        />
      ),
    },
    { title: '描述', dataIndex: 'description', width: 200, ellipsis: true, search: false },
    {
      title: '操作',
      valueType: 'option',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditData(record); setFormOpen(true); }}>编辑</Button>
          <Popconfirm title="确定删除吗？" onConfirm={async () => { try { await deleteConstraint(record.id); message.success('删除成功'); actionRef.current?.reload(); } catch { message.error('删除失败'); } }}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Card title="排课规则配置">
      <ProTable<any>
        columns={columns}
        actionRef={actionRef}
        request={async (params) => {
          const result = await getConstraints({ page: params.current || 1, page_size: params.pageSize || 10, name: params.name, type: params.type });
          return { data: result.items, total: result.total, success: true };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto' }}
        toolBarRender={() => [
          <Button key="add" type="primary" icon={<PlusOutlined />} onClick={() => { setEditData(null); setFormOpen(true); }}>新增约束</Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
      />
      <ConstraintForm
        open={formOpen}
        editData={editData}
        onClose={() => { setFormOpen(false); setEditData(null); }}
        onOk={async (values) => {
          try {
            if (editData) {
              await updateConstraint(editData.id, values);
              message.success('更新成功');
            } else {
              await createConstraint(values);
              message.success('创建成功');
            }
            actionRef.current?.reload();
            setFormOpen(false);
            setEditData(null);
          } catch { message.error('操作失败'); }
        }}
      />
    </Card>
  );
}
