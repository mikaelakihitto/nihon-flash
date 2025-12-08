from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Card, CardTemplate, Deck, Note, NoteField, NoteFieldValue, NoteType, User
from app.schemas.note_type import (
    CardTemplateCreate,
    CardTemplateRead,
    CardTemplateUpdate,
    NoteFieldCreate,
    NoteFieldRead,
    NoteFieldUpdate,
    NoteTypeCreate,
    NoteTypeRead,
    NoteTypeUpdate,
)

router = APIRouter(prefix="/note-types", tags=["note-types"])


def _ensure_deck_owner(deck: Deck | None, user: User) -> Deck:
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    if deck.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this deck")
    return deck


def _ensure_note_type_read_access(note_type: NoteType | None, user: User) -> NoteType:
    if not note_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note type not found")
    if note_type.deck and (not note_type.deck.is_public) and note_type.deck.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this deck")
    return note_type


def _ensure_note_type_edit_access(note_type: NoteType | None, user: User) -> NoteType:
    if not note_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note type not found")
    if note_type.deck and note_type.deck.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this deck")
    return note_type


@router.get("", response_model=list[NoteTypeRead])
def list_note_types(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note_types = (
        db.query(NoteType)
        .outerjoin(Deck, NoteType.deck_id == Deck.id)
        .filter(
            (NoteType.deck_id == None)  # noqa: E711
            | (Deck.is_public == True)  # noqa: E712
            | (Deck.owner_id == current_user.id)
        )
        .options(selectinload(NoteType.fields), selectinload(NoteType.templates))
        .all()
    )
    return note_types


@router.get("/{note_type_id}", response_model=NoteTypeRead)
def get_note_type(note_type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note_type = (
        db.query(NoteType)
        .options(selectinload(NoteType.fields), selectinload(NoteType.templates), joinedload(NoteType.deck))
        .filter(NoteType.id == note_type_id)
        .first()
    )
    return _ensure_note_type_read_access(note_type, current_user)


@router.post("", response_model=NoteTypeRead, status_code=status.HTTP_201_CREATED)
def create_note_type(payload: NoteTypeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.deck_id is not None:
        deck = _ensure_deck_owner(db.get(Deck, payload.deck_id), current_user)

    note_type = NoteType(name=payload.name, description=payload.description, deck_id=payload.deck_id)
    db.add(note_type)
    db.commit()
    db.refresh(note_type)
    return note_type


@router.put("/{note_type_id}", response_model=NoteTypeRead)
def update_note_type(note_type_id: int, payload: NoteTypeUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note_type = _ensure_note_type_edit_access(
        db.query(NoteType).options(joinedload(NoteType.deck)).filter(NoteType.id == note_type_id).first(),
        current_user,
    )

    if payload.deck_id is not None:
        deck = _ensure_deck_owner(db.get(Deck, payload.deck_id), current_user)

    for field_name in ["name", "description", "deck_id"]:
        value = getattr(payload, field_name)
        if value is not None:
            setattr(note_type, field_name, value)

    db.commit()
    db.refresh(note_type)
    return note_type


@router.delete("/{note_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note_type(note_type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note_type = _ensure_note_type_edit_access(
        db.query(NoteType).options(joinedload(NoteType.deck)).filter(NoteType.id == note_type_id).first(),
        current_user,
    )

    notes_count = db.scalar(select(func.count()).select_from(Note).where(Note.note_type_id == note_type_id))
    if notes_count and notes_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete note type with existing notes",
        )

    db.delete(note_type)
    db.commit()
    return None


@router.post("/{note_type_id}/fields", response_model=NoteFieldRead, status_code=status.HTTP_201_CREATED)
def create_field(note_type_id: int, payload: NoteFieldCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note_type = _ensure_note_type_edit_access(
        db.query(NoteType).options(joinedload(NoteType.deck), joinedload(NoteType.fields)).filter(NoteType.id == note_type_id).first(),
        current_user,
    )

    sort_order = payload.sort_order
    if sort_order is None:
        sort_order = len(note_type.fields)

    field = NoteField(
        note_type_id=note_type_id,
        name=payload.name,
        label=payload.label,
        field_type=payload.field_type,
        is_required=payload.is_required,
        sort_order=sort_order,
        hint=payload.hint,
        config=payload.config or {},
    )
    db.add(field)
    db.commit()
    db.refresh(field)
    return field


@router.put("/note-fields/{field_id}", response_model=NoteFieldRead)
def update_field(field_id: int, payload: NoteFieldUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    field = (
        db.query(NoteField)
        .options(joinedload(NoteField.note_type).joinedload(NoteType.deck))
        .filter(NoteField.id == field_id)
        .first()
    )
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    _ensure_note_type_edit_access(field.note_type, current_user)

    for attr in ["name", "label", "field_type", "is_required", "sort_order", "hint"]:
        value = getattr(payload, attr)
        if value is not None:
            setattr(field, attr, value)
    if payload.config is not None:
        field.config = payload.config

    db.commit()
    db.refresh(field)
    return field


@router.delete("/note-fields/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_field(field_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    field = (
        db.query(NoteField)
        .options(joinedload(NoteField.note_type).joinedload(NoteType.deck))
        .filter(NoteField.id == field_id)
        .first()
    )
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    _ensure_note_type_edit_access(field.note_type, current_user)

    values_count = db.scalar(
        select(func.count()).select_from(NoteFieldValue).where(NoteFieldValue.field_id == field_id)
    )
    if values_count and values_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete field with existing values",
        )

    db.delete(field)
    db.commit()
    return None


@router.post("/{note_type_id}/templates", response_model=CardTemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(note_type_id: int, payload: CardTemplateCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note_type = _ensure_note_type_edit_access(
        db.query(NoteType).options(joinedload(NoteType.deck)).filter(NoteType.id == note_type_id).first(),
        current_user,
    )

    template = CardTemplate(
        note_type_id=note_type_id,
        name=payload.name,
        front_template=payload.front_template,
        back_template=payload.back_template,
        css=payload.css,
        is_active=payload.is_active,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.put("/card-templates/{template_id}", response_model=CardTemplateRead)
def update_template(template_id: int, payload: CardTemplateUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    template = (
        db.query(CardTemplate)
        .options(joinedload(CardTemplate.note_type).joinedload(NoteType.deck))
        .filter(CardTemplate.id == template_id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    _ensure_note_type_edit_access(template.note_type, current_user)

    for attr in ["name", "front_template", "back_template", "css", "is_active"]:
        value = getattr(payload, attr)
        if value is not None:
            setattr(template, attr, value)

    db.commit()
    db.refresh(template)
    return template


@router.delete("/card-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(template_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    template = (
        db.query(CardTemplate)
        .options(joinedload(CardTemplate.note_type).joinedload(NoteType.deck))
        .filter(CardTemplate.id == template_id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    _ensure_note_type_edit_access(template.note_type, current_user)

    cards_count = db.scalar(select(func.count()).select_from(Card).where(Card.card_template_id == template_id))
    if cards_count and cards_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete template with existing cards",
        )

    db.delete(template)
    db.commit()
    return None
