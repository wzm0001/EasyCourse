import { useRef, useState, useEffect } from 'react';
import { Button, Space, Popconfirm, Modal, Form, Input, Transfer, Tag, App } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { getTeachers, createTeacher, updateTeacher, deleteTeacher, getTeacherCourses, setTeacherCourses, getCourses } from '@/api/basicData';
import { useResponsive } from '@/hooks/useResponsive';
import { useAppStore } from '@/store/app';
import TeacherForm from '@/components/TeacherForm';

export default function TeacherTab() {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const actionRef = useRef<ActionType>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editData, setEditData] = useState<any>(null);
  const [courseOpen, setCourseOpen] = useState(false);
  const [teacherId, setTeacherId] = useState('');
  const [allCourses, setAllCourses] = useState<any[]>([]);
  const [selectedCourseKeys, setSelectedCourseKeys] = useState<string[]>([]);
  const [form] = Form.useForm();
  const currentSemester = useAppStore((s) => s.currentSemester);

  useEffect(() => {
    actionRef.current?.reload();
  }, [currentSemester]);

  useEffect(() => {
    getCourses({ page: 1, page_size: 200 }).then((res) => setAllCourses(res.items || []));
  }, []);

  const openCourseAssign = async (record: any) => {
    setTeacherId(record.id);
    try {
      const res = await getTeacherCourses(record.id);
      const ids = (res.data || []).map((c: any) => c.course_id);
      setSelectedCourseKeys(ids);
    } catch {
      setSelectedCourseKeys([]);
    }
    setCourseOpen(true);
  };

  const columns: ProColumns<any>[] = [
    { title: '教师姓名', dataIndex: 'name', width: 120 },
    { title: '工号', dataIndex: 'employee_id', width: 100, search: false },
    { title: '教研组', dataIndex: 'teaching_group', width: 100, search: false },
    { title: '专业', dataIndex: 'specialization', width: 120, search: false },
    {
      title: '任教课程',
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
          <Popconfirm
            title="确定删除该教师吗？"
            description="删除教师将同时清除该教师的所有关联数据，包括教学安排、排课记录、课程分配和登录账号，此操作不可恢复。"
            onConfirm={async () => { try { await deleteTeacher(record.id); message.success('删除成功'); actionRef.current?.reload(); } catch { message.error('删除失败'); } }}
            okButtonProps={{ danger: true }}
          >
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
          const result = await getTeachers({ page: params.current || 1, page_size: params.pageSize || 10, name: params.name, semester_id: currentSemester || undefined });
          return { data: result.items, total: result.total, success: true };
        }}
        rowKey="id"
        search={{ labelWidth: 'auto' }}
        toolBarRender={() => [
          <Button key="add" type="primary" icon={<PlusOutlined />} onClick={() => { setEditData(null); form.resetFields(); setFormOpen(true); }}>新增教师</Button>,
        ]}
        pagination={{ defaultPageSize: 10 }}
      />
      <Modal
        title={editData ? '编辑教师' : '新增教师'}
        open={formOpen}
        onCancel={() => { setFormOpen(false); setEditData(null); }}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            if (editData) { await updateTeacher(editData.id, values); message.success('更新成功'); }
            else { await createTeacher(values, currentSemester || undefined); message.success('创建成功'); }
            actionRef.current?.reload(); setFormOpen(false); setEditData(null);
          } catch { message.error('操作失败'); }
        }}
        destroyOnHidden
        width={isMobile ? '90vw' : 520}
      >
        <TeacherForm form={form} showPasswordHint={!editData} />
      </Modal>
      <Modal
        title="分配课程"
        open={courseOpen}
        onCancel={() => setCourseOpen(false)}
        onOk={async () => {
          try {
            await setTeacherCourses(teacherId, { course_ids: selectedCourseKeys });
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
