from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.models import Card, CardTemplate, Deck, Note, NoteField, NoteFieldValue, NoteType
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


@router.get("", response_model=list[NoteTypeRead])
def list_note_types(db: Session = Depends(get_db)):
    note_types = (
        db.query(NoteType)
        .options(selectinload(NoteType.fields), selectinload(NoteType.templates))
        .all()
    )
    return note_types


@router.get("/{note_type_id}", response_model=NoteTypeRead)
def get_note_type(note_type_id: int, db: Session = Depends(get_db)):
    note_type = (
        db.query(NoteType)
        .options(selectinload(NoteType.fields), selectinload(NoteType.templates))
        .filter(NoteType.id == note_type_id)
        .first()
    )
    if not note_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note type not found")
    return note_type


@router.post("", response_model=NoteTypeRead, status_code=status.HTTP_201_CREATED)
def create_note_type(payload: NoteTypeCreate, db: Session = Depends(get_db)):
    if payload.deck_id is not None:
        deck = db.get(Deck, payload.deck_id)
        if not deck:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

    note_type = NoteType(name=payload.name, description=payload.description, deck_id=payload.deck_id)
    db.add(note_type)
    db.commit()
    db.refresh(note_type)
    return note_type


@router.put("/{note_type_id}", response_model=NoteTypeRead)
def update_note_type(note_type_id: int, payload: NoteTypeUpdate, db: Session = Depends(get_db)):
    note_type = db.get(NoteType, note_type_id)
    if not note_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note type not found")

    if payload.deck_id is not None:
        deck = db.get(Deck, payload.deck_id)
        if not deck:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

    for field_name in ["name", "description", "deck_id"]:
        value = getattr(payload, field_name)
        if value is not None:
            setattr(note_type, field_name, value)

    db.commit()
    db.refresh(note_type)
    return note_type


@router.delete("/{note_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note_type(note_type_id: int, db: Session = Depends(get_db)):
    note_type = db.get(NoteType, note_type_id)
    if not note_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note type not found")

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
def create_field(note_type_id: int, payload: NoteFieldCreate, db: Session = Depends(get_db)):
    note_type = db.get(NoteType, note_type_id)
    if not note_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note type not found")

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
def update_field(field_id: int, payload: NoteFieldUpdate, db: Session = Depends(get_db)):
    field = db.get(NoteField, field_id)
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")

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
def delete_field(field_id: int, db: Session = Depends(get_db)):
    field = db.get(NoteField, field_id)
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")

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
def create_template(note_type_id: int, payload: CardTemplateCreate, db: Session = Depends(get_db)):
    note_type = db.get(NoteType, note_type_id)
    if not note_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note type not found")

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
def update_template(template_id: int, payload: CardTemplateUpdate, db: Session = Depends(get_db)):
    template = db.get(CardTemplate, template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    for attr in ["name", "front_template", "back_template", "css", "is_active"]:
        value = getattr(payload, attr)
        if value is not None:
            setattr(template, attr, value)

    db.commit()
    db.refresh(template)
    return template


@router.delete("/card-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = db.get(CardTemplate, template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    cards_count = db.scalar(select(func.count()).select_from(Card).where(Card.card_template_id == template_id))
    if cards_count and cards_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete template with existing cards",
        )

    db.delete(template)
    db.commit()
    return None
