from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models import Note, NoteFieldValue
from app.schemas.note import NoteCreate, NoteRead
from app.services.notes import create_note_with_cards

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)):
    note = create_note_with_cards(db, payload)
    if not note:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create note")
    return NoteRead.model_validate(note, from_attributes=True)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = (
        db.query(Note)
        .options(
            joinedload(Note.field_values).joinedload(NoteFieldValue.field),
            joinedload(Note.field_values).joinedload(NoteFieldValue.media_asset),
            joinedload(Note.note_type),
        )
        .filter(Note.id == note_id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note
