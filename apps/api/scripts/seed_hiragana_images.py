"""
Seed para associar imagens estáticas aos cards de Hiragana.

Pré-requisito: arquivos PNG em apps/web/public/media/hiragana/<romaji>.png
URL pública padrão: MEDIA_BASE_URL/media/hiragana/<arquivo>.png
"""

from pathlib import Path
from typing import Dict

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import CardTemplate, Deck, MediaAsset, NoteField, NoteFieldValue, NoteType
from app.models.enums import MediaType, NoteFieldType
from utils.common import (
    HIRAGANA_PAIRS,
    get_deck_by_slug,
    get_field,
    get_media_base_url,
    get_note_type_for_deck,
    get_repo_root,
)


def ensure_image_field(session, note_type: NoteType) -> NoteField:
    field = session.scalar(
        select(NoteField).where(NoteField.note_type_id == note_type.id, NoteField.name == "imagem")
    )
    if field:
        return field

    sort_order = session.scalar(
        select(NoteField.sort_order)
        .where(NoteField.note_type_id == note_type.id)
        .order_by(NoteField.sort_order.desc())
        .limit(1)
    )
    field = NoteField(
        note_type_id=note_type.id,
        name="imagem",
        label="Imagem",
        field_type=NoteFieldType.image,
        is_required=False,
        sort_order=(sort_order or 0) + 1,
        hint="Imagem de apoio para o kana",
        config={},
    )
    session.add(field)
    session.flush()
    return field


def load_media_assets(session, deck: Deck, media_dir: Path, base_url: str) -> Dict[str, MediaAsset]:
    assets: Dict[str, MediaAsset] = {}
    if not media_dir.exists():
        print(f"Diretório de mídia não encontrado: {media_dir}")
        return assets

    for file_path in sorted(media_dir.glob("*.png")):
        base = file_path.stem.lower()
        url = f"{base_url}/media/hiragana/{file_path.name}"
        asset = session.scalar(
            select(MediaAsset).where(
                MediaAsset.deck_id == deck.id,
                MediaAsset.file_name == file_path.name,
                MediaAsset.media_type == MediaType.image,
            )
        )
        if not asset:
            asset = MediaAsset(
                deck_id=deck.id,
                file_name=file_path.name,
                url=url,
                media_type=MediaType.image,
            )
            session.add(asset)
            session.flush()
        assets[base] = asset
    return assets


def map_romaji_to_note(session, note_type: NoteType) -> Dict[str, int]:
    romaji_field = session.scalar(
        select(NoteField.id).where(NoteField.note_type_id == note_type.id, NoteField.name == "romaji")
    )
    if not romaji_field:
        return {}
    rows = session.execute(
        select(NoteFieldValue.note_id, NoteFieldValue.value_text).where(NoteFieldValue.field_id == romaji_field)
    ).all()
    return {str(value or "").strip().lower(): note_id for note_id, value in rows if value}


def upsert_image_values(session, note_type: NoteType, image_field: NoteField, assets: Dict[str, MediaAsset]) -> None:
    romaji_map = map_romaji_to_note(session, note_type)
    for _, romaji in HIRAGANA_PAIRS:
        asset = assets.get(romaji)
        if not asset:
            print(f"Sem asset para romaji '{romaji}', ignorando.")
            continue
        note_id = romaji_map.get(romaji)
        if not note_id:
            print(f"Sem nota para romaji '{romaji}', ignorando.")
            continue
        existing = session.scalar(
            select(NoteFieldValue).where(
                NoteFieldValue.note_id == note_id,
                NoteFieldValue.field_id == image_field.id,
            )
        )
        if existing:
            existing.media_asset_id = asset.id
            if not existing.value_text:
                existing.value_text = asset.url
        else:
            session.add(
                NoteFieldValue(
                    note_id=note_id,
                    field_id=image_field.id,
                    media_asset_id=asset.id,
                    value_text=asset.url,
                )
            )


def update_template(session, note_type: NoteType) -> None:
    template = session.scalar(
        select(CardTemplate).where(CardTemplate.note_type_id == note_type.id).order_by(CardTemplate.id).limit(1)
    )
    if not template:
        return
    img_snippet = '<img src="{{imagem}}" alt="" style="max-width:100%;height:auto;" />'
    if "{{imagem}}" not in (template.front_template or ""):
        template.front_template = f"{{{{kana}}}}\n{img_snippet}"
    if "{{imagem}}" not in (template.back_template or ""):
        template.back_template = f"{template.back_template}\n{img_snippet}"


def main():
    repo_root = get_repo_root()
    media_dir = repo_root / "apps" / "web" / "public" / "media" / "hiragana"
    base_url = get_media_base_url()

    session = SessionLocal()
    try:
        deck = get_deck_by_slug(session, "hiragana-basico")
        if not deck:
            print("Deck hiragana-basico não encontrado.")
            return
        note_type = get_note_type_for_deck(session, deck.id)
        if not note_type:
            print("NoteType do Hiragana não encontrado.")
            return

        image_field = ensure_image_field(session, note_type)
        assets = load_media_assets(session, deck, media_dir, base_url)
        upsert_image_values(session, note_type, image_field, assets)
        update_template(session, note_type)

        session.commit()
        print(f"Seed concluído: {len(assets)} imagens processadas.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
