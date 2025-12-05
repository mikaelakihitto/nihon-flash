# Nihon Flash

Plataforma de estudos de japonês com repetição espaçada (SRS) e decks personalizados. Monorepo contendo frontend (Next.js), backend (FastAPI) e pacote core compartilhado.

## Estrutura
```
nihon-flash/
├── apps/
│   ├── web/        # Frontend Next.js + Tailwind
│   └── api/        # Backend FastAPI
├── packages/
│   ├── core/       # Lógica SRS e modelos compartilhados
│   └── config/     # Utilidades e helpers para configs/env
├── infra/
│   ├── docker/
│   └── scripts/
└── docs/
```

### Backend (`apps/api`)
- `app/core`: configuração de app, middlewares, dependências globais.
- `app/models`: modelos de dados/ORM.
- `app/schemas`: schemas Pydantic expostos pela API.
- `app/routers`: rotas divididas por domínio.
- `app/services`: regras de negócio e integrações externas.
- `app/srs`: componentes específicos da lógica SRS.
- Alembic em `apps/api/migrations` para versionar o schema.

### Frontend (`apps/web`)
- App Router do Next.js em `src/app` com páginas iniciais (`/`, `/decks`, `/auth/login`).
- Tailwind configurado via `tailwind.config.ts` e `postcss.config.js`.

### Core (`packages/core`)
- `srs/algorithm_simple.py`: primeira função de cálculo de próxima revisão.

## Setup rápido

### 1) Backend
```bash
cd apps/api
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
API em http://localhost:8000 (rota de saúde: `/health`).

#### Migrações Alembic
```bash
cd apps/api
alembic revision --autogenerate -m "init"
alembic upgrade head
```
Certifique-se de que `DATABASE_URL` aponte para seu Postgres antes de rodar.

### 2) Frontend
```bash
cd apps/web
npm install
npm run dev
```
App em http://localhost:3000.

## Próximos passos
- Conectar backend ao banco definido em `DB_URL`.
- Criar primeiras entidades (Usuário, Deck, Card) e endpoints.
- Integrar pacote `packages/core` no backend e frontend (via alias ou publicação interna).
