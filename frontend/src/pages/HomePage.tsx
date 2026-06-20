import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, message, Card, Typography, Table, Tag, Spin, Button } from 'antd'
import { InboxOutlined, EyeOutlined } from '@ant-design/icons'
import api from '../api/client'
import type { UploadResponse } from '../types'

const { Dragger } = Upload
const { Title, Text } = Typography

function HomePage() {
  const navigate = useNavigate()
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const customUpload = useCallback(async (options: any) => {
    const { file, onSuccess, onError } = options
    setLoading(true)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setUploadResult(response.data)
      message.success('文件上传成功！')
      onSuccess?.('ok')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '上传失败')
      onError?.(error)
    } finally {
      setLoading(false)
    }
  }, [])

  const columns = [
    { title: '列名', dataIndex: 'name', key: 'name' },
    { title: '数据类型', dataIndex: 'dtype', key: 'dtype', render: (t: string) => <Tag>{t}</Tag> },
    { title: '缺失值', dataIndex: 'null_count', key: 'null_count' },
    { title: '唯一值', dataIndex: 'unique_count', key: 'unique_count' },
    { title: '样本值', dataIndex: 'sample', key: 'sample', render: (s: string[]) => s.slice(0, 3).join(', ') }
  ]

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: 24 }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: 32 }}>
        📊 DataInsight AI - 智能数据洞察
      </Title>

      <Card title="上传数据文件" style={{ marginBottom: 24 }}>
        <Dragger
          customRequest={customUpload}
          accept=".csv,.xlsx,.xls"
          maxCount={1}
          showUploadList={{ showRemoveIcon: false }}
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined style={{ fontSize: 48, color: '#1890ff' }} />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此处上传</p>
          <p className="ant-upload-hint">
            支持 CSV、Excel 文件，文件大小不超过 10MB
          </p>
        </Dragger>

        {loading && (
          <div style={{ textAlign: 'center', marginTop: 16 }}>
            <Spin tip="正在解析数据..." />
          </div>
        )}
      </Card>

      {uploadResult && (
        <Card
          title="数据解析结果"
          style={{ marginBottom: 24 }}
          extra={
            <Button type="primary" icon={<EyeOutlined />} onClick={() => navigate(`/detail/${uploadResult.id}`)}>
              查看详情
            </Button>
          }
        >
          <div style={{ marginBottom: 16 }}>
            <Text strong>文件名：</Text>{uploadResult.filename} &nbsp;&nbsp;
            <Text strong>行数：</Text>{uploadResult.rows} &nbsp;&nbsp;
            <Text strong>列数：</Text>{uploadResult.cols}
          </div>
          <Table
            dataSource={uploadResult.columns}
            columns={columns}
            rowKey="name"
            pagination={false}
            size="small"
          />
        </Card>
      )}
    </div>
  )
}

export default HomePage
