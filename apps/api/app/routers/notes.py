from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Note, NoteFieldValue, Deck, User
from app.schemas.note import NoteCreate, NoteRead
from app.services.notes import create_note_with_cards

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deck = db.get(Deck, payload.deck_id)
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    if deck.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this deck")

    note = create_note_with_cards(db, payload)
    if not note:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create note")
    return NoteRead.model_validate(note, from_attributes=True)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = (
        db.query(Note)
        .options(
            joinedload(Note.field_values).joinedload(NoteFieldValue.field),
            joinedload(Note.field_values).joinedload(NoteFieldValue.media_asset),
            joinedload(Note.note_type),
            joinedload(Note.deck),
        )
        .filter(Note.id == note_id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    if not note.deck.is_public and note.deck.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this deck")
    return note
