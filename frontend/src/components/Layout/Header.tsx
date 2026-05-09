import { Layout, Dropdown, Switch, Breadcrumb, Badge, Avatar, Space, Tag, Tooltip } from 'antd';
import {
  BellOutlined,
  UserOutlined,
  LogoutOutlined,
  KeyOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  SunOutlined,
  MoonOutlined,
  MenuOutlined,
  LockOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/auth';
import { useAppStore } from '@/store/app';
import { useResponsive } from '@/hooks/useResponsive';
import type { MenuProps } from 'antd';

const breadcrumbNameMap: Record<string, string> = {
  '/dashboard': '仪表盘',
  '/schools': '学校管理',
  '/approvals': '审批管理',
  '/users': '管理员用户管理',
  '/semesters': '学期管理',
  '/periods': '时间段配置',
  '/basic-data': '基础数据',
  '/constraints': '排课规则',
  '/schedule': '排课操作',
  '/schedule-view': '课表查看',
  '/export': '课表导出',
  '/teaching-classes': '教学班管理',
  '/notifications': '通知中心',
  '/logs': '日志管理',
  '/backups': '备份还原',
  '/settings': '系统设置',
  '/school-settings': '学校设置',
  '/profile': '个人信息',
  '/my-schedule': '我的课表',
  '/class-schedule': '班级课表',
};

export default function Header() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { theme, toggleTheme, sidebarCollapsed, toggleSidebar, setMobileDrawerOpen, unreadCount, currentSemesterName, currentSemesterArchived } = useAppStore();
  const { isMobile } = useResponsive();

  const pathSnippets = location.pathname.split('/').filter((i) => i);
  const breadcrumbItems = [
    { title: '首页' },
    ...pathSnippets.map((_, index) => {
      const url = `/${pathSnippets.slice(0, index + 1).join('/')}`;
      return { title: breadcrumbNameMap[url] || url };
    }),
  ];

  const userMenuItems: MenuProps['items'] = [
    { key: 'profile', icon: <UserOutlined />, label: '个人信息' },
    { key: 'password', icon: <KeyOutlined />, label: '修改密码' },
    { type: 'divider' },
    { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', danger: true },
  ];

  const handleUserMenuClick: MenuProps['onClick'] = ({ key }) => {
    switch (key) {
      case 'logout':
        logout();
        navigate('/login');
        break;
      case 'profile':
        navigate('/profile');
        break;
      case 'password':
        navigate('/profile');
        break;
    }
  };

  const toggleIconSize = isMobile ? 22 : 18;

  return (
    <Layout.Header
      style={{
        padding: isMobile ? '0 12px' : '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: theme === 'dark' ? '#141414' : '#fff',
        borderBottom: `1px solid ${theme === 'dark' ? '#303030' : '#f0f0f0'}`,
        height: isMobile ? 56 : 64,
        lineHeight: isMobile ? '56px' : '64px',
      }}
    >
      <Space size="middle">
        {isMobile ? (
          <span
            onClick={() => setMobileDrawerOpen(true)}
            style={{ fontSize: toggleIconSize, cursor: 'pointer', lineHeight: 'inherit', padding: '8px' }}
          >
            <MenuOutlined />
          </span>
        ) : (
          <span
            onClick={toggleSidebar}
            style={{ fontSize: toggleIconSize, cursor: 'pointer', lineHeight: 'inherit', padding: '8px' }}
          >
            {sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          </span>
        )}
        {!isMobile && <Breadcrumb items={breadcrumbItems} />}
        {isMobile && (
          <span style={{ fontSize: 16, fontWeight: 600, color: theme === 'dark' ? '#fff' : '#333' }}>
            {breadcrumbNameMap[location.pathname] || '智能排课系统'}
          </span>
        )}
      </Space>

      <Space size={isMobile ? 'small' : 'middle'}>
        {currentSemesterName && (
          currentSemesterArchived ? (
            <Tooltip title="当前学期已归档，数据为只读状态">
              <Tag color="red" icon={<LockOutlined />}>{currentSemesterName} (已归档)</Tag>
            </Tooltip>
          ) : (
            <Tag color="blue">{currentSemesterName}</Tag>
          )
        )}
        <Badge count={unreadCount} onClick={() => navigate('/notifications')} style={{ cursor: 'pointer' }}>
          <BellOutlined style={{ fontSize: isMobile ? 20 : 18, cursor: 'pointer', padding: '4px' }} />
        </Badge>

        {!isMobile && (
          <Switch
            checked={theme === 'dark'}
            onChange={toggleTheme}
            checkedChildren={<MoonOutlined />}
            unCheckedChildren={<SunOutlined />}
          />
        )}

        <Dropdown menu={{ items: userMenuItems, onClick: handleUserMenuClick }} placement="bottomRight">
          <Space style={{ cursor: 'pointer' }}>
            <Avatar icon={<UserOutlined />} size={isMobile ? 'small' : 'default'} />
            {!isMobile && <span>{user?.real_name || user?.username || '用户'}</span>}
          </Space>
        </Dropdown>
      </Space>
    </Layout.Header>
  );
}
