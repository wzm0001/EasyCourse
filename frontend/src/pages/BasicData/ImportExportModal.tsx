import { useState } from 'react';
import { Modal, Upload, Select, Button, Space, App, Radio } from 'antd';
import { UploadOutlined, DownloadOutlined } from '@ant-design/icons';
import { downloadTemplate, importData, exportData } from '@/api/basicData';

interface ImportExportModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const dataTypes = [
  { label: '年级', value: 'grades' },
  { label: '班级', value: 'classes' },
  { label: '课程', value: 'courses' },
  { label: '教师', value: 'teachers' },
  { label: '教室', value: 'classrooms' },
  { label: '教学安排', value: 'teaching_arrangements' },
];

export default function ImportExportModal({ open, onClose, onSuccess }: ImportExportModalProps) {
  const { message } = App.useApp();
  const [dataType, setDataType] = useState<string>('grades');
  const [mode, setMode] = useState<'import' | 'export'>('import');
  const [fileList, setFileList] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleDownloadTemplate = async () => {
    try {
      await downloadTemplate(dataType);
      message.success('模板下载成功');
    } catch {
      message.error('下载失败');
    }
  };

  const handleImport = async () => {
    if (fileList.length === 0) {
      message.warning('请选择文件');
      return;
    }
    setLoading(true);
    try {
      await importData(dataType, fileList[0].originFileObj);
      message.success('导入成功');
      onSuccess();
      onClose();
    } catch {
      message.error('导入失败');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    setLoading(true);
    try {
      await exportData(dataType);
      message.success('导出成功');
    } catch {
      message.error('导出失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title="导入导出"
      open={open}
      onCancel={onClose}
      footer={null}
      width={500}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <div>
          <span style={{ marginRight: 8 }}>数据类型：</span>
          <Select
            style={{ width: 200 }}
            value={dataType}
            onChange={setDataType}
            options={dataTypes}
          />
        </div>
        <div>
          <Radio.Group value={mode} onChange={(e) => setMode(e.target.value)}>
            <Radio value="import">导入</Radio>
            <Radio value="export">导出</Radio>
          </Radio.Group>
        </div>
        {mode === 'import' ? (
          <>
            <Button icon={<DownloadOutlined />} onClick={handleDownloadTemplate}>
              下载模板
            </Button>
            <Upload
              maxCount={1}
              accept=".xlsx,.xls"
              fileList={fileList}
              onChange={({ fileList: fl }) => setFileList(fl)}
              beforeUpload={() => false}
            >
              <Button icon={<UploadOutlined />}>选择文件</Button>
            </Upload>
            <Button type="primary" loading={loading} onClick={handleImport} block>
              开始导入
            </Button>
          </>
        ) : (
          <Button type="primary" loading={loading} onClick={handleExport} block>
            开始导出
          </Button>
        )}
      </Space>
    </Modal>
  );
}
