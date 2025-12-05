from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.card import Card
from app.models.deck import Deck
from app.schemas.card import CardRead
from app.schemas.deck import DeckRead

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("", response_model=list[DeckRead])
def list_decks(db: Session = Depends(get_db)):
    decks = db.execute(select(Deck)).scalars().all()
    return decks


@router.get("/{deck_id}/cards", response_model=list[CardRead])
def list_cards(deck_id: int, db: Session = Depends(get_db)):
    deck = db.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    cards = db.execute(select(Card).where(Card.deck_id == deck_id)).scalars().all()
    return cards
