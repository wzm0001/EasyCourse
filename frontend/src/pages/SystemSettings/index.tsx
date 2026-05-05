import { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Switch, InputNumber, message, Space, Alert } from 'antd';
import { getSettings, updateSettings, testMysql, switchDatabase, getPasswordPolicy, updatePasswordPolicy, setMaintenanceMode } from '@/api/settings';

export default function SystemSettings() {
  const [settingsForm] = Form.useForm();
  const [policyForm] = Form.useForm();
  const [dbForm] = Form.useForm();
  const [maintenance, setMaintenance] = useState(false);

  useEffect(() => {
    getSettings().then((res) => {
      settingsForm.setFieldsValue(res.data || {});
    });
    getPasswordPolicy().then((res) => {
      policyForm.setFieldsValue(res.data || {});
    });
  }, []);

  const handleSaveSettings = async () => {
    try {
      const values = await settingsForm.validateFields();
      await updateSettings(values);
      message.success('保存成功');
    } catch {
      message.error('保存失败');
    }
  };

  const handleSavePolicy = async () => {
    try {
      const values = await policyForm.validateFields();
      await updatePasswordPolicy(values);
      message.success('保存成功');
    } catch {
      message.error('保存失败');
    }
  };

  const handleTestMysql = async () => {
    try {
      const values = await dbForm.validateFields();
      await testMysql(values);
      message.success('连接成功');
    } catch {
      message.error('连接失败');
    }
  };

  const handleSwitchDb = async () => {
    try {
      const values = await dbForm.validateFields();
      await switchDatabase(values);
      message.success('切换成功');
    } catch {
      message.error('切换失败');
    }
  };

  const handleMaintenance = async (checked: boolean) => {
    try {
      await setMaintenanceMode(checked);
      setMaintenance(checked);
      message.success(checked ? '已开启维护模式' : '已关闭维护模式');
    } catch {
      message.error('操作失败');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <Card title="基本设置">
        <Form form={settingsForm} layout="vertical">
          <Form.Item name="token_expire_hours" label="Token 有效期（小时）">
            <InputNumber min={1} max={720} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="max_login_attempts" label="最大登录尝试次数">
            <InputNumber min={1} max={20} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="lock_duration_minutes" label="锁定时长（分钟）">
            <InputNumber min={5} max={1440} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="maintenance_mode" label="维护模式" valuePropName="checked">
            <Switch checked={maintenance} onChange={handleMaintenance} />
          </Form.Item>
          <Button type="primary" onClick={handleSaveSettings}>保存设置</Button>
        </Form>
      </Card>

      <Card title="密码策略">
        <Form form={policyForm} layout="vertical">
          <Form.Item name="min_length" label="最小密码长度">
            <InputNumber min={6} max={32} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="require_uppercase" label="需要大写字母" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="require_lowercase" label="需要小写字母" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="require_number" label="需要数字" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="require_special" label="需要特殊字符" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="expire_days" label="密码过期天数（0为不过期）">
            <InputNumber min={0} max={365} style={{ width: '100%' }} />
          </Form.Item>
          <Button type="primary" onClick={handleSavePolicy}>保存策略</Button>
        </Form>
      </Card>

      <Card title="数据库切换">
        <Alert type="warning" message="切换数据库将影响所有数据，请谨慎操作" style={{ marginBottom: 16 }} showIcon />
        <Form form={dbForm} layout="vertical">
          <Form.Item name="host" label="主机地址" rules={[{ required: true, message: '请输入主机地址' }]}>
            <Input placeholder="如：localhost" />
          </Form.Item>
          <Form.Item name="port" label="端口" rules={[{ required: true, message: '请输入端口' }]}>
            <InputNumber min={1} max={65535} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="database" label="数据库名" rules={[{ required: true, message: '请输入数据库名' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="username" label="用户名" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="password" label="密码">
            <Input.Password />
          </Form.Item>
          <Space>
            <Button onClick={handleTestMysql}>测试连接</Button>
            <Button type="primary" danger onClick={handleSwitchDb}>切换数据库</Button>
          </Space>
        </Form>
      </Card>
    </div>
  );
}
