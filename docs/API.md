# Nihon Flash API Reference (MVP)

Guia rápido dos principais endpoints expostos pelo backend FastAPI. Todas as rotas (exceto `/health`, `/auth/register` e `/auth/login`) exigem header `Authorization: Bearer <token>`.

## Autenticação
- `POST /auth/register` — cria usuário `{name, email, password}`.
- `POST /auth/login` — retorna `{access_token, token_type}` usado no header `Authorization`.

## Decks
- `GET /decks` — lista decks públicos ou do usuário autenticado.
- `GET /decks/{deck_id}` — detalhe por id.
- `GET /decks/slug/{slug}` — detalhe por slug (útil para o frontend evitar fetch de todos os decks).
- `POST /decks` — cria deck (campos: `name`, `slug?`, `description?`, `description_md?`, `cover_image_url?`, `instructions_md?`, `source_lang?`, `target_lang?`, `is_public?`, `tags?`).
- `PUT /decks/{deck_id}` — atualiza campos acima.

### Cards do deck
- `GET /decks/{deck_id}/cards` — cartas renderizadas com `front`, `back`, `note` e status SRS do usuário (ou defaults).
- `GET /decks/{deck_id}/cards/{card_id}/status` — status detalhado para um card específico.
- `GET /decks/{deck_id}/cards-with-stats` — lista com preview (`front` truncado), status, due dates e contadores.
- `GET /decks/{deck_id}/stats` — métricas do deck (total, due_today, new_available, distribuição de estágios, etc.).

## Note Types e Campos
- `GET /note-types` — lista modelos acessíveis (globais ou do usuário).
- `GET /note-types/{id}` — detalhe com campos e templates.
- `POST /note-types` — cria note type `{name, description?, deck_id?}`.
- `POST /note-types/{id}/fields` — cria campo `{name, label, field_type, is_required?, sort_order?, hint?, config?}`.
- `POST /note-types/{id}/templates` — cria template `{name, front_template, back_template, css?, is_active?}`.
- `PUT /note-types/{id}` / `/note-fields/{field_id}` / `/card-templates/{template_id}` — atualizam entidades respectivas.
- `DELETE /note-types/{id}` / `/note-fields/{field_id}` / `/card-templates/{template_id}` — removem se não houver dependências (notas/values/cards).

## Notas
- `POST /notes` — cria nota e cards automaticamente a partir dos templates ativos. Payload: `{deck_id, note_type_id, tags?, mnemonic?, field_values: [{field_id, value_text?, media_asset_id?}]}`.
- `GET /notes/{note_id}` — retorna nota com valores de campo, mídia e tipos.

## Estudo (novos) e Revisão (SRS)
- `GET /decks/{deck_id}/study?limit=5` — lote de novos cards sem progresso do usuário.
- `POST /study/submit` — registra acertos/erros iniciais: `{deck_id, results: [{card_id, correct}]}`.
- `GET /decks/{deck_id}/reviews?due_only=true&limit=20` — fila de revisão dos cards devidos (ou todos se `due_only=false`).
- `POST /cards/{card_id}/review` — aplica uma resposta (`{correct: bool}`) ao card.
- `GET /decks/{deck_id}/review-stats` — contagem de devidos hoje e próxima revisão.
- `GET /me/review-log?deck_id?&limit=50` — histórico de reviews do usuário.

## Saúde
- `GET /health` — status do serviço.

### Headers e Formato
Todas as rotas aceitam/retornam JSON. Inclua `Content-Type: application/json` e `Authorization: Bearer <token>` quando necessário. As datas são retornadas em ISO 8601.

## Seeds disponíveis
- **Hiragana - Básico**: criado via migração `b2de42f5a4ce_anki_structure.py` + scripts de áudio/imagem (`generate_hiragana_audio.py`, `link_hiragana_audio.py`, `seed_hiragana_images.py`, `seed_hiragana_public.py`).
- **Katakana - Básico**: criado via migração `e3c2b5b8aa31_seed_katakana.py` + scripts de áudio/imagem (`generate_katakana_audio.py`, `link_katakana_audio.py`, `seed_katakana_images.py`, `seed_katakana_public.py`).
