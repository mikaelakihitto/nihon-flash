from pydantic import BaseModel


class DeckBase(BaseModel):
    name: str
    description: str | None = None


class DeckCreate(DeckBase):
    owner_id: int | None = None


class DeckRead(DeckBase):
    id: int

    model_config = {"from_attributes": True}
