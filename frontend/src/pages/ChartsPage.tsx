import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Button, Typography, Spin, Alert, Row, Col, Tabs } from 'antd'
import { ArrowLeftOutlined, FileTextOutlined, BarChartOutlined } from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import api from '../api/client'

const { Title } = Typography

interface ChartItem {
  id: number
  chart_type: string
  chart_config: string
  description: string
}

function ChartsPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const taskId = parseInt(id || '0')

  const [charts, setCharts] = useState<ChartItem[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')

  const fetchCharts = async () => {
    setLoading(true)
    try {
      const res = await api.get(`/charts/${taskId}`)
      setCharts(res.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '获取图表失败')
    } finally {
      setLoading(false)
    }
  }

  const generateCharts = async () => {
    setGenerating(true)
    try {
      await api.post(`/charts/${taskId}/generate`)
      await fetchCharts()
    } catch (err: any) {
      setError(err.response?.data?.detail || '生成图表失败')
    } finally {
      setGenerating(false)
    }
  }

  useEffect(() => {
    fetchCharts()
  }, [taskId])

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" tip="加载图表..." />
      </div>
    )
  }

  return (
    <div style={{ maxWidth: 1400, margin: '0 auto', padding: 24 }}>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(`/detail/${taskId}`)} style={{ marginBottom: 16 }}>
        返回详情
      </Button>

      <Title level={3}>
        <BarChartOutlined /> 数据可视化
      </Title>

      {error && <Alert message="错误" description={error} type="error" showIcon style={{ marginBottom: 16 }} closable onClose={() => setError('')} />}

      <div style={{ marginBottom: 24 }}>
        <Button type="primary" onClick={generateCharts} loading={generating} style={{ marginRight: 8 }}>
          {charts.length > 0 ? '重新生成图表' : '生成图表'}
        </Button>
        <Button icon={<FileTextOutlined />} onClick={() => navigate(`/report/${taskId}`)}>
          查看报告
        </Button>
      </div>

      {charts.length === 0 && !generating && (
        <Card style={{ textAlign: 'center', padding: 60 }}>
          <p style={{ color: '#999', fontSize: 16 }}>点击"生成图表"按钮，AI 将自动为你生成数据可视化</p>
        </Card>
      )}

      <Tabs
        type="card"
        items={charts.map((chart, index) => ({
          key: String(chart.id),
          label: chart.description || `图表 ${index + 1}`,
          children: (
            <Card title={chart.description}>
              <ReactECharts
                option={JSON.parse(chart.chart_config)}
                style={{ height: 400 }}
              />
            </Card>
          )
        }))}
      />
    </div>
  )
}

export default ChartsPage
