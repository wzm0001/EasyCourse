import { Form, Input, Select } from 'antd';

interface TeacherFormProps {
  form: any;
  showSchoolName?: string;
  showPasswordHint?: boolean;
}

export default function TeacherForm({ form, showSchoolName, showPasswordHint }: TeacherFormProps) {
  return (
    <Form form={form} layout="vertical">
      <Form.Item name="name" label="教师姓名" rules={[{ required: true, message: '请输入教师姓名' }]} extra="教师姓名将作为登录用户名">
        <Input placeholder="请输入教师姓名" />
      </Form.Item>
      <Form.Item name="phone" label="手机号" rules={[{ required: true, message: '请输入手机号' }, { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式' }]}>
        <Input placeholder="请输入11位手机号" />
      </Form.Item>
      <Form.Item name="gender" label="性别">
        <Select options={[{ label: '男', value: 'male' }, { label: '女', value: 'female' }]} placeholder="选填" allowClear />
      </Form.Item>
      <Form.Item name="employee_id" label="工号">
        <Input placeholder="选填" />
      </Form.Item>
      <Form.Item name="teaching_group" label="教研组">
        <Input placeholder="选填，如：语文组" />
      </Form.Item>
      <Form.Item name="specialization" label="专业信息">
        <Input.TextArea rows={2} placeholder="教师专业背景、擅长领域等" />
      </Form.Item>
      <Form.Item name="email" label="邮箱">
        <Input placeholder="选填" />
      </Form.Item>
      {showSchoolName && (
        <Form.Item label="学校名称">
          <Input value={showSchoolName} disabled />
        </Form.Item>
      )}
      {showPasswordHint && (
        <div style={{ color: '#999', fontSize: 12, marginTop: -8, marginBottom: 16 }}>
          添加后默认密码为手机号
        </div>
      )}
    </Form>
  );
}
