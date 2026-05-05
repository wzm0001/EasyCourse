import { Tag } from 'antd';
import { LockOutlined } from '@ant-design/icons';
import { useDrag } from 'react-dnd';
import { useRef } from 'react';

interface ScheduleCellProps {
  cell: any | null;
  periodKey: string;
  dayKey: string;
  onClick?: (periodKey: string, dayKey: string, cell: any | null) => void;
  viewMode?: 'class' | 'teacher' | 'classroom';
}

export default function ScheduleCell({ cell, periodKey, dayKey, onClick, viewMode = 'class' }: ScheduleCellProps) {
  const divRef = useRef<HTMLDivElement>(null);

  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'SCHEDULE_CELL',
    item: { cell, periodKey, dayKey },
    canDrag: !!cell && !cell.is_fixed,
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }), [cell, periodKey, dayKey]);

  drag(divRef);

  if (!cell) {
    return (
      <div
        style={{
          minHeight: 56,
          border: '1px dashed #d9d9d9',
          borderRadius: 4,
          cursor: onClick ? 'pointer' : 'default',
          transition: 'background 0.2s',
        }}
        onClick={() => onClick?.(periodKey, dayKey, null)}
      />
    );
  }

  const bgColor = cell.has_conflict ? '#fff1f0' : '#f6ffed';
  const borderColor = cell.has_conflict ? '#ff4d4f' : '#b7eb8f';

  return (
    <div
      ref={divRef}
      style={{
        padding: '4px 8px',
        background: bgColor,
        border: `1px solid ${borderColor}`,
        borderRadius: 4,
        cursor: cell.is_fixed ? 'not-allowed' : 'grab',
        position: 'relative',
        opacity: isDragging ? 0.5 : 1,
        minHeight: 56,
      }}
      onClick={() => onClick?.(periodKey, dayKey, cell)}
    >
      <div style={{ fontSize: 13, fontWeight: 500 }}>{cell.course_name}</div>
      <div style={{ fontSize: 12, color: '#666' }}>{cell.teacher_name}</div>
      {viewMode !== 'class' && cell.class_name && (
        <div style={{ fontSize: 12, color: '#999' }}>{cell.class_name}</div>
      )}
      {cell.is_fixed && (
        <LockOutlined style={{ position: 'absolute', top: 4, right: 4, fontSize: 12, color: '#faad14' }} />
      )}
      {cell.has_conflict && (
        <Tag color="error" style={{ position: 'absolute', top: 2, right: cell.is_fixed ? 20 : 4, fontSize: 10, lineHeight: '16px', padding: '0 4px' }}>
          冲突
        </Tag>
      )}
    </div>
  );
}
