from pydantic import BaseModel


class CardBase(BaseModel):
    deck_id: int
    front: str
    back: str
    mnemonic: str | None = None
    type: str


class CardCreate(CardBase):
    pass


class CardRead(CardBase):
    id: int

    model_config = {"from_attributes": True}
