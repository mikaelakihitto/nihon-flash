from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

API_ROOT = Path(__file__).resolve().parents[3]
if str(API_ROOT) not in sys.path:
    sys.path.append(str(API_ROOT))

from sqlalchemy import select  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.models import Deck, NoteField, NoteType  # noqa: E402

# Conjunto padrão de pares kana/romaji usados nos seeds
HIRAGANA_PAIRS: list[tuple[str, str]] = [
    ("あ", "a"), ("い", "i"), ("う", "u"), ("え", "e"), ("お", "o"),
    ("か", "ka"), ("き", "ki"), ("く", "ku"), ("け", "ke"), ("こ", "ko"),
    ("さ", "sa"), ("し", "shi"), ("す", "su"), ("せ", "se"), ("そ", "so"),
    ("た", "ta"), ("ち", "chi"), ("つ", "tsu"), ("て", "te"), ("と", "to"),
    ("な", "na"), ("に", "ni"), ("ぬ", "nu"), ("ね", "ne"), ("の", "no"),
    ("は", "ha"), ("ひ", "hi"), ("ふ", "fu"), ("へ", "he"), ("ほ", "ho"),
    ("ま", "ma"), ("み", "mi"), ("む", "mu"), ("め", "me"), ("も", "mo"),
    ("や", "ya"), ("ゆ", "yu"), ("よ", "yo"),
    ("ら", "ra"), ("り", "ri"), ("る", "ru"), ("れ", "re"), ("ろ", "ro"),
    ("わ", "wa"), ("を", "wo"), ("ん", "n"),
]


def get_media_base_url() -> str:
    return os.getenv("MEDIA_BASE_URL", "http://localhost:3000").rstrip("/")


def get_repo_root() -> Path:
    return API_ROOT.parent.parent


def get_deck_by_slug(session, slug: str) -> Optional[Deck]:
    return session.scalar(select(Deck).where(Deck.slug == slug))


def get_note_type_for_deck(session, deck_id: int) -> Optional[NoteType]:
    return session.scalar(select(NoteType).where(NoteType.deck_id == deck_id))


def get_field(session, note_type_id: int, name: str) -> Optional[NoteField]:
    return session.scalar(
        select(NoteField).where(NoteField.note_type_id == note_type_id, NoteField.name == name)
    )
