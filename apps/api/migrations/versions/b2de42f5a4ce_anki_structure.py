"""Add Anki-like note model and seed Hiragana

Revision ID: b2de42f5a4ce
Revises: 6274349dfff2
Create Date: 2025-12-06 00:00:00.000000
"""
from __future__ import annotations

import datetime
import re
from typing import Any

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, select
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = "b2de42f5a4ce"
down_revision = "6274349dfff2"
branch_labels = None
depends_on = None

NOTE_FIELD_TYPE = sa.Enum(
    "text",
    "rich_text",
    "image",
    "audio",
    "furigana",
    "json",
    name="notefieldtype",
)
MEDIA_TYPE = sa.Enum("image", "audio", name="mediatype")
CARD_STATUS = sa.Enum("new", "learning", "review", "suspended", name="cardstatus")

HIRAGANA_ROWS = [
    {"kana": "あ", "romaji": "a"},
    {"kana": "い", "romaji": "i"},
    {"kana": "う", "romaji": "u"},
    {"kana": "え", "romaji": "e"},
    {"kana": "お", "romaji": "o"},
    {"kana": "か", "romaji": "ka"},
    {"kana": "き", "romaji": "ki"},
    {"kana": "く", "romaji": "ku"},
    {"kana": "け", "romaji": "ke"},
    {"kana": "こ", "romaji": "ko"},
    {"kana": "さ", "romaji": "sa"},
    {"kana": "し", "romaji": "shi"},
    {"kana": "す", "romaji": "su"},
    {"kana": "せ", "romaji": "se"},
    {"kana": "そ", "romaji": "so"},
    {"kana": "た", "romaji": "ta"},
    {"kana": "ち", "romaji": "chi"},
    {"kana": "つ", "romaji": "tsu"},
    {"kana": "て", "romaji": "te"},
    {"kana": "と", "romaji": "to"},
    {"kana": "な", "romaji": "na"},
    {"kana": "に", "romaji": "ni"},
    {"kana": "ぬ", "romaji": "nu"},
    {"kana": "ね", "romaji": "ne"},
    {"kana": "の", "romaji": "no"},
    {"kana": "は", "romaji": "ha"},
    {"kana": "ひ", "romaji": "hi"},
    {"kana": "ふ", "romaji": "fu"},
    {"kana": "へ", "romaji": "he"},
    {"kana": "ほ", "romaji": "ho"},
    {"kana": "ま", "romaji": "ma"},
    {"kana": "み", "romaji": "mi"},
    {"kana": "む", "romaji": "mu"},
    {"kana": "め", "romaji": "me"},
    {"kana": "も", "romaji": "mo"},
    {"kana": "や", "romaji": "ya"},
    {"kana": "ゆ", "romaji": "yu"},
    {"kana": "よ", "romaji": "yo"},
    {"kana": "ら", "romaji": "ra"},
    {"kana": "り", "romaji": "ri"},
    {"kana": "る", "romaji": "ru"},
    {"kana": "れ", "romaji": "re"},
    {"kana": "ろ", "romaji": "ro"},
    {"kana": "わ", "romaji": "wa"},
    {"kana": "を", "romaji": "wo"},
    {"kana": "ん", "romaji": "n"},
]


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "deck"


def upgrade() -> None:
    # Deck columns
    op.add_column("decks", sa.Column("slug", sa.String(length=150), nullable=True))
    op.add_column("decks", sa.Column("description_md", sa.Text(), nullable=True))
    op.add_column("decks", sa.Column("cover_image_url", sa.String(length=255), nullable=True))
    op.add_column("decks", sa.Column("instructions_md", sa.Text(), nullable=True))
    op.add_column("decks", sa.Column("source_lang", sa.String(length=10), nullable=True))
    op.add_column("decks", sa.Column("target_lang", sa.String(length=10), nullable=True))
    op.add_column("decks", sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("0")))
    op.add_column("decks", sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'")))

    # New core tables
    op.create_table(
        "note_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("deck_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["deck_id"], ["decks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_note_types_id"), "note_types", ["id"], unique=False)
    op.create_table(
        "note_fields",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("note_type_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=False),
        sa.Column("field_type", NOTE_FIELD_TYPE, nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("hint", sa.Text(), nullable=True),
        sa.Column("config", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.ForeignKeyConstraint(["note_type_id"], ["note_types.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_note_fields_id"), "note_fields", ["id"], unique=False)
    op.create_index("ix_note_fields_note_type_id", "note_fields", ["note_type_id"], unique=False)
    op.create_table(
        "card_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("note_type_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("front_template", sa.Text(), nullable=False),
        sa.Column("back_template", sa.Text(), nullable=False),
        sa.Column("css", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.ForeignKeyConstraint(["note_type_id"], ["note_types.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_card_templates_id"), "card_templates", ["id"], unique=False)
    op.create_index("ix_card_templates_note_type_id", "card_templates", ["note_type_id"], unique=False)
    op.create_table(
        "media_assets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("deck_id", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=False),
        sa.Column("media_type", MEDIA_TYPE, nullable=False),
        sa.Column("attribution", sa.String(length=255), nullable=True),
        sa.Column("license", sa.String(length=100), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.ForeignKeyConstraint(["deck_id"], ["decks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_media_assets_id"), "media_assets", ["id"], unique=False)
    op.create_index("ix_media_assets_deck_id", "media_assets", ["deck_id"], unique=False)
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("deck_id", sa.Integer(), nullable=False),
        sa.Column("note_type_id", sa.Integer(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=func.now()),
        sa.ForeignKeyConstraint(["deck_id"], ["decks.id"]),
        sa.ForeignKeyConstraint(["note_type_id"], ["note_types.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notes_id"), "notes", ["id"], unique=False)
    op.create_index("ix_notes_deck_id", "notes", ["deck_id"], unique=False)
    op.create_index("ix_notes_note_type_id", "notes", ["note_type_id"], unique=False)
    op.create_table(
        "note_field_values",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("note_id", sa.Integer(), nullable=False),
        sa.Column("field_id", sa.Integer(), nullable=False),
        sa.Column("value_text", sa.Text(), nullable=True),
        sa.Column("media_asset_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["field_id"], ["note_fields.id"]),
        sa.ForeignKeyConstraint(["media_asset_id"], ["media_assets.id"]),
        sa.ForeignKeyConstraint(["note_id"], ["notes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_note_field_values_id"), "note_field_values", ["id"], unique=False)
    op.create_index("ix_note_field_values_note_id", "note_field_values", ["note_id"], unique=False)
    op.create_index("ix_note_field_values_field_id", "note_field_values", ["field_id"], unique=False)

    # Prepare cards migration
    op.drop_index(op.f("ix_cards_id"), table_name="cards")
    op.drop_index(op.f("ix_cards_deck_id"), table_name="cards")
    op.rename_table("cards", "cards_legacy")

    op.create_table(
        "cards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("note_id", sa.Integer(), nullable=False),
        sa.Column("card_template_id", sa.Integer(), nullable=False),
        sa.Column("mnemonic", sa.Text(), nullable=True),
        sa.Column("status", CARD_STATUS, nullable=False, server_default=sa.text("'new'")),
        sa.Column("srs_interval", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("srs_ease", sa.Float(), nullable=False, server_default="2.5"),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("lapses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reps", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["card_template_id"], ["card_templates.id"]),
        sa.ForeignKeyConstraint(["note_id"], ["notes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cards_id"), "cards", ["id"], unique=False)
    op.create_index("ix_cards_note_id", "cards", ["note_id"], unique=False)
    op.create_index("ix_cards_card_template_id", "cards", ["card_template_id"], unique=False)

    # Data migrations
    bind = op.get_bind()
    metadata = sa.MetaData()
    metadata.bind = bind

    decks_table = sa.Table("decks", metadata, autoload_with=bind)
    legacy_cards_table = sa.Table("cards_legacy", metadata, autoload_with=bind)
    note_types_table = sa.Table("note_types", metadata, autoload_with=bind)
    note_fields_table = sa.Table("note_fields", metadata, autoload_with=bind)
    card_templates_table = sa.Table("card_templates", metadata, autoload_with=bind)
    notes_table = sa.Table("notes", metadata, autoload_with=bind)
    note_field_values_table = sa.Table("note_field_values", metadata, autoload_with=bind)
    cards_table = sa.Table("cards", metadata, autoload_with=bind)

    # Populate deck slugs and defaults
    existing_slugs: set[str] = set()
    decks = list(bind.execute(select(decks_table.c.id, decks_table.c.name, decks_table.c.description)).fetchall())
    for deck in decks:
        slug_base = slugify(deck.name or f"deck-{deck.id}")
        slug = slug_base
        suffix = 1
        while slug in existing_slugs:
            slug = f"{slug_base}-{suffix}"
            suffix += 1
        existing_slugs.add(slug)
        bind.execute(
            decks_table.update()
            .where(decks_table.c.id == deck.id)
            .values(
                slug=slug,
                description_md=deck.description,
                tags=[],
                is_public=False,
            )
        )

    # Migrate legacy cards into the new note-based structure
    now = datetime.datetime.utcnow()
    inspector = inspect(bind)
    legacy_cards = list(bind.execute(select(legacy_cards_table)).fetchall()) if inspector.has_table("cards_legacy") else []
    legacy_note_type_id = None
    legacy_template_id = None
    legacy_fields: dict[str, Any] = {}

    if legacy_cards:
        legacy_note_type_id = (
            bind.execute(
                note_types_table.insert().values(name="Legacy Básico", description="Note type criado a partir dos cards existentes.")
            ).inserted_primary_key[0]
        )
        fields_payload = [
            {"name": "front", "label": "Frente", "field_type": "text"},
            {"name": "back", "label": "Verso", "field_type": "rich_text"},
            {"name": "mnemonic", "label": "Mnemônico", "field_type": "rich_text"},
            {"name": "card_type", "label": "Tipo", "field_type": "text"},
        ]
        for order, payload in enumerate(fields_payload):
            payload.update(
                {
                    "note_type_id": legacy_note_type_id,
                    "is_required": False,
                    "sort_order": order,
                    "config": {},
                }
            )
            field_id = bind.execute(note_fields_table.insert().values(**payload)).inserted_primary_key[0]
            legacy_fields[payload["name"]] = field_id

        legacy_template_id = (
            bind.execute(
                card_templates_table.insert().values(
                    note_type_id=legacy_note_type_id,
                    name="Legacy",
                    front_template="{{front}}",
                    back_template="{{back}}",
                    css=None,
                    is_active=True,
                )
            ).inserted_primary_key[0]
        )

        for card in legacy_cards:
            note_id = (
                bind.execute(
                    notes_table.insert().values(
                        deck_id=card.deck_id,
                        note_type_id=legacy_note_type_id,
                        tags=[],
                        created_at=now,
                        updated_at=now,
                    )
                ).inserted_primary_key[0]
            )
            field_values = [
                {"note_id": note_id, "field_id": legacy_fields["front"], "value_text": card.front, "media_asset_id": None},
                {"note_id": note_id, "field_id": legacy_fields["back"], "value_text": card.back, "media_asset_id": None},
                {"note_id": note_id, "field_id": legacy_fields["mnemonic"], "value_text": card.mnemonic, "media_asset_id": None},
                {"note_id": note_id, "field_id": legacy_fields["card_type"], "value_text": card.type, "media_asset_id": None},
            ]
            bind.execute(note_field_values_table.insert(), field_values)
            bind.execute(
                cards_table.insert().values(
                    note_id=note_id,
                    card_template_id=legacy_template_id,
                    mnemonic=card.mnemonic,
                    status="new",
                    srs_interval=0,
                    srs_ease=2.5,
                    due_at=now,
                    last_reviewed_at=None,
                    lapses=0,
                    reps=0,
                )
            )

    # Seed Hiragana if not present
    deck_slug = "hiragana-basico"
    deck_exists = bind.execute(select(decks_table.c.id).where(decks_table.c.slug == deck_slug)).scalar_one_or_none()
    hiragana_deck_id = deck_exists
    if hiragana_deck_id is None:
        hiragana_deck_id = (
            bind.execute(
                decks_table.insert().values(
                    name="Hiragana - Básico",
                    slug=deck_slug,
                    description="46 caracteres essenciais do silabário Hiragana.",
                    description_md="46 caracteres essenciais do silabário Hiragana.",
                    cover_image_url="https://placehold.co/600x400?text=Hiragana",
                    instructions_md="Estude os sons e pratique a escrita antes de avançar para os próximos conjuntos.",
                    source_lang="ja",
                    target_lang="pt",
                    is_public=False,
                    tags=["hiragana", "kana", "iniciante"],
                )
            ).inserted_primary_key[0]
        )

    existing_hiragana_notes = (
        bind.execute(select(func.count()).select_from(notes_table).where(notes_table.c.deck_id == hiragana_deck_id)).scalar()
    )

    if existing_hiragana_notes == 0:
        hiragana_note_type_id = (
            bind.execute(
                note_types_table.insert().values(
                    name="Hiragana Básico",
                    description="Campos para o deck básico de Hiragana.",
                    deck_id=hiragana_deck_id,
                )
            ).inserted_primary_key[0]
        )
        hiragana_fields_def = [
            {"name": "kana", "label": "Kana", "field_type": "text", "is_required": True},
            {"name": "romaji", "label": "Romaji", "field_type": "text", "is_required": True},
            {"name": "exemplo", "label": "Exemplo", "field_type": "text", "is_required": False},
            {"name": "audio", "label": "Áudio", "field_type": "audio", "is_required": False},
            {"name": "dica", "label": "Dica", "field_type": "rich_text", "is_required": False},
        ]
        hiragana_field_ids: dict[str, int] = {}
        for idx, payload in enumerate(hiragana_fields_def):
            payload.update(
                {
                    "note_type_id": hiragana_note_type_id,
                    "sort_order": idx,
                    "config": {},
                }
            )
            hiragana_field_ids[payload["name"]] = bind.execute(note_fields_table.insert().values(**payload)).inserted_primary_key[0]

        hiragana_templates = [
            {
                "name": "Reconhecer kana",
                "front_template": "{{kana}}",
                "back_template": "{{romaji}}\n{{exemplo}}\n{{audio}}",
            },
            {
                "name": "Produzir kana",
                "front_template": "{{romaji}}",
                "back_template": "{{kana}}\n{{exemplo}}\n{{audio}}\n{{dica}}",
            },
        ]
        hiragana_template_ids: list[int] = []
        for tpl in hiragana_templates:
            hiragana_template_ids.append(
                bind.execute(
                    card_templates_table.insert().values(
                        note_type_id=hiragana_note_type_id,
                        name=tpl["name"],
                        front_template=tpl["front_template"],
                        back_template=tpl["back_template"],
                        css=None,
                        is_active=True,
                    )
                ).inserted_primary_key[0]
            )

        for row in HIRAGANA_ROWS:
            dica = f"Associe {row['kana']} ao som '{row['romaji']}' e pratique a escrita."
            exemplo_text = f"{row['kana']} -> {row['romaji']}"
            note_id = (
                bind.execute(
                    notes_table.insert().values(
                        deck_id=hiragana_deck_id,
                        note_type_id=hiragana_note_type_id,
                        tags=["hiragana", "basico"],
                        created_at=now,
                        updated_at=now,
                    )
                ).inserted_primary_key[0]
            )
            field_values = [
                {"note_id": note_id, "field_id": hiragana_field_ids["kana"], "value_text": row["kana"], "media_asset_id": None},
                {"note_id": note_id, "field_id": hiragana_field_ids["romaji"], "value_text": row["romaji"], "media_asset_id": None},
                {"note_id": note_id, "field_id": hiragana_field_ids["exemplo"], "value_text": exemplo_text, "media_asset_id": None},
                {"note_id": note_id, "field_id": hiragana_field_ids["audio"], "value_text": None, "media_asset_id": None},
                {"note_id": note_id, "field_id": hiragana_field_ids["dica"], "value_text": dica, "media_asset_id": None},
            ]
            bind.execute(note_field_values_table.insert(), field_values)

            for template_id in hiragana_template_ids:
                bind.execute(
                    cards_table.insert().values(
                        note_id=note_id,
                        card_template_id=template_id,
                        mnemonic=dica,
                        status="new",
                        srs_interval=0,
                        srs_ease=2.5,
                        due_at=now,
                        last_reviewed_at=None,
                        lapses=0,
                        reps=0,
                    )
                )

    # Finalize deck constraints
    with op.batch_alter_table("decks") as batch:
        batch.alter_column("slug", existing_type=sa.String(length=150), nullable=False)
    op.create_index("ix_decks_slug", "decks", ["slug"], unique=True)

    # Drop legacy table
    op.drop_table("cards_legacy")


def downgrade() -> None:
    # Best-effort rollback: drop new tables/columns and recreate legacy cards table without data.
    op.create_table(
        "cards_legacy",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("deck_id", sa.Integer(), nullable=False),
        sa.Column("front", sa.String(length=255), nullable=False),
        sa.Column("back", sa.Text(), nullable=False),
        sa.Column("mnemonic", sa.Text(), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["deck_id"], ["decks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cards_deck_id"), "cards_legacy", ["deck_id"], unique=False)
    op.create_index(op.f("ix_cards_id"), "cards_legacy", ["id"], unique=False)

    op.drop_table("cards")
    op.drop_table("note_field_values")
    op.drop_table("notes")
    op.drop_table("media_assets")
    op.drop_table("card_templates")
    op.drop_table("note_fields")
    op.drop_table("note_types")

    op.drop_index("ix_decks_slug", table_name="decks")
    with op.batch_alter_table("decks") as batch:
        batch.drop_column("slug")
        batch.drop_column("description_md")
        batch.drop_column("cover_image_url")
        batch.drop_column("instructions_md")
        batch.drop_column("source_lang")
        batch.drop_column("target_lang")
        batch.drop_column("is_public")
        batch.drop_column("tags")

    op.rename_table("cards_legacy", "cards")
    CARD_STATUS.drop(op.get_bind(), checkfirst=False)
    MEDIA_TYPE.drop(op.get_bind(), checkfirst=False)
    NOTE_FIELD_TYPE.drop(op.get_bind(), checkfirst=False)
