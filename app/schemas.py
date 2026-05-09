from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class TipoTransacao(str, Enum):
        receita = "receita"
        despesa = "despesa"


class TransacaoCreate(BaseModel):
        descricao: str = Field(min_length=3, max_length=120)
        valor: float = Field(gt=0)
        tipo: TipoTransacao
        categoria: Optional[str] = Field(default=None, max_length=60)


class TransacaoResponse(BaseModel):
        id: int
        descricao: str
        valor: float
        tipo: TipoTransacao
        categoria: Optional[str] = None
        criado_em: datetime

        class Config:
            from_attributes = True

class UsuarioCreate(BaseModel):
        nome: str = Field(min_length=2, max_length=100)
        email: EmailStr
        senha: str = Field(min_length=8, max_length=128)


class UsuarioResponse(BaseModel):
        id: int
        email: EmailStr

        class Config:
            from_attributes = True


class Token(BaseModel):
        access_token: str
        token_type: str
        