import json
import os

import pandas as pd
import numpy as np

from app.models import AnalysisTask


def _load_dataframe(task: AnalysisTask) -> pd.DataFrame:
    """从任务文件路径加载 DataFrame"""
    file_ext = os.path.splitext(task.file_path)[1].lower()
    if file_ext == '.csv':
        return pd.read_csv(task.file_path)
    elif file_ext in ['.xlsx', '.xls']:
        return pd.read_excel(task.file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_ext}")


def auto_generate_charts(task: AnalysisTask) -> list:
    """
    根据数据自动推荐并生成图表配置

    Returns:
        图表配置列表，每个元素包含 chart_type 和 chart_config
    """
    charts = []
    try:
        df = _load_dataframe(task)
    except Exception:
        return charts

    # 识别列类型
    numeric_cols = []
    categorical_cols = []
    datetime_cols = []

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_cols.append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
        else:
            # 尝试转换为数值
            try:
                pd.to_numeric(df[col], errors='raise')
                numeric_cols.append(col)
            except:
                categorical_cols.append(col)

    # 1. 数值列分布 - 柱状图（取前5个数值列）
    for col in numeric_cols[:5]:
        try:
            data = pd.to_numeric(df[col], errors='coerce').dropna()
            if len(data) == 0:
                continue

            # 分箱统计
            hist, bins = np.histogram(data, bins=10)
            bin_labels = [f"{bins[i]:.1f}-{bins[i+1]:.1f}" for i in range(len(bins)-1)]

            chart_config = {
                "title": {"text": f"{col} 分布", "left": "center"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": bin_labels, "axisLabel": {"rotate": 30}},
                "yAxis": {"type": "value", "name": "频数"},
                "series": [{
                    "type": "bar",
                    "data": hist.tolist(),
                    "itemStyle": {"color": "#5470c6"}
                }]
            }
            charts.append({
                "chart_type": "bar",
                "chart_config": json.dumps(chart_config),
                "description": f"{col} 的数值分布柱状图"
            })
        except Exception:
            continue

    # 2. 分类列 Top 值 - 饼图（取前3个分类列）
    for col in categorical_cols[:3]:
        try:
            value_counts = df[col].value_counts().head(8)
            if len(value_counts) < 2:
                continue

            chart_config = {
                "title": {"text": f"{col} 分布", "left": "center"},
                "tooltip": {"trigger": "item"},
                "legend": {"orient": "vertical", "left": "left"},
                "series": [{
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "data": [
                        {"value": int(v), "name": str(k)}
                        for k, v in value_counts.items()
                    ],
                    "emphasis": {
                        "itemStyle": {
                            "shadowBlur": 10,
                            "shadowOffsetX": 0,
                            "shadowColor": "rgba(0, 0, 0, 0.5)"
                        }
                    }
                }]
            }
            charts.append({
                "chart_type": "pie",
                "chart_config": json.dumps(chart_config),
                "description": f"{col} 的分类分布饼图"
            })
        except Exception:
            continue

    # 3. 两数值列散点图（取前2个数值列）
    if len(numeric_cols) >= 2:
        try:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
            x_data = pd.to_numeric(df[x_col], errors='coerce')
            y_data = pd.to_numeric(df[y_col], errors='coerce')

            valid_mask = x_data.notna() & y_data.notna()
            x_vals = x_data[valid_mask].tolist()[:100]  # 限制100个点
            y_vals = y_data[valid_mask].tolist()[:100]

            chart_config = {
                "title": {"text": f"{x_col} vs {y_col}", "left": "center"},
                "tooltip": {"trigger": "item"},
                "xAxis": {"type": "value", "name": x_col, "scale": True},
                "yAxis": {"type": "value", "name": y_col, "scale": True},
                "series": [{
                    "type": "scatter",
                    "data": [[x, y] for x, y in zip(x_vals, y_vals)],
                    "symbolSize": 10,
                    "itemStyle": {"color": "#91cc75"}
                }]
            }
            charts.append({
                "chart_type": "scatter",
                "chart_config": json.dumps(chart_config),
                "description": f"{x_col} 与 {y_col} 的相关性散点图"
            })
        except Exception:
            pass

    # 4. 分类列 vs 数值列 - 分组柱状图（取第一个分类列和前3个数值列）
    if categorical_cols and numeric_cols:
        try:
            cat_col = categorical_cols[0]
            num_cols = numeric_cols[:3]

            grouped = df.groupby(cat_col)[num_cols].sum().reset_index()
            categories = grouped[cat_col].tolist()

            series = []
            colors = ["#5470c6", "#91cc75", "#fac858"]
            for i, num_col in enumerate(num_cols):
                series.append({
                    "type": "bar",
                    "name": num_col,
                    "data": pd.to_numeric(grouped[num_col], errors='coerce').fillna(0).tolist(),
                    "itemStyle": {"color": colors[i % len(colors)]}
                })

            chart_config = {
                "title": {"text": f"{cat_col} 各分组数值对比", "left": "center"},
                "tooltip": {"trigger": "axis"},
                "legend": {"top": "bottom"},
                "xAxis": {"type": "category", "data": categories, "axisLabel": {"rotate": 30}},
                "yAxis": {"type": "value"},
                "series": series
            }
            charts.append({
                "chart_type": "bar",
                "chart_config": json.dumps(chart_config),
                "description": f"按 {cat_col} 分组的多维度对比柱状图"
            })
        except Exception:
            pass

    # 5. 热力图 - 数值列相关性矩阵
    if len(numeric_cols) >= 2:
        try:
            num_df = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
            corr = num_df.corr().fillna(0)

            # 取前8个数值列，避免热力图太大
            if len(numeric_cols) > 8:
                corr = corr.iloc[:8, :8]

            x_labels = corr.columns.tolist()
            y_labels = corr.index.tolist()
            data = []
            for i, row in enumerate(corr.values):
                for j, val in enumerate(row):
                    data.append([j, i, round(float(val), 2)])

            chart_config = {
                "title": {"text": "数值列相关性热力图", "left": "center"},
                "tooltip": {"position": "top"},
                "grid": {"height": "70%", "top": "10%"},
                "xAxis": {"type": "category", "data": x_labels, "splitArea": {"show": True}},
                "yAxis": {"type": "category", "data": y_labels, "splitArea": {"show": True}},
                "visualMap": {
                    "min": -1,
                    "max": 1,
                    "calculable": True,
                    "orient": "horizontal",
                    "left": "center",
                    "bottom": "5%",
                    "inRange": {"color": ["#50a3ba", "#eac736", "#d94e5d"]}
                },
                "series": [{
                    "type": "heatmap",
                    "data": data,
                    "label": {"show": True},
                    "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0, 0, 0, 0.5)"}}
                }]
            }
            charts.append({
                "chart_type": "heatmap",
                "chart_config": json.dumps(chart_config),
                "description": "数值列之间的相关性热力图"
            })
        except Exception:
            pass

    return charts
