from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    text,
)
from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from app.core.database import Base
from app.models.enums import CardStatus, MediaType, NoteFieldType


class NoteType(Base):
    __tablename__ = "note_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    deck_id = Column(Integer, ForeignKey("decks.id"), nullable=True)

    deck = relationship("Deck", back_populates="note_types")
    fields = relationship("NoteField", back_populates="note_type", cascade="all, delete-orphan", order_by="NoteField.sort_order")
    templates = relationship("CardTemplate", back_populates="note_type", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="note_type")


class NoteField(Base):
    __tablename__ = "note_fields"

    id = Column(Integer, primary_key=True, index=True)
    note_type_id = Column(Integer, ForeignKey("note_types.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    label = Column(String(100), nullable=False)
    field_type = Column(Enum(NoteFieldType), nullable=False)
    is_required = Column(Boolean, nullable=False, server_default=text("1"))
    sort_order = Column(Integer, nullable=False, server_default=text("0"))
    hint = Column(Text, nullable=True)
    config = Column(JSON, nullable=False, server_default=text("'{}'"))

    note_type = relationship("NoteType", back_populates="fields")
    values = relationship("NoteFieldValue", back_populates="field", cascade="all, delete-orphan")


class CardTemplate(Base):
    __tablename__ = "card_templates"

    id = Column(Integer, primary_key=True, index=True)
    note_type_id = Column(Integer, ForeignKey("note_types.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    front_template = Column(Text, nullable=False)
    back_template = Column(Text, nullable=False)
    css = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=text("1"))

    note_type = relationship("NoteType", back_populates="templates")
    cards = relationship("Card", back_populates="template")


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("decks.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    media_type = Column(Enum(MediaType), nullable=False)
    attribution = Column(String(255), nullable=True)
    license = Column(String(100), nullable=True)
    metadata_json = Column("metadata", JSON, nullable=False, server_default=text("'{}'"))

    deck = relationship("Deck", back_populates="media_assets")
    field_values = relationship("NoteFieldValue", back_populates="media_asset")


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("decks.id"), nullable=False, index=True)
    note_type_id = Column(Integer, ForeignKey("note_types.id"), nullable=False, index=True)
    tags = Column(JSON, nullable=False, server_default=text("'[]'"))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now())

    deck = relationship("Deck", back_populates="notes")
    note_type = relationship("NoteType", back_populates="notes")
    field_values = relationship("NoteFieldValue", back_populates="note", cascade="all, delete-orphan")
    cards = relationship("Card", back_populates="note", cascade="all, delete-orphan")


class NoteFieldValue(Base):
    __tablename__ = "note_field_values"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False, index=True)
    field_id = Column(Integer, ForeignKey("note_fields.id"), nullable=False, index=True)
    value_text = Column(Text, nullable=True)
    media_asset_id = Column(Integer, ForeignKey("media_assets.id"), nullable=True)

    note = relationship("Note", back_populates="field_values")
    field = relationship("NoteField", back_populates="values")
    media_asset = relationship("MediaAsset", back_populates="field_values")
