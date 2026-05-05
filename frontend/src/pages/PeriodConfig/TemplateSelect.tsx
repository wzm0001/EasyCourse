import { useState, useEffect } from 'react';
import { Modal, List, Tag, message } from 'antd';
import { getTemplates, applyTemplate } from '@/api/periods';

interface TemplateSelectProps {
  open: boolean;
  gradeId: string;
  onClose: () => void;
  onSuccess: () => void;
}

export default function TemplateSelect({ open, gradeId, onClose, onSuccess }: TemplateSelectProps) {
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      setLoading(true);
      getTemplates()
        .then((res) => setTemplates(res.data || []))
        .catch(() => message.error('获取模板失败'))
        .finally(() => setLoading(false));
    }
  }, [open]);

  return (
    <Modal
      title="选择时间段模板"
      open={open}
      onCancel={onClose}
      footer={null}
      width={600}
    >
      <List
        loading={loading}
        dataSource={templates}
        renderItem={(item) => (
          <List.Item
            actions={[
              <a
                key="apply"
                onClick={async () => {
                  try {
                    await applyTemplate(item.id, gradeId);
                    message.success('应用成功');
                    onSuccess();
                    onClose();
                  } catch {
                    message.error('应用失败');
                  }
                }}
              >
                应用
              </a>,
            ]}
          >
            <List.Item.Meta
              title={item.name}
              description={
                <div>
                  <Tag>早读 {item.morning_count || 0} 节</Tag>
                  <Tag color="blue">正课 {item.class_count || 0} 节</Tag>
                  <Tag color="purple">晚自习 {item.evening_count || 0} 节</Tag>
                </div>
              }
            />
          </List.Item>
        )}
      />
    </Modal>
  );
}
