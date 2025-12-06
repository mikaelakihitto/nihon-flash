from pydantic import BaseModel, Field

from app.schemas.note_type import NoteTypeSummary


class DeckBase(BaseModel):
    name: str
    description: str | None = None
    description_md: str | None = None
    cover_image_url: str | None = None
    instructions_md: str | None = None
    source_lang: str | None = None
    target_lang: str | None = None
    is_public: bool = False
    tags: list[str] = Field(default_factory=list)


class DeckCreate(DeckBase):
    slug: str | None = None
    owner_id: int | None = None


class DeckUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    description_md: str | None = None
    cover_image_url: str | None = None
    instructions_md: str | None = None
    source_lang: str | None = None
    target_lang: str | None = None
    is_public: bool | None = None
    tags: list[str] | None = None
    slug: str | None = None


class DeckRead(DeckBase):
    id: int
    slug: str
    owner_id: int | None = None
    note_types: list[NoteTypeSummary] = Field(default_factory=list)

    model_config = {"from_attributes": True}
