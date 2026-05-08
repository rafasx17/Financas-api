# Financas API

API REST para gerenciamento de financas pessoais com autenticacao JWT e isolamento de dados por usuario.

## Stack
- Python
- FastAPI
- SQLAlchemy
- SQLite

## Como rodar
```bash
git clone https://github.com/rafasx17/Financas-api.git
cd Financas-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Docs interativa: `http://127.0.0.1:8000/docs`

## Variaveis de ambiente
O projeto usa `.env` para configuracao. Exemplo em `.env.example`.

- `SECRET_KEY`: chave usada para assinar JWT
- `ALGORITHM`: algoritmo do JWT (padrao `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: expiracao do token
- `DATABASE_URL`: URL do banco SQLAlchemy

## Fluxo de autenticacao
1. `POST /registro` cria usuario.
2. `POST /login` retorna `access_token`.
3. Envie `Authorization: Bearer <token>` nas rotas protegidas.

## Endpoints principais
- `POST /registro`
- `POST /login`
- `GET /transacoes`
- `POST /transacoes`
- `PUT /transacoes/{id}`
- `DELETE /transacoes/{id}`
- `GET /transacoes/tipo/{tipo}`
- `GET /transacoes/periodo?inicio=YYYY-MM-DD&fim=YYYY-MM-DD`
- `GET /saldo`