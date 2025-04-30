from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Analisador de Feedback de Apps")

app.include_router(router)
