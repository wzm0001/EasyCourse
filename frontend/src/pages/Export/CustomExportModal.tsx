import { Modal, Form, Select, Checkbox } from 'antd';

interface CustomExportModalProps {
  open: boolean;
  onClose: () => void;
  onExport: (values: any) => void;
}

export default function CustomExportModal({ open, onClose, onExport }: CustomExportModalProps) {
  const [form] = Form.useForm();

  return (
    <Modal
      title="自定义导出"
      open={open}
      onCancel={onClose}
      onOk={async () => {
        try {
          const values = await form.validateFields();
          await onExport(values);
          onClose();
        } catch {}
      }}
      destroyOnClose
    >
      <Form form={form} layout="vertical" preserve={false}>
        <Form.Item name="export_type" label="导出类型" rules={[{ required: true, message: '请选择导出类型' }]}>
          <Select options={[
            { label: '班级课表', value: 'class' },
            { label: '教师课表', value: 'teacher' },
            { label: '教室课表', value: 'classroom' },
          ]} />
        </Form.Item>
        <Form.Item name="format" label="导出格式" rules={[{ required: true, message: '请选择导出格式' }]}>
          <Select options={[
            { label: 'Excel', value: 'excel' },
            { label: 'PDF', value: 'pdf' },
          ]} />
        </Form.Item>
        <Form.Item name="scope" label="导出范围" rules={[{ required: true, message: '请选择导出范围' }]}>
          <Select options={[
            { label: '单个班级', value: 'single_class' },
            { label: '单个教师', value: 'single_teacher' },
            { label: '年级所有班级', value: 'grade_classes' },
            { label: '年级所有教师', value: 'grade_teachers' },
          ]} />
        </Form.Item>
        <Form.Item name="target_id" label="目标ID">
          <Select showSearch placeholder="请选择" />
        </Form.Item>
        <Form.Item name="include_details" label="包含详细信息" valuePropName="checked">
          <Checkbox>包含教师、教室等信息</Checkbox>
        </Form.Item>
      </Form>
    </Modal>
  );
}
