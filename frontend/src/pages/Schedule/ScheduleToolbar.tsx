import { Space, Button, Tag, Popconfirm, Tooltip } from 'antd';
import {
  ThunderboltOutlined,
  ClearOutlined,
  LockOutlined,
  UnlockOutlined,
} from '@ant-design/icons';

interface ScheduleToolbarProps {
  lockStatus: any;
  onAutoSchedule: () => void;
  onClearSchedule: () => void;
  onAcquireLock: () => void;
  onReleaseLock: () => void;
  loading: boolean;
}

export default function ScheduleToolbar({
  lockStatus,
  onAutoSchedule,
  onClearSchedule,
  onAcquireLock,
  onReleaseLock,
  loading,
}: ScheduleToolbarProps) {
  const isLocked = lockStatus?.is_locked && lockStatus?.locked_by !== 'me';

  return (
    <Space style={{ marginBottom: 16 }} wrap>
      <Popconfirm
        title="确定要一键排课吗？这将自动生成课表。"
        onConfirm={onAutoSchedule}
      >
        <Button type="primary" icon={<ThunderboltOutlined />} loading={loading}>
          一键排课
        </Button>
      </Popconfirm>

      <Popconfirm
        title="确定要清除所有排课数据吗？此操作不可恢复。"
        onConfirm={onClearSchedule}
      >
        <Button danger icon={<ClearOutlined />} disabled={isLocked}>
          清除课表
        </Button>
      </Popconfirm>

      <div style={{ borderLeft: '1px solid #d9d9d9', height: 24, margin: '0 8px' }} />

      {isLocked ? (
        <Tooltip title={`当前被 ${lockStatus?.locked_by_name || '其他用户'} 锁定`}>
          <Tag color="error" icon={<LockOutlined />}>
            排课锁定中
          </Tag>
        </Tooltip>
      ) : lockStatus?.is_locked ? (
        <Space>
          <Tag color="success" icon={<UnlockOutlined />}>
            你已锁定排课
          </Tag>
          <Button size="small" onClick={onReleaseLock}>
            释放锁定
          </Button>
        </Space>
      ) : (
        <Button size="small" icon={<LockOutlined />} onClick={onAcquireLock}>
          锁定排课
        </Button>
      )}
    </Space>
  );
}
