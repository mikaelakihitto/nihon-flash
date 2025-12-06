import re
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models import Card, Deck, MediaAsset, Note, NoteField, NoteFieldValue, NoteType
from app.models.enums import CardStatus
from app.schemas.note import NoteCreate


def render_template(template: str, context: dict[str, str]) -> str:
    pattern = re.compile(r"{{\s*([\w\-]+)\s*}}")

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        value = context.get(key, "")
        return "" if value is None else str(value)

    return pattern.sub(replace, template)


def build_note_context(note: Note) -> dict[str, str]:
    context: dict[str, str] = {}
    for value in note.field_values:
        data = value.value_text or ""
        if value.media_asset:
            data = value.media_asset.url
        if value.field:
            context[value.field.name] = data
    return context


def _validate_media_asset(db: Session, asset_id: int, deck_id: int) -> MediaAsset:
    asset = db.get(MediaAsset, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Media asset not found")
    if asset.deck_id != deck_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Media asset must belong to the same deck"
        )
    return asset


def create_note_with_cards(db: Session, payload: NoteCreate) -> Note:
    note_type: NoteType | None = (
        db.query(NoteType)
        .filter(NoteType.id == payload.note_type_id)
        .options(joinedload(NoteType.fields), joinedload(NoteType.templates))
        .first()
    )
    if not note_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note type not found")

    deck = db.get(Deck, payload.deck_id)
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    if note_type.deck_id and note_type.deck_id != deck.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Note type is not part of this deck")

    field_map: dict[int, NoteField] = {field.id: field for field in note_type.fields}
    provided_field_ids = {value.field_id for value in payload.field_values}
    missing = [field.name for field in note_type.fields if field.is_required and field.id not in provided_field_ids]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing required fields: {', '.join(missing)}"
        )

    # Validate assets and field ownership
    for value in payload.field_values:
        field = field_map.get(value.field_id)
        if not field:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Field does not belong to note type")
        if value.media_asset_id:
            _validate_media_asset(db, value.media_asset_id, deck.id)

    note = Note(deck_id=payload.deck_id, note_type_id=payload.note_type_id, tags=payload.tags or [])
    db.add(note)
    db.flush()

    for value in payload.field_values:
        db.add(
            NoteFieldValue(
                note_id=note.id,
                field_id=value.field_id,
                value_text=value.value_text,
                media_asset_id=value.media_asset_id,
            )
        )

    now = datetime.utcnow()
    for template in note_type.templates:
        if not template.is_active:
            continue
        db.add(
            Card(
                note_id=note.id,
                card_template_id=template.id,
                mnemonic=payload.mnemonic,
                status=CardStatus.new,
                srs_interval=0,
                srs_ease=2.5,
                due_at=now,
                lapses=0,
                reps=0,
            )
        )

    db.commit()
    db.refresh(note)
    return (
        db.query(Note)
        .options(
            joinedload(Note.field_values).joinedload(NoteFieldValue.field),
            joinedload(Note.field_values).joinedload(NoteFieldValue.media_asset),
            joinedload(Note.note_type),
        )
        .filter(Note.id == note.id)
        .first()
    )
