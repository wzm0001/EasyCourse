import { useRef, useState, useEffect } from 'react';
import { Button, Space, Popconfirm, Modal, Form, Input, InputNumber, Select, Transfer, Tag, App } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { getClassrooms, createClassroom, updateClassroom, deleteClassroom, getClassroomCourses, setClassroomCourses, getCourses } from '@/api/basicData';
import { useResponsive } from '@/hooks/useResponsive';

export default function ClassroomTab() {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const actionRef = useRef<ActionType>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editData, setEditData] = useState<any>(null);
  const [courseOpen, setCourseOpen] = useState(false);
  const [classroomId, setClassroomId] = useState('');
  const [allCourses, setAllCourses] = useState<any[]>([]);
  const [selectedCourseKeys, setSelectedCourseKeys] = useState<string[]>([]);
  const [form] = Form.useForm();

  useEffect(() => {
    getCourses({ page: 1, page_size: 200 }).then((res) => setAllCourses(res.items || []));
  }, []);

  const openCourseAssign = async (record: any) => {
    setClassroomId(record.id);
    try {
      const res = await getClassroomCourses(record.id);
      const ids = (res.data || []).map((c: any) => c.id || c.course_id);
      setSelectedCourseKeys(ids);
    } catch {
      setSelectedCourseKeys([]);
    }
    setCourseOpen(true);
  };

  const columns: ProColumns<any>[] = [
    { title: '教室名称', dataIndex: 'name', width: 180 },
    { title: '教室编码', dataIndex: 'code', width: 120 },
    {
      title: '教室类型',
      dataIndex: 'type',
      width: 100,
      valueEnum: {
        normal: { text: '普通教室' },
        lab: { text: '实验室' },
        computer: { text: '机房' },
        music: { text: '音乐教室' },
        art: { text: '美术教室' },
        gym: { text: '体育馆' },
      },
    },
    { title: '容量', dataIndex: 'capacity', width: 80, search: false },
    {
      title: '可用课程',
      dataIndex: 'course_names',
      width: 200,
      search: false,
      render: (_, record) => {
        const names = record.course_names;
        if (!Array.isArray(names)) return null;
        return names.map((c: string) => <Tag key={c}>{c}</Tag>);
      },
    },
    {
      title: '操作',
      valueType: 'option',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => { setEditData(record); form.setFieldsValue(record); setFormOpen(true); }}>编辑</Button>
          <Button type="link" size="small" onClick={() => openCourseAssign(record)}>分配课程</Button>
          <Popconfirm title="确定删除吗？" onConfirm={async () => { try { await deleteClassroom(record.id); message.success('删除成功'); actionRef.current?.reload(); } catch { message.error('删除失败'); } }}>
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
          const result = await getClassrooms({ page: params.current || 1, page_size: params.pageSize || 10, name: params.name, type: params.type });
          return { data: result.items, total: result.total, success: true };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto' }}
        toolBarRender={() => [
          <Button key="add" type="primary" icon={<PlusOutlined />} onClick={() => { setEditData(null); form.resetFields(); setFormOpen(true); }}>新增教室</Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
      />
      <Modal
        title={editData ? '编辑教室' : '新增教室'}
        open={formOpen}
        onCancel={() => { setFormOpen(false); setEditData(null); }}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            if (editData) { await updateClassroom(editData.id, values); message.success('更新成功'); }
            else { await createClassroom(values); message.success('创建成功'); }
            actionRef.current?.reload(); setFormOpen(false); setEditData(null);
          } catch { message.error('操作失败'); }
        }}
        destroyOnHidden
        width={isMobile ? '90vw' : 520}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="教室名称" rules={[{ required: true, message: '请输入教室名称' }]}><Input /></Form.Item>
          <Form.Item name="code" label="教室编码" rules={[{ required: true, message: '请输入教室编码' }]}><Input /></Form.Item>
          <Form.Item name="type" label="教室类型" rules={[{ required: true, message: '请选择教室类型' }]}>
            <Select options={[{ label: '普通教室', value: 'normal' }, { label: '实验室', value: 'lab' }, { label: '机房', value: 'computer' }, { label: '音乐教室', value: 'music' }, { label: '美术教室', value: 'art' }, { label: '体育馆', value: 'gym' }]} />
          </Form.Item>
          <Form.Item name="capacity" label="容量"><InputNumber min={1} max={500} style={{ width: '100%' }} /></Form.Item>
        </Form>
      </Modal>
      <Modal
        title="分配课程"
        open={courseOpen}
        onCancel={() => setCourseOpen(false)}
        onOk={async () => {
          try {
            await setClassroomCourses(classroomId, { course_ids: selectedCourseKeys });
            message.success('分配成功');
            setCourseOpen(false);
            actionRef.current?.reload();
          } catch { message.error('分配失败'); }
        }}
        width={isMobile ? '90vw' : 600}
      >
        <Transfer
          dataSource={allCourses.map((c) => ({ key: c.id, title: c.name }))}
          targetKeys={selectedCourseKeys}
          onChange={(targetKeys) => setSelectedCourseKeys(targetKeys as string[])}
          render={(item) => item.title}
          titles={['可选课程', '已选课程']}
          listStyle={{ width: 250, height: 400 }}
        />
      </Modal>
    </>
  );
}
