# Nihon Flash API

Estrutura inicial do backend FastAPI.

## Pastas
- `app/core`: configuração de app, dependências globais, middlewares.
- `app/models`: modelos de ORM/Pydantic para persistência.
- `app/schemas`: esquemas de entrada/saída expostos pela API.
- `app/routers`: rotas organizadas por domínio.
- `app/services`: regras de negócio e integrações externas.
- `app/srs`: componentes específicos da lógica de repetição espaçada.

## Execução local
```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # configure JWT_SECRET e DATABASE_URL
uvicorn app.main:app --reload
```
Swagger: `http://localhost:8000/docs` (OpenAPI gerada pelo FastAPI).

## Modelo de dados (estilo Anki)
- `Deck`: agrupa estudo, agora com `slug`, instruções/descrição em Markdown, idiomas de origem/destino, `cover_image_url`, visibilidade (`is_public`) e `tags`.
- `NoteType`: define o formato do conteúdo (campos e templates). Pode ser global ou vinculado a um deck (`deck_id` opcional).
- `NoteField`: campos de um note type (`field_type` enum: `text`, `rich_text`, `image`, `audio`, `furigana`, `json`) com `config` e `hint`.
- `CardTemplate`: combina campos em `front_template`/`back_template` e gera cards automaticamente para cada nota.
- `MediaAsset`: repositório de mídia de um deck (`media_type` enum `image`/`audio` + metadados).
- `Note`: instância de um note type dentro de um deck, com `tags`, timestamps e valores por campo (`note_field_values`).
- `Card`: cartão gerado de um template para uma nota com estado SRS (`status`, `srs_interval`, `srs_ease`, `due_at`, `reps`, `lapses`, `mnemonic`).

As migrações atuais convertem cards legados para um note type genérico ("Legacy Básico") e criam os seeds "Hiragana - Básico" e "Katakana - Básico" com note type, templates e cards gerados a partir das listas de kana.

## Fluxo para criar um novo deck/nota
1. Criar deck (`POST /decks`) preenchendo `name`, `slug` (opcional, gerado), `instructions_md`, `source_lang`, `target_lang`, `tags`, `cover_image_url`.
2. Criar um note type (`POST /note-types`) e associar ao deck (`deck_id`).
3. Adicionar campos (`POST /note-types/{id}/fields`) e templates (`POST /note-types/{id}/templates`) com placeholders `{{field_name}}`.
4. Criar notas (`POST /notes`) enviando `deck_id`, `note_type_id`, `field_values` (field_id + texto ou `media_asset_id`) e `mnemonic`. Os cards são criados automaticamente para cada template ativo.
5. Consumir cards renderizados por deck em `GET /decks/{deck_id}/cards`, que já retornam `front`/`back` renderizados, dados da nota e status SRS.

## Endpoints úteis (referência curta)
- Saúde: `GET /health`.
- Auth: `POST /auth/register`, `POST /auth/login` (header `Authorization: Bearer <token>` nas demais).
- Decks: `GET /decks`, `GET /decks/{deck_id}`, `GET /decks/slug/{slug}`, `POST /decks`, `PUT /decks/{deck_id}`.
- Notes: `POST /notes`, `GET /notes/{note_id}`.
- Note types: `GET /note-types`, `GET /note-types/{id}`, `POST /note-types`, CRUD de fields/templates.
- Estudo: `GET /decks/{deck_id}/study`, `POST /study/submit`.
- Revisão: `GET /decks/{deck_id}/reviews`, `POST /cards/{card_id}/review`, `GET /decks/{deck_id}/review-stats`, `GET /me/review-log`.

Detalhes adicionais em `docs/API.md`.

## Seeds (Hiragana/Katakana)
- Hiragana é criado na migração `b2de42f5a4ce_anki_structure.py`.
- Katakana é criado na migração `e3c2b5b8aa31_seed_katakana.py` (deck `katakana-basico`).
- Scripts auxiliares:
  - `python apps/api/scripts/generate_hiragana_audio.py` / `generate_katakana_audio.py` — gera MP3 com gTTS.
  - `python apps/api/scripts/link_hiragana_audio.py` / `link_katakana_audio.py` — cria media_assets e vincula campo `audio`.
  - `python apps/api/scripts/seed_hiragana_images.py` / `seed_katakana_images.py` — associa PNGs locais e injeta campo `imagem`.
  - `python apps/api/scripts/seed_hiragana_public.py` / `seed_katakana_public.py` — marca deck como público.
