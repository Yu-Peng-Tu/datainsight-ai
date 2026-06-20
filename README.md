# 📊 DataInsight AI — 智能数据洞察平台

> AI 驱动的数据洞察平台 — 上传数据，秒获洞察

DataInsight AI 是一个面向非技术用户的智能数据分析平台。用户只需上传 CSV/Excel 文件，系统即可自动完成数据解析、统计分析、AI 洞察生成和多维度可视化展示。

## 核心特性

- 🤖 **AI 智能分析**：基于大模型自动生成数据洞察（流式输出）
- 📊 **自动可视化**：智能推荐并生成 5 种图表类型
- 💬 **对话追问**：用自然语言对数据进行深度探索
- 📄 **报告导出**：一键导出 Markdown 分析报告

## 技术栈

- 前端：React 18 + TypeScript + Vite + Ant Design + ECharts
- 后端：Python 3.11 + FastAPI + Pandas + SQLAlchemy
- 数据库：SQLite
- AI：Moonshot AI (Kimi) API

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/datainsight-ai.git
cd datainsight-ai
```

### 2. 启动后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 Moonshot API Key

uvicorn app.main:app --reload --port 8000
```

后端运行在 http://localhost:8000
API 文档：http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:5173

### 4. 测试数据

项目已提供测试数据 `backend/data/sales_demo.csv`（150 行真实销售数据），可直接拖拽上传测试。

## 项目结构

```
datainsight-ai/
├── backend/              # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库连接
│   │   ├── models.py        # ORM 数据模型
│   │   ├── routers/         # API 路由
│   │   │   ├── upload.py       # 文件上传/任务管理
│   │   │   ├── analyze.py      # AI 分析/对话追问
│   │   │   ├── charts.py       # 可视化图表
│   │   │   └── report.py       # 报告导出
│   │   └── services/        # 业务服务
│   │       ├── data_parser.py     # 数据解析
│   │       ├── ai_analyzer.py     # AI 分析（Kimi API）
│   │       └── chart_generator.py # 图表生成
│   ├── data/              # 数据存储目录
│   │   ├── test.csv
│   │   └── sales_demo.csv
│   └── requirements.txt
├── frontend/             # React 前端
│   ├── src/
│   │   ├── App.tsx          # 路由配置
│   │   ├── pages/           # 页面组件
│   │   │   ├── HomePage.tsx      # 首页/文件上传
│   │   │   ├── DetailPage.tsx    # 数据详情/统计
│   │   │   ├── AnalyzePage.tsx   # AI 分析/对话
│   │   │   ├── ChartsPage.tsx    # 可视化图表
│   │   │   └── ReportPage.tsx    # 报告导出
│   │   ├── api/
│   │   │   └── client.ts       # Axios 封装
│   │   └── types/
│   │       └── index.ts        # TypeScript 类型
│   └── package.json
└── docs/                 # 项目文档
    ├── PRD.md            # 产品需求文档
    ├── plan.md           # 14天开发计划
    └── resume.md         # 简历描述模板
```

## API 接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/upload` | 上传 CSV/Excel 文件 |
| GET | `/api/tasks` | 获取所有任务列表 |
| GET | `/api/tasks/{id}` | 获取任务详情 |
| GET | `/api/tasks/{id}/data` | 获取数据预览 |
| GET | `/api/tasks/{id}/stats` | 获取统计概览 |
| POST | `/api/analyze/{id}` | 触发 AI 分析 |
| GET | `/api/analyze/{id}/stream` | 流式获取 AI 分析结果 |
| POST | `/api/chat/{id}` | 对话追问 |
| POST | `/api/charts/{id}/generate` | 生成可视化图表 |
| GET | `/api/charts/{id}` | 获取图表列表 |
| GET | `/api/report/{id}` | 生成 Markdown 报告 |
| DELETE | `/api/tasks/{id}` | 删除任务 |

## 使用流程

```
上传文件 → 查看数据详情 → AI 智能分析 → 对话追问 → 可视化图表 → 导出报告
```

## 简历描述（可直接使用）

独立设计并开发了一个 AI 驱动的数据分析平台，支持用户上传 CSV/Excel 文件后自动完成数据清洗、统计分析、智能洞察和可视化报告生成。

**前端**：使用 React 18 + TypeScript + Vite + Ant Design + ECharts 构建现代化 Web 界面，实现拖拽上传、数据表格展示、图表渲染和流式对话交互。

**后端**：使用 Python FastAPI + Pandas + SQLAlchemy 构建 RESTful API，实现文件解析、数据预处理、异步 AI 分析任务和数据库持久化。

**AI 集成**：深度调用 Moonshot AI（Kimi）大模型 API，通过 Prompt Engineering 实现结构化数据分析、异常检测、趋势预测和多轮对话问答，支持 SSE 流式输出提升用户体验。

**工程实践**：采用前后端分离架构，数据库使用 SQLite 并设计完整的 ORM 模型，项目通过 GitHub 进行版本控制，具备 Docker 容器化部署能力。

## 开发计划

详见 [docs/plan.md](docs/plan.md)

## License

MIT
