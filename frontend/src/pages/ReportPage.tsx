import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Button, Typography, Spin, Alert } from 'antd'
import { ArrowLeftOutlined, DownloadOutlined } from '@ant-design/icons'
import api from '../api/client'

const { Title } = Typography

function ReportPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const taskId = parseInt(id || '0')

  const [report, setReport] = useState<{ filename: string; content: string } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchReport()
  }, [taskId])

  const fetchReport = async () => {
    setLoading(true)
    try {
      const res = await api.get(`/report/${taskId}`)
      setReport(res.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '生成报告失败')
    } finally {
      setLoading(false)
    }
  }

  const downloadReport = () => {
    if (!report) return
    const blob = new Blob([report.content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = report.filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" tip="生成报告中..." />
      </div>
    )
  }

  if (error) {
    return <Alert message="错误" description={error} type="error" showIcon style={{ margin: 24 }} />
  }

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: 24 }}>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(`/charts/${taskId}`)} style={{ marginBottom: 16 }}>
        返回图表
      </Button>

      <Title level={3}>
        <DownloadOutlined /> 数据洞察报告
      </Title>

      <Button type="primary" icon={<DownloadOutlined />} onClick={downloadReport} style={{ marginBottom: 24 }}>
        下载 Markdown 报告
      </Button>

      <Card>
        <div style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: 14, lineHeight: 1.8 }}>
          {report?.content}
        </div>
      </Card>
    </div>
  )
}

export default ReportPage
