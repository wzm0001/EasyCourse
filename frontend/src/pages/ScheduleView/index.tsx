import { Card, Tabs } from 'antd';
import ClassScheduleView from './ClassScheduleView';
import TeacherScheduleView from './TeacherScheduleView';
import ClassroomScheduleView from './ClassroomScheduleView';
import GradeScheduleView from './GradeScheduleView';

export default function ScheduleView() {
  return (
    <Card title="课表查看">
      <Tabs
        defaultActiveKey="class"
        items={[
          { key: 'class', label: '班级课表', children: <ClassScheduleView /> },
          { key: 'teacher', label: '教师课表', children: <TeacherScheduleView /> },
          { key: 'classroom', label: '教室课表', children: <ClassroomScheduleView /> },
          { key: 'grade', label: '年级总课表', children: <GradeScheduleView /> },
        ]}
      />
    </Card>
  );
}
