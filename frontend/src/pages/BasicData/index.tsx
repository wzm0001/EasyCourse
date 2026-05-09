import { useState } from 'react';
import { Card, Tabs, Button } from 'antd';
import { ImportOutlined } from '@ant-design/icons';
import GradeTab from './GradeTab';
import ClassTab from './ClassTab';
import TeacherTab from './TeacherTab';
import ClassroomTab from './ClassroomTab';
import ArrangementTab from './ArrangementTab';
import ImportExportModal from './ImportExportModal';
import { useResponsive } from '@/hooks/useResponsive';

export default function BasicData({ embedded }: { embedded?: boolean } = {}) {
  const [importOpen, setImportOpen] = useState(false);
  const { isMobile } = useResponsive();

  const content = (
    <>
      <Tabs
        defaultActiveKey="teacher"
        items={[
          { key: 'teacher', label: '教师信息', children: <TeacherTab /> },
          { key: 'classroom', label: '教室信息', children: <ClassroomTab /> },
          { key: 'grade', label: '年级信息', children: <GradeTab /> },
          { key: 'class', label: '班级信息', children: <ClassTab /> },
          { key: 'arrangement', label: '教学安排', children: <ArrangementTab /> },
        ]}
      />
      <ImportExportModal
        open={importOpen}
        onClose={() => setImportOpen(false)}
        onSuccess={() => {}}
      />
    </>
  );

  return embedded ? content : (
    <Card
      title="基础数据管理"
      style={isMobile ? { margin: -16 } : undefined}
      extra={
        <Button icon={<ImportOutlined />} onClick={() => setImportOpen(true)}>
          导入导出
        </Button>
      }
    >
      {content}
    </Card>
  );
}
