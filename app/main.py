from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, transacoes, resumos

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finanças API")

app.include_router(auth.router)
app.include_router(transacoes.router)
app.include_router(resumos.router)

@app.get("/")
def inicio():
    return {"mensagem": "API de Finanças funcionando!"}