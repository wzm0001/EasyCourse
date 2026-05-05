import { Steps } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import { CheckOutlined } from '@ant-design/icons';

const steps = [
  { title: '学期设置', path: '/semesters' },
  { title: '年级与时间段', path: '/periods' },
  { title: '基础数据', path: '/basic-data' },
  { title: '教学安排', path: '/teaching-classes' },
  { title: '排课规则', path: '/constraints' },
  { title: '排课操作', path: '/schedule' },
  { title: '课表查看与导出', path: '/schedule-view' },
];

export default function ScheduleStepper() {
  const navigate = useNavigate();
  const location = useLocation();

  const currentStep = steps.findIndex((s) => location.pathname.startsWith(s.path));

  return (
    <Steps
      current={currentStep}
      size="small"
      style={{ marginBottom: 24 }}
      items={steps.map((step, index) => ({
        title: step.title,
        status: index < currentStep ? 'finish' : index === currentStep ? 'process' : 'wait',
        icon: index < currentStep ? <CheckOutlined /> : undefined,
      }))}
      onChange={(index) => {
        navigate(steps[index].path);
      }}
    />
  );
}
