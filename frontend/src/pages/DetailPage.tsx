import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Table, Tag, Typography, Button, Row, Col, Statistic, Spin, Alert } from 'antd'
import { ArrowLeftOutlined, BarChartOutlined, RobotOutlined } from '@ant-design/icons'
import api from '../api/client'

const { Title, Text } = Typography

interface TaskDetail {
  id: number
  filename: string
  rows: number
  cols: number
  columns: any[]
  status: string
  ai_summary?: string
}

interface DataPreview {
  total: number
  columns: string[]
  data: any[]
}

interface StatsData {
  total_rows: number
  total_cols: number
  missing_values: number
  duplicate_rows: number
  column_stats: any[]
}

function DetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const taskId = parseInt(id || '0')

  const [task, setTask] = useState<TaskDetail | null>(null)
  const [preview, setPreview] = useState<DataPreview | null>(null)
  const [stats, setStats] = useState<StatsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchData()
  }, [taskId])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [taskRes, previewRes, statsRes] = await Promise.all([
        api.get(`/tasks/${taskId}`),
        api.get(`/tasks/${taskId}/data?limit=50`),
        api.get(`/tasks/${taskId}/stats`)
      ])
      setTask(taskRes.data)
      setPreview(previewRes.data)
      setStats(statsRes.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '加载数据失败')
    } finally {
      setLoading(false)
    }
  }

  const tableColumns = preview?.columns.map((col) => ({
    title: col,
    dataIndex: col,
    key: col,
    ellipsis: true,
    width: 150
  })) || []

  const statColumns = [
    { title: '列名', dataIndex: 'name', key: 'name', width: 120 },
    { title: '类型', dataIndex: 'dtype', key: 'dtype', render: (t: string) => <Tag>{t}</Tag> },
    { title: '缺失值', dataIndex: 'null_count', key: 'null_count', width: 80 },
    { title: '唯一值', dataIndex: 'unique_count', key: 'unique_count', width: 80 },
    {
      title: '均值', dataIndex: 'mean', key: 'mean',
      render: (v: number) => v !== undefined ? v : '-'
    },
    {
      title: '中位数', dataIndex: 'median', key: 'median',
      render: (v: number) => v !== undefined ? v : '-'
    },
    {
      title: '标准差', dataIndex: 'std', key: 'std',
      render: (v: number) => v !== undefined ? v : '-'
    },
  ]

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" tip="加载数据中..." />
      </div>
    )
  }

  if (error) {
    return <Alert message="错误" description={error} type="error" showIcon style={{ margin: 24 }} />
  }

  return (
    <div style={{ maxWidth: 1400, margin: '0 auto', padding: 24 }}>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/')} style={{ marginBottom: 16 }}>
        返回首页
      </Button>

      <Title level={3}>
        📋 {task?.filename}
      </Title>

      {/* 统计概览卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic title="数据行数" value={stats?.total_rows || 0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="数据列数" value={stats?.total_cols || 0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="缺失值总数" value={stats?.missing_values || 0} valueStyle={{ color: stats?.missing_values ? '#ff4d4f' : '#52c41a' }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="重复行数" value={stats?.duplicate_rows || 0} valueStyle={{ color: stats?.duplicate_rows ? '#ff4d4f' : '#52c41a' }} />
          </Card>
        </Col>
      </Row>

      {/* 操作按钮 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col>
          <Button type="primary" icon={<RobotOutlined />} size="large" onClick={() => navigate(`/analyze/${taskId}`)}>
            🤖 开始 AI 分析
          </Button>
        </Col>
        <Col>
          <Button icon={<BarChartOutlined />} size="large" onClick={() => navigate(`/charts/${taskId}`)}>
            📊 查看可视化图表
          </Button>
        </Col>
      </Row>

      {/* 列统计详情 */}
      <Card title="列统计详情" style={{ marginBottom: 24 }}>
        <Table
          dataSource={stats?.column_stats || []}
          columns={statColumns}
          rowKey="name"
          pagination={false}
          size="small"
          scroll={{ x: 'max-content' }}
        />
      </Card>

      {/* 数据预览 */}
      <Card title={`数据预览（前 ${preview?.data.length || 0} 行 / 共 ${preview?.total || 0} 行）`}>
        <Table
          dataSource={preview?.data || []}
          columns={tableColumns}
          rowKey={(record, index) => index?.toString() || '0'}
          pagination={{ pageSize: 10, showSizeChanger: false }}
          size="small"
          scroll={{ x: 'max-content' }}
        />
      </Card>
    </div>
  )
}

export default DetailPage
