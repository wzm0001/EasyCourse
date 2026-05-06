import { Layout, Drawer } from 'antd';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { useAppStore } from '@/store/app';
import { useResponsive } from '@/hooks/useResponsive';
import { getUnreadCount } from '@/api/notifications';
import { useEffect } from 'react';
import { useAuthStore } from '@/store/auth';

const { Sider, Content } = Layout;

export default function MainLayout() {
  const { sidebarCollapsed, theme, mobileDrawerOpen, setMobileDrawerOpen, setUnreadCount } = useAppStore();
  const { isMobile } = useResponsive();
  const token = useAuthStore((s) => s.token);

  useEffect(() => {
    if (!token) return;
    const fetchUnread = () => {
      getUnreadCount()
        .then((res) => setUnreadCount(res.data || 0))
        .catch(() => {});
    };
    fetchUnread();
    const interval = setInterval(fetchUnread, 30000);
    return () => clearInterval(interval);
  }, [token]);

  const sidebarContent = <Sidebar onMenuClick={() => { if (isMobile) setMobileDrawerOpen(false); }} />;

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {isMobile ? (
        <Drawer
          placement="left"
          open={mobileDrawerOpen}
          onClose={() => setMobileDrawerOpen(false)}
          width={260}
          styles={{ body: { padding: 0, background: theme === 'dark' ? '#141414' : '#fff' } }}
          destroyOnHidden
        >
          <div
            style={{
              height: 64,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#1677ff',
              fontSize: 18,
              fontWeight: 700,
              borderBottom: `1px solid ${theme === 'dark' ? '#303030' : '#f0f0f0'}`,
            }}
          >
            智能排课系统
          </div>
          {sidebarContent}
        </Drawer>
      ) : (
        <Sider
          trigger={null}
          collapsible
          collapsed={sidebarCollapsed}
          width={220}
          collapsedWidth={80}
          theme={theme === 'dark' ? 'dark' : 'light'}
          style={{
            overflow: 'auto',
            height: '100vh',
            position: 'fixed',
            left: 0,
            top: 0,
            bottom: 0,
            zIndex: 10,
          }}
        >
          <div
            style={{
              height: 64,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: theme === 'dark' ? '#fff' : '#1677ff',
              fontSize: sidebarCollapsed ? 16 : 20,
              fontWeight: 700,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              borderBottom: `1px solid ${theme === 'dark' ? '#303030' : '#f0f0f0'}`,
            }}
          >
            {sidebarCollapsed ? '排课' : '智能排课系统'}
          </div>
          <Sidebar />
        </Sider>
      )}
      <Layout
        style={{
          marginLeft: isMobile ? 0 : (sidebarCollapsed ? 80 : 220),
          transition: isMobile ? 'none' : 'margin-left 0.2s',
        }}
      >
        <Header />
        <Content
          style={{
            margin: isMobile ? 12 : 24,
            padding: isMobile ? 12 : 24,
            minHeight: 280,
            background: theme === 'dark' ? '#141414' : '#fff',
            borderRadius: 8,
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
