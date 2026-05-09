import { useDrag } from 'react-dnd';
import { Card, Input, Tag, Button, Modal, Form, App, Collapse } from 'antd';
import { UserOutlined, PlusOutlined, BookOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { createTeacher } from '@/api/basicData';
import { useAppStore } from '@/store/app';
import TeacherForm from '@/components/TeacherForm';

interface TeacherPanelProps {
  teachers: any[];
  selectedClassId?: string;
  onRefresh: () => void;
}

function TeacherItem({ teacher, selectedClassId }: { teacher: any; selectedClassId?: string }) {
  const arrangements = teacher.arrangements || [];
  const classArrangements = selectedClassId
    ? arrangements.filter((a: any) => a.class_id === selectedClassId)
    : arrangements;

  const dragItem = selectedClassId && classArrangements.length > 0
    ? {
        teacher,
        course_id: classArrangements[0].course_id,
        course_name: classArrangements[0].course_name,
      }
    : { teacher };

  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'TEACHER',
    item: dragItem,
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }), [teacher, selectedClassId, classArrangements]);

  const courseNames = teacher.course_names || [];

  return (
    <div
      ref={drag}
      style={{
        padding: '6px 10px',
        marginBottom: 4,
        background: isDragging ? '#e6f4ff' : '#fafafa',
        border: `1px solid ${isDragging ? '#1677ff' : '#f0f0f0'}`,
        borderRadius: 4,
        cursor: 'grab',
        opacity: isDragging ? 0.5 : 1,
        transition: 'background 0.2s, border-color 0.2s',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <UserOutlined style={{ color: '#1677ff' }} />
        <span style={{ fontSize: 13, fontWeight: 500 }}>{teacher.name}</span>
        {teacher.teaching_group && (
          <Tag style={{ fontSize: 10 }} color="blue">{teacher.teaching_group}</Tag>
        )}
      </div>
      {courseNames.length > 0 && (
        <div style={{ marginLeft: 22, marginTop: 2, display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          {courseNames.map((name: string) => (
            <Tag key={name} icon={<BookOutlined />} style={{ fontSize: 10, margin: 0 }} color="green">{name}</Tag>
          ))}
        </div>
      )}
      {selectedClassId && classArrangements.length > 0 && (
        <div style={{ marginLeft: 22, marginTop: 2, fontSize: 11, color: '#1677ff' }}>
          本班: {classArrangements.map((a: any) => `${a.course_name}(${a.weekly_hours}课时)`).join('、')}
        </div>
      )}
    </div>
  );
}

export default function TeacherPanel({ teachers, selectedClassId, onRefresh }: TeacherPanelProps) {
  const { message } = App.useApp();
  const [search, setSearch] = useState('');
  const [addOpen, setAddOpen] = useState(false);
  const [addLoading, setAddLoading] = useState(false);
  const [form] = Form.useForm();
  const currentSemester = useAppStore((s) => s.currentSemester);

  const filtered = teachers.filter((t) =>
    !search || t.name?.includes(search) || t.teaching_group?.includes(search) ||
    (t.course_names || []).some((c: string) => c.includes(search))
  );

  const groups = filtered.reduce((acc, t) => {
    const group = t.teaching_group || '未分组';
    if (!acc[group]) acc[group] = [];
    acc[group].push(t);
    return acc;
  }, {} as Record<string, any[]>);

  const handleAdd = async () => {
    try {
      const values = await form.validateFields();
      setAddLoading(true);
      await createTeacher(values, currentSemester || undefined);
      message.success('教师添加成功');
      setAddOpen(false);
      form.resetFields();
      onRefresh();
    } catch (e: any) {
      if (e?.response?.data?.detail) {
        message.error(e.response.data.detail);
      }
    } finally {
      setAddLoading(false);
    }
  };

  return (
    <Card
      title="教师列表"
      size="small"
      style={{ height: '100%' }}
      styles={{ body: { padding: '8px', overflowY: 'auto', maxHeight: 'calc(100vh - 300px)' } }}
      extra={
        <Button type="primary" size="small" icon={<PlusOutlined />} onClick={() => setAddOpen(true)}>
          添加
        </Button>
      }
    >
      <Input.Search
        placeholder="搜索教师/课程"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{ marginBottom: 8 }}
        size="small"
        allowClear
      />
      <div style={{ fontSize: 11, color: '#999', marginBottom: 8 }}>
        拖拽教师到课表即可排课
      </div>
      {Object.entries(groups).map(([group, list]) => (
        <div key={group} style={{ marginBottom: 8 }}>
          <div style={{ fontSize: 12, color: '#666', fontWeight: 600, marginBottom: 4, paddingLeft: 2 }}>
            {group}
          </div>
          {list.map((t) => (
            <TeacherItem key={t.id} teacher={t} selectedClassId={selectedClassId} />
          ))}
        </div>
      ))}

      <Modal
        title="添加教师"
        open={addOpen}
        onCancel={() => { setAddOpen(false); form.resetFields(); }}
        onOk={handleAdd}
        confirmLoading={addLoading}
        destroyOnHidden
      >
        <TeacherForm form={form} showPasswordHint />
      </Modal>
    </Card>
  );
}
