import { Table, Tag, Tooltip } from 'antd';
import { LockOutlined } from '@ant-design/icons';

interface ScheduleCellData {
  id: string;
  course_name: string;
  teacher_name: string;
  classroom_name?: string;
  is_locked: boolean;
  has_conflict: boolean;
  class_name?: string;
}

interface ScheduleTableProps {
  periods: { key: string; label: string }[];
  days: { key: string; label: string }[];
  data: Record<string, Record<string, ScheduleCellData | null>>;
  onCellClick?: (period: string, day: string, cell: ScheduleCellData | null) => void;
  viewMode?: 'class' | 'teacher' | 'classroom';
}

export default function ScheduleTable({
  periods,
  days,
  data,
  onCellClick,
  viewMode = 'class',
}: ScheduleTableProps) {
  const columns = [
    {
      title: '时间段',
      dataIndex: 'period',
      key: 'period',
      fixed: 'left' as const,
      width: 100,
      render: (text: string) => (
        <span style={{ fontWeight: 500, fontSize: 13 }}>{text}</span>
      ),
    },
    ...days.map((day) => ({
      title: day.label,
      dataIndex: day.key,
      key: day.key,
      width: 140,
      render: (cell: ScheduleCellData | null) => {
        if (!cell) {
          return (
            <div
              style={{
                minHeight: 48,
                border: '1px dashed #d9d9d9',
                borderRadius: 4,
                cursor: onCellClick ? 'pointer' : 'default',
              }}
              onClick={() => onCellClick?.(day.key, '', null)}
            />
          );
        }

        const bgColor = cell.has_conflict ? '#fff1f0' : cell.is_locked ? '#fff7e6' : '#f6ffed';
        const borderColor = cell.has_conflict ? '#ff4d4f' : cell.is_locked ? '#faad14' : '#b7eb8f';

        return (
          <Tooltip
            title={
              <div>
                <div>{cell.course_name}</div>
                <div>{cell.teacher_name}</div>
                {cell.classroom_name && <div>{cell.classroom_name}</div>}
                {cell.is_locked && <div>已锁定</div>}
                {cell.has_conflict && <div style={{ color: '#ff4d4f' }}>存在冲突</div>}
              </div>
            }
          >
            <div
              style={{
                padding: '4px 8px',
                background: bgColor,
                border: `1px solid ${borderColor}`,
                borderRadius: 4,
                cursor: onCellClick ? 'pointer' : 'default',
                position: 'relative',
              }}
              onClick={() => onCellClick?.(day.key, '', cell)}
            >
              <div style={{ fontSize: 13, fontWeight: 500 }}>{cell.course_name}</div>
              <div style={{ fontSize: 12, color: '#666' }}>{cell.teacher_name}</div>
              {viewMode === 'teacher' && cell.class_name && (
                <div style={{ fontSize: 12, color: '#999' }}>{cell.class_name}</div>
              )}
              {viewMode === 'teacher' && cell.classroom_name && (
                <div style={{ fontSize: 12, color: '#999' }}>{cell.classroom_name}</div>
              )}
              {viewMode === 'class' && cell.classroom_name && (
                <div style={{ fontSize: 12, color: '#999' }}>{cell.classroom_name}</div>
              )}
              {viewMode === 'classroom' && cell.class_name && (
                <div style={{ fontSize: 12, color: '#999' }}>{cell.class_name}</div>
              )}
              {cell.is_locked && (
                <LockOutlined
                  style={{
                    position: 'absolute',
                    top: 4,
                    right: 4,
                    fontSize: 12,
                    color: '#faad14',
                  }}
                />
              )}
              {cell.has_conflict && (
                <Tag color="error" style={{ position: 'absolute', top: 2, right: cell.is_locked ? 20 : 4, fontSize: 10, lineHeight: '16px', padding: '0 4px' }}>
                  冲突
                </Tag>
              )}
            </div>
          </Tooltip>
        );
      },
    })),
  ];

  const dataSource = periods.map((period) => {
    const row: Record<string, any> = {
      key: period.key,
      period: period.label,
    };
    days.forEach((day) => {
      row[day.key] = data[period.key]?.[day.key] || null;
    });
    return row;
  });

  return (
    <Table
      columns={columns}
      dataSource={dataSource}
      pagination={false}
      bordered
      size="small"
      scroll={{ x: days.length * 140 + 100 }}
    />
  );
}
