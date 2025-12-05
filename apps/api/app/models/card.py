from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("decks.id"), nullable=False, index=True)
    front = Column(String(255), nullable=False)
    back = Column(Text, nullable=False)
    mnemonic = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)

    deck = relationship("Deck", back_populates="cards")
