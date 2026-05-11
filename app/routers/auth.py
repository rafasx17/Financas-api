from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import Token, UsuarioCreate
from app.auth import hash_senha, verificar_senha, criar_token

router = APIRouter(tags=["Autenticação"])


@router.post("/registro", status_code=201)
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


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == form.username).first()
    if not usuario or not verificar_senha(form.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = criar_token({"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}