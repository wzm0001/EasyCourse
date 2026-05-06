import { useState } from 'react';
import { Card, Form, Input, Button, App, Descriptions, Divider, Modal } from 'antd';
import { useAuthStore } from '@/store/auth';
import { changePassword } from '@/api/auth';
import { updateUser } from '@/api/users';
import { useResponsive } from '@/hooks/useResponsive';

export default function Profile() {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const user = useAuthStore((s) => s.user);
  const refreshUser = useAuthStore((s) => s.refreshUser);
  const [pwdOpen, setPwdOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [form] = Form.useForm();
  const [pwdForm] = Form.useForm();

  const handleEditSave = async () => {
    try {
      const values = await form.validateFields();
      await updateUser(user!.id, values);
      message.success('信息更新成功');
      setEditOpen(false);
      await refreshUser();
    } catch {
      message.error('更新失败');
    }
  };

  return (
    <div style={{ maxWidth: isMobile ? '100%' : 600 }}>
      <Card title="个人信息" extra={<Button type="link" onClick={() => { form.setFieldsValue(user); setEditOpen(true); }}>编辑</Button>}>
        <Descriptions column={{ xs: 1, sm: 2 }} bordered>
          <Descriptions.Item label="用户名">{user?.username}</Descriptions.Item>
          <Descriptions.Item label="姓名">{user?.real_name || '-'}</Descriptions.Item>
          <Descriptions.Item label="手机号">{user?.phone || '-'}</Descriptions.Item>
          <Descriptions.Item label="邮箱">{user?.email || '-'}</Descriptions.Item>
          <Descriptions.Item label="角色">
            {user?.role === 'super_admin' ? '超级管理员' : user?.role === 'school_admin' ? '学校管理员' : '教师'}
          </Descriptions.Item>
          <Descriptions.Item label="学校">{user?.school_name || '-'}</Descriptions.Item>
        </Descriptions>
        <Divider />
        <Button type="primary" onClick={() => setPwdOpen(true)}>
          修改密码
        </Button>
      </Card>

      <Modal
        title="编辑个人信息"
        open={editOpen}
        onCancel={() => setEditOpen(false)}
        onOk={handleEditSave}
        destroyOnHidden
        width={isMobile ? '90vw' : 460}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="real_name" label="姓名" rules={[{ required: true, message: '请输入姓名' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="手机号">
            <Input />
          </Form.Item>
          <Form.Item name="email" label="邮箱">
            <Input />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="修改密码"
        open={pwdOpen}
        width={isMobile ? '90vw' : 600}
        style={{ top: 20 }}
        onCancel={() => setPwdOpen(false)}
        onOk={async () => {
          try {
            const values = await pwdForm.validateFields();
            if (values.new_password !== values.confirm_password) {
              message.error('两次密码不一致');
              return;
            }
            await changePassword({
              old_password: values.old_password,
              new_password: values.new_password,
            });
            message.success('密码修改成功');
            setPwdOpen(false);
            pwdForm.resetFields();
          } catch {
            message.error('密码修改失败');
          }
        }}
        destroyOnHidden
      >
        <Form form={pwdForm} layout="vertical">
          <Form.Item name="old_password" label="旧密码" rules={[{ required: true, message: '请输入旧密码' }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item name="new_password" label="新密码" rules={[{ required: true, message: '请输入新密码' }, { min: 6, message: '密码至少6位' }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item name="confirm_password" label="确认新密码" rules={[{ required: true, message: '请确认新密码' }]}>
            <Input.Password />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
