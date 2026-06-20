from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AnalysisTask, Visualization
from app.services.chart_generator import auto_generate_charts

router = APIRouter()


@router.post("/charts/{task_id}/generate")
async def generate_charts(task_id: int, db: Session = Depends(get_db)):
    """
    为任务自动生成可视化图表

    - **task_id**: 任务 ID
    """
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 清除已有图表
    db.query(Visualization).filter(Visualization.task_id == task_id).delete()

    # 生成图表
    charts = auto_generate_charts(task)

    # 保存到数据库
    for chart in charts:
        viz = Visualization(
            task_id=task_id,
            chart_type=chart["chart_type"],
            chart_config=chart["chart_config"],
            description=chart["description"]
        )
        db.add(viz)

    db.commit()

    return {
        "task_id": task_id,
        "generated_count": len(charts),
        "charts": [
            {
                "chart_type": c["chart_type"],
                "description": c["description"]
            }
            for c in charts
        ]
    }


@router.get("/charts/{task_id}")
async def get_charts(task_id: int, db: Session = Depends(get_db)):
    """
    获取任务的所有可视化图表

    - **task_id**: 任务 ID
    """
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    visualizations = db.query(Visualization).filter(
        Visualization.task_id == task_id
    ).order_by(Visualization.created_at).all()

    return [
        {
            "id": v.id,
            "chart_type": v.chart_type,
            "chart_config": v.chart_config,
            "description": v.description
        }
        for v in visualizations
    ]
