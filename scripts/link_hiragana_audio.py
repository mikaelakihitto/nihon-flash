"""
Vincula os áudios gerados em apps/web/public/audio/hiragana/<romaji>.mp3
ao deck Hiragana, criando media_assets e apontando os note_field_values (campo audio).

Execute a partir da raiz do repo:
    python scripts/link_hiragana_audio.py
"""

import sys
from pathlib import Path
from typing import Dict

from sqlalchemy import select

REPO_ROOT = Path(__file__).resolve().parent.parent
API_PATH = REPO_ROOT / "apps" / "api"
if str(API_PATH) not in sys.path:
    sys.path.append(str(API_PATH))

from app.core.database import SessionLocal  # noqa: E402
from app.models import MediaAsset, Note, NoteField, NoteFieldValue, NoteType, Deck  # noqa: E402
from app.models.enums import MediaType  # noqa: E402


HIRAGANA_PAIRS = [
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

BASE_URL = "http://localhost:3000/audio/hiragana"
DECK_SLUG = "hiragana-basico"


def main() -> None:
    session = SessionLocal()
    try:
        deck = session.scalar(select(Deck).where(Deck.slug == DECK_SLUG))
        if not deck:
            raise SystemExit("Deck 'hiragana-basico' não encontrado. Rode migrations/seed primeiro.")

        note_type = session.scalar(select(NoteType).where(NoteType.deck_id == deck.id, NoteType.name.ilike("hiragana%")))
        if not note_type:
            raise SystemExit("NoteType do Hiragana não encontrado.")

        audio_field = session.scalar(select(NoteField).where(NoteField.note_type_id == note_type.id, NoteField.name == "audio"))
        romaji_field = session.scalar(select(NoteField).where(NoteField.note_type_id == note_type.id, NoteField.name == "romaji"))
        if not audio_field or not romaji_field:
            raise SystemExit("Campos 'audio' ou 'romaji' não encontrados no note_type do Hiragana.")

        # Mapear romaji -> note_id
        romaji_to_note: Dict[str, int] = {}
        romaji_values = session.scalars(
            select(NoteFieldValue)
            .join(Note)
            .where(
                Note.deck_id == deck.id,
                NoteFieldValue.field_id == romaji_field.id,
            )
        ).all()
        for fv in romaji_values:
            if fv.value_text:
                romaji_to_note[fv.value_text.strip()] = fv.note_id

        created_assets = 0
        updated_values = 0

        for kana, romaji in HIRAGANA_PAIRS:
            note_id = romaji_to_note.get(romaji)
            if not note_id:
                print(f"[WARN] Nota não encontrada para romaji '{romaji}' ({kana})")
                continue

            file_name = f"{romaji}.mp3"
            url = f"{BASE_URL}/{file_name}"
            asset = session.scalar(
                select(MediaAsset).where(MediaAsset.deck_id == deck.id, MediaAsset.file_name == file_name)
            )
            if not asset:
                asset = MediaAsset(
                    deck_id=deck.id,
                    file_name=file_name,
                    url=url,
                    media_type=MediaType.audio,
                    attribution="gTTS",
                    license="",
                    metadata={},
                )
                session.add(asset)
                session.flush()
                created_assets += 1

            audio_value = session.scalar(
                select(NoteFieldValue).where(
                    NoteFieldValue.note_id == note_id,
                    NoteFieldValue.field_id == audio_field.id,
                )
            )
            if audio_value:
                audio_value.media_asset_id = asset.id
                if not audio_value.value_text:
                    audio_value.value_text = None
                updated_values += 1
            else:
                session.add(
                    NoteFieldValue(
                        note_id=note_id,
                        field_id=audio_field.id,
                        value_text=None,
                        media_asset_id=asset.id,
                    )
                )
                updated_values += 1

        session.commit()
        print(f"Concluído. Media assets novos: {created_assets}, valores de campo atualizados/criados: {updated_values}")
        print(f"URLs base usadas: {BASE_URL}/<romaji>.mp3")
    finally:
        session.close()


if __name__ == "__main__":
    main()
