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
Consulte o README raiz para os comandos; requisitos mínimos estão em `requirements.txt`.
