import { Card, Col, Row, Statistic, Typography, Space, Tag } from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  ScheduleOutlined,
  ShopOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '@/store/auth';
import { UserRole } from '@/types/auth';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

const roleLabels: Record<string, { label: string; color: string }> = {
  [UserRole.SUPER_ADMIN]: { label: 'Super Admin', color: 'red' },
  [UserRole.SCHOOL_ADMIN]: { label: 'School Admin', color: 'blue' },
  [UserRole.TEACHER]: { label: 'Teacher', color: 'green' },
};

export default function Dashboard() {
  const user = useAuthStore((s) => s.user);
  const roleInfo = user ? roleLabels[user.role] || { label: 'Unknown', color: 'default' } : { label: 'Unknown', color: 'default' };

  return (
    <div>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Title level={4} style={{ marginBottom: 4 }}>
            Welcome, {user?.real_name || user?.username || 'User'}
          </Title>
          <Space>
            <Text type="secondary">
              {dayjs().format('dddd, MMMM D, YYYY')}
            </Text>
            <Tag color={roleInfo.color}>{roleInfo.label}</Tag>
            {user?.school_name && <Tag>{user.school_name}</Tag>}
          </Space>
        </div>

        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Total Teachers"
                value={0}
                prefix={<UserOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Total Classes"
                value={0}
                prefix={<TeamOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Schedules"
                value={0}
                prefix={<ScheduleOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Schools"
                value={0}
                prefix={<ShopOutlined />}
              />
            </Card>
          </Col>
        </Row>

        <Card title="System Overview">
          <Text type="secondary">
            This is the class scheduling system dashboard. Use the sidebar to navigate to different
            modules for managing schools, teachers, classes, and generating schedules.
          </Text>
        </Card>
      </Space>
    </div>
  );
}
