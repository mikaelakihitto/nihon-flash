from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import CardStatus, LearningStage


class CardReviewLog(Base):
    __tablename__ = "card_review_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False, index=True)
    note_id = Column(Integer, nullable=False, index=True)
    deck_id = Column(Integer, nullable=False, index=True)
    correct = Column(Boolean, nullable=False, default=False)
    stage_before = Column(Enum(LearningStage), nullable=True)
    stage_after = Column(Enum(LearningStage), nullable=True)
    status_after = Column(Enum(CardStatus), nullable=True)
    due_at_after = Column(DateTime(timezone=True), nullable=True)
    srs_interval_after = Column(Integer, nullable=True)
    srs_ease_after = Column(Float, nullable=True)
    reps_after = Column(Integer, nullable=True)
    lapses_after = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    card = relationship("Card")
    user = relationship("User")
