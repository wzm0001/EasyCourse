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
  [UserRole.SUPER_ADMIN]: { label: '超级管理员', color: 'red' },
  [UserRole.SCHOOL_ADMIN]: { label: '学校管理员', color: 'blue' },
  [UserRole.TEACHER]: { label: '教师', color: 'green' },
};

export default function Dashboard() {
  const user = useAuthStore((s) => s.user);
  const roleInfo = user ? roleLabels[user.role] || { label: '未知', color: 'default' } : { label: '未知', color: 'default' };

  return (
    <div>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Title level={4} style={{ marginBottom: 4 }}>
            欢迎，{user?.real_name || user?.username || '用户'}
          </Title>
          <Space>
            <Text type="secondary">
              {dayjs().format('YYYY年MM月DD日 dddd')}
            </Text>
            <Tag color={roleInfo.color}>{roleInfo.label}</Tag>
            {user?.school_name && <Tag>{user.school_name}</Tag>}
          </Space>
        </div>

        <Row gutter={[16, 12]}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="教师总数"
                value={0}
                prefix={<UserOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="班级总数"
                value={0}
                prefix={<TeamOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="排课数量"
                value={0}
                prefix={<ScheduleOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="学校数量"
                value={0}
                prefix={<ShopOutlined />}
              />
            </Card>
          </Col>
        </Row>

        <Card title="系统概览">
          <Text type="secondary">
            这是智能排课系统仪表盘。使用左侧菜单导航到不同模块，管理学校、教师、班级和生成课表。
          </Text>
        </Card>
      </Space>
    </div>
  );
}
