import { Modal, Form, Input, Select, message } from 'antd';
import { createSchool, updateSchool } from '@/api/schools';

interface SchoolFormProps {
  open: boolean;
  editData: any | null;
  onClose: () => void;
  onSuccess: () => void;
}

export default function SchoolForm({ open, editData, onClose, onSuccess }: SchoolFormProps) {
  const [form] = Form.useForm();
  const isEdit = !!editData;

  return (
    <Modal
      title={isEdit ? '编辑学校' : '新增学校'}
      open={open}
      onCancel={onClose}
      onOk={async () => {
        try {
          const values = await form.validateFields();
          if (isEdit) {
            await updateSchool(editData.id, values);
            message.success('更新成功');
          } else {
            await createSchool(values);
            message.success('创建成功');
          }
          onSuccess();
          onClose();
        } catch {
          message.error('操作失败');
        }
      }}
      width={520}
      style={{ top: 20 }}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={editData || {}}
        preserve={false}
      >
        <Form.Item name="name" label="学校名称" rules={[{ required: true, message: '请输入学校名称' }]}>
          <Input />
        </Form.Item>
        <Form.Item
          name="code"
          label="学校编码"
          rules={[
            { required: true, message: '请输入学校编码' },
            { pattern: /^[a-zA-Z0-9_]+$/, message: '仅允许字母、数字和下划线' },
          ]}
        >
          <Input disabled={isEdit} />
        </Form.Item>
        <Form.Item name="school_type" label="学校类型" rules={[{ required: true, message: '请选择学校类型' }]}>
          <Select
            options={[
              { label: '小学', value: 'primary' },
              { label: '初中', value: 'middle' },
              { label: '高中', value: 'high' },
              { label: '九年一贯制', value: 'nine_year' },
              { label: '完全中学', value: 'complete' },
            ]}
          />
        </Form.Item>
        <Form.Item name="province" label="省份">
          <Input />
        </Form.Item>
        <Form.Item name="city" label="城市">
          <Input />
        </Form.Item>
        <Form.Item name="district" label="区县">
          <Input />
        </Form.Item>
        <Form.Item name="address" label="详细地址">
          <Input />
        </Form.Item>
        <Form.Item name="contact_person" label="联系人" rules={[{ required: true, message: '请输入联系人' }]}>
          <Input />
        </Form.Item>
        <Form.Item
          name="contact_phone"
          label="联系电话"
          rules={[
            { required: true, message: '请输入联系电话' },
            { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' },
          ]}
        >
          <Input />
        </Form.Item>
      </Form>
    </Modal>
  );
}
