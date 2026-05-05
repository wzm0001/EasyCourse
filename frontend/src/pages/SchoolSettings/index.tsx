import { useEffect } from 'react';
import { Card, Form, Input, Button, Select, InputNumber, Switch, message } from 'antd';
import { getSettings, updateSettings } from '@/api/settings';

export default function SchoolSettings() {
  const [form] = Form.useForm();

  useEffect(() => {
    getSettings().then((res) => {
      form.setFieldsValue(res.data || {});
    });
  }, []);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      await updateSettings(values);
      message.success('保存成功');
    } catch {
      message.error('保存失败');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <Card title="基本信息">
        <Form form={form} layout="vertical">
          <Form.Item name="school_name" label="学校名称" rules={[{ required: true, message: '请输入学校名称' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="school_code" label="学校编码">
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
          <Form.Item name="contact_name" label="联系人">
            <Input />
          </Form.Item>
          <Form.Item name="contact_phone" label="联系电话">
            <Input />
          </Form.Item>
          <Button type="primary" onClick={handleSave}>保存信息</Button>
        </Form>
      </Card>

      <Card title="排课参数">
        <Form layout="vertical">
          <Form.Item label="每天最大课时数">
            <InputNumber min={4} max={14} defaultValue={10} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="连排优先" valuePropName="checked">
            <Switch defaultChecked />
          </Form.Item>
          <Form.Item label="午休开始节次">
            <InputNumber min={3} max={6} defaultValue={4} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="排课算法">
            <Select
              defaultValue="greedy"
              options={[
                { label: '贪心算法', value: 'greedy' },
                { label: '遗传算法', value: 'genetic' },
                { label: '模拟退火', value: 'simulated_annealing' },
              ]}
            />
          </Form.Item>
          <Button type="primary" onClick={handleSave}>保存参数</Button>
        </Form>
      </Card>

      <Card title="课表偏好">
        <Form layout="vertical">
          <Form.Item label="主课优先排上午" valuePropName="checked">
            <Switch defaultChecked />
          </Form.Item>
          <Form.Item label="体育课不排上午第一节" valuePropName="checked">
            <Switch defaultChecked />
          </Form.Item>
          <Form.Item label="同一课程尽量分散" valuePropName="checked">
            <Switch defaultChecked />
          </Form.Item>
          <Form.Item label="班主任课优先集中">
            <Select
              defaultValue="prefer_morning"
              options={[
                { label: '优先上午', value: 'prefer_morning' },
                { label: '优先下午', value: 'prefer_afternoon' },
                { label: '不限制', value: 'no_preference' },
              ]}
            />
          </Form.Item>
          <Button type="primary" onClick={handleSave}>保存偏好</Button>
        </Form>
      </Card>
    </div>
  );
}
