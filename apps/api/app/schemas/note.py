from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.note_type import NoteFieldRead


class NoteFieldValueBase(BaseModel):
    field_id: int
    value_text: str | None = None
    media_asset_id: int | None = None


class NoteFieldValueCreate(NoteFieldValueBase):
    pass


class NoteFieldValueRead(NoteFieldValueBase):
    id: int
    note_id: int
    field: NoteFieldRead | None = None

    model_config = {"from_attributes": True}


class NoteBase(BaseModel):
    deck_id: int
    note_type_id: int
    tags: list[str] = Field(default_factory=list)


class NoteCreate(NoteBase):
    field_values: list[NoteFieldValueCreate]
    mnemonic: str | None = None


class NoteRead(NoteBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    field_values: list[NoteFieldValueRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}
