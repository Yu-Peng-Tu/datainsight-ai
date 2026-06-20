# 📊 DataInsight AI - 智能数据洞察平台

## 一、项目概述

### 项目定位
**DataInsight AI** 是一个面向非技术用户的 AI 驱动数据分析平台。用户只需上传 CSV/Excel 数据文件，平台即可自动完成数据清洗、统计分析、可视化图表生成，并产出结构化的数据洞察报告。

### 模仿对象
- **Kimi Chat** 的文件分析功能（上传表格自动分析）
- **通义千问** 的数据智能体
- **ChatGPT Code Interpreter** 的数据分析能力

### 核心亮点（简历可写）
1. ✅ **全栈独立开发**：从数据库设计到前后端联调，独立完成完整链路
2. ✅ **AI 深度集成**：调用大模型 API 实现智能分析、自然语言问答、报告生成
3. ✅ **数据可视化**：自动生成多维度图表（柱状图、折线图、散点图、热力图等）
4. ✅ **工程化实践**：RESTful API 设计、异步任务处理、数据库建模、Docker 部署
5. ✅ **用户体验**：拖拽上传、实时流式响应、对话式追问分析

---

## 二、核心功能

| 功能模块 | 描述 |
|---------|------|
| 📤 数据上传 | 支持 CSV / Excel 文件拖拽上传，自动解析数据类型 |
| 📋 数据概览 | 自动统计行列数、数据类型分布、缺失值、重复值 |
| 🤖 AI 智能分析 | 调用大模型自动生成数据描述、趋势分析、异常检测、关联性洞察 |
| 📊 可视化图表 | 自动推荐并生成合适的图表（柱状图、折线图、饼图、箱线图、热力图） |
| 💬 对话追问 | 用户可用自然语言对数据进行追问（如"哪个品类销售额最高？"） |
| 📄 报告导出 | 生成 Markdown / PDF 格式的数据洞察报告，支持一键下载 |
| 📜 历史记录 | 查看过往分析记录，支持重新分析 |

---

## 三、技术栈

### 前端
| 技术 | 用途 |
|------|------|
| React 18 | 前端框架 |
| TypeScript | 类型安全（减少Bug） |
| Vite | 构建工具（比Webpack快） |
| Ant Design | UI 组件库（表格、表单、按钮、模态框等） |
| ECharts | 数据可视化图表库 |
| Axios | HTTP 请求库 |

### 后端
| 技术 | 用途 |
|------|------|
| Python 3.11 | 后端语言 |
| FastAPI | 现代异步 Web 框架（高性能、自动文档） |
| Pandas | 数据处理与分析（核心） |
| SQLAlchemy | ORM 数据库操作 |
| SQLite | 轻量级数据库（项目首选，简单高效） |
| Uvicorn | ASGI 服务器 |
| python-multipart | 文件上传处理 |
| OpenPyXL | Excel 文件解析 |

### AI 能力
| 技术 | 用途 |
|------|------|
| Moonshot AI API (Kimi) | 大模型调用（数据分析、报告生成、对话问答） |
| Prompt Engineering | 提示词工程，确保输出稳定、结构化 |
| 流式输出 (SSE) | 实时显示 AI 分析过程（类似 ChatGPT 打字效果） |

### 部署
| 技术 | 用途 |
|------|------|
| Docker | 容器化部署（如果时间够） |
| Git / GitHub | 版本控制、代码托管 |

---

## 四、项目架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户浏览器 (Frontend)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ 文件上传  │  │ 数据表格  │  │ 可视化图表 │  │ 对话问答  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│                      React + Ant Design + ECharts            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP/JSON
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI 后端 (Backend)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ 文件上传  │  │ 数据解析  │  │ AI 分析   │  │ 报告生成  │     │
│  │ 接口     │  │ Pandas   │  │ Prompt   │  │ Markdown │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│                      SQLAlchemy + SQLite                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ API 调用
┌─────────────────────────────────────────────────────────────┐
│                     Moonshot AI (Kimi API)                    │
│                   数据分析 + 报告生成 + 问答                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 五、数据库设计

```sql
-- 分析任务表
CREATE TABLE analysis_tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    filename    TEXT NOT NULL,          -- 原始文件名
    file_path   TEXT NOT NULL,          -- 存储路径
    rows        INTEGER,                 -- 数据行数
    cols        INTEGER,                 -- 数据列数
    columns_info TEXT,                  -- 列信息 JSON
    ai_summary  TEXT,                   -- AI 分析摘要
    status      TEXT DEFAULT 'pending', -- pending / analyzing / completed / failed
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 对话记录表
CREATE TABLE chat_messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id     INTEGER REFERENCES analysis_tasks(id),
    role        TEXT NOT NULL,          -- user / assistant
    content     TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 可视化图表记录表
CREATE TABLE visualizations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id     INTEGER REFERENCES analysis_tasks(id),
    chart_type  TEXT NOT NULL,          -- bar / line / scatter / pie / heatmap
    chart_config TEXT,                   -- ECharts 配置 JSON
    description TEXT,                   -- 图表描述
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 六、API 接口设计

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/upload` | 上传数据文件 |
| GET | `/api/tasks` | 获取所有分析任务列表 |
| GET | `/api/tasks/{id}` | 获取单个任务详情 |
| POST | `/api/analyze/{id}` | 触发 AI 分析 |
| GET | `/api/analyze/{id}/stream` | 流式获取 AI 分析结果 |
| POST | `/api/chat/{id}` | 对数据进行对话追问 |
| GET | `/api/charts/{id}` | 获取可视化图表列表 |
| GET | `/api/report/{id}` | 生成并下载数据报告 |
| DELETE | `/api/tasks/{id}` | 删除分析任务 |

---

## 七、页面设计（前端）

### 页面清单

| 页面 | 描述 |
|------|------|
| **首页 / 上传页** | 大文件拖拽区域，上传 CSV/Excel，显示历史任务列表 |
| **数据详情页** | 展示数据表格（分页）、数据概览统计卡片、数据类型分布 |
| **AI 分析页** | AI 分析结果展示（流式输出）、对话式追问区域 |
| **可视化页** | 自动生成的图表画廊，支持切换图表类型 |
| **报告页** | Markdown 报告预览 + 导出按钮 |

### 核心交互流程

```
用户打开首页 → 拖拽上传 CSV 文件 → 后端解析并存储
    ↓
跳转到数据详情页 → 显示数据表格 + 统计概览
    ↓
点击【开始 AI 分析】→ 调用 Kimi API 流式分析 → 展示分析结果
    ↓
生成可视化图表 → 用户在对话区追问 → 导出完整报告
```

---

## 八、简历描述模板（可直接使用）

### 项目标题
**DataInsight AI — 智能数据洞察平台**（独立全栈开发）

### 描述
- 独立设计并开发了一个 AI 驱动的数据分析平台，支持用户上传 CSV/Excel 文件后自动完成数据清洗、统计分析、智能洞察和可视化报告生成。
- **前端**：使用 React 18 + TypeScript + Vite + Ant Design + ECharts 构建现代化 Web 界面，实现拖拽上传、数据表格展示、图表渲染和流式对话交互。
- **后端**：使用 Python FastAPI + Pandas + SQLAlchemy 构建 RESTful API，实现文件解析、数据预处理、异步 AI 分析任务和数据库持久化。
- **AI 集成**：深度调用 Moonshot AI（Kimi）大模型 API，通过 Prompt Engineering 实现结构化数据分析、异常检测、趋势预测和多轮对话问答，支持 SSE 流式输出提升用户体验。
- **工程实践**：采用前后端分离架构，数据库使用 SQLite 并设计完整的 ORM 模型，项目通过 GitHub 进行版本控制，具备 Docker 容器化部署能力。
- **技术成果**：支持自动生成 5+ 种图表类型，可导出 Markdown 报告，处理 1000+ 行数据文件响应时间 < 3 秒。

---

## 九、项目文件结构

```
datainsight-ai/
├── README.md                          # 项目说明
├── docs/                              # 文档目录
│   ├── PRD.md                         # 产品需求文档（本文件）
│   ├── API.md                         # 接口文档
│   ├── plan.md                        # 开发计划
│   └── resume.md                      # 简历描述
├── backend/                           # 后端项目
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI 入口
│   │   ├── config.py                  # 配置（API Key、路径等）
│   │   ├── database.py                # 数据库连接与 ORM
│   │   ├── models.py                  # 数据模型
│   │   ├── routers/
│   │   │   ├── upload.py              # 文件上传接口
│   │   │   ├── analyze.py             # AI 分析接口
│   │   │   ├── chat.py                # 对话接口
│   │   │   ├── charts.py              # 图表接口
│   │   │   └── report.py            # 报告接口
│   │   ├── services/
│   │   │   ├── data_parser.py         # 数据解析服务
│   │   │   ├── ai_analyzer.py         # AI 分析服务（Kimi API）
│   │   │   ├── chart_generator.py     # 图表生成服务
│   │   │   └── report_generator.py    # 报告生成服务
│   │   └── utils/
│   │       └── helpers.py
│   ├── requirements.txt               # Python 依赖
│   ├── Dockerfile                     # Docker 配置（可选）
│   └── data/                          # 数据存储目录
│       └── uploads/
├── frontend/                          # 前端项目
│   ├── src/
│   │   ├── main.tsx                   # 入口
│   │   ├── App.tsx                    # 主应用
│   │   ├── components/
│   │   │   ├── FileUploader.tsx       # 文件上传组件
│   │   │   ├── DataTable.tsx          # 数据表格组件
│   │   │   ├── StatCards.tsx          # 统计卡片组件
│   │   │   ├── ChartGallery.tsx       # 图表画廊组件
│   │   │   ├── AIChat.tsx             # AI 对话组件
│   │   │   └── ReportViewer.tsx       # 报告预览组件
│   │   ├── pages/
│   │   │   ├── HomePage.tsx           # 首页/上传页
│   │   │   ├── DetailPage.tsx         # 数据详情页
│   │   │   ├── AnalyzePage.tsx        # AI 分析页
│   │   │   └── ReportPage.tsx         # 报告页
│   │   ├── api/
│   │   │   └── client.ts              # Axios 封装
│   │   ├── types/
│   │   │   └── index.ts               # TypeScript 类型定义
│   │   └── utils/
│   │       └── helpers.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
└── docker-compose.yml                 # Docker Compose（可选）
```

---

## 十、为什么要做这个项目？

1. **高度匹配招聘需求**：字节、小米、阿里巴巴等公司的 AI 全栈实习 JD 明确要求 React + Python + AI Agent/RAG + LLM API 调用能力，本项目全部覆盖。
2. **展示技术深度**：不是简单的调用 API，而是涉及数据解析、Prompt Engineering、流式输出、数据库设计、前后端联调等完整工程链路。
3. **真实可演示**：可以上传一个真实的销售数据 CSV 文件，平台自动生成分析报告和图表，面试官可以当场体验。
4. **与 Kimi 结合**：使用 Kimi API 作为核心 AI 能力，展示对大模型应用开发的深入理解。

---

> **下一步：查看 `plan.md` 获取技术实现方案！** 🚀
