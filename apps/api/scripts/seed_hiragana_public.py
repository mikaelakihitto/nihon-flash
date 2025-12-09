"""
Marca o deck Hiragana como público (ou cria se não existir).

Uso:
    python apps/api/scripts/seed_hiragana_public.py
"""

import sys
from pathlib import Path

from sqlalchemy import select

API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.append(str(API_ROOT))

from app.core.database import SessionLocal  # noqa: E402
from app.models import Deck  # noqa: E402


def main() -> None:
    session = SessionLocal()
    try:
        deck = session.scalar(select(Deck).where(Deck.slug == "hiragana-basico"))
        if not deck:
            deck = Deck(
                name="Hiragana - Básico",
                slug="hiragana-basico",
                description="46 caracteres básicos do hiragana.",
                description_md="Deck básico de hiragana com 46 caracteres.",
                is_public=True,
            )
            session.add(deck)
            session.commit()
            print("Deck criado como público.")
            return

        if deck.is_public:
            print("Deck já está público.")
            return

        deck.is_public = True
        session.commit()
        print("Deck atualizado para público.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
