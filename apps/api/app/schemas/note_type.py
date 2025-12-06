from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import NoteFieldType


class NoteFieldBase(BaseModel):
    name: str
    label: str
    field_type: NoteFieldType
    is_required: bool = True
    sort_order: int = 0
    hint: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class NoteFieldCreate(NoteFieldBase):
    note_type_id: int | None = None


class NoteFieldUpdate(BaseModel):
    name: str | None = None
    label: str | None = None
    field_type: NoteFieldType | None = None
    is_required: bool | None = None
    sort_order: int | None = None
    hint: str | None = None
    config: dict[str, Any] | None = None


class NoteFieldRead(NoteFieldBase):
    id: int
    note_type_id: int

    model_config = {"from_attributes": True}


class CardTemplateBase(BaseModel):
    name: str
    front_template: str
    back_template: str
    css: str | None = None
    is_active: bool = True


class CardTemplateCreate(CardTemplateBase):
    note_type_id: int | None = None


class CardTemplateUpdate(BaseModel):
    name: str | None = None
    front_template: str | None = None
    back_template: str | None = None
    css: str | None = None
    is_active: bool | None = None


class CardTemplateRead(CardTemplateBase):
    id: int
    note_type_id: int

    model_config = {"from_attributes": True}


class NoteTypeBase(BaseModel):
    name: str
    description: str | None = None
    deck_id: int | None = None


class NoteTypeCreate(NoteTypeBase):
    pass


class NoteTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    deck_id: int | None = None


class NoteTypeRead(NoteTypeBase):
    id: int
    fields: list[NoteFieldRead] = Field(default_factory=list)
    templates: list[CardTemplateRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class NoteTypeSummary(BaseModel):
    id: int
    name: str
    description: str | None = None
    template_count: int = 0
    field_count: int = 0

    model_config = {"from_attributes": True}
