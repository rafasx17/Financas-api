import hashlib
import hmac
import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

# ── Configurações ────────────────────────────────────────────
SECRET_KEY = "troque-esta-chave-em-producao"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ── Hash de senha (hashlib nativo — sem bcrypt) ──────────────

def hash_senha(senha: str) -> str:
    salt = os.urandom(32)
    chave = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, 100_000)
    return salt.hex() + ":" + chave.hex()


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    try:
        salt_hex, chave_hex = hash_armazenado.split(":")
        salt = bytes.fromhex(salt_hex)
        chave_esperada = bytes.fromhex(chave_hex)
        chave_calculada = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, 100_000)
        return hmac.compare_digest(chave_calculada, chave_esperada)
    except Exception:
        return False


# ── JWT ──────────────────────────────────────────────────────

def criar_token(dados: dict) -> str:
    payload = dados.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str = Depends(oauth2_scheme)) -> str:
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise erro
        return email
    except JWTError:
        raise erro


# ── Usuário atual ─────────────────────────────────────────────

def get_usuario_atual(
    email: str = Depends(verificar_token),
    db: Session = Depends(get_db),
) -> models.Usuario:
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario