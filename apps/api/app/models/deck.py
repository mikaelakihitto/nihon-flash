from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, JSON, text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Deck(Base):
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(150), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)
    description_md = Column(Text, nullable=True)
    cover_image_url = Column(String(255), nullable=True)
    instructions_md = Column(Text, nullable=True)
    source_lang = Column(String(10), nullable=True)
    target_lang = Column(String(10), nullable=True)
    is_public = Column(Boolean, nullable=False, server_default=text("0"))
    tags = Column(JSON, nullable=False, server_default=text("'[]'"))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    owner = relationship("User", back_populates="decks")
    note_types = relationship("NoteType", back_populates="deck", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="deck", cascade="all, delete-orphan")
    media_assets = relationship("MediaAsset", back_populates="deck", cascade="all, delete-orphan")
