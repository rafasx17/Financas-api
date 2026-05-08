#main.py — em cada rota, ao invés de buscar todas as transações, busca só as do usuário logado. Ex: db.query(models.Transacao).filter(models.Transacao.usuario_id == usuario.id)


from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app import models
from app.schemas import TransacaoCreate, TransacaoResponse, UsuarioCreate
from app.auth import hash_senha, verificar_senha, criar_token, get_usuario_atual
from typing import List
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI()

# ── Geral ─────────────────────────────────────────────────────

@app.get("/")
def inicio():
    return {"mensagem": "API de Finanças funcionando!"}


# ── Autenticação ──────────────────────────────────────────────

@app.post("/registro", status_code=201)
def registro(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    novo = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=hash_senha(usuario.senha)
    )
    db.add(novo)
    db.commit()
    return {"mensagem": "Usuário criado com sucesso"}


@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == form.username).first()
    if not usuario or not verificar_senha(form.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = criar_token({"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}


# ── Transações (protegidas) ───────────────────────────────────

@app.post("/transacoes", response_model=TransacaoResponse)
def criar_transacao(
    transacao: TransacaoCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    nova = models.Transacao(**transacao.model_dump(), usuario_id=usuario.id)
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


@app.get("/transacoes", response_model=List[TransacaoResponse])
def listar_transacoes(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    return db.query(models.Transacao).filter(models.Transacao.usuario_id == usuario.id).all()


@app.get("/transacoes/tipo/{tipo}", response_model=List[TransacaoResponse])
def filtrar_por_tipo(
    tipo: str,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    return db.query(models.Transacao).filter(models.Transacao.usuario_id == usuario.id, models.Transacao.tipo == tipo).all()


@app.get("/transacoes/periodo")
def filtrar_por_periodo(
    inicio: str,
    fim: str,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    data_inicio = datetime.strptime(inicio, "%Y-%m-%d")
    data_fim = datetime.strptime(fim, "%Y-%m-%d")
    return db.query(models.Transacao).filter(
        models.Transacao.usuario_id == usuario.id,
        models.Transacao.criado_em >= data_inicio,
        models.Transacao.criado_em <= data_fim
    ).all()


@app.put("/transacoes/{id}", response_model=TransacaoResponse)
def atualizar_transacao(
    id: int,
    transacao: TransacaoCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    db_transacao = db.query(models.Transacao).filter(models.Transacao.id == id, models.Transacao.usuario_id == usuario.id).first()
    if not db_transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    for key, value in transacao.model_dump().items():
        setattr(db_transacao, key, value)
    db.commit()
    db.refresh(db_transacao)
    return db_transacao


@app.delete("/transacoes/{id}")
def deletar_transacao(
    id: int,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    transacao = db.query(models.Transacao).filter(models.Transacao.id == id, models.Transacao.usuario_id == usuario.id).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    db.delete(transacao)
    db.commit()
    return {"mensagem": "Transação deletada com sucesso"}


@app.get("/saldo")
def calcular_saldo(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    transacoes = db.query(models.Transacao).filter(models.Transacao.usuario_id == usuario.id).all()
    receitas = sum(t.valor for t in transacoes if t.tipo == "receita")
    despesas = sum(t.valor for t in transacoes if t.tipo == "despesa")
    return {"receitas": receitas, "despesas": despesas, "saldo": receitas - despesas}