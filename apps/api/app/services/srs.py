from datetime import datetime, timedelta

from app.models import Card
from app.models.enums import CardStatus


def _adjust_ease(current: float, correct: bool) -> float:
    # Ajuste simples de facilidade: aumenta um pouco em acertos, diminui em erros, com limites.
    if correct:
        return min(3.0, current + 0.1)
    return max(1.3, current - 0.2)


def calculate_next_interval(current_interval: int, correct: bool) -> int:
    # Intervalo em minutos; dobra em acertos, volta para 1 em erros.
    return max(1, current_interval * 2) if correct else 1


def apply_review(card: Card, correct: bool, initial: bool = False) -> None:
    """Atualiza campos SRS de um card após uma resposta."""
    now = datetime.utcnow()
    current_interval = card.srs_interval or 1
    next_interval = calculate_next_interval(current_interval, correct)
    card.srs_interval = next_interval
    card.srs_ease = _adjust_ease(card.srs_ease or 2.5, correct)
    card.due_at = now + timedelta(minutes=next_interval)
    card.last_reviewed_at = now
    card.reps = (card.reps or 0) + 1
    if not correct:
        card.lapses = (card.lapses or 0) + 1
    card.status = CardStatus.learning if initial and not correct else CardStatus.review
