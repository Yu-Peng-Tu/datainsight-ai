import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisTask(Base):
    """分析任务表"""
    __tablename__ = "analysis_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    rows = Column(Integer, nullable=True)
    cols = Column(Integer, nullable=True)
    columns_info = Column(Text, nullable=True)  # JSON 格式
    ai_summary = Column(Text, nullable=True)
    status = Column(String(20), default=TaskStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联
    chat_messages = relationship("ChatMessage", back_populates="task", cascade="all, delete-orphan")
    visualizations = relationship("Visualization", back_populates="task", cascade="all, delete-orphan")


class ChatMessage(Base):
    """对话记录表"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("analysis_tasks.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user / assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("AnalysisTask", back_populates="chat_messages")


class Visualization(Base):
    """可视化图表记录表"""
    __tablename__ = "visualizations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("analysis_tasks.id"), nullable=False)
    chart_type = Column(String(50), nullable=False)  # bar / line / scatter / pie / heatmap
    chart_config = Column(Text, nullable=True)  # ECharts 配置 JSON
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("AnalysisTask", back_populates="visualizations")
