import { useRef, useState, useEffect } from 'react';
import { Button, Space, Popconfirm, Modal, Form, Input, Select, Tag, App } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, LinkOutlined, UserOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { getClasses, createClass, updateClass, deleteClass, getGrades, getClassrooms, getTeachers } from '@/api/basicData';
import { useResponsive } from '@/hooks/useResponsive';
import { useAppStore } from '@/store/app';

export default function ClassTab() {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const actionRef = useRef<ActionType>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editData, setEditData] = useState<any>(null);
  const [grades, setGrades] = useState<any[]>([]);
  const [classrooms, setClassrooms] = useState<any[]>([]);
  const [teachers, setTeachers] = useState<any[]>([]);
  const [form] = Form.useForm();
  const currentSemester = useAppStore((s) => s.currentSemester);

  useEffect(() => {
    getGrades({ page: 1, page_size: 100, semester_id: currentSemester || undefined }).then((res) => setGrades(res.items || []));
    getClassrooms({ page: 1, page_size: 200, semester_id: currentSemester || undefined }).then((res) => setClassrooms(res.items || []));
    getTeachers({ page: 1, page_size: 200, semester_id: currentSemester || undefined }).then((res) => setTeachers(res.items || []));
    actionRef.current?.reload();
  }, [currentSemester]);

  const refreshClassrooms = () => {
    getClassrooms({ page: 1, page_size: 200, semester_id: currentSemester || undefined }).then((res) => setClassrooms(res.items || []));
  };

  const openForm = (record?: any) => {
    refreshClassrooms();
    if (record) {
      setEditData(record);
      form.setFieldsValue({
        ...record,
        head_teacher_id: record.head_teacher_id || undefined,
      });
    } else {
      setEditData(null);
      form.resetFields();
    }
    setFormOpen(true);
  };
  const columns: ProColumns<any>[] = [
    { title: '班级名称', dataIndex: 'name', width: 150 },
    { title: '所属年级', dataIndex: 'grade_name', width: 100 },
    {
      title: '班主任',
      dataIndex: 'head_teacher_name',
      width: 100,
      search: false,
      render: (_, record) => record.head_teacher_name
        ? <Tag color="green" icon={<UserOutlined />}>{record.head_teacher_name}</Tag>
        : <Tag color="default">未设置</Tag>,
    },
    {
      title: '绑定教室',
      dataIndex: 'classroom_name',
      width: 180,
      search: false,
      render: (_, record) => record.classroom_name
        ? <Tag color="blue" icon={<LinkOutlined />}>{record.classroom_name}</Tag>
        : <Tag color="red">未绑定</Tag>,
    },
    {
      title: '操作',
      valueType: 'option',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => openForm(record)}>编辑</Button>
          <Popconfirm title="确定删除吗？" onConfirm={async () => { try { await deleteClass(record.id); message.success('删除成功'); actionRef.current?.reload(); } catch { message.error('删除失败'); } }}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <>
      <ProTable<any>
        columns={columns}
        actionRef={actionRef}
        request={async (params) => {
          const result = await getClasses({ page: params.current || 1, page_size: params.pageSize || 10, name: params.name, grade_id: params.grade_id, semester_id: currentSemester || undefined });
          return { data: result.items, total: result.total, success: true };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto' }}
        toolBarRender={() => [
          <Button key="add" type="primary" icon={<PlusOutlined />} onClick={() => openForm()}>新增班级</Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
      />
      <Modal
        title={editData ? '编辑班级' : '新增班级'}
        open={formOpen}
        onCancel={() => { setFormOpen(false); setEditData(null); }}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            if (editData) { await updateClass(editData.id, values); message.success('更新成功'); }
            else { await createClass(values, currentSemester || undefined); message.success('创建成功'); }
            actionRef.current?.reload(); setFormOpen(false); setEditData(null);
          } catch { message.error('操作失败'); }
        }}
        destroyOnHidden
        width={isMobile ? '90vw' : 520}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="班级名称" rules={[{ required: true, message: '请输入班级名称' }]}>
            <Input placeholder="如：高一(1)班" />
          </Form.Item>
          <Form.Item name="grade_id" label="所属年级" rules={[{ required: true, message: '请选择年级' }]}>
            <Select options={grades.map((g) => ({ label: g.name, value: g.id }))} placeholder="请选择年级" />
          </Form.Item>
          <Form.Item name="head_teacher_id" label="班主任" extra="选择该班级的班主任">
            <Select
              showSearch
              allowClear
              options={teachers.map((t) => ({ label: t.name, value: t.id }))}
              placeholder="请选择班主任"
              filterOption={(input, option) => (option?.label ?? '').includes(input)}
            />
          </Form.Item>
          <Form.Item name="classroom_id" label="绑定教室" rules={[{ required: true, message: '请选择教室' }]} extra="班级教室所在位置，排课时默认使用该教室">
            <Select
              options={classrooms.map((c) => ({ label: `${c.building_name} ${c.room_number}${c.capacity ? ` (容量:${c.capacity})` : ''}`, value: c.id }))}
              placeholder="请选择教室"
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
