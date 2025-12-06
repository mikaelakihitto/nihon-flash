import re

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.database import get_db
from app.models import Card, Deck, Note, NoteFieldValue, NoteType
from app.models.enums import CardStatus, LearningStage
from app.schemas.card import RenderedCard
from app.schemas.deck import DeckCreate, DeckRead, DeckUpdate
from app.schemas.deck_stats import CardWithStats, DeckStats
from app.schemas.note import NoteRead
from app.schemas.note_type import NoteTypeSummary
from app.services.notes import build_note_context, render_template

router = APIRouter(prefix="/decks", tags=["decks"])


def _slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "deck"


def _build_deck_response(deck: Deck) -> DeckRead:
    summaries = [
        NoteTypeSummary(
            id=nt.id,
            name=nt.name,
            description=nt.description,
            template_count=len(nt.templates),
            field_count=len(nt.fields),
        )
        for nt in deck.note_types
    ]
    return DeckRead(
        id=deck.id,
        name=deck.name,
        slug=deck.slug,
        description=deck.description,
        description_md=deck.description_md,
        cover_image_url=deck.cover_image_url,
        instructions_md=deck.instructions_md,
        source_lang=deck.source_lang,
        target_lang=deck.target_lang,
        is_public=deck.is_public,
        tags=deck.tags or [],
        owner_id=deck.owner_id,
        note_types=summaries,
    )


@router.get("", response_model=list[DeckRead])
def list_decks(db: Session = Depends(get_db)):
    decks = (
        db.query(Deck)
        .options(
            selectinload(Deck.note_types).selectinload(NoteType.templates),
            selectinload(Deck.note_types).selectinload(NoteType.fields),
        )
        .all()
    )
    return [_build_deck_response(deck) for deck in decks]


@router.post("", response_model=DeckRead, status_code=status.HTTP_201_CREATED)
def create_deck(deck_in: DeckCreate, db: Session = Depends(get_db)):
    slug = deck_in.slug or _slugify(deck_in.name)
    exists = db.scalar(select(Deck.id).where(Deck.slug == slug))
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already in use")

    deck = Deck(
        name=deck_in.name,
        slug=slug,
        description=deck_in.description,
        description_md=deck_in.description_md or deck_in.description,
        cover_image_url=deck_in.cover_image_url,
        instructions_md=deck_in.instructions_md,
        source_lang=deck_in.source_lang,
        target_lang=deck_in.target_lang,
        is_public=deck_in.is_public,
        tags=deck_in.tags or [],
        owner_id=deck_in.owner_id,
    )
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return _build_deck_response(deck)


@router.get("/{deck_id}", response_model=DeckRead)
def get_deck(deck_id: int, db: Session = Depends(get_db)):
    deck = (
        db.query(Deck)
        .options(
            selectinload(Deck.note_types).selectinload(NoteType.templates),
            selectinload(Deck.note_types).selectinload(NoteType.fields),
        )
        .filter(Deck.id == deck_id)
        .first()
    )
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    return _build_deck_response(deck)


@router.put("/{deck_id}", response_model=DeckRead)
def update_deck(deck_id: int, deck_in: DeckUpdate, db: Session = Depends(get_db)):
    deck = db.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

    if deck_in.slug is not None:
        slug = deck_in.slug or _slugify(deck_in.name or deck.name)
        exists = db.scalar(select(Deck.id).where(Deck.slug == slug, Deck.id != deck_id))
        if exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already in use")
        deck.slug = slug

    for field_name in [
        "name",
        "description",
        "description_md",
        "cover_image_url",
        "instructions_md",
        "source_lang",
        "target_lang",
        "is_public",
    ]:
        value = getattr(deck_in, field_name)
        if value is not None:
            setattr(deck, field_name, value)

    if deck_in.tags is not None:
        deck.tags = deck_in.tags

    db.commit()
    db.refresh(deck)
    deck = (
        db.query(Deck)
        .options(
            selectinload(Deck.note_types).selectinload(NoteType.templates),
            selectinload(Deck.note_types).selectinload(NoteType.fields),
        )
        .filter(Deck.id == deck_id)
        .first()
    )
    return _build_deck_response(deck)


@router.get("/{deck_id}/cards", response_model=list[RenderedCard])
def list_cards(deck_id: int, db: Session = Depends(get_db)):
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
        .filter(Note.deck_id == deck_id)
        .all()
    )

    rendered: list[RenderedCard] = []
    for card in cards:
        context = build_note_context(card.note)
        front = render_template(card.template.front_template, context)
        back = render_template(card.template.back_template, context)
        note_read = NoteRead.model_validate(card.note, from_attributes=True)
        rendered.append(
            RenderedCard(
                id=card.id,
                note_id=card.note_id,
                card_template_id=card.card_template_id,
                mnemonic=card.mnemonic,
                status=card.status,
                stage=getattr(card, "stage", None),
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
        )

    return rendered


@router.get("/{deck_id}/stats", response_model=DeckStats)
def deck_stats(deck_id: int, db: Session = Depends(get_db)):
    deck = db.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

    now = datetime.utcnow()
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    cards_query = db.query(Card).join(Note).filter(Note.deck_id == deck_id)
    total_cards = cards_query.count()

    due_today = (
        cards_query.filter(Card.status != CardStatus.new, Card.status != CardStatus.suspended, Card.due_at != None, Card.due_at <= end_of_day)  # noqa: E711
        .with_entities(func.count())
        .scalar()
        or 0
    )

    next_due = (
        cards_query.filter(Card.due_at != None)  # noqa: E711
        .order_by(Card.due_at)
        .with_entities(Card.due_at)
        .first()
    )
    next_due_at = next_due[0] if next_due else None

    totals = cards_query.with_entities(func.sum(Card.reps), func.sum(Card.lapses)).first()
    sum_reps = totals[0] or 0
    sum_lapses = totals[1] or 0
    avg_reps = float(sum_reps) / total_cards if total_cards else None
    accuracy_estimate = None
    if sum_reps:
        accuracy_estimate = max(0.0, (sum_reps - sum_lapses) / sum_reps)

    stage_counts = (
        cards_query.with_entities(Card.stage, func.count())
        .group_by(Card.stage)
        .all()
    )
    stage_distribution = {stage.value if stage else "unknown": count for stage, count in stage_counts}

    return DeckStats(
        total_cards=total_cards,
        due_today=due_today,
        next_due_at=next_due_at,
        avg_reps=avg_reps,
        total_lapses=sum_lapses,
        accuracy_estimate=accuracy_estimate,
        stage_distribution=stage_distribution,
    )


@router.get("/{deck_id}/cards-with-stats", response_model=list[CardWithStats])
def deck_cards_with_stats(deck_id: int, db: Session = Depends(get_db)):
    deck = db.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

    cards = (
        db.query(Card)
        .join(Note)
        .options(joinedload(Card.template), joinedload(Card.note))
        .filter(Note.deck_id == deck_id)
        .order_by(Card.id)
        .all()
    )

    result: list[CardWithStats] = []
    for card in cards:
        context = build_note_context(card.note)
        front = render_template(card.template.front_template, context)
        preview = front if len(front) <= 80 else front[:77] + "..."
        result.append(
            CardWithStats(
                id=card.id,
                front=preview,
                status=card.status.value if card.status else "unknown",
                stage=card.stage.value if getattr(card, "stage", None) else None,
                due_at=card.due_at,
                reps=card.reps,
                lapses=card.lapses,
                srs_interval=card.srs_interval,
                srs_ease=card.srs_ease,
                last_reviewed_at=card.last_reviewed_at,
            )
        )
    return result
