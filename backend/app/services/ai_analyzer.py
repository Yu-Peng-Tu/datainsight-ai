import json
import os
from typing import AsyncGenerator

import httpx

from app.config import settings


class AIAnalyzer:
    """AI 数据分析服务 - 调用 Moonshot AI (Kimi) API"""

    def __init__(self):
        self.api_key = settings.MOONSHOT_API_KEY
        self.base_url = settings.MOONSHOT_BASE_URL
        self.model = settings.MOONSHOT_MODEL

    def _build_analysis_prompt(self, filename: str, rows: int, cols: int,
                             columns: list, sample_data: str) -> str:
        """构建数据分析 Prompt"""

        prompt = f"""你是一位资深数据分析师，拥有丰富的商业数据分析经验。

## 数据概览
- 文件名：{filename}
- 数据行数：{rows}
- 数据列数：{cols}

## 列信息
"""
        for col in columns:
            prompt += f"\n- {col['name']} ({col['dtype']})"
            prompt += f"  - 样本值：{', '.join(col['sample'][:3])}"
            prompt += f"  - 缺失值：{col['null_count']} 个"
            prompt += f"  - 唯一值：{col['unique_count']} 个"

        prompt += f"""

## 数据样本（前5行）
{sample_data}

## 分析任务
请对该数据进行全面的分析，并输出以下内容（用中文）：

### 1. 数据整体描述
简要描述这份数据的性质、用途和整体特征。

### 2. 数据质量评估
- 完整性（缺失值情况）
- 一致性（异常值检测）
- 建议的数据清洗步骤

### 3. 各列分析
对每一列进行详细分析：
- 数据类型是否合适
- 分布特征（数值型：均值、中位数、标准差；分类型：类别分布）
- 可能的异常值

### 4. 列间关联分析
分析列与列之间的关系：
- 数值型列之间的相关性
- 分类列与数值列的交叉分析
- 发现的关键规律

### 5. 业务洞察
基于数据特征，提出3-5个有价值的业务洞察或建议。

### 6. 可视化建议
推荐3-5种适合该数据的图表类型，并说明原因。

请确保输出结构清晰、内容专业、有数据支撑。"""

        return prompt

    def _build_chat_prompt(self, question: str, data_summary: str,
                          conversation_history: list) -> str:
        """构建对话追问 Prompt"""

        history_text = ""
        for msg in conversation_history[-5:]:  # 只取最近5轮
            role = "用户" if msg["role"] == "user" else "分析师"
            history_text += f"{role}：{msg['content']}\n"

        prompt = f"""你是一位数据分析师，正在回答用户关于数据的问题。

## 数据摘要
{data_summary}

## 对话历史
{history_text}

## 用户问题
{question}

请基于数据事实回答用户的问题，保持专业、准确。如果数据不足以回答，请明确说明。"""

        return prompt

    async def analyze(self, filename: str, rows: int, cols: int,
                     columns: list, sample_data: str) -> AsyncGenerator[str, None]:
        """
        执行 AI 数据分析（流式输出）

        Yields:
            分析文本片段（SSE 流式）
        """
        if not self.api_key:
            yield "⚠️ 未配置 Moonshot API Key，请在 .env 文件中设置 MOONSHOT_API_KEY"
            return

        prompt = self._build_analysis_prompt(filename, rows, cols, columns, sample_data)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位专业的数据分析师，擅长从数据中发现洞察。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "stream": True
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        yield f"API 调用失败: {response.status_code} - {error_text.decode()[:200]}"
                        return

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # 去掉 "data: " 前缀
                            if data == "[DONE]":
                                break

                            try:
                                chunk = json.loads(data)
                                delta = chunk.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue

        except httpx.TimeoutException:
            yield "\n\n⚠️ 分析请求超时，请稍后重试。"
        except Exception as e:
            yield f"\n\n⚠️ 分析过程出错: {str(e)}"

    async def chat(self, question: str, data_summary: str,
                  conversation_history: list) -> AsyncGenerator[str, None]:
        """
        对话式追问（流式输出）
        """
        if not self.api_key:
            yield "⚠️ 未配置 Moonshot API Key"
            return

        prompt = self._build_chat_prompt(question, data_summary, conversation_history)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位数据分析师，正在回答用户关于数据的问题。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "stream": True
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                delta = chunk.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield f"\n\n⚠️ 对话出错: {str(e)}"


# 单例实例
ai_analyzer = AIAnalyzer()
