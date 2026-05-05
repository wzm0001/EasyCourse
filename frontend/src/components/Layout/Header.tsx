import { Layout, Dropdown, Switch, Breadcrumb, Badge, Avatar, Space } from 'antd';
import {
  BellOutlined,
  UserOutlined,
  LogoutOutlined,
  KeyOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  SunOutlined,
  MoonOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/auth';
import { useAppStore } from '@/store/app';
import { getUnreadCount } from '@/api/notifications';
import type { MenuProps } from 'antd';
import { useState, useEffect } from 'react';

const breadcrumbNameMap: Record<string, string> = {
  '/dashboard': '仪表盘',
  '/schools': '学校管理',
  '/approvals': '审批管理',
  '/users': '用户管理',
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
  const { theme, toggleTheme, sidebarCollapsed, toggleSidebar } = useAppStore();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const fetchUnread = () => {
      getUnreadCount()
        .then((res) => setUnreadCount(res.data || 0))
        .catch(() => {});
    };
    fetchUnread();
    const interval = setInterval(fetchUnread, 60000);
    return () => clearInterval(interval);
  }, []);

  const pathSnippets = location.pathname.split('/').filter((i) => i);
  const breadcrumbItems = [
    { title: '首页' },
    ...pathSnippets.map((_, index) => {
      const url = `/${pathSnippets.slice(0, index + 1).join('/')}`;
      return {
        title: breadcrumbNameMap[url] || url,
      };
    }),
  ];

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
    },
    {
      key: 'password',
      icon: <KeyOutlined />,
      label: '修改密码',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
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

  return (
    <Layout.Header
      style={{
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: theme === 'dark' ? '#141414' : '#fff',
        borderBottom: `1px solid ${theme === 'dark' ? '#303030' : '#f0f0f0'}`,
      }}
    >
      <Space size="middle">
        <span
          onClick={toggleSidebar}
          style={{ fontSize: 18, cursor: 'pointer', lineHeight: '64px' }}
        >
          {sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
        </span>
        <Breadcrumb items={breadcrumbItems} />
      </Space>

      <Space size="middle">
        <Badge count={unreadCount} size="small" onClick={() => navigate('/notifications')} style={{ cursor: 'pointer' }}>
          <BellOutlined style={{ fontSize: 18, cursor: 'pointer' }} />
        </Badge>

        <Switch
          checked={theme === 'dark'}
          onChange={toggleTheme}
          checkedChildren={<MoonOutlined />}
          unCheckedChildren={<SunOutlined />}
        />

        <Dropdown menu={{ items: userMenuItems, onClick: handleUserMenuClick }} placement="bottomRight">
          <Space style={{ cursor: 'pointer' }}>
            <Avatar icon={<UserOutlined />} />
            <span>{user?.real_name || user?.username || '用户'}</span>
          </Space>
        </Dropdown>
      </Space>
    </Layout.Header>
  );
}
