import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const SYSTEM_NAME = '中小学走班排课系统';

const routeTitleMap: Record<string, string> = {
  '/dashboard': '仪表盘',
  '/schools': '学校管理',
  '/approvals': '审批管理',
  '/users': '管理员用户管理',
  '/semesters': '学期管理',
  '/periods': '时间段配置',
  '/basic-data': '基础数据',
  '/constraints': '排课规则',
  '/schedule': '排课操作',
  '/schedule-wizard': '排课操作',
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

export function useDocumentTitle() {
  const location = useLocation();

  useEffect(() => {
    if (location.pathname === '/login') {
      document.title = SYSTEM_NAME;
      return;
    }

    const pageName = routeTitleMap[location.pathname];
    if (pageName) {
      document.title = `${pageName} - ${SYSTEM_NAME}`;
    } else {
      document.title = SYSTEM_NAME;
    }
  }, [location.pathname]);
}
