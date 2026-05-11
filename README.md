# Finacas API

API REST para gerenciamento de finanças pessoais com autenticação JWT e isolamento de dados por usuário.
**API em produção:** https://financas-api-production-40db.up.railway.app/docs

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
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Documentação interativa: `http://127.0.0.1:8000/docs`

## Variáveis de ambiente

O projeto usa `.env` para configuração. Exemplo em `.env.example`.

| Variável | Descrição | Padrão |
|---|---|---|
| `SECRET_KEY` | Chave para assinar o JWT | — |
| `ALGORITHM` | Algoritmo do JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do token em minutos | `30` |
| `DATABASE_URL` | URL do banco SQLAlchemy | `sqlite:///./financas.db` |

## Fluxo de autenticação

1. `POST /registro` — cria o usuário
2. `POST /login` — retorna o `access_token`
3. Envie `Authorization: Bearer <token>` nas rotas protegidas

## Endpoints

### Autenticação
| Método | Rota | Descrição |
|---|---|---|
| POST | `/registro` | Cria um novo usuário |
| POST | `/login` | Retorna o token JWT |

### Transações
| Método | Rota | Descrição |
|---|---|---|
| GET | `/transacoes` | Lista transações (paginado: `?skip=0&limit=10`) |
| POST | `/transacoes` | Cria uma transação |
| GET | `/transacoes/{id}` | Busca transação por ID |
| PUT | `/transacoes/{id}` | Atualiza uma transação |
| DELETE | `/transacoes/{id}` | Deleta uma transação |
| GET | `/transacoes/tipo/{tipo}` | Filtra por `receita` ou `despesa` |
| GET | `/transacoes/periodo` | Filtra por período (`?inicio=YYYY-MM-DD&fim=YYYY-MM-DD`) |

### Resumos
| Método | Rota | Descrição |
|---|---|---|
| GET | `/saldo` | Retorna receitas, despesas e saldo total |
| GET | `/resumo/mensal` | Resumo agrupado por mês |
| GET | `/resumo/categorias` | Total gasto por categoria |

## Exemplo de uso

### Criar transação
```bash
curl -X POST http://localhost:8000/transacoes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"descricao": "Salário", "valor": 3000, "tipo": "receita", "categoria": "trabalho"}'
```

### Resumo mensal
```bash
curl http://localhost:8000/resumo/mensal \
  -H "Authorization: Bearer <token>"
```