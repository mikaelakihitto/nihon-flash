from datetime import datetime

from pydantic import BaseModel

from app.models.enums import CardStatus, LearningStage
from app.schemas.note import NoteRead


class CardBase(BaseModel):
    note_id: int
    card_template_id: int
    mnemonic: str | None = None
    status: CardStatus = CardStatus.new
    stage: LearningStage | None = None
    srs_interval: int = 0
    srs_ease: float = 2.5
    due_at: datetime | None = None
    last_reviewed_at: datetime | None = None
    lapses: int = 0
    reps: int = 0


class CardCreate(CardBase):
    pass


class CardRead(CardBase):
    id: int

    model_config = {"from_attributes": True}


class RenderedCard(BaseModel):
    id: int
    note_id: int
    card_template_id: int
    mnemonic: str | None = None
    status: CardStatus
    stage: LearningStage | None = None
    srs_interval: int
    srs_ease: float
    due_at: datetime | None = None
    last_reviewed_at: datetime | None = None
    lapses: int
    reps: int
    front: str
    back: str
    note: NoteRead | None = None
    template_name: str | None = None

    model_config = {"from_attributes": True}
