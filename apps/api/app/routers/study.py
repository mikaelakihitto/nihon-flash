from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models import Card, CardTemplate, Deck, Note, NoteFieldValue
from app.models.enums import CardStatus
from app.schemas.card import RenderedCard
from app.schemas.note import NoteRead
from app.schemas.study import ReviewResponse, ReviewResult, StudyBatch, StudySubmit
from app.services.notes import build_note_context, render_template
from app.services.srs import apply_review

router = APIRouter(prefix="", tags=["study"])


def _render_card(card: Card) -> RenderedCard:
    context = build_note_context(card.note)
    front = render_template(card.template.front_template, context)
    back = render_template(card.template.back_template, context)
    note_read = NoteRead.model_validate(card.note, from_attributes=True)
    return RenderedCard(
        id=card.id,
        note_id=card.note_id,
        card_template_id=card.card_template_id,
        mnemonic=card.mnemonic,
        status=card.status,
        srs_interval=card.srs_interval,
        srs_ease=card.srs_ease,
        due_at=card.due_at,
        last_reviewed_at=card.last_reviewed_at,
        lapses=card.lapses,
        reps=card.reps,
        front=front,
        back=back,
        note=note_read,
        template_name=card.template.name if card.template else None,
    )


@router.get("/decks/{deck_id}/study", response_model=StudyBatch)
def get_study_batch(deck_id: int, limit: int = Query(5, ge=1, le=50), db: Session = Depends(get_db)):
    deck = db.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

    cards = (
        db.query(Card)
        .join(Note)
        .options(
            joinedload(Card.template),
            joinedload(Card.note).joinedload(Note.field_values).joinedload(NoteFieldValue.field),
            joinedload(Card.note).joinedload(Note.field_values).joinedload(NoteFieldValue.media_asset),
            joinedload(Card.note).joinedload(Note.note_type),
        )
        .filter(and_(Note.deck_id == deck_id, Card.status == CardStatus.new))
        .order_by(Card.id)
        .limit(limit)
        .all()
    )
    rendered = [_render_card(card) for card in cards]
    return StudyBatch(cards=rendered)


@router.post("/study/submit", status_code=status.HTTP_200_OK)
def submit_study(payload: StudySubmit, db: Session = Depends(get_db)):
    deck = db.get(Deck, payload.deck_id)
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

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

    result_map = {r.card_id: r.correct for r in payload.results}
    for card in cards:
        correct = result_map.get(card.id, False)
        apply_review(card, correct=correct, initial=True)

    db.commit()
    return {"updated": len(cards)}


@router.get("/decks/{deck_id}/reviews", response_model=list[RenderedCard])
def get_reviews(
    deck_id: int,
    due_only: bool = Query(True),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    deck = db.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

    now = datetime.utcnow()
    query = (
        db.query(Card)
        .join(Note)
        .options(
            joinedload(Card.template),
            joinedload(Card.note).joinedload(Note.field_values).joinedload(NoteFieldValue.field),
            joinedload(Card.note).joinedload(Note.field_values).joinedload(NoteFieldValue.media_asset),
            joinedload(Card.note).joinedload(Note.note_type),
        )
        .filter(Note.deck_id == deck_id, Card.status != CardStatus.suspended, Card.status != CardStatus.new)
    )
    if due_only:
        query = query.filter(or_(Card.due_at == None, Card.due_at <= now))  # noqa: E711

    cards = query.order_by(Card.due_at.nullsfirst(), Card.id).limit(limit).all()
    return [_render_card(card) for card in cards]


@router.post("/cards/{card_id}/review", response_model=ReviewResponse)
def review_card(card_id: int, payload: ReviewResult, db: Session = Depends(get_db)):
    card = (
        db.query(Card)
        .options(joinedload(Card.note))
        .filter(Card.id == card_id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    apply_review(card, correct=payload.correct, initial=False)
    db.commit()
    db.refresh(card)
    return ReviewResponse(
        card_id=card.id,
        status=card.status.value,
        due_at=card.due_at,
        srs_interval=card.srs_interval,
        srs_ease=card.srs_ease,
        reps=card.reps,
        lapses=card.lapses,
    )
