import { Alert, Tag, Space } from 'antd';
import { WarningOutlined } from '@ant-design/icons';

interface ConflictAlertProps {
  conflicts: any[];
}

export default function ConflictAlert({ conflicts }: ConflictAlertProps) {
  if (conflicts.length === 0) return null;

  return (
    <Alert
      type="error"
      icon={<WarningOutlined />}
      message={`发现 ${conflicts.length} 个冲突`}
      description={
        <Space direction="vertical" size={4}>
          {conflicts.slice(0, 5).map((c, i) => (
            <div key={i}>
              <Tag color="error">{c.type === 'teacher' ? '教师冲突' : c.type === 'classroom' ? '教室冲突' : '班级冲突'}</Tag>
              <span>{c.description || `${c.teacher_name || c.class_name || c.classroom_name} 在 ${c.day_name} 第${c.period_name} 存在冲突`}</span>
            </div>
          ))}
          {conflicts.length > 5 && <span style={{ color: '#999' }}>...还有 {conflicts.length - 5} 个冲突</span>}
        </Space>
      }
      showIcon
      style={{ marginBottom: 16 }}
    />
  );
}
