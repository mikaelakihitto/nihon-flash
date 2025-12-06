from datetime import datetime, timedelta

from app.models import Card
from app.models.enums import CardStatus, LearningStage

STAGE_SCHEDULE: list[tuple[LearningStage, timedelta]] = [
    (LearningStage.curto_prazo, timedelta(hours=4)),
    (LearningStage.transicao, timedelta(hours=8)),
    (LearningStage.consolidacao, timedelta(days=1)),
    (LearningStage.longo_prazo, timedelta(days=2)),
    (LearningStage.memoria_estavel, timedelta(days=4)),
]

FALLBACK_LAST_INTERVAL = timedelta(days=7)


def _adjust_ease(current: float, correct: bool) -> float:
    if correct:
        return min(3.0, current + 0.05)
    return max(1.3, current - 0.1)


def _stage_index(stage: LearningStage | None) -> int:
    for idx, (st, _) in enumerate(STAGE_SCHEDULE):
        if stage == st:
            return idx
    return 0


def _stage_to_status(stage: LearningStage) -> CardStatus:
    # Estágios iniciais ficam como "learning", demais como "review"
    return CardStatus.learning if stage in {LearningStage.curto_prazo, LearningStage.transicao} else CardStatus.review


def apply_review(card: Card, correct: bool, initial: bool = False) -> None:
    """Atualiza SRS com base em estágios fixos."""
    now = datetime.utcnow()
    current_stage = card.stage or LearningStage.curto_prazo
    current_idx = _stage_index(current_stage)

    if initial:
        target_stage, interval = STAGE_SCHEDULE[0]
    elif correct:
        if current_idx < len(STAGE_SCHEDULE) - 1:
            target_stage, interval = STAGE_SCHEDULE[current_idx + 1]
        else:
            target_stage, interval = STAGE_SCHEDULE[-1]
            interval = FALLBACK_LAST_INTERVAL
    else:
        if current_idx > 0:
            target_stage, interval = STAGE_SCHEDULE[current_idx - 1]
        else:
            target_stage, interval = STAGE_SCHEDULE[0]

    card.stage = target_stage
    card.status = _stage_to_status(target_stage)
    card.srs_interval = int(interval.total_seconds() // 60)
    card.srs_ease = _adjust_ease(card.srs_ease or 2.5, correct)
    card.due_at = now + interval
    card.last_reviewed_at = now
    card.reps = (card.reps or 0) + 1
    if not correct:
        card.lapses = (card.lapses or 0) + 1
