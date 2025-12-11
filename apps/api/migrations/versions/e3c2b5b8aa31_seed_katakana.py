"""Seed Katakana basic deck

Revision ID: e3c2b5b8aa31
Revises: b2de42f5a4ce
Create Date: 2025-12-07 00:00:00.000000
"""
from __future__ import annotations

import datetime
import re
from typing import Any

from alembic import op
import sqlalchemy as sa
from sqlalchemy import select

# revision identifiers, used by Alembic.
revision = "e3c2b5b8aa31"
down_revision = "7f3e9b2b6f9f"
branch_labels = None
depends_on = None


KATAKANA_ROWS = [
    {"kana": "ア", "romaji": "a"},
    {"kana": "イ", "romaji": "i"},
    {"kana": "ウ", "romaji": "u"},
    {"kana": "エ", "romaji": "e"},
    {"kana": "オ", "romaji": "o"},
    {"kana": "カ", "romaji": "ka"},
    {"kana": "キ", "romaji": "ki"},
    {"kana": "ク", "romaji": "ku"},
    {"kana": "ケ", "romaji": "ke"},
    {"kana": "コ", "romaji": "ko"},
    {"kana": "サ", "romaji": "sa"},
    {"kana": "シ", "romaji": "shi"},
    {"kana": "ス", "romaji": "su"},
    {"kana": "セ", "romaji": "se"},
    {"kana": "ソ", "romaji": "so"},
    {"kana": "タ", "romaji": "ta"},
    {"kana": "チ", "romaji": "chi"},
    {"kana": "ツ", "romaji": "tsu"},
    {"kana": "テ", "romaji": "te"},
    {"kana": "ト", "romaji": "to"},
    {"kana": "ナ", "romaji": "na"},
    {"kana": "ニ", "romaji": "ni"},
    {"kana": "ヌ", "romaji": "nu"},
    {"kana": "ネ", "romaji": "ne"},
    {"kana": "ノ", "romaji": "no"},
    {"kana": "ハ", "romaji": "ha"},
    {"kana": "ヒ", "romaji": "hi"},
    {"kana": "フ", "romaji": "fu"},
    {"kana": "ヘ", "romaji": "he"},
    {"kana": "ホ", "romaji": "ho"},
    {"kana": "マ", "romaji": "ma"},
    {"kana": "ミ", "romaji": "mi"},
    {"kana": "ム", "romaji": "mu"},
    {"kana": "メ", "romaji": "me"},
    {"kana": "モ", "romaji": "mo"},
    {"kana": "ヤ", "romaji": "ya"},
    {"kana": "ユ", "romaji": "yu"},
    {"kana": "ヨ", "romaji": "yo"},
    {"kana": "ラ", "romaji": "ra"},
    {"kana": "リ", "romaji": "ri"},
    {"kana": "ル", "romaji": "ru"},
    {"kana": "レ", "romaji": "re"},
    {"kana": "ロ", "romaji": "ro"},
    {"kana": "ワ", "romaji": "wa"},
    {"kana": "ヲ", "romaji": "wo"},
    {"kana": "ン", "romaji": "n"},
]


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "deck"


def upgrade() -> None:
    bind = op.get_bind()
    metadata = sa.MetaData()
    metadata.bind = bind

    decks_table = sa.Table("decks", metadata, autoload_with=bind)
    note_types_table = sa.Table("note_types", metadata, autoload_with=bind)
    note_fields_table = sa.Table("note_fields", metadata, autoload_with=bind)
    card_templates_table = sa.Table("card_templates", metadata, autoload_with=bind)
    notes_table = sa.Table("notes", metadata, autoload_with=bind)
    note_field_values_table = sa.Table("note_field_values", metadata, autoload_with=bind)
    cards_table = sa.Table("cards", metadata, autoload_with=bind)

    now = datetime.datetime.utcnow()
    deck_slug = "katakana-basico"

    deck_id = bind.execute(select(decks_table.c.id).where(decks_table.c.slug == deck_slug)).scalar_one_or_none()
    if deck_id is None:
        deck_name = "Katakana - Básico"
        deck_id = (
            bind.execute(
                decks_table.insert().values(
                    name=deck_name,
                    slug=deck_slug,
                    description="46 caracteres essenciais do silabário Katakana.",
                    description_md="46 caracteres essenciais do silabário Katakana.",
                    cover_image_url="https://placehold.co/600x400?text=Katakana",
                    instructions_md="Estude os sons e pratique a leitura antes de avançar para combinações e dakuten.",
                    source_lang="ja",
                    target_lang="pt",
                    is_public=False,
                    tags=["katakana", "kana", "iniciante"],
                )
            ).inserted_primary_key[0]
        )
    else:
        # Garantir slug preenchido e descrição markdown
        deck_row = bind.execute(select(decks_table).where(decks_table.c.id == deck_id)).first()
        if deck_row:
            bind.execute(
                decks_table.update()
                .where(decks_table.c.id == deck_id)
                .values(
                    slug=deck_row.slug or slugify(deck_row.name or "katakana"),
                    description_md=deck_row.description or deck_row.description_md,
                )
            )

    note_type_id = bind.execute(
        select(note_types_table.c.id).where(note_types_table.c.deck_id == deck_id, note_types_table.c.name == "Katakana Básico")
    ).scalar_one_or_none()

    if note_type_id is None:
        note_type_id = (
            bind.execute(
                note_types_table.insert().values(
                    name="Katakana Básico",
                    description="Campos para o deck básico de Katakana.",
                    deck_id=deck_id,
                )
            ).inserted_primary_key[0]
        )

    # Se já existirem notas para este deck/note type, evitamos duplicar
    field_defs = [
        {"name": "kana", "label": "Kana", "field_type": "text", "is_required": True},
        {"name": "romaji", "label": "Romaji", "field_type": "text", "is_required": True},
        {"name": "exemplo", "label": "Exemplo", "field_type": "text", "is_required": False},
        {"name": "audio", "label": "Áudio", "field_type": "audio", "is_required": False},
        {"name": "dica", "label": "Dica", "field_type": "rich_text", "is_required": False},
    ]
    field_ids: dict[str, Any] = {}
    for idx, fd in enumerate(field_defs):
        existing_field = bind.execute(
            select(note_fields_table.c.id).where(
                note_fields_table.c.note_type_id == note_type_id,
                note_fields_table.c.name == fd["name"],
            )
        ).scalar_one_or_none()
        if existing_field:
            field_ids[fd["name"]] = existing_field
            continue
        field_ids[fd["name"]] = (
            bind.execute(
                note_fields_table.insert().values(
                    note_type_id=note_type_id,
                    name=fd["name"],
                    label=fd["label"],
                    field_type=fd["field_type"],
                    is_required=fd["is_required"],
                    sort_order=idx,
                    hint=None,
                    config={},
                )
            ).inserted_primary_key[0]
        )

    template_id = bind.execute(
        select(card_templates_table.c.id).where(card_templates_table.c.note_type_id == note_type_id).order_by(card_templates_table.c.id)
    ).scalar_one_or_none()
    if template_id is None:
        template_id = (
            bind.execute(
                card_templates_table.insert().values(
                    note_type_id=note_type_id,
                    name="Reconhecer kana",
                    front_template="{{kana}}",
                    back_template="{{romaji}}\n{{exemplo}}\n{{audio}}",
                    css=None,
                    is_active=True,
                )
            ).inserted_primary_key[0]
        )

    existing_notes_rows = bind.execute(
        select(notes_table.c.id).where(notes_table.c.deck_id == deck_id, notes_table.c.note_type_id == note_type_id)
    ).fetchall()
    existing_note_ids = [row[0] for row in existing_notes_rows]

    if not existing_note_ids:
        for row in KATAKANA_ROWS:
            dica = f"Associe {row['kana']} ao som '{row['romaji']}'."
            exemplo_text = f"{row['kana']} -> {row['romaji']}"
            note_id = (
                bind.execute(
                    notes_table.insert().values(
                        deck_id=deck_id,
                        note_type_id=note_type_id,
                        tags=["katakana", "basico"],
                        created_at=now,
                        updated_at=now,
                    )
                ).inserted_primary_key[0]
            )
            field_values = [
                {"note_id": note_id, "field_id": field_ids["kana"], "value_text": row["kana"], "media_asset_id": None},
                {"note_id": note_id, "field_id": field_ids["romaji"], "value_text": row["romaji"], "media_asset_id": None},
                {"note_id": note_id, "field_id": field_ids["exemplo"], "value_text": exemplo_text, "media_asset_id": None},
                {"note_id": note_id, "field_id": field_ids["audio"], "value_text": None, "media_asset_id": None},
                {"note_id": note_id, "field_id": field_ids["dica"], "value_text": dica, "media_asset_id": None},
            ]
            bind.execute(note_field_values_table.insert(), field_values)

            bind.execute(
                cards_table.insert().values(
                    note_id=note_id,
                    card_template_id=template_id,
                    mnemonic=dica,
                    status="new",
                    stage="curto_prazo",
                    srs_interval=0,
                    srs_ease=2.5,
                    due_at=now,
                    last_reviewed_at=None,
                    lapses=0,
                    reps=0,
                )
            )
    else:
        # Caso a migração tenha falhado no meio, garantir que cada nota tenha um card e stage definido
        for row in bind.execute(select(notes_table.c.id).where(notes_table.c.deck_id == deck_id, notes_table.c.note_type_id == note_type_id)):
            note_id = row[0]
            has_card = bind.execute(select(cards_table.c.id).where(cards_table.c.note_id == note_id)).scalar_one_or_none()
            if has_card:
                continue
            bind.execute(
                cards_table.insert().values(
                    note_id=note_id,
                    card_template_id=template_id,
                    mnemonic=None,
                    status="new",
                    stage="curto_prazo",
                    srs_interval=0,
                    srs_ease=2.5,
                    due_at=now,
                    last_reviewed_at=None,
                    lapses=0,
                    reps=0,
                )
            )


def downgrade() -> None:
    bind = op.get_bind()
    metadata = sa.MetaData()
    metadata.bind = bind

    deck_slug = "katakana-basico"
    decks_table = sa.Table("decks", metadata, autoload_with=bind)
    notes_table = sa.Table("notes", metadata, autoload_with=bind)
    note_types_table = sa.Table("note_types", metadata, autoload_with=bind)
    note_fields_table = sa.Table("note_fields", metadata, autoload_with=bind)
    card_templates_table = sa.Table("card_templates", metadata, autoload_with=bind)
    cards_table = sa.Table("cards", metadata, autoload_with=bind)
    note_field_values_table = sa.Table("note_field_values", metadata, autoload_with=bind)

    deck_id = bind.execute(select(decks_table.c.id).where(decks_table.c.slug == deck_slug)).scalar_one_or_none()
    if deck_id is None:
        return

    # Remove cards e valores relacionados às notas deste deck
    note_ids = [row[0] for row in bind.execute(select(notes_table.c.id).where(notes_table.c.deck_id == deck_id)).fetchall()]
    if note_ids:
        bind.execute(cards_table.delete().where(cards_table.c.note_id.in_(note_ids)))
        bind.execute(note_field_values_table.delete().where(note_field_values_table.c.note_id.in_(note_ids)))
        bind.execute(notes_table.delete().where(notes_table.c.id.in_(note_ids)))

    nt_ids = [row[0] for row in bind.execute(select(note_types_table.c.id).where(note_types_table.c.deck_id == deck_id)).fetchall()]
    if nt_ids:
        bind.execute(card_templates_table.delete().where(card_templates_table.c.note_type_id.in_(nt_ids)))
        bind.execute(note_fields_table.delete().where(note_fields_table.c.note_type_id.in_(nt_ids)))
        bind.execute(note_types_table.delete().where(note_types_table.c.id.in_(nt_ids)))

    bind.execute(decks_table.delete().where(decks_table.c.id == deck_id))
