import { useState, useEffect } from 'react';
import { Card, Select, Button, Form, InputNumber, Space, App } from 'antd';
import { AppstoreOutlined, SaveOutlined } from '@ant-design/icons';
import { useResponsive } from '@/hooks/useResponsive';
import { useAppStore } from '@/store/app';
import { getGrades, updateGrade } from '@/api/basicData';
import { getGradePeriods, setupGradePeriods, setupDayPeriods } from '@/api/periods';
import PeriodTimeline from './PeriodTimeline';
import TemplateSelect from './TemplateSelect';

export default function PeriodConfig({ embedded }: { embedded?: boolean } = {}) {
  const { message } = App.useApp();
  const { isMobile } = useResponsive();
  const [grades, setGrades] = useState<any[]>([]);
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  const [periods, setPeriods] = useState<any[]>([]);
  const [templateOpen, setTemplateOpen] = useState(false);
  const [form] = Form.useForm();
  const currentSemester = useAppStore((s) => s.currentSemester);

  useEffect(() => {
    getGrades({ page: 1, page_size: 100, semester_id: currentSemester || undefined }).then((res) => {
      setGrades(res.items || []);
      if (res.items?.length > 0) {
        setSelectedGrade(res.items[0].id);
      } else {
        setSelectedGrade('');
      }
    });
  }, [currentSemester]);

  useEffect(() => {
    if (selectedGrade) {
      const grade = grades.find((g) => g.id === selectedGrade);
      if (grade) {
        form.setFieldsValue({
          morning_reading_count: grade.morning_reading_count ?? 1,
          regular_class_count: grade.regular_class_count ?? 8,
          evening_study_count: grade.evening_study_count ?? 0,
        });
      }
      getGradePeriods(selectedGrade)
        .then((res) => setPeriods(res.data || []))
        .catch(() => setPeriods([]));
    }
  }, [selectedGrade, grades]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      await updateGrade(selectedGrade, {
        morning_reading_count: values.morning_reading_count,
        regular_class_count: values.regular_class_count,
        evening_study_count: values.evening_study_count,
      });
      await setupGradePeriods(selectedGrade, {
        morning_count: values.morning_reading_count,
        class_count: values.regular_class_count,
        evening_count: values.evening_study_count,
      });
      message.success('课时配置保存成功');
      const res = await getGradePeriods(selectedGrade);
      setPeriods(res.data || []);
      const updatedGrades = grades.map((g) =>
        g.id === selectedGrade
          ? { ...g, morning_reading_count: values.morning_reading_count, regular_class_count: values.regular_class_count, evening_study_count: values.evening_study_count }
          : g
      );
      setGrades(updatedGrades);
    } catch {
      message.error('保存失败');
    }
  };

  const handleToggleNoSchedule = async (periodId: string) => {
    try {
      const period = periods.find((p) => (p.id || p.key) === periodId);
      if (!period) return;
      await setupDayPeriods(selectedGrade, {
        period_id: periodId,
        no_schedule: !period.no_schedule,
      });
      const res = await getGradePeriods(selectedGrade);
      setPeriods(res.data || []);
      message.success('更新成功');
    } catch {
      message.error('更新失败');
    }
  };

  const content = (
    <>
      <Space style={{ marginBottom: 24 }} size="middle">
        <span>选择年级：</span>
        <Select
          style={{ width: 200 }}
          value={selectedGrade}
          onChange={setSelectedGrade}
          options={grades.map((g) => ({ label: g.name, value: g.id }))}
          placeholder="请选择年级"
        />
        <Button icon={<AppstoreOutlined />} onClick={() => setTemplateOpen(true)}>
          使用模板
        </Button>
      </Space>

      {selectedGrade && (
        <>
          <Card type="inner" title="课时配置（按年级设置）" style={{ marginBottom: 24 }}>
            <Form form={form} layout="inline" initialValues={{ morning_reading_count: 1, regular_class_count: 8, evening_study_count: 0 }}>
              <Form.Item name="morning_reading_count" label="早读节数">
                <InputNumber min={0} max={3} />
              </Form.Item>
              <Form.Item name="regular_class_count" label="正课节数">
                <InputNumber min={1} max={12} />
              </Form.Item>
              <Form.Item name="evening_study_count" label="晚自习节数">
                <InputNumber min={0} max={4} />
              </Form.Item>
              <Form.Item>
                <Button type="primary" icon={<SaveOutlined />} onClick={handleSave}>
                  保存配置
                </Button>
              </Form.Item>
            </Form>
          </Card>

          <Card type="inner" title="时间轴预览（点击标记不排课时段）">
            <PeriodTimeline periods={periods} onToggleNoSchedule={handleToggleNoSchedule} />
          </Card>
        </>
      )}

      <TemplateSelect
        open={templateOpen}
        gradeId={selectedGrade}
        onClose={() => setTemplateOpen(false)}
        onSuccess={async () => {
          const res = await getGradePeriods(selectedGrade);
          setPeriods(res.data || []);
        }}
      />
    </>
  );

  return embedded ? content : <Card title="课时配置">{content}</Card>;
}
