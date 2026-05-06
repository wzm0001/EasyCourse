import { useState, useEffect } from 'react';
import { Card, Select, Space, Button, Radio, App } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { useResponsive } from '@/hooks/useResponsive';
import { exportClassExcel, exportClassPdf, exportTeacherExcel, exportTeacherPdf, batchExportTeachers, batchExportClasses, customExport } from '@/api/exports';
import { getSemesters } from '@/api/semesters';
import { getGrades, getClasses, getTeachers } from '@/api/basicData';
import CustomExportModal from './CustomExportModal';

export default function Export() {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const [semesters, setSemesters] = useState<any[]>([]);
  const [grades, setGrades] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [teachers, setTeachers] = useState<any[]>([]);
  const [selectedSemester, setSelectedSemester] = useState<string>('');
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  const [selectedTarget, setSelectedTarget] = useState<string>('');
  const [exportType, setExportType] = useState<'class' | 'teacher'>('class');
  const [format, setFormat] = useState<'excel' | 'pdf'>('excel');
  const [customOpen, setCustomOpen] = useState(false);

  useEffect(() => {
    getSemesters({ page: 1, page_size: 100 }).then((res) => {
      setSemesters(res.items || []);
      const active = res.items?.find((s: any) => s.status === 'in_progress');
      if (active) setSelectedSemester(active.id);
    });
    getGrades({ page: 1, page_size: 100 }).then((res) => setGrades(res.items || []));
    getTeachers({ page: 1, page_size: 200 }).then((res) => setTeachers(res.items || []));
  }, []);

  useEffect(() => {
    if (selectedGrade) {
      getClasses({ page: 1, page_size: 200, grade_id: selectedGrade }).then((res) => {
        setClasses(res.items || []);
        if (res.items?.length > 0) setSelectedTarget(res.items[0].id);
      });
    }
  }, [selectedGrade]);

  useEffect(() => {
    if (exportType === 'teacher' && teachers.length > 0) {
      setSelectedTarget(teachers[0].id);
    }
  }, [exportType, teachers]);

  const handleExport = async () => {
    if (!selectedTarget || !selectedSemester) {
      message.warning('请选择学期和导出目标');
      return;
    }
    try {
      if (exportType === 'class') {
        format === 'excel' ? await exportClassExcel(selectedTarget, selectedSemester) : await exportClassPdf(selectedTarget, selectedSemester);
      } else {
        format === 'excel' ? await exportTeacherExcel(selectedTarget, selectedSemester) : await exportTeacherPdf(selectedTarget, selectedSemester);
      }
      message.success('导出成功');
    } catch {
      message.error('导出失败');
    }
  };

  const handleBatchExport = async () => {
    if (!selectedGrade || !selectedSemester) {
      message.warning('请选择学期和年级');
      return;
    }
    try {
      if (exportType === 'class') {
        await batchExportClasses(selectedGrade, selectedSemester);
      } else {
        await batchExportTeachers(selectedGrade, selectedSemester);
      }
      message.success('批量导出成功');
    } catch {
      message.error('批量导出失败');
    }
  };

  const handleCustomExport = async (values: any) => {
    try {
      await customExport({ ...values, semester_id: selectedSemester, grade_id: selectedGrade });
      message.success('导出成功');
    } catch {
      message.error('导出失败');
    }
  };

  return (
    <Card title="课表导出">
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Space wrap>
          <span>学期：</span>
          <Select style={{ width: 220 }} value={selectedSemester} onChange={setSelectedSemester} options={semesters.map((s) => ({ label: s.name, value: s.id }))} placeholder="请选择学期" />
        </Space>

        <Space wrap>
          <span>导出类型：</span>
          <Radio.Group value={exportType} onChange={(e) => setExportType(e.target.value)}>
            <Radio value="class">班级课表</Radio>
            <Radio value="teacher">教师课表</Radio>
          </Radio.Group>
        </Space>

        <Space wrap>
          <span>导出格式：</span>
          <Radio.Group value={format} onChange={(e) => setFormat(e.target.value)}>
            <Radio value="excel">Excel</Radio>
            <Radio value="pdf">PDF</Radio>
          </Radio.Group>
        </Space>

        <Space wrap>
          <span>年级：</span>
          <Select style={{ width: 150 }} value={selectedGrade} onChange={setSelectedGrade} options={grades.map((g) => ({ label: g.name, value: g.id }))} placeholder="请选择年级" />
          <span>{exportType === 'class' ? '班级' : '教师'}：</span>
          <Select
            style={{ width: 200 }}
            value={selectedTarget}
            onChange={setSelectedTarget}
            options={exportType === 'class' ? classes.map((c) => ({ label: c.name, value: c.id })) : teachers.map((t) => ({ label: t.real_name, value: t.id }))}
            placeholder={exportType === 'class' ? '请选择班级' : '请选择教师'}
          />
        </Space>

        <Space>
          <Button type="primary" icon={<DownloadOutlined />} onClick={handleExport}>
            导出课表
          </Button>
          <Button icon={<DownloadOutlined />} onClick={handleBatchExport}>
            批量导出年级
          </Button>
          <Button onClick={() => setCustomOpen(true)}>
            自定义导出
          </Button>
        </Space>
      </Space>

      <CustomExportModal open={customOpen} onClose={() => setCustomOpen(false)} onExport={handleCustomExport} />
    </Card>
  );
}
