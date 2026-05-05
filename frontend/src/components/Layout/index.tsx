import { Layout } from 'antd';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { useAppStore } from '@/store/app';

const { Sider, Content } = Layout;

export default function MainLayout() {
  const { sidebarCollapsed, theme } = useAppStore();

  return (
    <Layout style={{ minHeight: '100vh' }}>
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
          {sidebarCollapsed ? 'SC' : 'ScheduleCraft'}
        </div>
        <Sidebar />
      </Sider>
      <Layout
        style={{
          marginLeft: sidebarCollapsed ? 80 : 220,
          transition: 'margin-left 0.2s',
        }}
      >
        <Header />
        <Content
          style={{
            margin: 24,
            padding: 24,
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
