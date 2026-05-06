import { useState } from 'react';
import { Card, Tabs, Button } from 'antd';
import { ImportOutlined } from '@ant-design/icons';
import GradeTab from './GradeTab';
import ClassTab from './ClassTab';
import CourseTab from './CourseTab';
import TeacherTab from './TeacherTab';
import ClassroomTab from './ClassroomTab';
import ArrangementTab from './ArrangementTab';
import { ImportExportModal } from './ImportExportModal';
import { useResponsive } from '@/hooks/useResponsive';

export default function BasicData() {
  const [importOpen, setImportOpen] = useState(false);
  const { isMobile } = useResponsive();

  return (
    <Card
      title="基础数据管理"
      style={isMobile ? { margin: -16 } : undefined}
      extra={
        <Button icon={<ImportOutlined />} onClick={() => setImportOpen(true)}>
          导入导出
        </Button>
      }
    >
      <Tabs
        defaultActiveKey="grade"
        items={[
          { key: 'grade', label: '年级', children: <GradeTab /> },
          { key: 'class', label: '班级', children: <ClassTab /> },
          { key: 'course', label: '课程', children: <CourseTab /> },
          { key: 'teacher', label: '教师', children: <TeacherTab /> },
          { key: 'classroom', label: '教室', children: <ClassroomTab /> },
          { key: 'arrangement', label: '教学安排', children: <ArrangementTab /> },
        ]}
      />
      <ImportExportModal
        open={importOpen}
        onClose={() => setImportOpen(false)}
        onSuccess={() => {}}
      />
    </Card>
  );
}
