from fastapi import APIRouter
from app.modules import coleta, sentimentos, sugestoes  # importa os módulos que serão usados
import datetime

router = APIRouter()

@router.get("/")
async def index():
    return {"message": f"Server time: {datetime.date.today()}"}
