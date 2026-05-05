import { useState } from 'react';
import { Form, Input, Button, Card, message, Checkbox, Modal, Steps, Row, Col } from 'antd';
import { UserOutlined, LockOutlined, BankOutlined, PhoneOutlined, EnvironmentOutlined, KeyOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/auth';
import api from '@/api';
import type { LoginRequest } from '@/types/auth';

export default function Login() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);
  const [form] = Form.useForm<LoginRequest>();
  const [registerOpen, setRegisterOpen] = useState(false);
  const [resetOpen, setResetOpen] = useState(false);
  const [registerLoading, setRegisterLoading] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);
  const [resetStep, setResetStep] = useState(0);
  const [verifyForm] = Form.useForm();
  const [resetForm] = Form.useForm();
  const [verifiedUsername, setVerifiedUsername] = useState('');

  const handleSubmit = async (values: LoginRequest & { remember?: boolean }) => {
    try {
      const remember = values.remember ?? false;
      await login({ username: values.username, password: values.password }, remember);
      message.success('登录成功');
      navigate('/dashboard');
    } catch {
      message.error('登录失败，请检查用户名和密码');
    }
  };

  const handleRegister = async (values: any) => {
    setRegisterLoading(true);
    try {
      const response = await api.post('/auth/register', {
        name: values.name,
        code: values.code,
        address: values.address || '',
        contact_person: values.contact_person,
        contact_phone: values.contact_phone,
      });
      const result = response.data as any;
      message.success(result?.message || result?.data?.message || '注册申请已提交，请等待管理员审批');
      setRegisterOpen(false);
    } catch (e: any) {
      const errMsg = e?.response?.data?.detail || '注册失败，请稍后重试';
      message.error(errMsg);
    } finally {
      setRegisterLoading(false);
    }
  };

  const handleVerifyIdentity = async (values: any) => {
    setResetLoading(true);
    try {
      const verifyRes = await api.post('/auth/verify-identity', {
        username: values.username,
        phone: values.phone,
      });
      const verifyResult = verifyRes.data as any;
      if (verifyResult?.code !== 0 && !verifyResult?.data?.verified) {
        message.error('身份验证失败，用户名或手机号不匹配');
        return;
      }
      setVerifiedUsername(values.username);
      setResetStep(1);
    } catch (e: any) {
      const errMsg = e?.response?.data?.detail || '身份验证失败';
      message.error(errMsg);
    } finally {
      setResetLoading(false);
    }
  };

  const handleResetPassword = async (values: any) => {
    setResetLoading(true);
    try {
      const resetRes = await api.put('/auth/reset-password', {
        username: verifiedUsername,
        new_password: values.new_password,
      });
      const resetResult = resetRes.data as any;
      message.success(resetResult?.message || resetResult?.data?.message || '密码重置成功，请使用新密码登录');
      setResetOpen(false);
      setResetStep(0);
      setVerifiedUsername('');
    } catch (e: any) {
      const errMsg = e?.response?.data?.detail || '密码重置失败';
      message.error(errMsg);
    } finally {
      setResetLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card
        style={{
          width: 420,
          borderRadius: 12,
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.15)',
        }}
      >
        <div
          style={{
            textAlign: 'center',
            marginBottom: 32,
          }}
        >
          <h1
            style={{
              fontSize: 28,
              fontWeight: 700,
              color: '#1677ff',
              marginBottom: 8,
            }}
          >
            智能排课系统
          </h1>
          <p style={{ color: '#666', fontSize: 14 }}>
            中小学走班排课系统
          </p>
        </div>

        <Form
          form={form}
          onFinish={handleSubmit}
          size="large"
          autoComplete="off"
          initialValues={{ remember: true }}
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item>
            <Row justify="space-between" align="middle">
              <Col>
                <Form.Item name="remember" valuePropName="checked" noStyle>
                  <Checkbox>记住我</Checkbox>
                </Form.Item>
              </Col>
              <Col>
                <a onClick={() => { setResetOpen(true); setResetStep(0); }} style={{ color: '#1677ff', fontSize: 14 }}>
                  忘记密码？
                </a>
              </Col>
            </Row>
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              block
              style={{ height: 44, borderRadius: 8 }}
            >
              登录
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            <span style={{ color: '#999', fontSize: 14 }}>还没有账号？</span>
            <a
              onClick={() => setRegisterOpen(true)}
              style={{ color: '#1677ff', fontSize: 14, marginLeft: 4 }}
            >
              申请学校开户
            </a>
          </div>
        </Form>
      </Card>

      <Modal
        title="申请学校开户"
        open={registerOpen}
        onCancel={() => setRegisterOpen(false)}
        footer={null}
        width={520}
        destroyOnClose
      >
        <div style={{ marginBottom: 16, color: '#666', fontSize: 13 }}>
          请填写学校信息提交申请，管理员审批通过后即可使用系统。初始密码为学校编码 + @123
        </div>
        <Form
          layout="vertical"
          onFinish={handleRegister}
          size="middle"
        >
          <Form.Item
            name="name"
            label="学校名称"
            rules={[{ required: true, message: '请输入学校名称' }]}
          >
            <Input prefix={<BankOutlined />} placeholder="请输入学校名称" />
          </Form.Item>
          <Form.Item
            name="code"
            label="学校编码"
            rules={[
              { required: true, message: '请输入学校编码' },
              { pattern: /^[a-zA-Z0-9_]+$/, message: '仅允许字母、数字和下划线' },
            ]}
            extra="学校编码将作为登录用户名，不可修改"
          >
            <Input prefix={<KeyOutlined />} placeholder="请输入学校编码（如：school001）" />
          </Form.Item>
          <Form.Item name="address" label="学校地址">
            <Input prefix={<EnvironmentOutlined />} placeholder="请输入学校地址" />
          </Form.Item>
          <Form.Item
            name="contact_person"
            label="联系人"
            rules={[{ required: true, message: '请输入联系人姓名' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="请输入联系人姓名" />
          </Form.Item>
          <Form.Item
            name="contact_phone"
            label="联系电话"
            rules={[
              { required: true, message: '请输入联系电话' },
              { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' },
            ]}
          >
            <Input prefix={<PhoneOutlined />} placeholder="请输入联系电话" />
          </Form.Item>
          <Form.Item>
            <Row gutter={12} justify="end">
              <Col>
                <Button onClick={() => setRegisterOpen(false)}>取消</Button>
              </Col>
              <Col>
                <Button type="primary" htmlType="submit" loading={registerLoading}>
                  提交申请
                </Button>
              </Col>
            </Row>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="找回密码"
        open={resetOpen}
        onCancel={() => { setResetOpen(false); setResetStep(0); setVerifiedUsername(''); }}
        footer={null}
        width={480}
        destroyOnClose
      >
        <Steps
          current={resetStep}
          size="small"
          style={{ marginBottom: 24 }}
          items={[
            { title: '身份验证' },
            { title: '重置密码' },
          ]}
        />
        {resetStep === 0 && (
          <Form
            form={verifyForm}
            layout="vertical"
            onFinish={handleVerifyIdentity}
            size="middle"
          >
            <Form.Item
              name="username"
              label="用户名"
              rules={[{ required: true, message: '请输入用户名' }]}
            >
              <Input prefix={<UserOutlined />} placeholder="请输入您的用户名" />
            </Form.Item>
            <Form.Item
              name="phone"
              label="注册手机号"
              rules={[
                { required: true, message: '请输入注册手机号' },
                { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' },
              ]}
              extra="请输入注册时填写的手机号以验证身份"
            >
              <Input prefix={<PhoneOutlined />} placeholder="请输入注册手机号" />
            </Form.Item>
            <Form.Item>
              <Row gutter={12} justify="end">
                <Col>
                  <Button onClick={() => { setResetOpen(false); setResetStep(0); }}>取消</Button>
                </Col>
                <Col>
                  <Button type="primary" htmlType="submit" loading={resetLoading}>
                    验证身份
                  </Button>
                </Col>
              </Row>
            </Form.Item>
          </Form>
        )}
        {resetStep === 1 && (
          <Form
            form={resetForm}
            layout="vertical"
            onFinish={handleResetPassword}
            size="middle"
          >
            <Form.Item
              name="new_password"
              label="新密码"
              rules={[
                { required: true, message: '请输入新密码' },
                { min: 8, message: '密码至少8位' },
                {
                  pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
                  message: '密码需包含大小写字母和数字',
                },
              ]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="请输入新密码" />
            </Form.Item>
            <Form.Item
              name="confirm_password"
              label="确认密码"
              dependencies={['new_password']}
              rules={[
                { required: true, message: '请确认新密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('new_password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('两次输入的密码不一致'));
                  },
                }),
              ]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="请再次输入新密码" />
            </Form.Item>
            <Form.Item>
              <Row gutter={12} justify="end">
                <Col>
                  <Button onClick={() => { setResetOpen(false); setResetStep(0); setVerifiedUsername(''); }}>取消</Button>
                </Col>
                <Col>
                  <Button onClick={() => setResetStep(0)}>返回上一步</Button>
                </Col>
                <Col>
                  <Button type="primary" htmlType="submit" loading={resetLoading}>
                    重置密码
                  </Button>
                </Col>
              </Row>
            </Form.Item>
          </Form>
        )}
      </Modal>
    </div>
  );
}
