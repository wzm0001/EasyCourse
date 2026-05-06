import { useState, useEffect, useCallback } from 'react';
import { Card, Select, Space, App, Modal, Alert } from 'antd';
import { LockOutlined, UnlockOutlined, DeleteOutlined, SwapOutlined } from '@ant-design/icons';
import { useResponsive } from '@/hooks/useResponsive';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import ScheduleGrid from './ScheduleGrid';
import ScheduleToolbar from './ScheduleToolbar';
import ConflictAlert from './ConflictAlert';
import DragLayer from './DragLayer';
import ScheduleStepper from '@/components/ScheduleStepper';
import {
  getClassSchedule,
  autoSchedule,
  clearSchedule,
  getLockStatus,
  acquireLock,
  releaseLock,
  placeCell,
  removeCell,
  fixCell,
  unfixCell,
  swapCells,
} from '@/api/schedules';
import { getGrades, getClasses } from '@/api/basicData';
import { getSemesters } from '@/api/semesters';

const defaultDays = [
  { key: '1', label: '周一' },
  { key: '2', label: '周二' },
  { key: '3', label: '周三' },
  { key: '4', label: '周四' },
  { key: '5', label: '周五' },
  { key: '6', label: '周六' },
  { key: '7', label: '周日' },
];

const defaultPeriods = [
  { key: 'morning_1', label: '早读1' },
  { key: 'morning_2', label: '早读2' },
  { key: 'class_1', label: '第1节' },
  { key: 'class_2', label: '第2节' },
  { key: 'class_3', label: '第3节' },
  { key: 'class_4', label: '第4节' },
  { key: 'class_5', label: '第5节' },
  { key: 'class_6', label: '第6节' },
  { key: 'class_7', label: '第7节' },
  { key: 'class_8', label: '第8节' },
  { key: 'evening_1', label: '晚自习1' },
  { key: 'evening_2', label: '晚自习2' },
];

export default function Schedule({ embedded }: { embedded?: boolean } = {}) {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const [semesters, setSemesters] = useState<any[]>([]);
  const [grades, setGrades] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [selectedSemester, setSelectedSemester] = useState<string>('');
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  const [selectedClass, setSelectedClass] = useState<string>('');
  const [scheduleData, setScheduleData] = useState<Record<string, Record<string, any | null>>>({});
  const [conflicts, setConflicts] = useState<any[]>([]);
  const [lockStatus, setLockStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [swapSource, setSwapSource] = useState<{ periodKey: string; dayKey: string; cell: any } | null>(null);

  useEffect(() => {
    getSemesters({ page: 1, page_size: 100 }).then((res) => {
      setSemesters(res.items || []);
      const active = res.items?.find((s: any) => s.status === 'in_progress');
      if (active) setSelectedSemester(active.id);
    });
    getGrades({ page: 1, page_size: 100 }).then((res) => setGrades(res.items || []));
  }, []);

  useEffect(() => {
    if (selectedGrade) {
      getClasses({ page: 1, page_size: 200, grade_id: selectedGrade }).then((res) => {
        setClasses(res.items || []);
        if (res.items?.length > 0) setSelectedClass(res.items[0].id);
      });
    }
  }, [selectedGrade]);

  const loadSchedule = useCallback(async () => {
    if (!selectedClass || !selectedSemester) return;
    try {
      const res = await getClassSchedule(selectedClass, selectedSemester);
      setScheduleData(res.data?.grid || {});
      setConflicts(res.data?.conflicts || []);
    } catch {
      setScheduleData({});
      setConflicts([]);
    }
  }, [selectedClass, selectedSemester]);

  const loadLockStatus = useCallback(async () => {
    if (!selectedSemester) return;
    try {
      const res = await getLockStatus(selectedSemester);
      setLockStatus(res.data);
    } catch {
      setLockStatus(null);
    }
  }, [selectedSemester]);

  useEffect(() => {
    loadSchedule();
    loadLockStatus();
  }, [loadSchedule, loadLockStatus]);

  const handleCellClick = (periodKey: string, dayKey: string, cell: any | null) => {
    if (cell) {
      Modal.confirm({
        title: '课程操作',
        content: (
          <Space direction="vertical">
            <span>{cell.course_name} - {cell.teacher_name}</span>
            <Space>
              {cell.is_fixed ? (
                <a onClick={async () => { try { await unfixCell(cell.id); message.success('已取消固定'); loadSchedule(); Modal.destroyAll(); } catch { message.error('操作失败'); } }}>
                  <UnlockOutlined /> 取消固定
                </a>
              ) : (
                <a onClick={async () => { try { await fixCell(cell.id); message.success('已固定'); loadSchedule(); Modal.destroyAll(); } catch { message.error('操作失败'); } }}>
                  <LockOutlined /> 固定课程
                </a>
              )}
              <a onClick={() => { setSwapSource({ periodKey, dayKey, cell }); Modal.destroyAll(); message.info('请点击要交换的目标位置'); }}>
                <SwapOutlined /> 交换位置
              </a>
              <a onClick={async () => { try { await removeCell(cell.id); message.success('已移除'); loadSchedule(); Modal.destroyAll(); } catch { message.error('操作失败'); } }}>
                <DeleteOutlined /> 移除课程
              </a>
            </Space>
          </Space>
        ),
        okText: '关闭',
        cancelText: undefined,
      });
    } else if (swapSource) {
      handleSwap(periodKey, dayKey);
    } else {
      Modal.info({
        title: '放置课程',
        content: '请选择要放置的课程（此处应弹出课程选择器）',
      });
    }
  };

  const handleSwap = async (targetPeriodKey: string, targetDayKey: string) => {
    if (!swapSource) return;
    const targetCell = scheduleData[targetPeriodKey]?.[targetDayKey];
    if (targetCell && swapSource.cell) {
      try {
        await swapCells({ cell_id_1: swapSource.cell.id, cell_id_2: targetCell.id });
        message.success('交换成功');
        loadSchedule();
      } catch {
        message.error('交换失败');
      }
    } else if (swapSource.cell) {
      try {
        await placeCell({
          cell_id: swapSource.cell.id,
          target_period: targetPeriodKey,
          target_day: targetDayKey,
          class_id: selectedClass,
          semester_id: selectedSemester,
        });
        message.success('移动成功');
        loadSchedule();
      } catch {
        message.error('移动失败');
      }
    }
    setSwapSource(null);
  };

  const handleAutoSchedule = async () => {
    setLoading(true);
    try {
      await autoSchedule({ semester_id: selectedSemester, grade_id: selectedGrade });
      message.success('排课完成');
      loadSchedule();
    } catch {
      message.error('排课失败');
    } finally {
      setLoading(false);
    }
  };

  const handleClearSchedule = async () => {
    setLoading(true);
    try {
      await clearSchedule({ semester_id: selectedSemester, grade_id: selectedGrade });
      message.success('已清除');
      loadSchedule();
    } catch {
      message.error('清除失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAcquireLock = async () => {
    try {
      await acquireLock(selectedSemester);
      message.success('已锁定');
      loadLockStatus();
    } catch {
      message.error('锁定失败');
    }
  };

  const handleReleaseLock = async () => {
    try {
      await releaseLock(selectedSemester);
      message.success('已释放');
      loadLockStatus();
    } catch {
      message.error('释放失败');
    }
  };

  const content = (
    <>
      <ScheduleStepper />

      <Space style={{ marginBottom: 16 }} wrap>
        <span>学期：</span>
        <Select
          style={{ width: 220 }}
          value={selectedSemester}
          onChange={setSelectedSemester}
          options={semesters.map((s) => ({ label: s.name, value: s.id }))}
          placeholder="请选择学期"
        />
        <span>年级：</span>
        <Select
          style={{ width: 150 }}
          value={selectedGrade}
          onChange={setSelectedGrade}
          options={grades.map((g) => ({ label: g.name, value: g.id }))}
          placeholder="请选择年级"
        />
        <span>班级：</span>
        <Select
          style={{ width: 180 }}
          value={selectedClass}
          onChange={setSelectedClass}
          options={classes.map((c) => ({ label: c.name, value: c.id }))}
          placeholder="请选择班级"
        />
      </Space>

      <ScheduleToolbar
        lockStatus={lockStatus}
        onAutoSchedule={handleAutoSchedule}
        onClearSchedule={handleClearSchedule}
        onAcquireLock={handleAcquireLock}
        onReleaseLock={handleReleaseLock}
        loading={loading}
      />

      <ConflictAlert conflicts={conflicts} />

      {swapSource && (
        <Alert
          type="info"
          message={`已选择 ${swapSource.cell.course_name}，请点击目标位置进行交换`}
          closable
          onClose={() => setSwapSource(null)}
          style={{ marginBottom: 16 }}
        />
      )}

      <ScheduleGrid
        periods={defaultPeriods}
        days={defaultDays}
        data={scheduleData}
        onCellClick={handleCellClick}
        viewMode="class"
      />

      <DragLayer />
    </>
  );

  return (
    <DndProvider backend={HTML5Backend}>
      {embedded ? content : <Card title="排课操作">{content}</Card>}
    </DndProvider>
  );
}
