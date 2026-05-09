import { List, Tag, Typography } from 'antd';
import { WarningFilled, CloseOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface ConflictInfo {
  type: string;
  message: string;
  severity?: string;
}

interface ConflictAlertProps {
  conflicts: ConflictInfo[];
  onClose?: () => void;
}

const conflictTypeLabels: Record<string, { label: string; color: string }> = {
  teacher_conflict: { label: '教师冲突', color: 'red' },
  classroom_conflict: { label: '教室冲突', color: 'orange' },
  teacher_continuous_limit: { label: '教师连堂限制', color: 'magenta' },
  teacher_daily_hours_limit: { label: '教师每日课时限制', color: 'purple' },
  class_daily_period_conflict: { label: '班级每日节次冲突', color: 'cyan' },
};

function formatMessage(msg: string): string {
  if (msg.includes(' | ')) {
    const parts = msg.split(' | ');
    return parts.slice(1).join(' | ');
  }
  return msg;
}

export default function ConflictAlert({ conflicts, onClose }: ConflictAlertProps) {
  if (!conflicts || conflicts.length === 0) return null;

  const deduped = conflicts.filter(
    (c, i, arr) => arr.findIndex((x) => x.type === c.type && x.message === c.message) === i
  );

  return (
    <div
      style={{
        background: '#fff2f0',
        border: '1px solid #ffccc7',
        borderRadius: 8,
        padding: '10px 14px',
        marginBottom: 12,
        position: 'relative',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <WarningFilled style={{ color: '#ff4d4f', fontSize: 16 }} />
          <Text strong style={{ color: '#cf1322' }}>
            存在 {deduped.length} 个冲突（请解决冲突后课表才能正常使用）
          </Text>
        </span>
        {onClose && (
          <CloseOutlined
            onClick={onClose}
            style={{ color: '#999', cursor: 'pointer', fontSize: 12 }}
          />
        )}
      </div>
      <List
        size="small"
        dataSource={deduped}
        renderItem={(item: ConflictInfo) => {
          const typeCfg = conflictTypeLabels[item.type] || { label: item.type, color: 'default' };
          return (
            <List.Item style={{ padding: '4px 0', borderBottom: '1px solid #ffd8bf' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8, width: '100%' }}>
                <Tag color={typeCfg.color} style={{ flexShrink: 0, marginTop: 1 }}>
                  {typeCfg.label}
                </Tag>
                <Text style={{ color: '#595959', fontSize: 13, wordBreak: 'break-all' }}>
                  {formatMessage(item.message)}
                </Text>
              </div>
            </List.Item>
          );
        }}
        style={{ maxHeight: 160, overflowY: 'auto' }}
      />
    </div>
  );
}
