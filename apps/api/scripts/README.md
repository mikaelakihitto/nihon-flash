# Scripts de seeds e assets

Todos os scripts rodam com o venv do backend e importam as models diretamente.

## Comandos
- `python apps/api/scripts/generate_hiragana_audio.py` — gera MP3s em `apps/web/public/audio/hiragana`.
- `python apps/api/scripts/link_hiragana_audio.py` — cria media_assets e vincula os áudios aos cards.
- `python apps/api/scripts/seed_hiragana_images.py` — cria media_assets de imagem e vincula aos cards, atualizando o template para exibir `{{imagem}}`.

## Observações
- Execute a partir da raiz do repositório com o `.env` configurado.
- `MEDIA_BASE_URL` (opcional) define o host para servir arquivos estáticos; fallback: `http://localhost:3000`.
- Scripts são idempotentes: podem ser reexecutados sem duplicar dados.
