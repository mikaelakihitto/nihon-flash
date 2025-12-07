from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import CardStatus, LearningStage


class UserCardProgress(Base):
    __tablename__ = "user_card_progress"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    card_id = Column(Integer, ForeignKey("cards.id"), primary_key=True)
    status = Column(Enum(CardStatus), nullable=False, server_default=text("'new'"))
    stage = Column(Enum(LearningStage), nullable=True)
    srs_interval = Column(Integer, nullable=True)
    srs_ease = Column(Float, nullable=True)
    due_at = Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    lapses = Column(Integer, nullable=False, server_default="0")
    reps = Column(Integer, nullable=False, server_default="0")

    card = relationship("Card", back_populates="progresses")
    user = relationship("User", back_populates="card_progress")
