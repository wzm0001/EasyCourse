import { useState } from 'react';
import { Steps, Card, Button, Space } from 'antd';
import {
  CalendarOutlined,
  DatabaseOutlined,
  TableOutlined,
  ExportOutlined,
} from '@ant-design/icons';
import SemesterManage from '@/pages/SemesterManage';
import BasicData from '@/pages/BasicData';
import Schedule from '@/pages/Schedule';
import Export from '@/pages/Export';
import { useResponsive } from '@/hooks/useResponsive';

const STEPS = [
  { title: '学期设置', icon: <CalendarOutlined /> },
  { title: '基础数据', icon: <DatabaseOutlined /> },
  { title: '排课', icon: <TableOutlined /> },
  { title: '导出课表', icon: <ExportOutlined /> },
];

export default function ScheduleWizard() {
  const [current, setCurrent] = useState(0);
  const { isMobile } = useResponsive();

  const renderContent = () => {
    switch (current) {
      case 0: return <SemesterManage embedded />;
      case 1: return <BasicData embedded />;
      case 2: return <Schedule embedded />;
      case 3: return <Export embedded />;
      default: return null;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Card
        size="small"
        style={{ marginBottom: 12, flexShrink: 0 }}
        styles={{ body: { padding: isMobile ? '8px 0' : '8px 16px' } }}
      >
        <Steps
          current={current}
          onChange={setCurrent}
          size={isMobile ? 'small' : 'default'}
          direction={isMobile ? 'vertical' : 'horizontal'}
          items={STEPS.map((s) => ({
            title: s.title,
            icon: s.icon,
            style: { cursor: 'pointer' },
          }))}
        />
      </Card>
      <div style={{ flex: 1, overflow: 'auto' }}>
        {renderContent()}
      </div>
      <div
        style={{
          position: 'sticky',
          bottom: 0,
          background: '#fff',
          padding: '8px 16px',
          borderTop: '1px solid #f0f0f0',
          display: 'flex',
          justifyContent: 'space-between',
          flexShrink: 0,
        }}
      >
        <Button
          disabled={current === 0}
          onClick={() => setCurrent(current - 1)}
        >
          上一步
        </Button>
        <Space>
          <span style={{ color: '#999', fontSize: 12 }}>
            第 {current + 1} 步 / 共 {STEPS.length} 步
          </span>
        </Space>
        <Button
          type="primary"
          disabled={current === STEPS.length - 1}
          onClick={() => setCurrent(current + 1)}
        >
          下一步
        </Button>
      </div>
    </div>
  );
}
