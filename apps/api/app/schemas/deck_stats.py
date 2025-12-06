from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DeckStats(BaseModel):
    total_cards: int
    due_today: int
    next_due_at: datetime | None = None
    avg_reps: float | None = None
    total_lapses: int | None = None
    accuracy_estimate: float | None = None
    stage_distribution: dict[str, int] = Field(default_factory=dict)


class CardWithStats(BaseModel):
    id: int
    front: str
    status: str
    stage: str | None = None
    due_at: datetime | None = None
    reps: int | None = None
    lapses: int | None = None
    srs_interval: int | None = None
    srs_ease: float | None = None
    last_reviewed_at: datetime | None = None

    model_config = {"from_attributes": True}
