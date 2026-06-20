import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Button, Typography, Input, List, Avatar, Spin, Alert, Divider } from 'antd'
import { ArrowLeftOutlined, RobotOutlined, UserOutlined, SendOutlined } from '@ant-design/icons'
import api from '../api/client'

const { Title, Text } = Typography
const { TextArea } = Input

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

function AnalyzePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const taskId = parseInt(id || '0')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const [analyzing, setAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState('')
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [chatInput, setChatInput] = useState('')
  const [chatting, setChatting] = useState(false)
  const [error, setError] = useState('')

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [analysisResult, chatMessages])

  const startAnalysis = async () => {
    setAnalyzing(true)
    setAnalysisResult('')
    setError('')

    try {
      // 先触发分析
      await api.post(`/analyze/${taskId}`)

      // 然后连接 SSE 流
      const eventSource = new EventSource(`/api/analyze/${taskId}/stream`)

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data)

        if (data.done) {
          eventSource.close()
          setAnalyzing(false)
        } else if (data.content) {
          setAnalysisResult(prev => prev + data.content)
        }
      }

      eventSource.onerror = (err) => {
        console.error('SSE error:', err)
        eventSource.close()
        setAnalyzing(false)
        setError('流式连接出错，请重试')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '分析启动失败')
      setAnalyzing(false)
    }
  }

  const sendChat = async () => {
    if (!chatInput.trim() || chatting) return

    const question = chatInput.trim()
    setChatInput('')
    setChatting(true)

    // 添加用户消息
    setChatMessages(prev => [...prev, { role: 'user', content: question }])

    try {
      const eventSource = new EventSource(`/api/chat/${taskId}?question=${encodeURIComponent(question)}`)

      let assistantContent = ''

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data)

        if (data.done) {
          eventSource.close()
          setChatting(false)
        } else if (data.content) {
          assistantContent += data.content
          // 更新最后一条 assistant 消息
          setChatMessages(prev => {
            const newMessages = [...prev]
            const lastMsg = newMessages[newMessages.length - 1]
            if (lastMsg && lastMsg.role === 'assistant') {
              lastMsg.content = assistantContent
            } else {
              newMessages.push({ role: 'assistant', content: assistantContent })
            }
            return newMessages
          })
        }
      }

      eventSource.onerror = (err) => {
        console.error('Chat SSE error:', err)
        eventSource.close()
        setChatting(false)
      }
    } catch (err: any) {
      setChatting(false)
      setError('对话请求失败')
    }
  }

  const formatContent = (content: string) => {
    return content.split('\n').map((line, i) => (
      <p key={i} style={{ marginBottom: 4, lineHeight: 1.8 }}>
        {line}
      </p>
    ))
  }

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: 24 }}>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(`/detail/${taskId}`)} style={{ marginBottom: 16 }}>
        返回详情
      </Button>

      <Title level={3}>
        🤖 AI 智能分析
      </Title>

      {error && <Alert message="错误" description={error} type="error" showIcon style={{ marginBottom: 16 }} />}

      {/* 分析结果区域 */}
      <Card
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span><RobotOutlined /> AI 分析结果</span>
            <Button
              type="primary"
              onClick={startAnalysis}
              loading={analyzing}
              disabled={analyzing}
            >
              {analysisResult ? '重新分析' : '开始分析'}
            </Button>
          </div>
        }
        style={{ marginBottom: 24, minHeight: 300 }}
      >
        {analyzing && !analysisResult && (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin size="large" tip="AI 正在分析数据，请稍候..." />
          </div>
        )}

        {analysisResult ? (
          <div style={{ whiteSpace: 'pre-wrap', fontSize: 14, lineHeight: 1.8 }}>
            {formatContent(analysisResult)}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
            {!analyzing && '点击"开始分析"让 AI 为你生成数据洞察报告'}
          </div>
        )}
      </Card>

      {/* 对话追问区域 */}
      {analysisResult && (
        <>
          <Divider />
          <Title level={4}>💬 对话追问</Title>

          <Card style={{ marginBottom: 16, maxHeight: 400, overflow: 'auto' }}>
            <List
              dataSource={chatMessages}
              renderItem={(msg) => (
                <List.Item
                  style={{
                    justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    padding: '8px 0'
                  }}
                >
                  <div
                    style={{
                      maxWidth: '80%',
                      padding: '10px 16px',
                      borderRadius: 16,
                      backgroundColor: msg.role === 'user' ? '#1890ff' : '#f0f0f0',
                      color: msg.role === 'user' ? '#fff' : '#333',
                    }}
                  >
                    <div style={{ fontSize: 12, marginBottom: 4, opacity: 0.7 }}>
                      {msg.role === 'user' ? '你' : 'AI 分析师'}
                    </div>
                    <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                  </div>
                </List.Item>
              )}
            />
            <div ref={messagesEndRef} />
          </Card>

          <div style={{ display: 'flex', gap: 8 }}>
            <TextArea
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="输入你的问题，例如：哪个品类的销售额最高？"
              autoSize={{ minRows: 1, maxRows: 3 }}
              onPressEnter={(e) => {
                if (!e.shiftKey) {
                  e.preventDefault()
                  sendChat()
                }
              }}
              style={{ flex: 1 }}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={sendChat}
              loading={chatting}
              disabled={!chatInput.trim()}
              style={{ height: 'auto' }}
            >
              发送
            </Button>
          </div>
        </>
      )}
    </div>
  )
}

export default AnalyzePage
