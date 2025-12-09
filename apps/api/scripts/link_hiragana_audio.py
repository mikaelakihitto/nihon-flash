"""
Vincula os áudios gerados em apps/web/public/audio/hiragana/<romaji>.mp3
ao deck Hiragana, criando media_assets e apontando os note_field_values (campo audio).

Execute a partir da raiz do repo:
    python apps/api/scripts/link_hiragana_audio.py
"""

from typing import Dict

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import MediaAsset, Note, NoteFieldValue
from app.models.enums import MediaType
from utils.common import (
    HIRAGANA_PAIRS,
    get_deck_by_slug,
    get_field,
    get_media_base_url,
    get_note_type_for_deck,
)

BASE_URL = f"{get_media_base_url()}/audio/hiragana"
DECK_SLUG = "hiragana-basico"


def map_romaji_to_note(session, romaji_field_id: int, deck_id: int) -> Dict[str, int]:
    romaji_map: Dict[str, int] = {}
    romaji_values = session.scalars(
        select(NoteFieldValue)
        .join(Note)
        .where(
            Note.deck_id == deck_id,
            NoteFieldValue.field_id == romaji_field_id,
        )
    ).all()
    for fv in romaji_values:
        if fv.value_text:
            romaji_map[fv.value_text.strip().lower()] = fv.note_id
    return romaji_map


def main() -> None:
    session = SessionLocal()
    try:
        deck = get_deck_by_slug(session, DECK_SLUG)
        if not deck:
            raise SystemExit("Deck 'hiragana-basico' não encontrado. Rode migrations/seed primeiro.")

        note_type = get_note_type_for_deck(session, deck.id)
        if not note_type:
            raise SystemExit("NoteType do Hiragana não encontrado.")

        audio_field = get_field(session, note_type.id, "audio")
        romaji_field = get_field(session, note_type.id, "romaji")
        if not audio_field or not romaji_field:
            raise SystemExit("Campos 'audio' ou 'romaji' não encontrados no note_type do Hiragana.")

        romaji_to_note = map_romaji_to_note(session, romaji_field.id, deck.id)

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
                if audio_value.value_text:
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
