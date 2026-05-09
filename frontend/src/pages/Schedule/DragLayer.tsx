import { useDragLayer } from 'react-dnd';
import type { XYCoord } from 'react-dnd';
import type { CSSProperties } from 'react';

const layerStyle: CSSProperties = {
  position: 'fixed',
  pointerEvents: 'none',
  zIndex: 10000,
  left: 0,
  top: 0,
  width: '100%',
  height: '100%',
};

function getItemStyles(currentOffset: XYCoord | null) {
  if (!currentOffset) return { display: 'none' };
  const { x, y } = currentOffset;
  return {
    transform: `translate(${x}px, ${y}px)`,
    WebkitTransform: `translate(${x}px, ${y}px)`,
  };
}

export default function DragLayer() {
  const { isDragging, item, currentOffset } = useDragLayer((monitor) => ({
    item: monitor.getItem() as any,
    itemType: monitor.getItemType(),
    currentOffset: monitor.getSourceClientOffset(),
    isDragging: monitor.isDragging(),
  }));

  if (!isDragging || !item?.cell) return null;

  return (
    <div style={layerStyle}>
      <div style={getItemStyles(currentOffset)}>
        <div
          style={{
            padding: '4px 8px',
            background: '#e6f4ff',
            border: '1px solid #1677ff',
            borderRadius: 4,
            opacity: 0.8,
            width: 'fit-content',
            maxWidth: 160,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          <div style={{ fontSize: 13, fontWeight: 500 }}>{item.cell.course_name}</div>
          <div style={{ fontSize: 12, color: '#666' }}>{item.cell.teacher_name}</div>
        </div>
      </div>
    </div>
  );
}
