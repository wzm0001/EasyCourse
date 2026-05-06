import { useEffect } from 'react';
import { Card, Form, Input, Button, App } from 'antd';
import { getSchool, updateSchool } from '@/api/schools';
import { useAuthStore } from '@/store/auth';
import { useResponsive } from '@/hooks/useResponsive';

export default function SchoolSettings() {
  const { message } = App.useApp();
  const [form] = Form.useForm();
  const { isMobile } = useResponsive();
  const user = useAuthStore((s) => s.user);
  const refreshUser = useAuthStore((s) => s.refreshUser);
  const schoolId = user?.school_id;

  useEffect(() => {
    if (schoolId) {
      getSchool(schoolId).then((res) => {
        const data = (res as any)?.data || res;
        form.setFieldsValue(data);
      }).catch(() => {});
    }
  }, [schoolId]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      await updateSchool(schoolId!, values);
      message.success('保存成功');
      await refreshUser();
    } catch {
      message.error('保存失败');
    }
  };

  return (
    <div style={{ maxWidth: isMobile ? '100%' : 720 }}>
      <Card title="学校信息">
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="学校名称" rules={[{ required: true, message: '请输入学校名称' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="code" label="统一社会信用代码">
            <Input disabled />
          </Form.Item>
          <Form.Item name="school_type" label="学校类型">
            <Input disabled />
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
          <Form.Item name="contact_phone" label="联系电话" rules={[{ required: true, message: '请输入联系电话' }]}>
            <Input />
          </Form.Item>
          <Button type="primary" onClick={handleSave}>保存信息</Button>
        </Form>
      </Card>
    </div>
  );
}
