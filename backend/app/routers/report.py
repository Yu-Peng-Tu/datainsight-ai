import json
import os

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AnalysisTask, Visualization

router = APIRouter()


def _load_dataframe(task: AnalysisTask) -> pd.DataFrame:
    """从任务文件路径加载 DataFrame"""
    file_ext = os.path.splitext(task.file_path)[1].lower()
    if file_ext == '.csv':
        return pd.read_csv(task.file_path)
    elif file_ext in ['.xlsx', '.xls']:
        return pd.read_excel(task.file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_ext}")


@router.get("/report/{task_id}")
async def generate_report(task_id: int, db: Session = Depends(get_db)):
    """
    生成 Markdown 格式的数据洞察报告

    - **task_id**: 任务 ID
    """
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    try:
        df = _load_dataframe(task)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"数据读取失败: {str(e)}")

    # 基础统计
    total_rows = len(df)
    total_cols = len(df.columns)
    missing_total = int(df.isna().sum().sum())
    duplicate_count = int(df.duplicated().sum())

    # 列统计
    column_stats = []
    for col in df.columns:
        col_data = df[col]
        stat = {
            "name": str(col),
            "dtype": str(col_data.dtype),
            "null_count": int(col_data.isna().sum()),
            "unique_count": int(col_data.nunique()),
        }
        if pd.api.types.is_numeric_dtype(col_data):
            stat.update({
                "mean": round(float(col_data.mean()), 4) if pd.notna(col_data.mean()) else None,
                "median": round(float(col_data.median()), 4) if pd.notna(col_data.median()) else None,
                "std": round(float(col_data.std()), 4) if pd.notna(col_data.std()) else None,
                "min": float(col_data.min()) if pd.notna(col_data.min()) else None,
                "max": float(col_data.max()) if pd.notna(col_data.max()) else None,
            })
        else:
            top_values = col_data.value_counts().head(3).to_dict()
            stat["top_values"] = {str(k): int(v) for k, v in top_values.items()}
        column_stats.append(stat)

    # 获取图表
    charts = db.query(Visualization).filter(Visualization.task_id == task_id).all()

    # 构建 Markdown 报告
    report = f"""# 📊 DataInsight AI 数据洞察报告

## 文件信息

- **文件名**: {task.filename}
- **分析时间**: {task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else 'N/A'}
- **数据行数**: {total_rows}
- **数据列数**: {total_cols}
- **缺失值总数**: {missing_total}
- **重复行数**: {duplicate_count}

---

## 数据概览

### 列信息统计

| 列名 | 数据类型 | 缺失值 | 唯一值 | 均值/中位数 | 最小值 | 最大值 |
|------|----------|--------|--------|-------------|--------|--------|
"""

    for stat in column_stats:
        if "mean" in stat:
            report += f"| {stat['name']} | {stat['dtype']} | {stat['null_count']} | {stat['unique_count']} | {stat.get('mean', '-')}/{stat.get('median', '-')} | {stat.get('min', '-')} | {stat.get('max', '-')} |\n"
        else:
            top = stat.get('top_values', {})
            top_str = ', '.join([f"{k}({v})" for k, v in list(top.items())[:3]])
            report += f"| {stat['name']} | {stat['dtype']} | {stat['null_count']} | {stat['unique_count']} | {top_str} | - | - |\n"

    report += f"""
---

## AI 分析摘要

{task.ai_summary or "尚未进行 AI 分析，请先在平台上触发分析。"}

---

## 可视化图表

共生成 {len(charts)} 张图表：

"""

    for i, chart in enumerate(charts, 1):
        report += f"{i}. **{chart.description}** ({chart.chart_type})\n"

    report += """
---

## 数据样本（前 10 行）

"""

    # 添加前 10 行数据
    sample = df.head(10)
    report += "| " + " | ".join([str(c) for c in df.columns]) + " |\n"
    report += "| " + " | ".join(["---"] * len(df.columns)) + " |\n"
    for _, row in sample.iterrows():
        report += "| " + " | ".join([str(v) if pd.notna(v) else "NULL" for v in row]) + " |\n"

    report += f"""
---

> 本报告由 DataInsight AI 自动生成
> 项目地址: https://github.com/yourusername/datainsight-ai
"""

    return {
        "task_id": task_id,
        "filename": f"{task.filename}_report.md",
        "content": report
    }
