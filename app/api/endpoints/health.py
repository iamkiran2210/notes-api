from fastapi import APIRouter
from sqlalchemy import text
from app.api.deps import db_session


router = APIRouter()


@router.get("/")
def health_check():
    return {"msg": "Server is running..."}


@router.get("/db")
async def db_readiness(db: db_session):
    await db.execute(statement=text("select 1"))
    return {"msg": "Database is running..."}
