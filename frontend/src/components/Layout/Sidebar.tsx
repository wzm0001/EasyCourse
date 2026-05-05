import { Menu } from 'antd';
import {
  DashboardOutlined,
  ShopOutlined,
  AuditOutlined,
  SettingOutlined,
  FileTextOutlined,
  CloudServerOutlined,
  ScheduleOutlined,
  DatabaseOutlined,
  TableOutlined,
  CalendarOutlined,
  UserOutlined,
  TeamOutlined,
  BellOutlined,
  SwapOutlined,
  ExportOutlined,
  SafetyCertificateOutlined,
  ClockCircleOutlined,
  UserSwitchOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/auth';
import { useAppStore } from '@/store/app';
import { UserRole } from '@/types/auth';
import type { MenuProps } from 'antd';

const superAdminMenus: MenuProps['items'] = [
  {
    key: '/dashboard',
    icon: <DashboardOutlined />,
    label: '仪表盘',
  },
  {
    key: '/schools',
    icon: <ShopOutlined />,
    label: '学校管理',
  },
  {
    key: '/approvals',
    icon: <AuditOutlined />,
    label: '审批管理',
  },
  {
    key: '/users',
    icon: <UserSwitchOutlined />,
    label: '用户管理',
  },
  {
    key: '/logs',
    icon: <FileTextOutlined />,
    label: '日志管理',
  },
  {
    key: '/backups',
    icon: <CloudServerOutlined />,
    label: '备份还原',
  },
  {
    key: '/settings',
    icon: <SettingOutlined />,
    label: '系统设置',
  },
];

const schoolAdminMenus: MenuProps['items'] = [
  {
    key: '/dashboard',
    icon: <DashboardOutlined />,
    label: '仪表盘',
  },
  {
    key: '/semesters',
    icon: <CalendarOutlined />,
    label: '学期管理',
  },
  {
    key: '/periods',
    icon: <ClockCircleOutlined />,
    label: '时间段配置',
  },
  {
    key: '/basic-data',
    icon: <DatabaseOutlined />,
    label: '基础数据',
  },
  {
    key: '/teaching-classes',
    icon: <SwapOutlined />,
    label: '教学班管理',
  },
  {
    key: '/constraints',
    icon: <SafetyCertificateOutlined />,
    label: '排课规则',
  },
  {
    key: '/schedule',
    icon: <TableOutlined />,
    label: '排课操作',
  },
  {
    key: '/schedule-view',
    icon: <ScheduleOutlined />,
    label: '课表查看',
  },
  {
    key: '/export',
    icon: <ExportOutlined />,
    label: '课表导出',
  },
  {
    key: '/users',
    icon: <TeamOutlined />,
    label: '教师管理',
  },
  {
    key: '/notifications',
    icon: <BellOutlined />,
    label: '通知中心',
  },
  {
    key: '/school-settings',
    icon: <SettingOutlined />,
    label: '学校设置',
  },
];

const teacherMenus: MenuProps['items'] = [
  {
    key: '/dashboard',
    icon: <DashboardOutlined />,
    label: '仪表盘',
  },
  {
    key: '/my-schedule',
    icon: <UserOutlined />,
    label: '我的课表',
  },
  {
    key: '/class-schedule',
    icon: <TeamOutlined />,
    label: '班级课表',
  },
  {
    key: '/notifications',
    icon: <BellOutlined />,
    label: '通知中心',
  },
];

const menuMap: Record<string, MenuProps['items']> = {
  [UserRole.SUPER_ADMIN]: superAdminMenus,
  [UserRole.SCHOOL_ADMIN]: schoolAdminMenus,
  [UserRole.TEACHER]: teacherMenus,
};

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const user = useAuthStore((s) => s.user);
  const sidebarCollapsed = useAppStore((s) => s.sidebarCollapsed);

  const menuItems = user ? menuMap[user.role] || [] : [];

  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    navigate(key);
  };

  return (
    <Menu
      mode="inline"
      selectedKeys={[location.pathname]}
      items={menuItems}
      onClick={handleMenuClick}
      style={{ height: '100%', borderRight: 0 }}
      inlineCollapsed={sidebarCollapsed}
    />
  );
}
