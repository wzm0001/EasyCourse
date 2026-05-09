import { Tag, Tooltip } from 'antd';
import { SafetyCertificateOutlined, WarningFilled } from '@ant-design/icons';
import { useDrag, useDrop } from 'react-dnd';
import { useRef, useCallback } from 'react';

interface ScheduleCellProps {
  cell: any | null;
  periodKey: string;
  dayKey: string;
  periodType?: string;
  periodIndex?: number;
  onClick?: (periodKey: string, dayKey: string, cell: any | null) => void;
  viewMode?: 'class' | 'teacher' | 'classroom';
  isSwapSource?: boolean;
  onDragDropTeacher?: (teacher: any, targetDayKey: string, periodInfo: { period_type: string; period_index: number }, courseId?: string) => void;
  onDragDropCell?: (sourceCell: any, targetDayKey: string, periodInfo: { period_type: string; period_index: number }) => void;
  onHoverConflictCheck?: (teacherId: string, dayKey: string, periodInfo: { period_type: string; period_index: number }) => void;
  onHoverCellConflictCheck?: (cellId: string, teacherId: string, classroomId: string, classId: string, dayKey: string, periodInfo: { period_type: string; period_index: number }) => void;
  onClearHoverConflicts?: () => void;
}

const conflictColors = [
  { bg: '#fff2f0', border: '#ff4d4f', text: '#cf1322' },
  { bg: '#fff7e6', border: '#fa8c16', text: '#d46b08' },
  { bg: '#fff0f6', border: '#eb2f96', text: '#c41d7f' },
  { bg: '#f9f0ff', border: '#722ed1', text: '#531dab' },
  { bg: '#e6fffb', border: '#13c2c2', text: '#006d75' },
];

export default function ScheduleCell({
  cell, periodKey, dayKey, periodType, periodIndex,
  onClick, viewMode = 'class', isSwapSource = false,
  onDragDropTeacher, onDragDropCell, onHoverConflictCheck, onHoverCellConflictCheck, onClearHoverConflicts,
}: ScheduleCellProps) {
  const divRef = useRef<HTMLDivElement>(null);

  const handleTeacherDrop = useCallback((item: any) => {
    if (onDragDropTeacher && periodType && periodIndex) {
      onDragDropTeacher(item.teacher, dayKey, { period_type: periodType, period_index: periodIndex }, item.course_id);
    }
  }, [onDragDropTeacher, dayKey, periodType, periodIndex]);

  const handleCellDrop = useCallback((item: any) => {
    if (onDragDropCell && periodType && periodIndex && item.cell) {
      onDragDropCell(item.cell, dayKey, { period_type: periodType, period_index: periodIndex });
    }
  }, [onDragDropCell, dayKey, periodType, periodIndex]);

  const handleTeacherHover = useCallback((item: any) => {
    if (onHoverConflictCheck && periodType && periodIndex) {
      onHoverConflictCheck(item.teacher.id, dayKey, { period_type: periodType, period_index: periodIndex });
    }
  }, [onHoverConflictCheck, dayKey, periodType, periodIndex]);

  const handleCellHover = useCallback((item: any) => {
    if (onHoverCellConflictCheck && periodType && periodIndex && item.cell) {
      onHoverCellConflictCheck(
        item.cell.id, item.cell.teacher_id, item.cell.classroom_id, item.cell.class_id,
        dayKey, { period_type: periodType, period_index: periodIndex },
      );
    }
  }, [onHoverCellConflictCheck, dayKey, periodType, periodIndex]);

  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'SCHEDULE_CELL',
    item: { cell, periodKey, dayKey },
    canDrag: !!cell && !cell.is_locked,
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }), [cell, periodKey, dayKey]);

  const [{ isOverTeacher }, dropTeacher] = useDrop(() => ({
    accept: 'TEACHER',
    drop: handleTeacherDrop,
    hover: handleTeacherHover,
    collect: (monitor) => ({
      isOverTeacher: monitor.isOver(),
    }),
  }), [handleTeacherDrop, handleTeacherHover]);

  const [{ isOverCell }, dropCell] = useDrop(() => ({
    accept: 'SCHEDULE_CELL',
    drop: handleCellDrop,
    hover: handleCellHover,
    collect: (monitor) => ({
      isOverCell: monitor.isOver(),
    }),
  }), [handleCellDrop, handleCellHover]);

  drag(divRef);
  dropTeacher(divRef);
  dropCell(divRef);

  const isOver = isOverTeacher || isOverCell;

  if (!cell) {
    return (
      <div
        ref={divRef}
        style={{
          minHeight: 56,
          border: isOver ? '2px solid #1677ff' : '1px dashed #d9d9d9',
          borderRadius: 4,
          cursor: onDragDropTeacher || onDragDropCell ? 'pointer' : 'default',
          transition: 'background 0.2s, border-color 0.2s',
          background: isOver ? '#e6f4ff' : 'transparent',
        }}
        onClick={() => onClick?.(periodKey, dayKey, null)}
        onMouseLeave={onClearHoverConflicts}
      />
    );
  }

  const hasConflict = cell.has_conflict;
  const conflictReasons = cell.conflict_reasons || [];
  const colorIdx = hasConflict ? (cell.id.charCodeAt(cell.id.length - 1) % conflictColors.length) : 0;
  const palette = conflictColors[colorIdx];

  const bgColor = hasConflict ? palette.bg : cell.is_locked ? '#fff7e6' : '#f6ffed';
  const borderColor = hasConflict ? palette.border : cell.is_locked ? '#faad14' : '#b7eb8f';
  const textColor = hasConflict ? palette.text : 'inherit';

  return (
    <Tooltip
      title={
        hasConflict ? (
          <div>
            <strong style={{ color: '#ff4d4f' }}>冲突详情：</strong>
            {conflictReasons.map((r: string, i: number) => {
              const display = r.includes(' | ') ? r.split(' | ').slice(1).join(' | ') : r;
              return <div key={i} style={{ marginTop: 4 }}>{display}</div>;
            })}
          </div>
        ) : undefined
      }
    >
      <div
        ref={divRef}
        style={{
          padding: '4px 8px',
          background: isSwapSource ? '#fff1b8' : isOver ? '#e6f4ff' : bgColor,
          border: isSwapSource
            ? '3px solid #faad14'
            : isOver
              ? '2px solid #1677ff'
              : hasConflict
                ? `2px solid ${palette.border}`
                : `1px solid ${borderColor}`,
          borderRadius: 4,
          cursor: cell.is_locked ? 'not-allowed' : 'grab',
          position: 'relative',
          opacity: isDragging ? 0.5 : 1,
          minHeight: 56,
          boxShadow: isSwapSource
            ? '0 0 8px #faad1480'
            : hasConflict
              ? `0 0 6px ${palette.border}40`
              : 'none',
        }}
        onClick={() => onClick?.(periodKey, dayKey, cell)}
        onMouseLeave={onClearHoverConflicts}
      >
        <div style={{ fontSize: 13, fontWeight: 500, color: textColor }}>{cell.course_name}</div>
        <div style={{ fontSize: 12, color: hasConflict ? textColor : '#666' }}>{cell.teacher_name}</div>
        {viewMode !== 'class' && cell.class_name && (
          <div style={{ fontSize: 12, color: '#999' }}>{cell.class_name}</div>
        )}
        {cell.is_locked && (
          <SafetyCertificateOutlined style={{ position: 'absolute', top: 4, right: 4, fontSize: 12, color: '#faad14' }} />
        )}
        {hasConflict && (
          <WarningFilled style={{ position: 'absolute', top: 4, right: cell.is_locked ? 20 : 4, fontSize: 14, color: palette.border }} />
        )}
        {hasConflict && (
          <div
            style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              height: 3,
              background: palette.border,
              borderBottomLeftRadius: 3,
              borderBottomRightRadius: 3,
            }}
          />
        )}
      </div>
    </Tooltip>
  );
}
