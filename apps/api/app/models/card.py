from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, Text, text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import CardStatus


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False, index=True)
    card_template_id = Column(Integer, ForeignKey("card_templates.id"), nullable=False, index=True)
    mnemonic = Column(Text, nullable=True)
    status = Column(Enum(CardStatus), nullable=False, server_default=text("'new'"))
    srs_interval = Column(Integer, nullable=False, server_default="0")
    srs_ease = Column(Float, nullable=False, server_default="2.5")
    due_at = Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    lapses = Column(Integer, nullable=False, server_default="0")
    reps = Column(Integer, nullable=False, server_default="0")

    note = relationship("Note", back_populates="cards")
    template = relationship("CardTemplate", back_populates="cards")
