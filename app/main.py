from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app import models
from app.schemas import Token, TipoTransacao, TransacaoCreate, TransacaoResponse, UsuarioCreate
from app.auth import hash_senha, verificar_senha, criar_token, get_usuario_atual
from typing import List
from datetime import date, datetime, time
from collections import defaultdict

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


@app.post("/login", response_model=Token)
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
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    return db.query(models.Transacao).filter(
        models.Transacao.usuario_id == usuario.id
    ).offset(skip).limit(limit).all()


@app.get("/transacoes/tipo/{tipo}", response_model=List[TransacaoResponse])
def filtrar_por_tipo(
    tipo: TipoTransacao,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    return db.query(models.Transacao).filter(
        models.Transacao.usuario_id == usuario.id,
        models.Transacao.tipo == tipo
    ).all()


@app.get("/transacoes/periodo", response_model=List[TransacaoResponse])
def filtrar_por_periodo(
    inicio: date,
    fim: date,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    data_inicio = datetime.combine(inicio, time.min)
    data_fim = datetime.combine(fim, time.max)
    return db.query(models.Transacao).filter(
        models.Transacao.usuario_id == usuario.id,
        models.Transacao.criado_em >= data_inicio,
        models.Transacao.criado_em <= data_fim
    ).all()


@app.get("/transacoes/{id}", response_model=TransacaoResponse)
def buscar_transacao(
    id: int,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    transacao = db.query(models.Transacao).filter(
        models.Transacao.id == id,
        models.Transacao.usuario_id == usuario.id
    ).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return transacao


@app.put("/transacoes/{id}", response_model=TransacaoResponse)
def atualizar_transacao(
    id: int,
    transacao: TransacaoCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    db_transacao = db.query(models.Transacao).filter(
        models.Transacao.id == id,
        models.Transacao.usuario_id == usuario.id
    ).first()
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
    transacao = db.query(models.Transacao).filter(
        models.Transacao.id == id,
        models.Transacao.usuario_id == usuario.id
    ).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    db.delete(transacao)
    db.commit()
    return {"mensagem": "Transação deletada com sucesso"}


# ── Resumos ───────────────────────────────────────────────────

@app.get("/resumo/mensal")
def resumo_mensal(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    transacoes = db.query(models.Transacao).filter(
        models.Transacao.usuario_id == usuario.id
    ).all()

    resumo = defaultdict(lambda: {"receitas": 0.0, "despesas": 0.0, "saldo": 0.0})

    for t in transacoes:
        chave = t.criado_em.strftime("%Y-%m")
        if t.tipo == TipoTransacao.receita:
            resumo[chave]["receitas"] += t.valor
        else:
            resumo[chave]["despesas"] += t.valor
        resumo[chave]["saldo"] = resumo[chave]["receitas"] - resumo[chave]["despesas"]

    return dict(sorted(resumo.items()))


@app.get("/resumo/categorias")
def resumo_por_categoria(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    transacoes = db.query(models.Transacao).filter(
        models.Transacao.usuario_id == usuario.id
    ).all()

    resumo = defaultdict(float)

    for t in transacoes:
        chave = t.categoria or "sem categoria"
        resumo[chave] += t.valor

    return dict(sorted(resumo.items()))


@app.get("/saldo")
def calcular_saldo(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_atual)
):
    transacoes = db.query(models.Transacao).filter(models.Transacao.usuario_id == usuario.id).all()
    receitas = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.receita)
    despesas = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.despesa)
    return {"receitas": receitas, "despesas": despesas, "saldo": receitas - despesas}