import re

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, and_
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Card, Deck, Note, NoteFieldValue, NoteType, User, UserCardProgress
from app.models.enums import CardStatus, LearningStage
from app.schemas.card import CardStatusResponse, RenderedCard
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


def _ensure_can_read_deck(deck: Deck | None, user: User) -> Deck:
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    if not deck.is_public and deck.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this deck")
    return deck


def _ensure_can_edit_deck(deck: Deck | None, user: User) -> Deck:
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    if deck.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this deck")
    return deck


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
def list_decks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    decks = (
        db.query(Deck)
        .filter((Deck.is_public == True) | (Deck.owner_id == current_user.id))  # noqa: E712
        .options(
            selectinload(Deck.note_types).selectinload(NoteType.templates),
            selectinload(Deck.note_types).selectinload(NoteType.fields),
        )
        .all()
    )
    return [_build_deck_response(deck) for deck in decks]


@router.get("/slug/{slug}", response_model=DeckRead)
def get_deck_by_slug(slug: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deck = (
        db.query(Deck)
        .options(
            selectinload(Deck.note_types).selectinload(NoteType.templates),
            selectinload(Deck.note_types).selectinload(NoteType.fields),
        )
        .filter(Deck.slug == slug)
        .first()
    )
    deck = _ensure_can_read_deck(deck, current_user)
    return _build_deck_response(deck)


@router.post("", response_model=DeckRead, status_code=status.HTTP_201_CREATED)
def create_deck(deck_in: DeckCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
        owner_id=current_user.id,
    )
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return _build_deck_response(deck)


@router.get("/{deck_id}", response_model=DeckRead)
def get_deck(deck_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deck = (
        db.query(Deck)
        .options(
            selectinload(Deck.note_types).selectinload(NoteType.templates),
            selectinload(Deck.note_types).selectinload(NoteType.fields),
        )
        .filter(Deck.id == deck_id)
        .first()
    )
    deck = _ensure_can_read_deck(deck, current_user)
    return _build_deck_response(deck)


@router.put("/{deck_id}", response_model=DeckRead)
def update_deck(deck_id: int, deck_in: DeckUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deck = _ensure_can_edit_deck(db.get(Deck, deck_id), current_user)

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
def list_cards(deck_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deck = _ensure_can_read_deck(db.get(Deck, deck_id), current_user)

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

    if not cards:
        return []

    progress_map = {
        p.card_id: p
        for p in db.query(UserCardProgress).filter(
            UserCardProgress.user_id == current_user.id,
            UserCardProgress.card_id.in_([c.id for c in cards]),
        )
    }

    rendered: list[RenderedCard] = []
    for card in cards:
        context = build_note_context(card.note)
        front = render_template(card.template.front_template, context)
        back = render_template(card.template.back_template, context)
        note_read = NoteRead.model_validate(card.note, from_attributes=True)
        progress = progress_map.get(card.id)
        rendered.append(
            RenderedCard(
                id=card.id,
                note_id=card.note_id,
                card_template_id=card.card_template_id,
                mnemonic=card.mnemonic,
                status=progress.status if progress else card.status,
                stage=progress.stage if progress else getattr(card, "stage", None),
                srs_interval=progress.srs_interval if progress else card.srs_interval,
                srs_ease=progress.srs_ease if progress else card.srs_ease,
                due_at=progress.due_at if progress else card.due_at,
                last_reviewed_at=progress.last_reviewed_at if progress else card.last_reviewed_at,
                lapses=progress.lapses if progress else card.lapses,
                reps=progress.reps if progress else card.reps,
                front=front,
                back=back,
                note=note_read,
                template_name=card.template.name if card.template else None,
            )
        )

    return rendered


@router.get("/{deck_id}/cards/{card_id}/status", response_model=CardStatusResponse)
def get_card_status(
    deck_id: int,
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deck = _ensure_can_read_deck(db.get(Deck, deck_id), current_user)

    card = (
        db.query(Card)
        .join(Note)
        .options(
            joinedload(Card.template),
            joinedload(Card.note).joinedload(Note.field_values).joinedload(NoteFieldValue.field),
            joinedload(Card.note).joinedload(Note.field_values).joinedload(NoteFieldValue.media_asset),
            joinedload(Card.note).joinedload(Note.note_type),
        )
        .filter(Note.deck_id == deck_id, Card.id == card_id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found in this deck")

    progress = (
        db.query(UserCardProgress)
        .filter(UserCardProgress.card_id == card.id, UserCardProgress.user_id == current_user.id)
        .first()
    )

    context = build_note_context(card.note)
    front = render_template(card.template.front_template, context)
    back = render_template(card.template.back_template, context)
    note_read = NoteRead.model_validate(card.note, from_attributes=True)

    status_value = progress.status if progress else card.status
    stage_value = progress.stage if progress else getattr(card, "stage", None)
    srs_interval = progress.srs_interval if progress else card.srs_interval
    srs_ease = progress.srs_ease if progress else card.srs_ease
    due_at = progress.due_at if progress else card.due_at
    last_reviewed_at = progress.last_reviewed_at if progress else card.last_reviewed_at
    lapses = progress.lapses if progress else card.lapses
    reps = progress.reps if progress else card.reps

    return CardStatusResponse(
        id=card.id,
        deck_id=deck.id,
        note_id=card.note_id,
        card_template_id=card.card_template_id,
        mnemonic=card.mnemonic,
        status=status_value,
        stage=stage_value,
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


@router.get("/{deck_id}/stats", response_model=DeckStats)
def deck_stats(deck_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deck = _ensure_can_read_deck(db.get(Deck, deck_id), current_user)

    now = datetime.utcnow()
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    cards_query = db.query(Card).join(Note).filter(Note.deck_id == deck_id)
    total_cards = cards_query.count()

    # cards sem progresso para este usuário = novos disponíveis
    new_available = (
        db.query(Card)
        .join(Note)
        .outerjoin(
            UserCardProgress,
            and_(UserCardProgress.card_id == Card.id, UserCardProgress.user_id == current_user.id),
        )
        .filter(
            Note.deck_id == deck_id,
            UserCardProgress.card_id == None,  # noqa: E711
            Card.status == CardStatus.new,
        )
        .count()
    )

    progress_query = (
        db.query(UserCardProgress)
        .join(Card, UserCardProgress.card_id == Card.id)
        .join(Note, Card.note_id == Note.id)
        .filter(UserCardProgress.user_id == current_user.id, Note.deck_id == deck_id)
    )

    due_today = (
        progress_query.filter(
            UserCardProgress.status != CardStatus.suspended,
            UserCardProgress.due_at != None,  # noqa: E711
            UserCardProgress.due_at <= end_of_day,
        )
        .with_entities(func.count())
        .scalar()
        or 0
    )

    next_due = (
        progress_query.filter(UserCardProgress.due_at != None)  # noqa: E711
        .order_by(UserCardProgress.due_at)
        .with_entities(UserCardProgress.due_at)
        .first()
    )
    next_due_at = next_due[0] if next_due else None

    totals = progress_query.with_entities(func.sum(UserCardProgress.reps), func.sum(UserCardProgress.lapses)).first()
    sum_reps = totals[0] or 0
    sum_lapses = totals[1] or 0
    avg_reps = float(sum_reps) / total_cards if total_cards else None
    accuracy_estimate = None
    if sum_reps:
        accuracy_estimate = max(0.0, (sum_reps - sum_lapses) / sum_reps)

    stage_counts = (
        progress_query.with_entities(UserCardProgress.stage, func.count())
        .group_by(UserCardProgress.stage)
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
        new_available=new_available,
    )


@router.get("/{deck_id}/cards-with-stats", response_model=list[CardWithStats])
def deck_cards_with_stats(deck_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deck = _ensure_can_read_deck(db.get(Deck, deck_id), current_user)

    cards = (
        db.query(Card)
        .join(Note)
        .options(joinedload(Card.template), joinedload(Card.note))
        .filter(Note.deck_id == deck_id)
        .order_by(Card.id)
        .all()
    )

    if not cards:
        return []

    progress_map = {
        p.card_id: p
        for p in db.query(UserCardProgress).filter(
            UserCardProgress.user_id == current_user.id,
            UserCardProgress.card_id.in_([c.id for c in cards]),
        )
    }

    result: list[CardWithStats] = []
    for card in cards:
        context = build_note_context(card.note)
        front = render_template(card.template.front_template, context)
        preview = front if len(front) <= 80 else front[:77] + "..."
        progress = progress_map.get(card.id)
        result.append(
            CardWithStats(
                id=card.id,
                front=preview,
                status=(progress.status.value if progress and progress.status else card.status.value if card.status else "unknown"),
                stage=progress.stage.value if progress and progress.stage else getattr(card, "stage", None) and card.stage.value,
                due_at=progress.due_at if progress else card.due_at,
                reps=progress.reps if progress else card.reps,
                lapses=progress.lapses if progress else card.lapses,
                srs_interval=progress.srs_interval if progress else card.srs_interval,
                srs_ease=progress.srs_ease if progress else card.srs_ease,
                last_reviewed_at=progress.last_reviewed_at if progress else card.last_reviewed_at,
            )
        )
    return result
