from datetime import datetime

from pydantic import BaseModel

from app.models.enums import CardStatus, LearningStage


class ReviewLogRead(BaseModel):
    id: int
    user_id: int
    card_id: int
    note_id: int
    deck_id: int
    correct: bool
    stage_before: LearningStage | None = None
    stage_after: LearningStage | None = None
    status_after: CardStatus | None = None
    due_at_after: datetime | None = None
    srs_interval_after: int | None = None
    srs_ease_after: float | None = None
    reps_after: int | None = None
    lapses_after: int | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
