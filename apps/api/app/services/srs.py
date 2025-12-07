from datetime import datetime, timedelta

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


def apply_review(obj: object, correct: bool, initial: bool = False) -> None:
    """Atualiza SRS com base em estágios fixos."""
    now = datetime.utcnow()
    current_stage = getattr(obj, "stage", None) or LearningStage.curto_prazo
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

    setattr(obj, "stage", target_stage)
    setattr(obj, "status", _stage_to_status(target_stage))
    setattr(obj, "srs_interval", int(interval.total_seconds() // 60))
    setattr(obj, "srs_ease", _adjust_ease(getattr(obj, "srs_ease", None) or 2.5, correct))
    setattr(obj, "due_at", now + interval)
    setattr(obj, "last_reviewed_at", now)
    setattr(obj, "reps", (getattr(obj, "reps", None) or 0) + 1)
    if not correct:
        setattr(obj, "lapses", (getattr(obj, "lapses", None) or 0) + 1)
