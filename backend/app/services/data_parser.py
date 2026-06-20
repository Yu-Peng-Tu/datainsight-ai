import os
import json

import pandas as pd


def parse_data_file(file_path: str, file_ext: str) -> dict:
    """
    解析 CSV 或 Excel 文件

    Args:
        file_path: 文件路径
        file_ext: 文件扩展名 (.csv, .xlsx, .xls)

    Returns:
        解析结果字典:
        {
            "rows": int,
            "cols": int,
            "columns": [
                {"name": str, "dtype": str, "sample": list}
            ]
        }
    """
    # 读取文件
    if file_ext == '.csv':
        df = pd.read_csv(file_path)
    elif file_ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_ext}")

    # 基础统计
    rows = len(df)
    cols = len(df.columns)

    # 列信息
    columns_info = []
    for col in df.columns:
        col_data = df[col]
        dtype = str(col_data.dtype)

        # 获取样本值（最多5个非空值）
        sample = col_data.dropna().head(5).tolist()
        # 转换为可序列化的类型
        sample = [str(v) for v in sample]

        columns_info.append({
            "name": str(col),
            "dtype": dtype,
            "sample": sample,
            "null_count": int(col_data.isna().sum()),
            "unique_count": int(col_data.nunique())
        })

    return {
        "rows": rows,
        "cols": cols,
        "columns": columns_info
    }
