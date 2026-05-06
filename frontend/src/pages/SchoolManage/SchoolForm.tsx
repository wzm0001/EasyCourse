import { Modal, Form, Input, Select, Upload, Button, App } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { createSchool, updateSchool } from '@/api/schools';
import api from '@/api';
import { useState } from 'react';
import { useResponsive } from '@/hooks/useResponsive';
import { useAuthStore } from '@/store/auth';

interface SchoolFormProps {
  open: boolean;
  editData: any | null;
  onClose: () => void;
  onSuccess: () => void;
}

export default function SchoolForm({ open, editData, onClose, onSuccess }: SchoolFormProps) {
  const [form] = Form.useForm();
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const refreshUser = useAuthStore((s) => s.refreshUser);
  const isEdit = !!editData;
  const [attachmentUrl, setAttachmentUrl] = useState(editData?.attachment || '');

  const handleOpen = () => {
    setAttachmentUrl(editData?.attachment || '');
  };

  return (
    <Modal
      title={isEdit ? '编辑学校' : '新增学校'}
      open={open}
      onCancel={onClose}
      afterOpenChange={(visible) => { if (visible) handleOpen(); }}
      onOk={async () => {
        try {
          const values = await form.validateFields();
          const data = { ...values, attachment: attachmentUrl };
          if (isEdit) {
            await updateSchool(editData.id, data);
            message.success('更新成功');
            await refreshUser();
          } else {
            const res = await createSchool(data);
            message.success((res as any)?.message || '创建成功');
          }
          onSuccess();
          onClose();
        } catch (e: any) {
          const detail = e?.response?.data?.detail;
          if (detail) {
            message.error(detail);
          } else if (e?.errorFields) {
            message.error('请检查表单填写是否正确');
          } else {
            message.error('操作失败');
          }
        }
      }}
      width={isMobile ? '90vw' : 520}
      style={{ top: 20 }}
      destroyOnHidden
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={editData || {}}
        preserve={false}
      >
        <Form.Item name="name" label="学校名称" rules={[{ required: true, message: '请输入学校名称' }]} extra="学校名称将作为登录用户名">
          <Input />
        </Form.Item>
        <Form.Item
          name="code"
          label="统一社会信用代码"
          rules={[
            { required: true, message: '请输入统一社会信用代码' },
            { len: 18, message: '统一社会信用代码为18位' },
            { pattern: /^[0-9A-Z]+$/, message: '仅允许大写字母和数字' },
          ]}
          extra="统一社会信用代码用于学校资质认证"
        >
          <Input placeholder="请输入18位统一社会信用代码" style={{ textTransform: 'uppercase' }} />
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
        <Form.Item label="附件上传" extra="请上传学校资质证明等材料">
          <Upload
            maxCount={1}
            accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
            defaultFileList={editData?.attachment ? [{
              uid: '-1',
              name: '附件',
              status: 'done' as const,
              url: editData.attachment,
            }] : []}
            customRequest={async ({ file, onSuccess, onError }) => {
              const formData = new FormData();
              formData.append('file', file as File);
              try {
                const res = await api.post('/schools/upload', formData, {
                  headers: { 'Content-Type': 'multipart/form-data' },
                });
                const data = (res.data as any)?.data;
                setAttachmentUrl(data?.url || '');
                onSuccess?.(data);
              } catch (e: any) {
                onError?.(e);
                message.error('文件上传失败');
              }
            }}
            onRemove={() => {
              setAttachmentUrl('');
            }}
          >
            <Button icon={<UploadOutlined />}>选择文件</Button>
          </Upload>
        </Form.Item>
      </Form>
    </Modal>
  );
}
