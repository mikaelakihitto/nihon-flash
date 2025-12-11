# Nihon Flash Web (Next.js)

Frontend em Next.js (App Router) com Tailwind. Consome a API via `NEXT_PUBLIC_API_URL` (default: `http://localhost:8000`).

## Como rodar
```bash
cd apps/web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
# app em http://localhost:3000
```

## Rotas principais (MVP)
- `/` landing.
- `/login` e `/register` — autenticação; token salvo em `localStorage` (`nf_auth_token`).
- `/dashboard` — visão geral de decks, stats e próximos passos.
- `/decks` — lista de decks (inclui placeholders).
- `/decks/[deck]` — detalhes + stats do deck (busca pelo slug).
- `/decks/[deck]/cards/[cardId]` — status detalhado do card.
- `/study/[deck]` — fluxo de estudo inicial (pré-visualização + quiz).
- `/review/[deck]` — fila de revisões devidas.
- `/profile` — preferências (mock).

## Convenções de API
- Helpers em `src/lib/api.ts` e `src/lib/auth.ts`.
- Todas as chamadas usam `Authorization: Bearer <token>` quando disponível; logout limpa `nf_auth_token`.
- As páginas de estudo/revisão renderizam `front`/`back` com `dangerouslySetInnerHTML`; mantenha sanitização no backend.
