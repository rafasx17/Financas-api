from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_inicio():
    response = client.get("/")
    assert response.status_code == 200


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