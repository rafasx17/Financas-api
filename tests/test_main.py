from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ── Geral ─────────────────────────────────────────────────────

def test_inicio():
    response = client.get("/")
    assert response.status_code == 200


# ── Autenticação ──────────────────────────────────────────────

def test_registro():
    response = client.post("/registro", json={
        "nome": "Teste",
        "email": "teste@teste.com",
        "senha": "senha123"
    })
    assert response.status_code in [201, 400]


def test_login_invalido():
    response = client.post("/login", data={
        "username": "naoexiste@teste.com",
        "password": "senhaerrada"
    })
    assert response.status_code == 401


def test_transacoes_sem_token():
    response = client.get("/transacoes")
    assert response.status_code == 401


# ── Fluxo completo ────────────────────────────────────────────

def get_token():
    client.post("/registro", json={
        "nome": "Usuario Teste",
        "email": "fluxo@teste.com",
        "senha": "senha123"
    })
    response = client.post("/login", data={
        "username": "fluxo@teste.com",
        "password": "senha123"
    })
    return response.json()["access_token"]


def test_criar_transacao():
    token = get_token()
    response = client.post("/transacoes", json={
        "descricao": "Salário",
        "valor": 3000,
        "tipo": "receita",
        "categoria": "trabalho"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["descricao"] == "Salário"


def test_listar_transacoes():
    token = get_token()
    response = client.get("/transacoes", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_saldo():
    token = get_token()
    response = client.get("/resumo/saldo", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "saldo" in response.json()


def test_resumo_mensal():
    token = get_token()
    response = client.get("/resumo/mensal", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_resumo_categorias():
    token = get_token()
    response = client.get("/resumo/categorias", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200