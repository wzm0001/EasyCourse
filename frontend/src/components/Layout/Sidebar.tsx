import { Menu, Badge } from 'antd';
import {
  DashboardOutlined,
  ShopOutlined,
  AuditOutlined,
  SettingOutlined,
  FileTextOutlined,
  CloudServerOutlined,
  ScheduleOutlined,
  UserOutlined,
  TeamOutlined,
  BellOutlined,
  UserSwitchOutlined,
  RocketOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/auth';
import { useAppStore } from '@/store/app';
import { UserRole } from '@/types/auth';
import type { MenuProps } from 'antd';
import { ReactNode } from 'react';

const superAdminMenus: MenuProps['items'] = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: '仪表盘' },
  { key: '/schools', icon: <ShopOutlined />, label: '学校管理' },
  { key: '/approvals', icon: <AuditOutlined />, label: '审批管理' },
  { key: '/users', icon: <UserSwitchOutlined />, label: '管理员用户管理' },
  { key: '/logs', icon: <FileTextOutlined />, label: '日志管理' },
  { key: '/backups', icon: <CloudServerOutlined />, label: '备份还原' },
  { key: '/settings', icon: <SettingOutlined />, label: '系统设置' },
];

function getSchoolAdminMenus(unreadCount: number): MenuProps['items'] {
  const notificationLabel: ReactNode = unreadCount > 0
    ? <span>通知中心 <Badge count={unreadCount} size="small" style={{ marginLeft: 4 }} /></span>
    : '通知中心';
  return [
    { key: '/dashboard', icon: <DashboardOutlined />, label: '仪表盘' },
    { key: '/schedule-wizard', icon: <RocketOutlined />, label: '排课操作' },
    { key: '/schedule-view', icon: <EyeOutlined />, label: '课表查看' },
    { key: '/users', icon: <TeamOutlined />, label: '教师管理' },
    { key: '/notifications', icon: <BellOutlined />, label: notificationLabel },
    { key: '/school-settings', icon: <SettingOutlined />, label: '学校设置' },
  ];
}

function getTeacherMenus(unreadCount: number): MenuProps['items'] {
  const notificationLabel: ReactNode = unreadCount > 0
    ? <span>通知中心 <Badge count={unreadCount} size="small" style={{ marginLeft: 4 }} /></span>
    : '通知中心';
  return [
    { key: '/dashboard', icon: <DashboardOutlined />, label: '仪表盘' },
    { key: '/my-schedule', icon: <UserOutlined />, label: '我的课表' },
    { key: '/class-schedule', icon: <TeamOutlined />, label: '班级课表' },
    { key: '/notifications', icon: <BellOutlined />, label: notificationLabel },
  ];
}

interface SidebarProps {
  onMenuClick?: () => void;
}

export default function Sidebar({ onMenuClick }: SidebarProps = {}) {
  const navigate = useNavigate();
  const location = useLocation();
  const user = useAuthStore((s) => s.user);
  const sidebarCollapsed = useAppStore((s) => s.sidebarCollapsed);
  const unreadCount = useAppStore((s) => s.unreadCount);

  const menuItems = user
    ? user.role === UserRole.SUPER_ADMIN
      ? superAdminMenus
      : user.role === UserRole.SCHOOL_ADMIN
        ? getSchoolAdminMenus(unreadCount)
        : getTeacherMenus(unreadCount)
    : [];

  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    navigate(key);
    onMenuClick?.();
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
