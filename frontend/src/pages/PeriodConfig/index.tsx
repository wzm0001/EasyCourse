import { useState, useEffect } from 'react';
import { Card, Select, Button, Form, InputNumber, Space, App } from 'antd';
import { AppstoreOutlined, SaveOutlined } from '@ant-design/icons';
import { useResponsive } from '@/hooks/useResponsive';
import { getGrades } from '@/api/basicData';
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

  useEffect(() => {
    getGrades({ page: 1, page_size: 100 }).then((res) => {
      setGrades(res.items || []);
      if (res.items?.length > 0) {
        setSelectedGrade(res.items[0].id);
      }
    });
  }, []);

  useEffect(() => {
    if (selectedGrade) {
      getGradePeriods(selectedGrade)
        .then((res) => setPeriods(res.data || []))
        .catch(() => setPeriods([]));
    }
  }, [selectedGrade]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      await setupGradePeriods(selectedGrade, {
        morning_count: values.morning_count,
        class_count: values.class_count,
        evening_count: values.evening_count,
      });
      message.success('保存成功');
      const res = await getGradePeriods(selectedGrade);
      setPeriods(res.data || []);
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
          <Card type="inner" title="节数配置" style={{ marginBottom: 24 }}>
            <Form form={form} layout="inline" initialValues={{ morning_count: 1, class_count: 8, evening_count: 2 }}>
              <Form.Item name="morning_count" label="早读节数">
                <InputNumber min={0} max={3} />
              </Form.Item>
              <Form.Item name="class_count" label="正课节数">
                <InputNumber min={1} max={12} />
              </Form.Item>
              <Form.Item name="evening_count" label="晚自习节数">
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

  return embedded ? content : <Card title="时间段配置">{content}</Card>;
}
