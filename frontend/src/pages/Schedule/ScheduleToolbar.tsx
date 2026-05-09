import { Space, Button, Tag, Popconfirm, Tooltip, Checkbox } from 'antd';
import {
  ThunderboltOutlined,
  ClearOutlined,
  LockOutlined,
  UnlockOutlined,
} from '@ant-design/icons';
import { useState } from 'react';

interface ScheduleToolbarProps {
  lockStatus: any;
  onAutoSchedule: (keepLocked: boolean) => void;
  onClearSchedule: (keepLocked: boolean) => void;
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
  const [keepLocked, setKeepLocked] = useState(true);
  const isLocked = lockStatus?.is_locked && lockStatus?.locked_by !== 'me';

  return (
    <Space style={{ marginBottom: 16 }} wrap>
      <Popconfirm
        title={
          <div>
            <p>确定要一键排课吗？这将自动生成课表。</p>
            <Checkbox
              checked={keepLocked}
              onChange={(e) => setKeepLocked(e.target.checked)}
            >
              保留已锁定的课程
            </Checkbox>
          </div>
        }
        onConfirm={() => onAutoSchedule(keepLocked)}
      >
        <Button type="primary" icon={<ThunderboltOutlined />} loading={loading}>
          一键排课
        </Button>
      </Popconfirm>

      <Popconfirm
        title={
          <div>
            <p>确定要清除排课数据吗？</p>
            <Checkbox
              checked={keepLocked}
              onChange={(e) => setKeepLocked(e.target.checked)}
            >
              保留已锁定的课程
            </Checkbox>
          </div>
        }
        onConfirm={() => onClearSchedule(keepLocked)}
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

      <Tag color="blue" style={{ fontSize: 11 }}>
        💡 拖拽右侧教师到课表可快速排课
      </Tag>
    </Space>
  );
}
