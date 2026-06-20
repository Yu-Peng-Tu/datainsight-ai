import ast
import os
import uuid

import pandas as pd
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import AnalysisTask, TaskStatus
from app.services.data_parser import parse_data_file

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


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传 CSV 或 Excel 文件"""
    allowed_extensions = {'.csv', '.xlsx', '.xls'}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_ext}。请上传 CSV 或 Excel 文件。"
        )

    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        f.write(contents)

    try:
        parse_result = parse_data_file(file_path, file_ext)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")

    task = AnalysisTask(
        filename=file.filename,
        file_path=file_path,
        rows=parse_result["rows"],
        cols=parse_result["cols"],
        columns_info=str(parse_result["columns"]),
        status=TaskStatus.PENDING.value
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "filename": task.filename,
        "rows": task.rows,
        "cols": task.cols,
        "columns": parse_result["columns"],
        "status": task.status,
        "message": "文件上传成功"
    }


@router.get("/tasks")
async def get_tasks(db: Session = Depends(get_db)):
    """获取所有分析任务列表"""
    tasks = db.query(AnalysisTask).order_by(AnalysisTask.created_at.desc()).all()
    return [
        {
            "id": t.id,
            "filename": t.filename,
            "rows": t.rows,
            "cols": t.cols,
            "status": t.status,
            "created_at": t.created_at.isoformat() if t.created_at else None
        }
        for t in tasks
    ]


@router.get("/tasks/{task_id}")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取单个任务详情"""
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    try:
        columns = ast.literal_eval(task.columns_info) if task.columns_info else []
    except:
        columns = []

    return {
        "id": task.id,
        "filename": task.filename,
        "rows": task.rows,
        "cols": task.cols,
        "columns": columns,
        "ai_summary": task.ai_summary,
        "status": task.status,
        "created_at": task.created_at.isoformat() if task.created_at else None
    }


@router.get("/tasks/{task_id}/data")
async def get_task_data(
    task_id: int,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取任务的数据预览（前N行）"""
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    try:
        df = _load_dataframe(task)
        limit = min(max(limit, 1), 1000)
        offset = max(offset, 0)

        total = len(df)
        df_slice = df.iloc[offset:offset + limit]

        data = []
        for _, row in df_slice.iterrows():
            data.append({str(k): str(v) if pd.notna(v) else None for k, v in row.items()})

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "columns": list(df.columns),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"数据读取失败: {str(e)}")


@router.get("/tasks/{task_id}/stats")
async def get_task_stats(task_id: int, db: Session = Depends(get_db)):
    """获取任务的数据统计概览"""
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    try:
        df = _load_dataframe(task)

        stats = {
            "total_rows": len(df),
            "total_cols": len(df.columns),
            "missing_values": int(df.isna().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "column_stats": []
        }

        for col in df.columns:
            col_data = df[col]
            col_stat = {
                "name": str(col),
                "dtype": str(col_data.dtype),
                "null_count": int(col_data.isna().sum()),
                "unique_count": int(col_data.nunique()),
            }

            if pd.api.types.is_numeric_dtype(col_data):
                col_stat.update({
                    "mean": round(float(col_data.mean()), 4) if pd.notna(col_data.mean()) else None,
                    "median": round(float(col_data.median()), 4) if pd.notna(col_data.median()) else None,
                    "std": round(float(col_data.std()), 4) if pd.notna(col_data.std()) else None,
                    "min": float(col_data.min()) if pd.notna(col_data.min()) else None,
                    "max": float(col_data.max()) if pd.notna(col_data.max()) else None,
                })
            else:
                top_values = col_data.value_counts().head(3).to_dict()
                col_stat["top_values"] = {str(k): int(v) for k, v in top_values.items()}

            stats["column_stats"].append(col_stat)

        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"统计计算失败: {str(e)}")


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """删除分析任务"""
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if os.path.exists(task.file_path):
        os.remove(task.file_path)

    db.delete(task)
    db.commit()

    return {"message": "任务删除成功"}
