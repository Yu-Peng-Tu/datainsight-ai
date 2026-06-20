import ast
import json

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AnalysisTask, ChatMessage, TaskStatus
from app.services.ai_analyzer import ai_analyzer

router = APIRouter()


def _load_dataframe(task: AnalysisTask) -> pd.DataFrame:
    """从任务文件路径加载 DataFrame"""
    import os
    file_ext = os.path.splitext(task.file_path)[1].lower()
    if file_ext == '.csv':
        return pd.read_csv(task.file_path)
    elif file_ext in ['.xlsx', '.xls']:
        return pd.read_excel(task.file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_ext}")


@router.post("/analyze/{task_id}")
async def analyze_task(task_id: int, db: Session = Depends(get_db)):
    """触发 AI 分析任务"""
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task.status = TaskStatus.ANALYZING.value
    db.commit()

    return {
        "task_id": task.id,
        "status": task.status,
        "message": "AI 分析已启动，请使用流式接口获取结果"
    }


@router.get("/analyze/{task_id}/stream")
async def analyze_stream(task_id: int, db: Session = Depends(get_db)):
    """流式获取 AI 分析结果（SSE）"""
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    try:
        columns = ast.literal_eval(task.columns_info) if task.columns_info else []
    except:
        columns = []

    try:
        df = _load_dataframe(task)
        sample_data = df.head(5).to_string(index=False)
    except Exception as e:
        return StreamingResponse(
            iter([f"data: {json.dumps({'content': f'数据读取失败: {str(e)}'})}\n\n"]),
            media_type="text/event-stream"
        )

    async def event_generator():
        full_content = ""
        async for chunk in ai_analyzer.analyze(
            filename=task.filename,
            rows=task.rows or 0,
            cols=task.cols or 0,
            columns=columns,
            sample_data=sample_data
        ):
            full_content += chunk
            yield f"data: {json.dumps({'content': chunk})}\n\n"

        # 保存分析结果到数据库
        task.ai_summary = full_content
        task.status = TaskStatus.COMPLETED.value
        db.commit()

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.post("/chat/{task_id}")
async def chat_task(
    task_id: int,
    question: str,
    db: Session = Depends(get_db)
):
    """对数据进行对话追问"""
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 获取对话历史
    history = db.query(ChatMessage).filter(
        ChatMessage.task_id == task_id
    ).order_by(ChatMessage.created_at).all()

    conversation_history = [
        {"role": h.role, "content": h.content}
        for h in history
    ]

    # 保存用户问题
    user_msg = ChatMessage(task_id=task_id, role="user", content=question)
    db.add(user_msg)
    db.commit()

    # 构建数据摘要
    data_summary = f"文件: {task.filename}, 行数: {task.rows}, 列数: {task.cols}"
    if task.ai_summary:
        data_summary += f"\nAI分析摘要: {task.ai_summary[:500]}..."

    async def event_generator():
        full_content = ""
        async for chunk in ai_analyzer.chat(
            question=question,
            data_summary=data_summary,
            conversation_history=conversation_history
        ):
            full_content += chunk
            yield f"data: {json.dumps({'content': chunk})}\n\n"

        # 保存 AI 回复
        assistant_msg = ChatMessage(
            task_id=task_id,
            role="assistant",
            content=full_content
        )
        db.add(assistant_msg)
        db.commit()

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
