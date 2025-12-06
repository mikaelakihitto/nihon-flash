from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.card import RenderedCard


class StudyBatch(BaseModel):
    cards: list[RenderedCard] = Field(default_factory=list)


class StudyResult(BaseModel):
    card_id: int
    correct: bool


class StudySubmit(BaseModel):
    deck_id: int
    results: list[StudyResult]


class ReviewResult(BaseModel):
    correct: bool


class ReviewResponse(BaseModel):
    card_id: int
    status: str
    stage: str | None = None
    due_at: datetime | None = None
    srs_interval: int | None = None
    srs_ease: float | None = None
    reps: int | None = None
    lapses: int | None = None

    model_config = {"from_attributes": True}
