import { Modal, Form, Select, InputNumber, Switch, Input } from 'antd';
import { useResponsive } from '@/hooks/useResponsive';

interface ConstraintFormProps {
  open: boolean;
  editData: any | null;
  onClose: () => void;
  onOk: (values: any) => Promise<void>;
}

const constraintTypes = [
  { label: '教师不可排课时段', value: 'teacher_unavailable' },
  { label: '班级不可排课时段', value: 'class_unavailable' },
  { label: '教室不可排课时段', value: 'classroom_unavailable' },
  { label: '课程连排约束', value: 'course_continuous' },
  { label: '课程分散约束', value: 'course_scattered' },
  { label: '教师每天最大课时', value: 'teacher_max_daily' },
  { label: '课程优先时段', value: 'course_preferred_period' },
  { label: '年级互斥约束', value: 'grade_exclusive' },
];

export default function ConstraintForm({ open, editData, onClose, onOk }: ConstraintFormProps) {
  const [form] = Form.useForm();
  const constraintType = Form.useWatch('type', form);
  const { isMobile } = useResponsive();

  return (
    <Modal
      title={editData ? '编辑约束' : '新增约束'}
      open={open}
      onCancel={onClose}
      onOk={async () => {
        try {
          const values = await form.validateFields();
          await onOk(values);
        } catch {}
      }}
      destroyOnHidden
      width={isMobile ? '90vw' : 520}
    >
      <Form form={form} layout="vertical" initialValues={editData || { enabled: true }} preserve={false}>
        <Form.Item name="name" label="约束名称" rules={[{ required: true, message: '请输入约束名称' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="type" label="约束类型" rules={[{ required: true, message: '请选择约束类型' }]}>
          <Select options={constraintTypes} disabled={!!editData} />
        </Form.Item>
        <Form.Item name="enabled" label="是否启用" valuePropName="checked">
          <Switch />
        </Form.Item>
        <Form.Item name="priority" label="优先级">
          <InputNumber min={1} max={10} style={{ width: '100%' }} />
        </Form.Item>

        {(constraintType === 'teacher_unavailable' || constraintType === 'class_unavailable' || constraintType === 'classroom_unavailable') && (
          <>
            <Form.Item name="target_id" label="目标ID" rules={[{ required: true, message: '请输入目标ID' }]}>
              <Input />
            </Form.Item>
            <Form.Item name="day_of_week" label="星期" rules={[{ required: true, message: '请选择星期' }]}>
              <Select options={[
                { label: '周一', value: 1 }, { label: '周二', value: 2 }, { label: '周三', value: 3 },
                { label: '周四', value: 4 }, { label: '周五', value: 5 }, { label: '周六', value: 6 }, { label: '周日', value: 7 },
              ]} />
            </Form.Item>
            <Form.Item name="period_id" label="时间段ID">
              <Input />
            </Form.Item>
          </>
        )}

        {(constraintType === 'course_continuous' || constraintType === 'course_scattered') && (
          <>
            <Form.Item name="course_id" label="课程ID" rules={[{ required: true, message: '请输入课程ID' }]}>
              <Input />
            </Form.Item>
            <Form.Item name="count" label="连排/分散节数" rules={[{ required: true, message: '请输入节数' }]}>
              <InputNumber min={1} max={6} style={{ width: '100%' }} />
            </Form.Item>
          </>
        )}

        {constraintType === 'teacher_max_daily' && (
          <>
            <Form.Item name="teacher_id" label="教师ID" rules={[{ required: true, message: '请输入教师ID' }]}>
              <Input />
            </Form.Item>
            <Form.Item name="max_hours" label="每天最大课时" rules={[{ required: true, message: '请输入最大课时' }]}>
              <InputNumber min={1} max={12} style={{ width: '100%' }} />
            </Form.Item>
          </>
        )}

        {constraintType === 'course_preferred_period' && (
          <>
            <Form.Item name="course_id" label="课程ID" rules={[{ required: true, message: '请输入课程ID' }]}>
              <Input />
            </Form.Item>
            <Form.Item name="preferred_period_id" label="优先时间段ID">
              <Input />
            </Form.Item>
          </>
        )}

        {constraintType === 'grade_exclusive' && (
          <Form.Item name="grade_ids" label="互斥年级ID（逗号分隔）" rules={[{ required: true, message: '请输入年级ID' }]}>
            <Input placeholder="如: id1,id2,id3" />
          </Form.Item>
        )}

        <Form.Item name="description" label="描述">
          <Input.TextArea rows={3} />
        </Form.Item>
      </Form>
    </Modal>
  );
}
