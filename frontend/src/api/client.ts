import axios from 'axios'

// 生产环境使用后端 Render 地址，开发环境使用 Vite proxy
const baseURL = import.meta.env.PROD
  ? 'https://datainsight-ai-backend.onrender.com/api'
  : '/api'

const api = axios.create({
  baseURL,
  timeout: 30000,
})

export default api
