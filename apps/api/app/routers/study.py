from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Card, CardTemplate, Deck, Note, NoteFieldValue, User, UserCardProgress, CardReviewLog
from app.models.enums import CardStatus
from app.schemas.card import RenderedCard
from app.schemas.note import NoteRead
from app.schemas.study import ReviewResponse, ReviewResult, ReviewStats, StudyBatch, StudySubmit
from app.schemas.review_log import ReviewLogRead
from app.services.notes import build_note_context, render_template
from app.services.srs import apply_review

router = APIRouter(prefix="", tags=["study"])


def _ensure_deck_access(deck: Deck | None, user: User) -> Deck:
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    if not deck.is_public and deck.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this deck")
    return deck


def _render_card(card: Card, progress: UserCardProgress | None = None) -> RenderedCard:
    context = build_note_context(card.note)
    front = render_template(card.template.front_template, context)
    back = render_template(card.template.back_template, context)
    note_read = NoteRead.model_validate(card.note, from_attributes=True)

    status = progress.status if progress else card.status
    stage = getattr(progress, "stage", None) if progress else getattr(card, "stage", None)
    srs_interval = progress.srs_interval if progress else card.srs_interval
    srs_ease = progress.srs_ease if progress else card.srs_ease
    due_at = progress.due_at if progress else card.due_at
    last_reviewed_at = progress.last_reviewed_at if progress else card.last_reviewed_at
    lapses = progress.lapses if progress else card.lapses
    reps = progress.reps if progress else card.reps

    return RenderedCard(
        id=card.id,
        note_id=card.note_id,
        card_template_id=card.card_template_id,
        mnemonic=card.mnemonic,
        status=status,
        stage=stage,
        srs_interval=srs_interval,
        srs_ease=srs_ease,
        due_at=due_at,
        last_reviewed_at=last_reviewed_at,
        lapses=lapses,
        reps=reps,
        front=front,
        back=back,
        note=note_read,
        template_name=card.template.name if card.template else None,
    )


@router.get("/decks/{deck_id}/study", response_model=StudyBatch)
def get_study_batch(
    deck_id: int,
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deck = _ensure_deck_access(db.get(Deck, deck_id), current_user)

    cards = (
        db.query(Card)
        .join(Note)
        .outerjoin(
            UserCardProgress,
            and_(UserCardProgress.card_id == Card.id, UserCardProgress.user_id == current_user.id),
        )
        .options(
            joinedload(Card.template),
            joinedload(Card.note).joinedload(Note.field_values).joinedload(NoteFieldValue.field),
            joinedload(Card.note).joinedload(Note.field_values).joinedload(NoteFieldValue.media_asset),
            joinedload(Card.note).joinedload(Note.note_type),
        )
        .filter(
            Note.deck_id == deck_id,
            Card.status != CardStatus.suspended,
            UserCardProgress.card_id == None,  # noqa: E711
        )
        .order_by(Card.id)
        .limit(limit)
        .all()
    )
    rendered = [_render_card(card) for card in cards]
    return StudyBatch(cards=rendered)


@router.post("/study/submit", status_code=status.HTTP_200_OK)
def submit_study(
    payload: StudySubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deck = _ensure_deck_access(db.get(Deck, payload.deck_id), current_user)

    card_ids = [r.card_id for r in payload.results]
    if not card_ids:
        return {"updated": 0}

    cards = (
        db.query(Card)
        .join(Note)
        .filter(Note.deck_id == payload.deck_id, Card.id.in_(card_ids))
        .options(joinedload(Card.note))
        .all()
    )
    if len(cards) != len(set(card_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid card ids for this deck")

    progress_map = {
        p.card_id: p
        for p in db.query(UserCardProgress).filter(
            UserCardProgress.user_id == current_user.id, UserCardProgress.card_id.in_(card_ids)
        )
    }

    result_map = {r.card_id: r.correct for r in payload.results}
    for card in cards:
        correct = result_map.get(card.id, False)
        progress = progress_map.get(card.id)
        if not progress:
            progress = UserCardProgress(
                user_id=current_user.id,
                card_id=card.id,
                status=CardStatus.new,
                stage=None,
                srs_interval=0,
                srs_ease=card.srs_ease,
                reps=0,
                lapses=0,
            )
            db.add(progress)
        before_stage = progress.stage
        apply_review(progress, correct=correct, initial=True)
        db.add(
            CardReviewLog(
                user_id=current_user.id,
                card_id=card.id,
                note_id=card.note_id,
                deck_id=payload.deck_id,
                correct=correct,
                stage_before=before_stage,
                stage_after=progress.stage,
                status_after=progress.status,
                due_at_after=progress.due_at,
                srs_interval_after=progress.srs_interval,
                srs_ease_after=progress.srs_ease,
                reps_after=progress.reps,
                lapses_after=progress.lapses,
            )
        )

    db.commit()
    return {"updated": len(cards)}


@router.get("/decks/{deck_id}/reviews", response_model=list[RenderedCard])
def get_reviews(
    deck_id: int,
    due_only: bool = Query(True),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deck = _ensure_deck_access(db.get(Deck, deck_id), current_user)

    now = datetime.utcnow()
    query = (
        db.query(UserCardProgress)
        .join(Card, UserCardProgress.card_id == Card.id)
        .join(Note, Card.note_id == Note.id)
        .options(
            joinedload(UserCardProgress.card)
            .joinedload(Card.template),
            joinedload(UserCardProgress.card)
            .joinedload(Card.note)
            .joinedload(Note.field_values)
            .joinedload(NoteFieldValue.field),
            joinedload(UserCardProgress.card)
            .joinedload(Card.note)
            .joinedload(Note.field_values)
            .joinedload(NoteFieldValue.media_asset),
            joinedload(UserCardProgress.card).joinedload(Card.note).joinedload(Note.note_type),
        )
        .filter(
            Note.deck_id == deck_id,
            UserCardProgress.user_id == current_user.id,
            UserCardProgress.status != CardStatus.suspended,
        )
    )
    if due_only:
        query = query.filter(or_(UserCardProgress.due_at == None, UserCardProgress.due_at <= now))  # noqa: E711

    progresses = query.order_by(UserCardProgress.due_at.nullsfirst(), Card.id).limit(limit).all()
    return [_render_card(p.card, p) for p in progresses]


@router.post("/cards/{card_id}/review", response_model=ReviewResponse)
def review_card(
    card_id: int,
    payload: ReviewResult,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    card = (
        db.query(Card)
        .options(joinedload(Card.note).joinedload(Note.deck))
        .filter(Card.id == card_id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    _ensure_deck_access(card.note.deck if card.note else None, current_user)

    progress = (
        db.query(UserCardProgress)
        .filter(UserCardProgress.card_id == card_id, UserCardProgress.user_id == current_user.id)
        .first()
    )
    if not progress:
        progress = UserCardProgress(
            user_id=current_user.id,
            card_id=card.id,
            status=CardStatus.new,
            stage=None,
            srs_interval=card.srs_interval,
            srs_ease=card.srs_ease,
            reps=0,
            lapses=0,
        )
        db.add(progress)

    before_stage = progress.stage
    apply_review(progress, correct=payload.correct, initial=False)
    db.add(
        CardReviewLog(
            user_id=current_user.id,
            card_id=card.id,
            note_id=card.note_id,
            deck_id=card.note.deck_id if card.note else None,
            correct=payload.correct,
            stage_before=before_stage,
            stage_after=progress.stage,
            status_after=progress.status,
            due_at_after=progress.due_at,
            srs_interval_after=progress.srs_interval,
            srs_ease_after=progress.srs_ease,
            reps_after=progress.reps,
            lapses_after=progress.lapses,
        )
    )
    db.commit()
    db.refresh(progress)
    return ReviewResponse(
        card_id=card.id,
        status=progress.status.value if progress.status else None,
        stage=progress.stage.value if progress.stage else None,
        due_at=progress.due_at,
        srs_interval=progress.srs_interval,
        srs_ease=progress.srs_ease,
        reps=progress.reps,
        lapses=progress.lapses,
    )


@router.get("/decks/{deck_id}/review-stats", response_model=ReviewStats)
def get_review_stats(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deck = _ensure_deck_access(db.get(Deck, deck_id), current_user)

    now = datetime.utcnow()
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    base_query = (
        db.query(UserCardProgress)
        .join(Card, UserCardProgress.card_id == Card.id)
        .join(Note, Card.note_id == Note.id)
        .filter(
            Note.deck_id == deck_id,
            UserCardProgress.user_id == current_user.id,
            UserCardProgress.status != CardStatus.suspended,
        )
    )

    due_today_count = (
        base_query.filter(UserCardProgress.due_at != None, UserCardProgress.due_at <= end_of_day)  # noqa: E711
        .with_entities(func.count())
        .scalar()
        or 0
    )

    next_due_at = (
        base_query.filter(UserCardProgress.due_at != None)  # noqa: E711
        .order_by(UserCardProgress.due_at)
        .with_entities(UserCardProgress.due_at)
        .first()
    )
    next_due_value = next_due_at[0] if next_due_at else None

    return ReviewStats(due_count_today=due_today_count, next_due_at=next_due_value)


@router.get("/me/review-log", response_model=list[ReviewLogRead])
def list_my_review_logs(
    deck_id: int | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(CardReviewLog)
        .filter(CardReviewLog.user_id == current_user.id)
        .order_by(CardReviewLog.created_at.desc())
    )
    if deck_id:
        _ensure_deck_access(db.get(Deck, deck_id), current_user)
        query = query.filter(CardReviewLog.deck_id == deck_id)
    logs = query.limit(limit).all()
    return [ReviewLogRead.model_validate(log, from_attributes=True) for log in logs]
