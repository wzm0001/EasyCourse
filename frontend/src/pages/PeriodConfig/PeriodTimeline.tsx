interface PeriodTimelineProps {
  periods: any[];
  onToggleNoSchedule: (periodId: string) => void;
}

export default function PeriodTimeline({ periods, onToggleNoSchedule }: PeriodTimelineProps) {
  const morningPeriods = periods.filter((p) => p.type === 'morning');
  const classPeriods = periods.filter((p) => p.type === 'class');
  const eveningPeriods = periods.filter((p) => p.type === 'evening');

  const renderSection = (title: string, items: any[], color: string) => (
    <div style={{ marginBottom: 16 }}>
      <div style={{ fontWeight: 600, marginBottom: 8, color }}>{title}</div>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {items.map((item) => (
          <div
            key={item.id || item.key}
            onClick={() => onToggleNoSchedule(item.id || item.key)}
            style={{
              padding: '8px 12px',
              background: item.no_schedule ? '#fff1f0' : '#f6ffed',
              border: `1px solid ${item.no_schedule ? '#ffccc7' : '#b7eb8f'}`,
              borderRadius: 6,
              cursor: 'pointer',
              minWidth: 120,
              textAlign: 'center',
              opacity: item.no_schedule ? 0.6 : 1,
            }}
          >
            <div style={{ fontSize: 13, fontWeight: 500 }}>
              {item.name || `第${item.order}节`}
            </div>
            <div style={{ fontSize: 12, color: '#666' }}>
              {item.start_time} - {item.end_time}
            </div>
            {item.no_schedule && (
              <div style={{ fontSize: 11, color: '#ff4d4f', marginTop: 2 }}>不排课</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div>
      {renderSection('早读', morningPeriods, '#faad14')}
      {renderSection('正课', classPeriods, '#1677ff')}
      {renderSection('晚自习', eveningPeriods, '#722ed1')}
    </div>
  );
}
