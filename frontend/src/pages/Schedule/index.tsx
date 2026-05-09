import { useState, useEffect, useCallback, useRef } from 'react';
import { Card, Select, Space, App, Modal, Alert, Checkbox } from 'antd';
import { LockOutlined, UnlockOutlined, DeleteOutlined, SwapOutlined } from '@ant-design/icons';
import { useResponsive } from '@/hooks/useResponsive';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import ScheduleGrid from './ScheduleGrid';
import ScheduleToolbar from './ScheduleToolbar';
import ConflictAlert from './ConflictAlert';
import DragLayer from './DragLayer';
import TeacherPanel from './TeacherPanel';
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
  lockCell,
  unlockCell,
  swapCells,
  dragDropCell,
  moveCell,
  checkConflicts,
} from '@/api/schedules';
import { getGrades, getClasses, getTeachers } from '@/api/basicData';
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

function buildPeriods(grade: any) {
  const periods = [];
  const mr = grade?.morning_reading_count ?? 1;
  const rc = grade?.regular_class_count ?? 8;
  const es = grade?.evening_study_count ?? 0;
  for (let i = 1; i <= mr; i++) {
    periods.push({ key: `morning_reading_${i}`, label: `早读${i}`, period_type: 'morning_reading', period_index: i });
  }
  for (let i = 1; i <= rc; i++) {
    periods.push({ key: `regular_${i}`, label: `第${i}节`, period_type: 'regular', period_index: i });
  }
  for (let i = 1; i <= es; i++) {
    periods.push({ key: `evening_study_${i}`, label: `晚自习${i}`, period_type: 'evening_study', period_index: i });
  }
  return periods;
}

function parsePeriodKey(periodKey: string): { period_type: string; period_index: number } | null {
  const match = periodKey.match(/^(morning_reading|regular|evening_study)_(\d+)$/);
  if (!match) return null;
  return { period_type: match[1], period_index: parseInt(match[2]) };
}

export default function Schedule({ embedded }: { embedded?: boolean } = {}) {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const [semesters, setSemesters] = useState<any[]>([]);
  const [grades, setGrades] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [teachers, setTeachers] = useState<any[]>([]);
  const [selectedSemester, setSelectedSemester] = useState<string>('');
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  const [selectedClass, setSelectedClass] = useState<string>('');
  const [scheduleData, setScheduleData] = useState<Record<string, Record<string, any | null>>>({});
  const [conflicts, setConflicts] = useState<any[]>([]);
  const [lockStatus, setLockStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [swapSource, setSwapSource] = useState<{ periodKey: string; dayKey: string; cell: any } | null>(null);
  const [hoverConflicts, setHoverConflicts] = useState<any[]>([]);
  const [periods, setPeriods] = useState(buildPeriods(null));

  useEffect(() => {
    getSemesters({ page: 1, page_size: 100 }).then((res) => {
      setSemesters(res.items || []);
      const active = res.items?.find((s: any) => s.status === 'in_progress');
      if (active) setSelectedSemester(active.id);
    });
  }, []);

  useEffect(() => {
    if (selectedSemester) {
      getGrades({ page: 1, page_size: 100, semester_id: selectedSemester }).then((res) => {
        setGrades(res.items || []);
        setSelectedGrade('');
        setSelectedClass('');
        setClasses([]);
        setScheduleData({});
        setConflicts([]);
      });
    } else {
      setGrades([]);
      setSelectedGrade('');
      setSelectedClass('');
      setClasses([]);
      setScheduleData({});
      setConflicts([]);
    }
  }, [selectedSemester]);

  useEffect(() => {
    if (selectedGrade && selectedSemester) {
      getClasses({ page: 1, page_size: 200, grade_id: selectedGrade, semester_id: selectedSemester }).then((res) => {
        setClasses(res.items || []);
        if (res.items?.length > 0) setSelectedClass(res.items[0].id);
        else setSelectedClass('');
      });
      const grade = grades.find((g) => g.id === selectedGrade);
      setPeriods(buildPeriods(grade));
    } else {
      setClasses([]);
      setSelectedClass('');
      setPeriods(buildPeriods(null));
    }
  }, [selectedGrade, grades, selectedSemester]);

  useEffect(() => {
    if (selectedSemester) {
      getTeachers({ page: 1, page_size: 200, semester_id: selectedSemester }).then((res) => {
        setTeachers(res.items || []);
      });
    }
  }, [selectedSemester]);

  const refreshTeachers = useCallback(() => {
    if (selectedSemester) {
      getTeachers({ page: 1, page_size: 200, semester_id: selectedSemester }).then((res) => {
        setTeachers(res.items || []);
      });
    }
  }, [selectedSemester]);

  const loadSchedule = useCallback(async () => {
    if (!selectedClass || !selectedSemester) return;
    try {
      const res = await getClassSchedule(selectedClass, selectedSemester);
      const grid: Record<string, Record<string, any | null>> = {};
      const cells = res.data?.cells || [];
      for (const cell of cells) {
        const pKey = `${cell.period_type}_${cell.period_index}`;
        const dKey = String(cell.day_of_week);
        if (!grid[pKey]) grid[pKey] = {};
        grid[pKey][dKey] = cell;
      }
      setScheduleData(grid);
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
    if (swapSource) {
      if (cell && swapSource.cell.id === cell.id) {
        setSwapSource(null);
        return;
      }
      handleSwap(periodKey, dayKey, cell);
      return;
    }
    if (cell) {
      Modal.confirm({
        title: '课程操作',
        content: (
          <Space direction="vertical">
            <span>{cell.course_name} - {cell.teacher_name}</span>
            <Space wrap>
              {cell.is_locked ? (
                <a onClick={async () => { try { await unlockCell(cell.id); message.success('已取消锁定'); loadSchedule(); Modal.destroyAll(); } catch { message.error('操作失败'); } }}>
                  <UnlockOutlined /> 取消锁定
                </a>
              ) : (
                <a onClick={async () => { try { await lockCell(cell.id); message.success('已锁定，一键排课不会重排此课程'); loadSchedule(); Modal.destroyAll(); } catch { message.error('操作失败'); } }}>
                  <LockOutlined /> 锁定课程
                </a>
              )}
              {!cell.is_locked && (
                <>
                  <a onClick={() => { setSwapSource({ periodKey, dayKey, cell }); Modal.destroyAll(); message.info('请点击目标位置进行交换（可切换班级选择目标）'); }}>
                    <SwapOutlined /> 交换位置
                  </a>
                  <a onClick={async () => { try { await removeCell(cell.id); message.success('已移除'); loadSchedule(); Modal.destroyAll(); } catch { message.error('操作失败'); } }}>
                    <DeleteOutlined /> 移除课程
                  </a>
                </>
              )}
            </Space>
          </Space>
        ),
        okText: '关闭',
        cancelText: undefined,
      });
    }
  };

  const handleSwap = async (targetPeriodKey: string, targetDayKey: string, targetCell: any | null) => {
    if (!swapSource) return;
    try {
      if (targetCell) {
        await swapCells({ cell_id_1: swapSource.cell.id, cell_id_2: targetCell.id });
        message.success('交换成功');
      } else {
        message.warning('请选择一个有课程的单元格进行交换');
        return;
      }
      loadSchedule();
    } catch (e: any) {
      message.error(e?.response?.data?.detail || '操作失败');
    }
    setSwapSource(null);
  };

  const handleDragDropTeacher = useCallback(async (teacher: any, targetDayKey: string, periodInfo: { period_type: string; period_index: number }, courseId?: string) => {
    try {
      await dragDropCell({
        teacher_id: teacher.id,
        target_class_id: selectedClass,
        target_day_of_week: parseInt(targetDayKey),
        target_period_type: periodInfo.period_type,
        target_period_index: periodInfo.period_index,
        course_id: courseId,
      });
      message.success('排课成功');
      loadSchedule();
    } catch (e: any) {
      message.error(e?.response?.data?.detail || '排课失败');
    }
  }, [selectedClass, loadSchedule, message]);

  const handleDragDropCell = useCallback(async (sourceCell: any, targetDayKey: string, periodInfo: { period_type: string; period_index: number }) => {
    if (sourceCell.is_locked) {
      message.warning('锁定的课程不可移动');
      return;
    }
    try {
      const res = await moveCell({
        cell_id: sourceCell.id,
        target_day_of_week: parseInt(targetDayKey),
        target_period_type: periodInfo.period_type,
        target_period_index: periodInfo.period_index,
      });
      if (res.data?.code === 0) {
        message.warning(res.data?.message || '移动成功，但存在冲突');
      } else {
        message.success('移动成功');
      }
      loadSchedule();
    } catch (e: any) {
      message.error(e?.response?.data?.detail || '移动失败');
    }
  }, [loadSchedule, message]);

  const hoverCellTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleHoverCellConflictCheck = useCallback((cellId: string, teacherId: string, classroomId: string, classId: string, dayKey: string, periodInfo: { period_type: string; period_index: number }) => {
    if (hoverCellTimerRef.current) {
      clearTimeout(hoverCellTimerRef.current);
    }
    hoverCellTimerRef.current = setTimeout(async () => {
      try {
        const res = await checkConflicts({
          teacher_id: teacherId || undefined,
          classroom_id: classroomId || undefined,
          class_id: classId || undefined,
          day_of_week: parseInt(dayKey),
          period_type: periodInfo.period_type,
          period_index: periodInfo.period_index,
          exclude_cell_id: cellId,
        });
        setHoverConflicts(res.data || []);
      } catch {
        setHoverConflicts([]);
      }
    }, 200);
  }, []);

  const hoverTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleHoverConflictCheck = useCallback(async (teacherId: string, dayKey: string, periodInfo: { period_type: string; period_index: number }) => {
    if (hoverTimerRef.current) {
      clearTimeout(hoverTimerRef.current);
    }
    hoverTimerRef.current = setTimeout(async () => {
      try {
        const res = await checkConflicts({
          teacher_id: teacherId,
          class_id: selectedClass,
          day_of_week: parseInt(dayKey),
          period_type: periodInfo.period_type,
          period_index: periodInfo.period_index,
        });
        setHoverConflicts(res.data || []);
      } catch {
        setHoverConflicts([]);
      }
    }, 200);
  }, [selectedClass]);

  const handleClearHoverConflicts = useCallback(() => {
    if (hoverTimerRef.current) {
      clearTimeout(hoverTimerRef.current);
      hoverTimerRef.current = null;
    }
    if (hoverCellTimerRef.current) {
      clearTimeout(hoverCellTimerRef.current);
      hoverCellTimerRef.current = null;
    }
    setHoverConflicts([]);
  }, []);

  const handleAutoSchedule = async (keepLocked: boolean = true) => {
    setLoading(true);
    try {
      await autoSchedule({ semester_id: selectedSemester, grade_id: selectedGrade, keep_locked: keepLocked });
      message.success('排课完成');
      loadSchedule();
    } catch {
      message.error('排课失败');
    } finally {
      setLoading(false);
    }
  };

  const handleClearSchedule = async (keepLocked: boolean = true) => {
    setLoading(true);
    try {
      await clearSchedule({ semester_id: selectedSemester, grade_id: selectedGrade, keep_locked: keepLocked });
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
      {!embedded && <ScheduleStepper />}

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

      <ConflictAlert conflicts={[...conflicts, ...hoverConflicts]} />

      {swapSource && (
        <Alert
          type="info"
          message={`已选择「${swapSource.cell.course_name} - ${swapSource.cell.teacher_name}」，请点击目标课程进行交换（可切换班级/年级选择目标，点击同一课程取消）`}
          closable
          onClose={() => setSwapSource(null)}
          style={{ marginBottom: 16 }}
        />
      )}

      <div style={{ display: 'flex', gap: 16 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <ScheduleGrid
            periods={periods}
            days={defaultDays}
            data={scheduleData}
            onCellClick={handleCellClick}
            viewMode="class"
            swapSourceCellId={swapSource?.cell?.id || null}
            onDragDropTeacher={handleDragDropTeacher}
            onDragDropCell={handleDragDropCell}
            onHoverConflictCheck={handleHoverConflictCheck}
            onHoverCellConflictCheck={handleHoverCellConflictCheck}
            onClearHoverConflicts={handleClearHoverConflicts}
          />
        </div>
        {!isMobile && (
          <div style={{ width: 240, flexShrink: 0 }}>
            <TeacherPanel teachers={teachers} selectedClassId={selectedClass} onRefresh={refreshTeachers} />
          </div>
        )}
      </div>

      <DragLayer />
    </>
  );

  return (
    <DndProvider backend={HTML5Backend}>
      {embedded ? content : <Card title="排课操作">{content}</Card>}
    </DndProvider>
  );
}
