# DataInsight AI

> 让数据洞察触手可及 — 上传 CSV/Excel，即刻获取分析与可视化。

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Yu-Peng-Tu/datainsight-ai)

DataInsight AI 是一个数据智能分析平台，帮助用户快速理解数据。上传数据文件后，系统自动完成数据解析、统计分析、生成可视化图表，并产出结构化分析报告。支持通过自然语言与数据进行对话式探索。

## 在线演示

点击上方 **「Deploy to Render」** 按钮即可一键部署到公网（免费）。部署约需 5 分钟。

## 功能

- **数据上传**：支持 CSV / Excel 文件拖拽上传，自动解析数据类型
- **数据概览**：统计行列数、缺失值、重复值、各列分布特征
- **AI 分析**：调用大语言模型自动生成数据描述、趋势分析、异常检测与关联性洞察
- **可视化图表**：根据数据特征自动推荐并生成柱状图、饼图、散点图、热力图等
- **对话追问**：用自然语言对数据进行深入提问（如"哪个品类销售额最高？"）
- **报告导出**：生成 Markdown 格式的数据洞察报告，支持一键下载

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 18 + TypeScript + Vite + Ant Design + ECharts |
| 后端 | Python 3.11 + FastAPI + Pandas + SQLAlchemy |
| 数据库 | SQLite |
| AI 能力 | Moonshot AI (Kimi) API，SSE 流式输出 |

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Yu-Peng-Tu/datainsight-ai.git
cd datainsight-ai
```

### 2. 启动服务

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置 Moonshot API Key（可选，用于 AI 分析）
cp .env.example .env
# 编辑 .env，填入你的 API Key

uvicorn app.main:app --reload --port 8000
```

服务运行在 http://localhost:8000
API 文档：http://localhost:8000/docs

### 3. 测试数据

项目包含 `backend/data/sales_demo.csv`（150 行模拟销售数据），可直接上传体验。

## 项目结构

```
datainsight-ai/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── routers/        # API 路由：上传、分析、图表、报告
│   │   └── services/     # 业务逻辑：数据解析、AI 分析、图表生成
│   ├── data/             # 测试数据
│   └── requirements.txt
├── frontend/             # React 前端
│   └── src/pages/        # 首页、详情、分析、图表、报告
└── docs/                 # 技术文档
```

## API 接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/upload` | 上传 CSV/Excel 文件 |
| GET | `/api/tasks/{id}` | 获取任务详情 |
| GET | `/api/tasks/{id}/data` | 分页获取数据预览 |
| GET | `/api/tasks/{id}/stats` | 获取统计概览 |
| POST | `/api/analyze/{id}` | 触发 AI 分析 |
| GET | `/api/analyze/{id}/stream` | 流式获取 AI 分析结果 |
| POST | `/api/chat/{id}` | 对话追问 |
| POST | `/api/charts/{id}/generate` | 自动生成可视化图表 |
| GET | `/api/charts/{id}` | 获取图表配置 |
| GET | `/api/report/{id}` | 生成 Markdown 报告 |
| DELETE | `/api/tasks/{id}` | 删除任务 |

## 使用流程

```
上传文件 → 查看数据详情 → AI 智能分析 → 对话追问 → 可视化图表 → 导出报告
```

## 技术亮点

- **流式输出**：AI 分析采用 SSE 流式传输，实现类似 ChatGPT 的逐字显示效果
- **Prompt Engineering**：针对数据分析场景设计结构化 Prompt，确保模型输出稳定、专业
- **自动图表推荐**：根据数据列类型智能匹配图表类型（数值型 → 柱状图/散点图，分类型 → 饼图，多数值列 → 热力图）
- **前后端分离**：RESTful API 设计，数据库 ORM 建模，支持容器化部署

## 文档

- [PRD.md](docs/PRD.md) — 产品需求文档
- [plan.md](docs/plan.md) — 技术实现方案

## License

MIT
