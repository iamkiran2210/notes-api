from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.core.config import settings
from app.database.base import Base


async_engine = create_async_engine(url=settings.DATABASE_URL)

asyncSessionLocal = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, autoflush=False
)


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with asyncSessionLocal() as session:
        try:
            yield session

        except Exception as e:
            await session.rollback()
            raise e

        finally:
            await session.close()
