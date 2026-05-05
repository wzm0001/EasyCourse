import { Fragment } from 'react';
import ScheduleCell from './ScheduleCell';

interface ScheduleGridProps {
  periods: { key: string; label: string }[];
  days: { key: string; label: string }[];
  data: Record<string, Record<string, any | null>>;
  onCellClick?: (periodKey: string, dayKey: string, cell: any | null) => void;
  viewMode?: 'class' | 'teacher' | 'classroom';
}

export default function ScheduleGrid({ periods, days, data, onCellClick, viewMode = 'class' }: ScheduleGridProps) {
  return (
    <div style={{ overflowX: 'auto' }}>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `100px repeat(${days.length}, minmax(130px, 1fr))`,
          gap: '1px',
          background: '#d9d9d9',
          borderRadius: 6,
          overflow: 'hidden',
        }}
      >
        <div style={{ background: '#fafafa', padding: '8px 12px', fontWeight: 600, textAlign: 'center' }}>
          时间段
        </div>
        {days.map((day) => (
          <div key={day.key} style={{ background: '#fafafa', padding: '8px 12px', fontWeight: 600, textAlign: 'center' }}>
            {day.label}
          </div>
        ))}

        {periods.map((period) => (
          <Fragment key={period.key}>
            <div style={{ background: '#fff', padding: '8px 12px', fontWeight: 500, fontSize: 13, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {period.label}
            </div>
            {days.map((day) => (
              <div
                key={`${period.key}-${day.key}`}
                style={{ background: '#fff', padding: '4px' }}
              >
                <ScheduleCell
                  cell={data[period.key]?.[day.key] || null}
                  periodKey={period.key}
                  dayKey={day.key}
                  onClick={onCellClick}
                  viewMode={viewMode}
                />
              </div>
            ))}
          </Fragment>
        ))}
      </div>
    </div>
  );
}
